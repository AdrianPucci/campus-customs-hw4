"""FastAPI backend for Campus Customs.

Run from the HMW 4 folder:
    uvicorn backend.main:app --reload --port 8000
"""
import json
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .auth import router as auth_router
from .db import DATA_DIR, get_db

# Sizes sort in this order, not alphabetically (alphabetical would put L before S).
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API")

# image_file_path in the catalogue is relative to data/ (e.g. "products/x.jpg"),
# so the image URL is "/media/" + that path. Only the products folder is served,
# never data/ itself, or the database file would be downloadable.
app.mount("/media/products", StaticFiles(directory=DATA_DIR / "products"), name="media")
app.include_router(auth_router)


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
        "image_url": "/media/" + row["image_file_path"],
        "price": row["price"],
        "inventory": [{"size": r["size"], "quantity": r["quantity"]} for r in sizes],
        "total_stock": sum(r["quantity"] for r in sizes),
    }


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_db() as conn:
        products = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        stock: dict[str, list[sqlite3.Row]] = {}
        for r in conn.execute("SELECT product_id, size, quantity FROM inventory"):
            stock.setdefault(r["product_id"], []).append(r)
    return [product_to_dict(p, stock.get(p["product_id"], [])) for p in products]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()
    return product_to_dict(row, inventory)
