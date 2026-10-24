"""The shop chatbot: a PydanticAI agent whose model calls go through Portkey."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from models import ChatTurn, ProductInfo, ProductSummary, ShopReply, StockReport
from tools import product_info, search_products, stock_report

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR.parent / ".env")
SYSTEM_PROMPT = (BACKEND_DIR / "prompts" / "prompt.md").read_text(encoding="utf-8")

# At most this many model calls per shopper message (a normal answer uses 2 to 4).
# Caps cost if the agent gets stuck calling tools over and over.
MAX_MODEL_REQUESTS = 8
MAX_HISTORY_TURNS = 12  # older messages are dropped to keep requests small


@dataclass
class ShopperDeps:
    first_name: str | None  # None when nobody is logged in


def build_portkey_model() -> OpenAIResponsesModel:
    """Return a PydanticAI model that sends every AI call through Portkey."""
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is missing. Add it to HMW 4/.env.")
    base_url = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").strip()
    model_name = os.getenv("PORTKEY_MODEL", "gpt-6-luna").strip()
    headers = {"x-portkey-api-key": api_key}
    virtual_key = os.getenv("PORTKEY_VIRTUAL_KEY", "").strip()
    if virtual_key:
        headers["x-portkey-virtual-key"] = virtual_key
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, default_headers=headers)
    return OpenAIResponsesModel(model_name, provider=OpenAIProvider(openai_client=client))


shop_agent = Agent(
    build_portkey_model(),
    deps_type=ShopperDeps,
    output_type=ShopReply,
    system_prompt=SYSTEM_PROMPT,
)


@shop_agent.system_prompt
def shopper_name(ctx: RunContext[ShopperDeps]) -> str:
    if ctx.deps.first_name:
        return f"The shopper is logged in as {ctx.deps.first_name}."
    return "The shopper is not logged in."


# ---------- Tools: every answer about products comes from campus_customs.db ----------

NOT_FOUND = "No product matches {key!r}. Use find_products first to get a valid product_id."


@shop_agent.tool_plain
def find_products(query: str, max_price: float | None = None, browse: bool = False) -> list[ProductSummary]:
    """Search the catalogue. query: product words only, e.g. "navy hockey hoodie" or "mom" (leave sizes out).
    max_price: only items at or under this price.
    browse: True for "what X do you have?" questions; returns up to 30 matches instead of 8.
    Each match has product_id, price and sizes_in_stock. Sold-out sizes are simply missing from
    sizes_in_stock; the product is still one we carry."""
    # No size filter on purpose: filtering hid products whose size was sold out,
    # and the agent then wrongly said "we don't carry that".
    return search_products(query, max_price=max_price, limit=30 if browse else 8)


@shop_agent.tool_plain
def get_product_info(product_id: str) -> ProductInfo | str:
    """Description, price, garment type and colors for one product (product_id from find_products).
    Use when the shopper asks what an item looks like, what it's made of, or how much it costs."""
    return product_info(product_id) or NOT_FOUND.format(key=product_id)


@shop_agent.tool_plain
def check_stock(product_id: str, size: str | None = None) -> StockReport | str:
    """How many units are in stock for each size (XS-XXL) of one product, plus its price.
    size: optional, e.g. "M", to also get requested_size_quantity for that one size.
    Always call this before telling the shopper a size is available."""
    return stock_report(product_id, size) or NOT_FOUND.format(key=product_id)


def to_model_history(history: list[ChatTurn]) -> list[ModelMessage]:
    """Turn the chat panel's past messages into PydanticAI's message format."""
    messages: list[ModelMessage] = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


async def ask_shop_agent(message: str, history: list[ChatTurn], first_name: str | None) -> ShopReply:
    result = await shop_agent.run(
        message,
        message_history=to_model_history(history),
        deps=ShopperDeps(first_name=first_name),
        usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS),
    )
    return result.output
