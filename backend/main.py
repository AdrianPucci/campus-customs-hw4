"""FastAPI backend for Campus Customs.

Run from the backend folder:
    cd backend
    uvicorn main:app --reload --port 8000
"""
import logging

from fastapi import Cookie, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic_ai.exceptions import UsageLimitExceeded

from agent import ask_shop_agent
from auth import SESSIONS
from auth import router as auth_router
from db import DATA_DIR, get_db
from models import ChatRequest, ChatResponse
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


@app.post("/api/chat")
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    first_name = None
    user_id = SESSIONS.get(cc_session or "")
    if user_id is not None:
        with get_db() as conn:
            row = conn.execute("SELECT first_name FROM users WHERE id = ?", (user_id,)).fetchone()
        first_name = row["first_name"] if row else None

    try:
        answer = await ask_shop_agent(body.message, body.history, first_name)
    except UsageLimitExceeded:
        return ChatResponse(reply="Sorry, that one took me too long. Could you ask it a simpler way?", products=[])
    except Exception:
        log.exception("Chat agent failed")
        raise HTTPException(status_code=502, detail="The assistant is unavailable right now. Please try again.")

    # Show only real products: drop any id the model made up, keep its order, no repeats.
    ids = list(dict.fromkeys(answer.product_ids))
    cards = [to_card(p) for p in load_products(ids)] if ids else []
    return ChatResponse(reply=answer.message, products=cards)
