"""FastAPI backend for Campus Customs.

Run from the backend folder:
    cd backend
    uvicorn main:app --reload --port 8000
"""
import logging

from fastapi import Cookie, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic_ai.exceptions import UsageLimitExceeded

from agent import MAX_HISTORY_TURNS, ShopperDeps, ask_shop_agent
from auth import SESSIONS
from auth import router as auth_router
from chat_history import history_as_turns, load_history, save_message
from db import DATA_DIR, get_db
from models import ChatHistoryResponse, ChatRequest, ChatResponse
from tools import get_product_details, load_products, to_card

log = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")

# image_file_path in the catalogue is relative to data/ (e.g. "products/x.jpg"),
# so the image URL is "/media/" + that path. Only the products folder is served,
# never data/ itself, or the database file would be downloadable.
app.mount("/media/products", StaticFiles(directory=DATA_DIR / "products"), name="media")
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


@app.post("/api/chat")
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    shopper = current_shopper(cc_session)
    # Logged in: the saved history in the database is the context (it survives reloads and
    # can't be edited by the browser). Guests: whatever the chat panel sent.
    history = history_as_turns(shopper.user_id, MAX_HISTORY_TURNS) if shopper.logged_in else body.history

    try:
        answer = await ask_shop_agent(body.message, history, shopper)
    except UsageLimitExceeded:
        return ChatResponse(reply="Sorry, that one took me too long. Could you ask it a simpler way?", products=[])
    except Exception:
        log.exception("Chat agent failed")
        raise HTTPException(status_code=502, detail="The assistant is unavailable right now. Please try again.")

    # Show only real products: drop any id the model made up, keep its order, no repeats.
    ids = list(dict.fromkeys(answer.product_ids))
    cards = [to_card(p) for p in load_products(ids)] if ids else []

    # Saved only after a successful answer, so a failed request leaves no half-conversation.
    if shopper.logged_in:
        save_message(shopper.user_id, "user", body.message)
        save_message(shopper.user_id, "assistant", answer.message, cards)
    return ChatResponse(reply=answer.message, products=cards, saved=shopper.logged_in)


@app.get("/api/chat/history")
def chat_history(cc_session: str | None = Cookie(default=None)) -> ChatHistoryResponse:
    """The logged-in shopper's saved conversation, reloaded into the chat panel."""
    shopper = current_shopper(cc_session)
    if not shopper.logged_in:
        raise HTTPException(status_code=401, detail="Log in to see your saved chat.")
    return ChatHistoryResponse(messages=load_history(shopper.user_id))
