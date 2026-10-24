"""The shop chatbot: a PydanticAI agent whose model calls go through Portkey."""
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, AgentRunResultEvent, RunContext
from pydantic_ai.messages import (
    FunctionToolCallEvent, ModelMessage, ModelRequest, ModelResponse, TextPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from models import (
    CatalogueOverview, Category, ChatTurn, ProductInfo, ProductSummary, ShopperProfile, ShopReply, SortBy,
    StockReport,
)
from tools import catalogue_overview as get_catalogue_overview
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
    """Who is chatting. Filled by main.py from the login session (never from the chat text),
    and handed to the agent on every run, so the model can't be talked into being someone else."""

    user_id: int | None = None  # None = guest (not logged in)
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    viewing_product_id: str | None = None  # product page open in the browser, if any

    @property
    def logged_in(self) -> bool:
        return self.user_id is not None


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
def who_is_chatting(ctx: RunContext[ShopperDeps]) -> str:
    # Name only here; the email is available through get_shopper_profile when it's needed.
    if ctx.deps.logged_in:
        who = (f"The shopper is logged in as {ctx.deps.first_name} {ctx.deps.last_name}. "
               "Their earlier conversation with you is saved and included above.")
    else:
        who = "The shopper is a guest (not logged in); this chat is not saved."
    return who + " " + viewing_note(ctx.deps.viewing_product_id)


def viewing_note(product_id: str | None) -> str:
    """Tells the agent which product page is open, so "this" and "it" make sense."""
    info = product_info(product_id) if product_id else None
    if info is None:
        return "They are not on a product page right now."
    return (f'They are looking at the product page for "{info.name}" (product_id {info.product_id}, '
            f"{info.garment_type}, ${info.price:.2f}, colors: {', '.join(info.colors)}). "
            '"This", "it" or "this one" means that product unless they say otherwise.')


@shop_agent.tool
def get_shopper_profile(ctx: RunContext[ShopperDeps]) -> ShopperProfile:
    """The logged-in shopper's own name and email (from their account). Use when they ask what
    name or email their account uses, or to personalize. Returns logged_in=false for guests."""
    d = ctx.deps
    if not d.logged_in:
        return ShopperProfile(logged_in=False)
    return ShopperProfile(logged_in=True, first_name=d.first_name, last_name=d.last_name, email=d.email)


# ---------- Tools: every answer about products comes from campus_customs.db ----------

NOT_FOUND = "No product matches {key!r}. Use find_products first to get a valid product_id."


@shop_agent.tool_plain
def find_products(
    query: str = "",
    category: Category | None = None,
    color: str | None = None,
    color_anywhere: bool = False,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: SortBy = "relevance",
    browse: bool = False,
) -> list[ProductSummary]:
    """Search the catalogue. Every argument is optional; combine them to match what the shopper describes.
    query: descriptive words, e.g. "vintage bulldog", "mom", "hockey", "zip" (leave sizes and colors out).
    category: hoodie, crewneck, t-shirt, long-sleeve, quarter-zip or jacket.
    color: the garment's own color, e.g. "navy", "gray", "cream". color_anywhere=true also matches
      print/trim colors (e.g. red lettering on a gray shirt).
    min_price / max_price: price limits. sort_by: relevance, price_low, price_high, most_in_stock, name.
    browse: true for "what X do you have?" questions; returns up to 30 instead of 8.
    Each match has main_color, accent_colors, price, sizes_in_stock and total_in_stock. Sold-out sizes
    are simply missing from sizes_in_stock; the product is still one we carry."""
    # No size filter on purpose: filtering hid products whose size was sold out,
    # and the agent then wrongly said "we don't carry that".
    return search_products(
        query, max_price=max_price, min_price=min_price, color=color, color_anywhere=color_anywhere,
        category_filter=category, sort_by=sort_by, limit=30 if browse else 8,
    )


@shop_agent.tool_plain
def catalogue_overview() -> CatalogueOverview:
    """What the store carries overall: product count, each category's count and price range, and every
    garment color and print color with counts. Use for "what colors do you have?", "do you have anything
    in pink?" (to offer the closest real colors), "what's your cheapest…?" or "what kinds of items?"."""
    return get_catalogue_overview()


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


async def ask_shop_agent(message: str, history: list[ChatTurn], shopper: ShopperDeps) -> ShopReply:
    result = await shop_agent.run(
        message,
        message_history=to_model_history(history),
        deps=shopper,
        usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS),
    )
    return result.output


# What the chat panel shows while each tool runs (the agent's real steps, not a timer).
TOOL_STATUS = {
    "find_products": "🔎 Searching the catalogue…",
    "get_product_info": "👕 Reading the product details…",
    "check_stock": "📦 Checking stock by size…",
    "catalogue_overview": "🎨 Looking over all our styles and colors…",
    "get_shopper_profile": "🙋 Checking your account…",
}


async def stream_shop_agent(
    message: str, history: list[ChatTurn], shopper: ShopperDeps
) -> AsyncIterator[str | ShopReply]:
    """Same as ask_shop_agent, but yields a status line as each tool starts, then the ShopReply."""
    yield "💭 Thinking about your question…"
    async with shop_agent.run_stream_events(
        message,
        message_history=to_model_history(history),
        deps=shopper,
        usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS),
    ) as events:
        async for event in events:
            if isinstance(event, FunctionToolCallEvent):
                yield TOOL_STATUS.get(event.part.tool_name, "⚙️ Working on it…")
            elif isinstance(event, AgentRunResultEvent):
                yield "✍️ Writing your answer…"
                yield event.result.output
