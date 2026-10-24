"""Create-account / log-in endpoints.

Passwords are never stored. The users table keeps "pbkdf2_sha256$<salt>$<hash>":
PBKDF2-HMAC-SHA256 of the password with a random per-user salt.
"""
import hashlib
import hmac
import re
import secrets
import sqlite3

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from .db import get_db, get_db_writable

# The stored format has no slot for the iteration count, so every hash must use
# the same number. Change it here only if the course gives a different one.
PBKDF2_ITERATIONS = 100_000

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


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        method, salt, _ = stored.split("$")
    except ValueError:
        return False
    if method != "pbkdf2_sha256":
        return False
    # compare_digest takes the same time whether or not the start matches,
    # so the response time doesn't leak how close a guess was.
    return hmac.compare_digest(hash_password(password, salt), stored)


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
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")

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
def login(body: LoginRequest, response: Response) -> dict:
    email = body.email.strip().lower()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
    # Same message for "no such email" and "wrong password", so the form
    # can't be used to find out which emails have accounts.
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Email or password is incorrect.")
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
