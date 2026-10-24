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
| `product_id` | 🛑 **Adrian:** |
| `name` | 🛑 **Adrian:** |
| `garment_type` | 🛑 **Adrian:** |
| `description` | 🛑 **Adrian:** |
| `colors` | 🛑 **Adrian:** |
| `search_tags` | 🛑 **Adrian:** |
| `image_file_path` | 🛑 **Adrian:** |
| `price` | 🛑 **Adrian:** |

### `inventory`: stock by size

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `product_id` | 🛑 **Adrian:** |
| `size` | 🛑 **Adrian:** |
| `quantity` | 🛑 **Adrian:** |

### `users`: shopper accounts

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `name` | 🛑 **Adrian:** |
| `email` | 🛑 **Adrian:** |
| `password_hash` | 🛑 **Adrian:** |
| `created_at` | 🛑 **Adrian:** |
| `first_name` | 🛑 **Adrian:** |
| `last_name` | 🛑 **Adrian:** |

### `chat_messages` (optional)

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | 🛑 **Adrian:** |
| `user_id` | 🛑 **Adrian:** |
| `role` | 🛑 **Adrian:** |
| `content` | 🛑 **Adrian:** |
| `products_json` | 🛑 **Adrian:** |
| `created_at` | 🛑 **Adrian:** |

---

## 2. Models

_To be added in a later problem._

## 3. Tools

_To be added in a later problem._

## 4. Safety

_To be added in a later problem._

## 5. Specs

_To be added in a later problem._
