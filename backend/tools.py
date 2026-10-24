"""Read-only product lookups, shared by the API and the agent's tools.

Only the catalogue and inventory tables are touched here, so nothing the agent
can call is able to reach the users table or password hashes.
"""
import json
import re
import sqlite3

from db import get_db
from models import (
    CatalogueOverview, CountAndPrices, ProductCard, ProductInfo, ProductSummary, SizeStock, StockReport,
)

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


def category(p: dict) -> str:
    """One simple category per product; the database's garment_type has 22 different spellings."""
    text = (p["garment_type"] + " " + p["name"]).lower()
    for cat, words in [
        ("quarter-zip", ["quarter-zip", "1 4 zip", "1/4 zip"]),
        ("jacket", ["jacket"]),
        ("hoodie", ["hood"]),
        ("long-sleeve", ["long-sleeve", "long sleeve"]),
        ("t-shirt", ["t-shirt", "t shirt"]),
        ("crewneck", ["crewneck", "crew", "sweatshirt", "mockneck"]),
    ]:
        if any(w in text for w in words):
            return cat
    return "other"


def _matches_color(color: str, colors: list[str]) -> bool:
    """'gray' or 'grey' matches 'heather gray'; 'blue' matches 'navy blue'; 'navy' matches 'navy'."""
    wanted = color.lower().replace("grey", "gray").strip()
    return any(wanted in c.lower() for c in colors)


def _summary(p: dict) -> ProductSummary:
    """The compact view the agent needs to pick products; keeps tool output small."""
    return ProductSummary(
        product_id=p["product_id"],
        name=p["name"],
        category=category(p),
        garment_type=p["garment_type"],
        price=p["price"],
        main_color=p["colors"][0] if p["colors"] else "",
        accent_colors=p["colors"][1:],
        sizes_in_stock=[s["size"] for s in p["inventory"] if s["quantity"] > 0],
        total_in_stock=p["total_stock"],
    )


def search_products(
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    color: str | None = None,
    color_anywhere: bool = False,
    category_filter: str | None = None,
    sort_by: str = "relevance",
    limit: int = 8,
) -> list[ProductSummary]:
    """Keyword search over name, type, description, colors and tags, with optional filters.

    color: the garment's own (main) color, unless color_anywhere also allows print/trim colors.
    sort_by: relevance (best match first), price_low, price_high, most_in_stock or name.
    """
    terms = _words(query) - STOP_WORDS
    scored = []
    for p in load_products():
        if max_price is not None and p["price"] > max_price:
            continue
        if min_price is not None and p["price"] < min_price:
            continue
        if category_filter and category(p) != category_filter:
            continue
        if color and not _matches_color(color, p["colors"] if color_anywhere else p["colors"][:1]):
            continue
        # Name and type matches count more than words buried in the description.
        strong = _words(p["name"] + " " + p["garment_type"] + " " + " ".join(p["search_tags"]))
        weak = _words(p["description"] + " " + " ".join(p["colors"]))
        score = sum(3 if t in strong else 1 if t in weak else 0 for t in terms)
        if score or not terms:
            scored.append((score, p))
    sort_keys = {
        "price_low": lambda sp: (sp[1]["price"], -sp[0], sp[1]["name"]),
        "price_high": lambda sp: (-sp[1]["price"], -sp[0], sp[1]["name"]),
        "most_in_stock": lambda sp: (-sp[1]["total_stock"], sp[1]["name"]),
        "name": lambda sp: sp[1]["name"],
    }
    scored.sort(key=sort_keys.get(sort_by, lambda sp: (-sp[0], sp[1]["name"])))
    return [_summary(p) for _, p in scored[:limit]]


def catalogue_overview() -> CatalogueOverview:
    products = load_products()
    cats: dict[str, list[float]] = {}
    main: dict[str, int] = {}
    accent: dict[str, int] = {}
    for p in products:
        cats.setdefault(category(p), []).append(p["price"])
        if p["colors"]:
            main[p["colors"][0]] = main.get(p["colors"][0], 0) + 1
        for c in p["colors"][1:]:
            accent[c] = accent.get(c, 0) + 1
    return CatalogueOverview(
        total_products=len(products),
        categories={c: CountAndPrices(count=len(v), min_price=min(v), max_price=max(v)) for c, v in sorted(cats.items())},
        main_colors=dict(sorted(main.items(), key=lambda kv: -kv[1])),
        accent_colors=dict(sorted(accent.items(), key=lambda kv: -kv[1])),
    )


def short_info(description: str, max_chars: int = 110) -> str:
    """First sentence of the description, cut at a word boundary if it's long."""
    first = description.split(". ")[0].rstrip(".")
    if len(first) <= max_chars:
        return first + "."
    return first[:max_chars].rsplit(" ", 1)[0].rstrip(",") + "…"


def to_card(p: dict) -> ProductCard:
    in_stock = [s["size"] for s in p["inventory"] if s["quantity"] > 0]
    return ProductCard(
        product_id=p["product_id"],
        name=p["name"],
        garment_type=p["garment_type"],
        price=p["price"],
        image_url=p["image_url"],
        short_info=short_info(p["description"]),
        sizes_in_stock=in_stock,
        in_stock=bool(in_stock),
    )


def get_product_details(product_id: str) -> dict | None:
    products = load_products([product_id])
    return products[0] if products else None


def find_product(id_or_name: str) -> dict | None:
    """Look up by product_id, or by exact product name if the AI passed the name instead."""
    key = id_or_name.strip()
    product = get_product_details(key)
    if product is None:
        with get_db() as conn:
            row = conn.execute("SELECT product_id FROM catalogue WHERE lower(name) = lower(?)", (key,)).fetchone()
        product = get_product_details(row["product_id"]) if row else None
    return product


def product_info(id_or_name: str) -> ProductInfo | None:
    p = find_product(id_or_name)
    if p is None:
        return None
    return ProductInfo(
        product_id=p["product_id"],
        name=p["name"],
        garment_type=p["garment_type"],
        description=p["description"],
        colors=p["colors"],
        price=p["price"],
    )


def stock_report(id_or_name: str, size: str | None = None) -> StockReport | None:
    p = find_product(id_or_name)
    if p is None:
        return None
    sizes = [SizeStock(size=s["size"], quantity=s["quantity"]) for s in p["inventory"]]
    report = StockReport(
        product_id=p["product_id"],
        name=p["name"],
        price=p["price"],
        sizes=sizes,
        total_in_stock=p["total_stock"],
    )
    if size:
        wanted = size.strip().upper()
        report.requested_size = wanted if wanted in SIZE_ORDER else None
        report.requested_size_quantity = next((s.quantity for s in sizes if s.size == wanted), None)
    return report
