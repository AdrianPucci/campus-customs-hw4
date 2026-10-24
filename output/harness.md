# Campus Customs Harness

> **Key:** 🛑 **Adrian:** marks my own answers. Everything else is the template.

---

## 1. Database (`data/campus_customs.db`)

### 🛑 Adrian's overview: the 4 tables

- 🛑 **Adrian: Catalogue:** The catalogue, **shows what we sell** and gives the product id information, confirms it is a **unique item**, what type of clothing, and the key descriptors.
- 🛑 **Adrian: Inventory:** Inventory shows **how many of each item, size, quantity** ect. This is important to know what we have and **if there is enough** for what the shopper wants to buy.
- 🛑 **Adrian: Shopper accounts & chats:** Then we have shopper accounts and chat messages. The shopper accounts is a need to know list of who has shopped, and keeps their **login info** and when the account was created so we can **service the shoppers**.
- 🛑 **Adrian: Customer chats:** Lastly we have the customer chats. This is for us to have the ability to **answer easy questions** and **support the shoppers** in their purchases. If they can’t find something, if the inventory is low, if they want to request we carry other items we may not have instock can all be communicated and responded to.

---

### `catalogue`: what we sell

| Field | Why it matters (shop / chatbot) |
|---|---|
| `product_id` | 🛑 **Adrian:** gives the product id information, confirms it is a **unique item** |
| `name` | 🛑 **Adrian:** |
| `garment_type` | 🛑 **Adrian:** what type of clothing |
| `description` | 🛑 **Adrian:** the key descriptors |
| `colors` | 🛑 **Adrian:** |
| `search_tags` | 🛑 **Adrian:** |
| `image_file_path` | 🛑 **Adrian:** |
| `price` | 🛑 **Adrian:** |

### `inventory`: stock by size

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `product_id` | 🛑 **Adrian:** |
| `size` | 🛑 **Adrian:** **how many of each item, size, quantity** ect. |
| `quantity` | 🛑 **Adrian:** This is important to know what we have and **if there is enough** for what the shopper wants to buy. |

### `users`: shopper accounts

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `name` | 🛑 **Adrian:** a need to know list of who has shopped |
| `email` | 🛑 **Adrian:** keeps their **login info** |
| `password_hash` | 🛑 **Adrian:** keeps their **login info** |
| `created_at` | 🛑 **Adrian:** when the account was created so we can **service the shoppers** |
| `first_name` | 🛑 **Adrian:** |
| `last_name` | 🛑 **Adrian:** |

### `chat_messages` (optional)

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `user_id` | 🛑 **Adrian:** |
| `role` | 🛑 **Adrian:** |
| `content` | 🛑 **Adrian:** **answer easy questions** and **support the shoppers** in their purchases |
| `products_json` | 🛑 **Adrian:** |
| `created_at` | 🛑 **Adrian:** |

---

## 2. Models

_To be added in a later problem._

## 3. Tools

> Agent tools live in `backend/agent.py`; the lookups they call are in `backend/tools.py`.
> **All tools are read-only** and touch only `catalogue` and `inventory`, never `users`.

### The agent's tools

| Tool | Reads | Returns | Used when the shopper asks… |
|---|---|---|---|
| `find_products(query, max_price, browse)` | `catalogue` + `inventory` | list of `ProductSummary` (id, name, type, **price**, sizes in stock); up to 8, or **up to 30 with `browse=true`** | "what hoodies do you have?", "gift for my dad" |
| `get_product_info(product_id)` | `catalogue` | `ProductInfo` (**description**, **price**, type, colors) | "what does it look like?", "how much is…?" |
| `check_stock(product_id, size)` | `catalogue` + `inventory` | `StockReport` (**quantity per size** XS–XXL, total, the asked size's count) | "do you have it in M?", "how many left?" |

🛑 **Adrian:**

### How search results reach the page

1. **Shopper asks** in the chat panel → the website sends `POST /api/chat` with the message and recent history.
2. **Agent searches** with its tools and returns a structured `ShopReply`: a short `message` + the matching **`product_ids`**.
3. **Backend builds the cards** (`main.py`): looks each id up in the database and returns a `ProductCard` per product (image, name, **price**, short info, sizes in stock). **Ids that don't exist are dropped**, so the AI can't put a fake product on the page.
4. **Website shows them**: `ChatWidget` hands the cards to a shared `ChatResultsContext`; the **Matching items** section (`MatchingProducts.tsx`) shows them at the **top of whatever page is open** (up to 4 also appear inside the chat panel).
5. **Click a card → detail page** at `/products/<product_id>` (the Problem 3 single-item page): **large image + full description, price, colors and stock per size**. The page opens scrolled to the top; the matches shrink to a **"← Back to your N matching items"** bar so the detail view stays in sight.

```
Chat panel ─POST /api/chat─► FastAPI ─► Agent + tools ─► campus_customs.db
     ▲                          │ product_ids → ProductCards (from the DB)
     └──── reply + cards ◄──────┘
Cards on page ─click─► /products/<id> ─GET /api/products/<id>─► detail view
```

🛑 **Adrian:**

## 4. Safety

_To be added in a later problem._

## 5. Specs

_To be added in a later problem._
