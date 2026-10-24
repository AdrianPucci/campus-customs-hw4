# Database Review: `data/campus_customs.db`

A study sheet for Problem 1. It's yours to read, not a submission file. Your own write-up goes in `output/harness.md`.

SQLite database, 4 tables. Numbers below were checked directly against the file.

```
catalogue (102 products)
   │ product_id
   ├────────────► inventory (612 rows = 102 products × 6 sizes)
   │
users (3 accounts)
   │ id
   └────────────► chat_messages (22 rows, saved chat history)
```

The arrows are **foreign keys**: `inventory.product_id` points at a row in `catalogue`, and `chat_messages.user_id` points at a row in `users`. That link is how you JOIN two tables, e.g. "show me this hoodie *with* its stock per size".

---

## 1. `catalogue`: what we sell

| Field | Type | Example | Why it matters |
|---|---|---|---|
| `product_id` | TEXT, **primary key** | `basic-hoodie-big-yale` | The unique ID of a product. Every other table and every API call refers to a product by this. It's a readable "slug", also matching the image file name. |
| `name` | TEXT | `Basic Hoodie Big Yale` | Display title on product cards; what the chatbot says out loud. |
| `garment_type` | TEXT | `pullover hoodie` | Lets shoppers and the agent filter by kind ("show me hoodies"). **Watch out:** labels are inconsistent: 22 different values, e.g. `hoodie`, `pullover hoodie`, `hooded sweatshirt` all mean hoodie; `t-shirt` vs `short-sleeve T-shirt` (capital T). A search for `= 'hoodie'` would miss most hoodies, so search with `LIKE '%hood%'` or match on tags too. |
| `description` | TEXT | `Navy pullover hoodie with a front kangaroo pocket…` | Product page text, and the agent's main source for answering "what does it look like?" Keeps the bot from inventing details. |
| `colors` | TEXT holding a **JSON list** | `["navy blue", "white"]` | Color filtering ("anything in gray?"). It's stored as text, so the backend must `json.loads()` it into a real list before using it. |
| `search_tags` | TEXT holding a **JSON list** | `["Yale hoodie", "navy hoodie", "college sweatshirt"]` | Extra keywords so fuzzy questions ("something for hockey fans", "gift for my dad") find the right items. Same JSON-in-text catch as `colors`. |
| `image_file_path` | TEXT | `products/basic-hoodie-big-yale.jpg` | Where the photo lives, **relative to the `data/` folder**. The backend must serve `data/products/` as web files (old chat logs show the URL `/media/products/...`) so the page can display it. |
| `price` | REAL (decimal) | `68.0` | The honest price the bot must quote. Prices come in tiers: T-shirts $32, performance/mockneck/some hoodies $45, crewnecks $58, most hoodies $68, quarter-zips $72, full-zip hoodies $88, jackets $98. |

## 2. `inventory`: stock by size

| Field | Type | Example | Why it matters |
|---|---|---|---|
| `id` | INTEGER, primary key, auto-increment | `1` | Internal row number. You'll rarely use it. |
| `product_id` | TEXT, **foreign key → catalogue** | `basic-hoodie-big-yale` | Connects the stock row to the product. |
| `size` | TEXT | `XS`, `S`, `M`, `L`, `XL`, `XXL` | Every product has all 6 sizes. Sort order matters on the page: alphabetical would give L, M, S, XL… so sort in size order yourself. |
| `quantity` | INTEGER | `0` to `25` | Units in stock. **0 = sold out in that size.** 145 of the 612 size slots are 0, but no product is fully sold out. This is the field the bot must check before saying "yes, we have it in M." |

`UNIQUE (product_id, size)` means there's exactly one row per product + size, never duplicates.

## 3. `users`: shopper accounts

| Field | Type | Example | Why it matters |
|---|---|---|---|
| `id` | INTEGER, primary key, auto-increment | `1` | The user's ID. Chat history and sign-in sessions attach to this. |
| `name` | TEXT, required | `Ada Lovelace` | Full name (older field). Still required, so sign-up must fill it, e.g. first + " " + last. |
| `email` | TEXT, required, **UNIQUE** | `test@campuscustoms.yale.edu` | The login username. UNIQUE means the database itself refuses a second account with the same email, so sign-up must catch that error and show "email already registered". |
| `password_hash` | TEXT, required | `pbkdf2_sha256$<salt>$<64 hex chars>` | **Never the real password.** Three parts split by `$`: the method (PBKDF2 with SHA-256), a salt (random text mixed in so equal passwords get different hashes), and the hash. Login = re-hash the typed password with the same salt and compare. New sign-ups must be saved in this same format. |
| `created_at` | TEXT, defaults to now | `2026-09-19 11:34:09` | When the account was made. Filled in automatically. |
| `first_name`, `last_name` | TEXT, optional | `Ada`, `Lovelace` | Added later (they're tacked onto the end of the table definition). Lets the bot greet people by first name. Optional, so old rows could be empty. |

Existing accounts: Test User, Ada Lovelace, Tauhid Zaman.

## 4. `chat_messages`: saved conversations (bonus table)

Not required for Problem 1, but a later problem probably uses it.

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key | Message order. |
| `user_id` | INTEGER, **foreign key → users** | Whose conversation it is, so each shopper sees only their own history. |
| `role` | TEXT: `user` or `assistant` | Who said it. 11 of each right now. |
| `content` | TEXT | The message text (bot replies use Markdown like `**$68**`). |
| `products_json` | TEXT holding JSON, optional | For bot replies: the products shown next to that answer (with stock per size), so the "matching items appear on the page" panel can be rebuilt when history reloads. Empty for user messages. |
| `created_at` | TEXT, defaults to now | Timestamp. |

---

## Check yourself

Try answering before you look back at the tables:

1. A shopper asks "Do you have the Crew Left Chest Hoodie in medium?" Which two tables does the bot need, and which field gives the answer?
2. Why doesn't the `users` table store the password itself?
3. Why would a search for `garment_type = 'hoodie'` give a bad answer?
4. `colors` looks like a list. Why can't Python loop over it straight out of the database?
5. Two people try to sign up with the same email. What stops the second one?
6. Which two fields together make sure an inventory row is never duplicated?



## 1. `catalogue`: what we sell
## 2. `inventory`: stock by size 
## 3. `users`: shopper accounts
## 4. `chat_messages`: saved conversations (bonus table)

