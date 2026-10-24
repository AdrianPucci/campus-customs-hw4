"""Read-only product lookups, shared by the API and the agent's tools.

Only the catalogue and inventory tables are touched here, so nothing the agent
can call is able to reach the users table or password hashes.
"""
import json
import re
import sqlite3

from db import get_db
from models import ProductCard

# Sizes sort in this order, not alphabetically (alphabetical would put L before S).
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# Everyday words that would match almost every product, so they don't count in a search.
STOP_WORDS = {"a", "an", "and", "any", "do", "for", "have", "i", "in", "is", "me", "my", "of", "show",
              "some", "something", "the", "to", "want", "with", "you", "yale", "looking", "need"}


def product_to_dict(row: sqlite3.Row, inventory: list[sqlite3.Row]) -> dict:
    """Turn a catalogue row into JSON-ready data with an image URL and stock per size."""
    sizes = sorted(inventory, key=lambda r: SIZE_ORDER.index(r["size"]))
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),  # stored as JSON text in the database
        "search_tags": json.loads(row["search_tags"]),
        "image_file_path": row["image_file_path"],
        # image_file_path is relative to data/ (e.g. "products/x.jpg"); main.py serves it under /media/
        "image_url": "/media/" + row["image_file_path"],
        "price": row["price"],
        "inventory": [{"size": r["size"], "quantity": r["quantity"]} for r in sizes],
        "total_stock": sum(r["quantity"] for r in sizes),
    }


def load_products(product_ids: list[str] | None = None) -> list[dict]:
    """All products (sorted by name), or just the given ids in the given order."""
    with get_db() as conn:
        if product_ids is None:
            rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        else:
            marks = ",".join("?" * len(product_ids))
            rows = conn.execute(f"SELECT * FROM catalogue WHERE product_id IN ({marks})", product_ids).fetchall()
        stock: dict[str, list[sqlite3.Row]] = {}
        for r in conn.execute("SELECT product_id, size, quantity FROM inventory"):
            stock.setdefault(r["product_id"], []).append(r)
    products = [product_to_dict(r, stock.get(r["product_id"], [])) for r in rows]
    if product_ids is not None:
        order = {pid: i for i, pid in enumerate(product_ids)}
        products.sort(key=lambda p: order[p["product_id"]])
    return products


def _words(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    # "hoodies" should match "hoodie", "shirts" should match "shirt"
    return words | {w[:-1] for w in words if w.endswith("s") and len(w) > 3}


def _summary(p: dict) -> dict:
    """The compact view the agent needs to pick products; keeps tool output small."""
    return {
        "product_id": p["product_id"],
        "name": p["name"],
        "garment_type": p["garment_type"],
        "price": p["price"],
        "colors": p["colors"],
        "sizes_in_stock": [s["size"] for s in p["inventory"] if s["quantity"] > 0],
    }


def search_products(query: str, max_price: float | None = None, size: str | None = None, limit: int = 8) -> list[dict]:
    """Keyword search over name, type, description, colors and tags, best match first."""
    terms = _words(query) - STOP_WORDS
    size = size.upper() if size else None
    scored = []
    for p in load_products():
        if max_price is not None and p["price"] > max_price:
            continue
        if size and not any(s["size"] == size and s["quantity"] > 0 for s in p["inventory"]):
            continue
        # Name and type matches count more than words buried in the description.
        strong = _words(p["name"] + " " + p["garment_type"] + " " + " ".join(p["search_tags"]))
        weak = _words(p["description"] + " " + " ".join(p["colors"]))
        score = sum(3 if t in strong else 1 if t in weak else 0 for t in terms)
        if score or not terms:
            scored.append((score, p))
    scored.sort(key=lambda sp: (-sp[0], sp[1]["name"]))
    return [_summary(p) for _, p in scored[:limit]]


def to_card(p: dict) -> ProductCard:
    in_stock = [s["size"] for s in p["inventory"] if s["quantity"] > 0]
    return ProductCard(
        product_id=p["product_id"],
        name=p["name"],
        garment_type=p["garment_type"],
        price=p["price"],
        image_url=p["image_url"],
        sizes_in_stock=in_stock,
        in_stock=bool(in_stock),
    )


def get_product_details(product_id: str) -> dict | None:
    products = load_products([product_id])
    return products[0] if products else None
