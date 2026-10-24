"""Saved chat history for logged-in shoppers, in the existing chat_messages table.

chat_messages: id, user_id -> users.id, role ('user' | 'assistant'), content,
products_json (the product cards shown with that reply, as JSON), created_at.
"""
import json

from db import get_db, get_db_writable
from models import ChatTurn, HistoryMessage, ProductCard
from tools import load_products, to_card

HISTORY_LIMIT = 50  # newest messages reloaded into the chat panel


def save_message(user_id: int, role: str, content: str, products: list[ProductCard] | None = None) -> None:
    products_json = json.dumps([p.model_dump() for p in products]) if products else None
    with get_db_writable() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )


def _cards_from_json(products_json: str | None) -> list[ProductCard]:
    """Rebuild a saved reply's cards from the database, so prices and stock are current.
    Works for both our saved cards and the older rows that stored full product data."""
    if not products_json:
        return []
    try:
        ids = [p["product_id"] for p in json.loads(products_json) if isinstance(p, dict) and "product_id" in p]
    except (ValueError, TypeError):
        return []
    return [to_card(p) for p in load_products(ids)] if ids else []


def load_history(user_id: int, limit: int = HISTORY_LIMIT) -> list[HistoryMessage]:
    """This shopper's newest messages, oldest first. Only ever their own rows."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [
        HistoryMessage(role=r["role"], content=r["content"], products=_cards_from_json(r["products_json"]))
        for r in reversed(rows)
    ]


def history_as_turns(user_id: int, limit: int) -> list[ChatTurn]:
    """The saved conversation as plain turns, for the agent's context."""
    return [ChatTurn(role=m.role, content=m.content) for m in load_history(user_id, limit)]
