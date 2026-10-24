"""Pydantic / PydanticAI structured types for the chat API and the agent."""
from typing import Literal

from pydantic import BaseModel, Field

Size = Literal["XS", "S", "M", "L", "XL", "XXL"]


# ---------- Products ----------

class SizeStock(BaseModel):
    size: Size
    quantity: int = Field(ge=0, description="Units in stock; 0 means sold out in this size.")


class ProductCard(BaseModel):
    """The small product card shown under a chat reply. Built from the database, never by the AI."""

    product_id: str
    name: str
    garment_type: str
    price: float
    image_url: str = Field(description='Browser path to the photo, e.g. "/media/products/yale-mom-hoodie.jpg"')
    short_info: str = Field(description="First sentence of the description, trimmed for a card.")
    sizes_in_stock: list[Size]
    in_stock: bool


# ---------- Agent tool results (what each tool hands back to the AI) ----------

class ProductSummary(BaseModel):
    """One search hit from find_products."""

    product_id: str
    name: str
    garment_type: str
    price: float
    sizes_in_stock: list[Size]


class ProductInfo(BaseModel):
    """get_product_info: the catalogue facts for one product."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(description="Every color on this one item (one colorway), not color choices.")
    price: float


class StockReport(BaseModel):
    """check_stock: units on hand per size, straight from the inventory table."""

    product_id: str
    name: str
    price: float
    sizes: list[SizeStock] = Field(description="All six sizes, XS to XXL, including sold-out ones (quantity 0).")
    total_in_stock: int
    requested_size: Size | None = None
    requested_size_quantity: int | None = Field(
        default=None, description="Units of requested_size on hand; 0 means sold out in that size."
    )


# ---------- Chat API (website <-> backend) ----------

class ChatTurn(BaseModel):
    """One earlier message in the conversation, sent back by the website for context."""

    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=40)


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)


# ---------- Agent output (PydanticAI structured output) ----------

class ShopReply(BaseModel):
    """What the agent must return: the answer, plus which products to show as cards."""

    message: str = Field(description="Friendly answer to the shopper. Plain text with **bold** for names and prices.")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="product_id of each catalogue item to show as a card on the page, best match first. "
        "For browsing questions (\"what hoodies do you have?\") include every good match, up to 30. "
        "Only ids returned by a tool. Empty if no product is relevant.",
    )
