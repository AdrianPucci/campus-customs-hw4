# Campus Customs Harness

## 1. Database (`data/campus_customs.db`)

<!-- For each field: why it matters for the shop, the chatbot, or both. Your own words. -->

### `catalogue`: what we sell

| Field | Why it matters (shop / chatbot) |
|---|---|
| `product_id` | |
| `name` | |
| `garment_type` | |
| `description` | |
| `colors` | |
| `search_tags` | |
| `image_file_path` | |
| `price` | |

### `inventory`: stock by size

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | |
| `product_id` | |
| `size` | |
| `quantity` | |

### `users`: shopper accounts

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | |
| `name` | |
| `email` | |
| `password_hash` | |
| `created_at` | |
| `first_name` | |
| `last_name` | |

### `chat_messages` (optional)

| Field | Why it matters (shop / chatbot) |
|---|---|
| `id` | |
| `user_id` | |
| `role` | |
| `content` | |
| `products_json` | |
| `created_at` | |

## 2. Models

_To be added in a later problem._

## 3. Tools

_To be added in a later problem._

## 4. Safety

_To be added in a later problem._

## 5. Specs

_To be added in a later problem._
