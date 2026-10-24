"""Chat safety: rate limits, sensitive-data redaction, injection detection and an audit log.

Follows the OWASP Top 10 for LLM Applications where it applies to a shop chatbot:
unbounded consumption (rate limits), sensitive information disclosure (redaction),
and prompt injection (detected and logged; the agent's prompt and read-only tools do the blocking).
"""
import json
import logging
import re
import time
from collections import deque
from datetime import datetime, timezone

from db import DATA_DIR

log = logging.getLogger("campus_customs.safety")

# ---------- Rate limits (sliding windows) ----------
# (max messages, window in seconds). Guests are counted per IP address, shoppers per account.
GUEST_LIMITS = [(6, 60), (30, 3600)]
SHOPPER_LIMITS = [(12, 60), (120, 3600)]
SITE_LIMIT = (600, 3600)  # circuit breaker for the whole site: protects the Portkey bill

_hits: dict[str, deque[float]] = {}
_in_flight: set[str] = set()


def _retry_after(key: str, limit: int, window: int, now: float) -> int:
    """Seconds until another message is allowed for this key and window (0 = allowed now)."""
    hits = _hits.setdefault(key, deque())
    while hits and hits[0] <= now - window:
        hits.popleft()
    relevant = [t for t in hits if t > now - window]
    if len(relevant) < limit:
        return 0
    return int(relevant[-limit] + window - now) + 1


def check_rate_limit(user_id: int | None, ip: str) -> int:
    """0 if this message may go ahead (and counts it); otherwise seconds to wait."""
    now = time.time()
    key = f"user:{user_id}" if user_id is not None else f"ip:{ip}"
    limits = SHOPPER_LIMITS if user_id is not None else GUEST_LIMITS
    waits = [_retry_after(key, n, w, now) for n, w in limits]
    waits.append(_retry_after("site", *SITE_LIMIT, now))
    wait = max(waits)
    if wait:
        audit("rate_limited", key=key, retry_after=wait)
        return wait
    _hits[key].append(now)
    _hits["site"].append(now)
    return 0


def start_request(key: str) -> bool:
    """One message at a time per shopper. False if one is already being answered."""
    if key in _in_flight:
        audit("concurrent_request_blocked", key=key)
        return False
    _in_flight.add(key)
    return True


def end_request(key: str) -> None:
    _in_flight.discard(key)


# ---------- Sensitive data redaction ----------

CARD_RE = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")  # 13-19 digits, spaces or dashes between, ends on a digit
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PASSWORD_RE = re.compile(r"\b(password|passcode|pin)\b(\s*(is|:|=)\s*)\S+", re.IGNORECASE)


def _luhn_ok(digits: str) -> bool:
    """The checksum every real card number passes; avoids redacting order numbers or phone numbers."""
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d)
        if i % 2 == 1:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
    return total % 10 == 0


def redact_sensitive(text: str) -> tuple[str, list[str]]:
    """Remove card numbers, SSNs and passwords before the message reaches the AI or the database.
    Returns the cleaned text and what was removed (e.g. ["card number"])."""
    found: list[str] = []

    def card(m: re.Match) -> str:
        digits = re.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            found.append("card number")
            return "[card number removed]"
        return m.group()

    text = CARD_RE.sub(card, text)
    if SSN_RE.search(text):
        found.append("Social Security number")
        text = SSN_RE.sub("[SSN removed]", text)
    if PASSWORD_RE.search(text):
        found.append("password")
        text = PASSWORD_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[removed]", text)
    return text, found


# ---------- Prompt injection detection ----------

INJECTION_RE = re.compile(
    r"ignore (all |any |your |the |previous |prior )*(instructions|rules|prompt)"
    r"|(reveal|show|print|repeat) (me )?(your|the) (system )?(prompt|instructions)"
    r"|system prompt|developer mode|jailbreak|you are now|act as (an? )?(admin|developer|system)"
    r"|(list|show|give me) (all )?(the )?(users|customers|emails|password)",
    re.IGNORECASE,
)


def looks_like_injection(text: str) -> bool:
    """Flags common manipulation attempts for the audit log. It does not block them:
    the prompt's safety rules and the read-only tools already keep the agent safe."""
    return bool(INJECTION_RE.search(text))


# ---------- Audit log ----------

AUDIT_FILE = DATA_DIR / "safety_events.jsonl"  # in data/, so it never goes to GitHub


def audit(event: str, **details) -> None:
    """One JSON line per safety event (limit hit, redaction, injection attempt). Never the message text."""
    entry = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **details}
    log.warning("safety %s", entry)
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # logging must never break the chat
