"""Data shapes for the chat API and the agent's structured answer."""
from typing import Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=40)


class ShopReply(BaseModel):
    """What the agent must return: the answer, plus which products to show beside the chat."""

    message: str = Field(description="Friendly answer to the shopper. Plain text with light Markdown.")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="product_id of each catalogue item the answer recommends or talks about, best match first. "
        "Only ids returned by a tool. Empty if no product is relevant.",
    )


class ChatResponse(BaseModel):
    reply: str
    products: list[dict]  # full product data, same shape as /api/products
