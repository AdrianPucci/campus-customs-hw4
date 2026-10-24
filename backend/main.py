"""FastAPI backend for Campus Customs.

Run from the backend folder:
    cd backend
    uvicorn main:app --reload --port 8000
"""
import json
import logging
from dataclasses import dataclass

from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic_ai.exceptions import UsageLimitExceeded

from agent import MAX_HISTORY_TURNS, ShopperDeps, ask_shop_agent, stream_shop_agent
from auth import SESSIONS
from auth import router as auth_router
from chat_history import history_as_turns, load_history, save_message
from db import DATA_DIR, get_db
from models import ChatHistoryResponse, ChatRequest, ChatResponse, ShopReply
from safety import audit, check_rate_limit, end_request, looks_like_injection, redact_sensitive, start_request
from tools import get_product_details, load_products, to_card

log = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")

# image_file_path in the catalogue is relative to data/ (e.g. "products/x.jpg"),
# so the image URL is "/media/" + that path. Only the products folder is served,
# never data/ itself, or the database file would be downloadable.
app.mount("/media/products", StaticFiles(directory=DATA_DIR / "products"), name="media")
# Home page banner (a muted loop cut from the Campus Customs ad), kept in gitignored data/.
# check_dir=False: the site still starts without it; the page then shows its plain banner.
app.mount("/media/hero", StaticFiles(directory=DATA_DIR / "hero", check_dir=False), name="hero")
app.include_router(auth_router)


@app.get("/api/products")
def list_products() -> list[dict]:
    return load_products()


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    product = get_product_details(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def current_shopper(cc_session: str | None) -> ShopperDeps:
    """Who is chatting, from the login cookie. Guests get an empty ShopperDeps."""
    user_id = SESSIONS.get(cc_session or "")
    if user_id is None:
        return ShopperDeps()
    with get_db() as conn:
        row = conn.execute("SELECT id, first_name, last_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        return ShopperDeps()
    return ShopperDeps(user_id=row["id"], first_name=row["first_name"], last_name=row["last_name"], email=row["email"])


@dataclass
class Turn:
    """One chat message on its way through the safety checks and the agent."""

    shopper: ShopperDeps
    history: list
    message: str  # after redaction: this is what the AI sees and what gets saved
    notice: str | None  # shown to the shopper if something was removed from their message
    key: str  # who is chatting, for the one-message-at-a-time rule


def start_turn(body: ChatRequest, cc_session: str | None, request: Request) -> Turn:
    """Safety checks before the agent runs: rate limits, one message at a time, redaction."""
    shopper = current_shopper(cc_session)
    shopper.viewing_product_id = body.viewing_product_id
    ip = request.client.host if request.client else "unknown"
    key = f"user:{shopper.user_id}" if shopper.logged_in else f"ip:{ip}"

    wait = check_rate_limit(shopper.user_id, ip)
    if wait:
        raise HTTPException(
            status_code=429,
            detail=f"Whoa, Bulldog! 🐾 That's a lot of questions at once. Please try again in {wait} seconds.",
            headers={"Retry-After": str(wait)},
        )
    if not start_request(key):
        raise HTTPException(status_code=429, detail="I'm still working on your last question. One moment! ⏳")

    message, removed = redact_sensitive(body.message)
    notice = None
    if removed:
        audit("redacted", key=key, kinds=removed)
        notice = (f"🔒 For your safety we removed the {' and '.join(removed)} from your message. "
                  "Please never share payment details or passwords in chat.")
    if looks_like_injection(message):
        audit("injection_attempt", key=key)

    # Logged in: the saved history in the database is the context (it survives reloads and
    # can't be edited by the browser). Guests: whatever the chat panel sent.
    history = history_as_turns(shopper.user_id, MAX_HISTORY_TURNS) if shopper.logged_in else body.history
    return Turn(shopper, history, message, notice, key)


def finish_turn(turn: Turn, answer: ShopReply) -> ChatResponse:
    """Turn the agent's answer into the response: real product cards, saved if logged in."""
    # Show only real products: drop any id the model made up, keep its order, no repeats.
    ids = list(dict.fromkeys(answer.product_ids))
    cards = [to_card(p) for p in load_products(ids)] if ids else []
    # Saved only after a successful answer, so a failed request leaves no half-conversation.
    # Guests are never saved. The saved user message is the redacted one.
    if turn.shopper.logged_in:
        save_message(turn.shopper.user_id, "user", turn.message)
        save_message(turn.shopper.user_id, "assistant", answer.message, cards)
    return ChatResponse(
        reply=answer.message, products=cards, saved=turn.shopper.logged_in,
        notice=turn.notice, shown_message=turn.message if turn.notice else None,
    )


def ndjson(obj: dict) -> str:
    """One line of newline-delimited JSON."""
    return json.dumps(obj) + "\n"


TOO_LONG = "Sorry, that one took me too long. Could you ask it a simpler way?"
UNAVAILABLE = "The assistant is unavailable right now. Please try again."


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    turn = start_turn(body, cc_session, request)
    try:
        answer = await ask_shop_agent(turn.message, turn.history, turn.shopper)
        return finish_turn(turn, answer)
    except UsageLimitExceeded:
        return ChatResponse(reply=TOO_LONG, products=[])
    except Exception:
        log.exception("Chat agent failed")
        raise HTTPException(status_code=502, detail=UNAVAILABLE)
    finally:
        end_request(turn.key)


@app.post("/api/chat/stream")
async def chat_stream(
    body: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)
) -> StreamingResponse:
    """Like /api/chat, but sends one JSON line per step as it happens (NDJSON):
    {"type": "status", "text": "📦 Checking stock by size…"} ... then {"type": "done", ...ChatResponse}.
    Rate limits are checked first, so a limited request gets a normal 429 response."""
    turn = start_turn(body, cc_session, request)

    async def lines():
        if turn.notice:
            # First line, before the agent runs: the chat swaps in the cleaned message right away,
            # so a card number never stays on screen even if the agent then fails.
            yield ndjson({"type": "redacted", "shown_message": turn.message, "notice": turn.notice})
        try:
            async for item in stream_shop_agent(turn.message, turn.history, turn.shopper):
                if isinstance(item, ShopReply):
                    yield ndjson({"type": "done", **finish_turn(turn, item).model_dump()})
                else:
                    yield ndjson({"type": "status", "text": item})
        except UsageLimitExceeded:
            yield ndjson({"type": "done", **ChatResponse(reply=TOO_LONG).model_dump()})
        except Exception:
            log.exception("Chat agent failed")
            yield ndjson({"type": "error", "detail": UNAVAILABLE})
        finally:
            end_request(turn.key)

    return StreamingResponse(lines(), media_type="application/x-ndjson")


@app.get("/api/chat/history")
def chat_history(cc_session: str | None = Cookie(default=None)) -> ChatHistoryResponse:
    """The logged-in shopper's saved conversation, reloaded into the chat panel."""
    shopper = current_shopper(cc_session)
    if not shopper.logged_in:
        raise HTTPException(status_code=401, detail="Log in to see your saved chat.")
    return ChatHistoryResponse(messages=load_history(shopper.user_id))
