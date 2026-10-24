"""Create-account / log-in endpoints.

Passwords are never stored. The users table keeps only a PBKDF2-HMAC-SHA256 hash
with a random per-user salt:
  new accounts:   "pbkdf2_sha256$<iterations>$<salt>$<hash>"
  given accounts: "pbkdf2_sha256$<salt>$<hash>" (older format, no iteration count)
"""
import hashlib
import hmac
import re
import secrets
import sqlite3
import time

from fastapi import APIRouter, Cookie, HTTPException, Request, Response
from pydantic import BaseModel

from db import get_db, get_db_writable

# Work factor for new hashes (OWASP's current recommendation for PBKDF2-SHA256).
# Each guess costs an attacker this many rounds, so stolen hashes are slow to crack.
PBKDF2_ITERATIONS = 600_000
# The given accounts' hashes don't record their count. Change this one number
# if the course says which count it used.
LEGACY_ITERATIONS = 100_000

MAX_PASSWORD_LENGTH = 128  # stops absurdly long inputs from tying up the server

# Login attempt limit: after 5 failures for one email (or from one address)
# within 15 minutes, further attempts are refused until the window passes.
MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60
FAILED_LOGINS: dict[str, list[float]] = {}

SESSION_COOKIE = "cc_session"
# token -> user id. Kept in memory, so everyone is logged out when the server restarts.
SESSIONS: dict[str, int] = {}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

router = APIRouter(prefix="/api/auth")


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)  # 128 random bits, different for every account
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${_pbkdf2(password, salt, PBKDF2_ITERATIONS)}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if parts[0] != "pbkdf2_sha256":
        return False
    if len(parts) == 4 and parts[1].isdigit():  # new format
        _, iterations, salt, expected = parts
        actual = _pbkdf2(password, salt, int(iterations))
    elif len(parts) == 3:  # given accounts
        _, salt, expected = parts
        actual = _pbkdf2(password, salt, LEGACY_ITERATIONS)
    else:
        return False
    # compare_digest takes the same time whether or not the start matches,
    # so the response time doesn't leak how close a guess was.
    return hmac.compare_digest(actual, expected)


def _recent_failures(key: str) -> list[float]:
    cutoff = time.time() - LOCKOUT_SECONDS
    recent = [t for t in FAILED_LOGINS.get(key, []) if t > cutoff]
    FAILED_LOGINS[key] = recent
    return recent


def public_user(row: sqlite3.Row) -> dict:
    """Only what the browser needs; never the password hash."""
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
    }


def start_session(response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user_id
    # httponly: page scripts can't read the cookie; samesite=lax blocks most cross-site use.
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7)


@router.post("/register", status_code=201)
def register(body: RegisterRequest, response: Response) -> dict:
    first = body.first_name.strip()
    last = body.last_name.strip()
    email = body.email.strip().lower()
    if not first or not last:
        raise HTTPException(400, "First and last name are required.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if not 8 <= len(body.password) <= MAX_PASSWORD_LENGTH:
        raise HTTPException(400, f"Password must be 8 to {MAX_PASSWORD_LENGTH} characters.")

    with get_db_writable() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", email, hash_password(body.password), first, last),
            )
        except sqlite3.IntegrityError:  # email column is UNIQUE
            raise HTTPException(409, "An account with this email already exists.")
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()

    start_session(response, row["id"])
    return public_user(row)


@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response) -> dict:
    email = body.email.strip().lower()
    keys = [f"email:{email}", f"ip:{request.client.host if request.client else '?'}"]
    if any(len(_recent_failures(k)) >= MAX_FAILED_LOGINS for k in keys):
        raise HTTPException(429, "Too many failed attempts. Please wait 15 minutes and try again.")

    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
    # Same message for "no such email" and "wrong password", so the form
    # can't be used to find out which emails have accounts.
    if (
        row is None
        or len(body.password) > MAX_PASSWORD_LENGTH
        or not verify_password(body.password, row["password_hash"])
    ):
        for k in keys:
            FAILED_LOGINS.setdefault(k, []).append(time.time())
        raise HTTPException(401, "Email or password is incorrect.")

    for k in keys:
        FAILED_LOGINS.pop(k, None)
    start_session(response, row["id"])
    return public_user(row)


@router.post("/logout")
def logout(response: Response, cc_session: str | None = Cookie(default=None)) -> dict:
    if cc_session:
        SESSIONS.pop(cc_session, None)
    response.delete_cookie(SESSION_COOKIE)
    return {"ok": True}


@router.get("/me")
def me(cc_session: str | None = Cookie(default=None)) -> dict:
    user_id = SESSIONS.get(cc_session or "")
    if user_id is None:
        raise HTTPException(401, "Not logged in.")
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(401, "Not logged in.")
    return public_user(row)
