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

🛑 **Adrian:** General descriptors give the categories for each of the sub items that may be introduced by a user in the chat. Each is important for providing the customer with the feedback and items they are looking for.

| Field | Why it matters (shop / chatbot) |
|---|---|
| `product_id` | 🛑 **Adrian:** gives the product id information, confirms it is a **unique item** |
| `name` | 🛑 **Adrian:** Item name and type |
| `garment_type` | 🛑 **Adrian:** what type of clothing |
| `description` | 🛑 **Adrian:** the key descriptors |
| `colors` | 🛑 **Adrian:** Color descriptor |
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

> Drafted with the AI assistant from the code; 🛑 marks my notes.

| Item | Choice | Why |
|---|---|---|
| **Model** | OpenAI **`gpt-6-luna`** (6 series) | Strong at tool calling and following a long system prompt |
| **Gateway** | **Portkey** (`PORTKEY_API_KEY`) | Course key; one place for usage and cost |
| **Framework** | **PydanticAI** `Agent` (`backend/agent.py`) | Typed tools, typed output, per-shopper deps, streaming events |
| **System prompt** | `backend/prompts/prompt.md` | Voice, honesty rules, tools, store info, safety |
| **Cache** | Portkey cache forced off | Cached replies broke repeated questions; stock changes anyway |

**Structured types** (`backend/models.py`): `ShopReply` is the agent's required output (`message` + `product_ids`); `ProductSummary`, `ProductInfo`, `StockReport`, `CatalogueOverview` are tool results; `ProductCard` is a page card **built from the database, never by the AI**; `ChatRequest` / `ChatResponse` connect the website and backend; `AuditEntry` is one audit-trail line.

**Who is chatting (deps):** `ShopperDeps` carries the **user id, name, email** and the **open product page**, filled **from the login cookie, never from chat text**. The tool `get_shopper_profile` returns the shopper's own email when asked.

**Loop limits:** max **8 model calls** per message; last **12** turns as history.

🛑 **Adrian:**

## 3. Tools

> Read-only lookups on `catalogue` and `inventory` (`backend/tools.py`); never the `users` table.

| Tool | Returns | Used when the shopper asks… |
|---|---|---|
| `find_products(query, category, color, min/max_price, sort_by, browse)` | Matches with **price**, colors, sizes in stock; up to 30 when browsing | "what hoodies do you have?", "cheapest hoodie", "cream crewnecks" |
| `get_product_info(product_id)` | **Description**, **price**, type, colors | "what does it look like?", "how much is it?" |
| `check_stock(product_id, size)` | **Quantity per size** XS-XXL | "do you have it in M?", "how many left?" |
| `catalogue_overview()` | Categories with price ranges, every color | "what colors do you have?", "anything in pink?" |
| `get_shopper_profile()` | The logged-in shopper's own name and email | "what email is my account under?" |

**Page context:** "this" / "it" = the product page that's open.

### How search results reach the page

1. The chat sends `POST /api/chat/stream` (message, history, open page).
2. Each tool call streams a **live status** ("🔎 Searching the catalogue…").
3. The agent returns `ShopReply` with **`product_ids`**.
4. The backend builds `ProductCard`s **from the database**; unknown ids are dropped.
5. Cards appear in **Matching items** at the top of the page; clicking one opens `/products/<id>` (large image, description, price, stock per size).

**Chat history:** logged-in shoppers' chats are saved in `chat_messages` and reloaded; guests' are never saved.

🛑 **Adrian:**

## 4. Safety

> Based on the **OWASP Top 10 for LLM Applications**; code in `backend/safety.py`, rules in `prompt.md`.

| Risk | What we do |
|---|---|
| **Too many requests / cost** | Guests **6/min, 30/hour** per IP; shoppers **12/min, 120/hour**; site **600/hour**; one message at a time; **HTTP 429** + "Whoa, Bulldog! 🐾" |
| **Sensitive data** | **Card numbers, SSNs, passwords removed before** the AI or database sees them, with a 🔒 notice |
| **Prompt injection** | Attempts logged; read-only tools and prompt rules keep the agent safe |
| **Data leaks** | Tools can't read `users`; only the shopper's own name and email; identity from the login |
| **Passwords** | PBKDF2-SHA256, 600,000 rounds, random salt; 5 failed logins → 15-min lockout |
| **Made-up answers** | Prices and stock only from tools; cards from the database |
| **Unsafe content** | On-topic, family-friendly, no medical or legal advice, crisis → 911 / 988 |
| **Audit** | `output/audit_trail.json` (every agent run); safety log in `data/` |
| **Secrets** | `.env`, database and product images gitignored |

🛑 **Adrian:**

## 5. Specs

**Stack:** React + Vite + TypeScript · FastAPI (run from `backend/`) · PydanticAI · SQLite · Portkey → `gpt-6-luna`.

| API | Does |
|---|---|
| `GET /api/products`, `/api/products/{id}` | Catalogue with stock and image URL |
| `POST /api/chat/stream` (and `/api/chat`) | Chat: live status, then reply + product cards |
| `GET /api/chat/history` | Logged-in shopper's saved chat |
| `POST /api/auth/register`, `/login`, `/logout`; `GET /api/auth/me` | Accounts |

**Acceptance checks (passed; see `app_check.html`):** stock by size matches the database (Yale Dad Hoodie); "what hoodies?" → 27 cards = all 27 hoodies; cards open the detail page; seasonal chips and live status; accounts and saved chat; card number removed, 7th guest message → 429.

🛑 **Adrian:**
