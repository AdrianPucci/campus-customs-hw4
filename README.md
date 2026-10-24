# Campus Customs: Yale Bulldog Blue shop + chatbot

Homework 4 (AI class). A customer website for Campus Customs with a shopping chatbot:
**React + Vite + TypeScript** front end, **Python FastAPI** backend, and a **PydanticAI** agent
(OpenAI `gpt-6-luna` through Portkey) that answers from the store's SQLite database.

Shoppers can browse products, open a product page, create an account and log in, and chat about
merch. Matching items appear on the page as cards, and price and stock answers come from the
database.

## Project layout

```
backend/              FastAPI app + agent (run from this folder)
  main.py             API: products, auth, /api/chat and /api/chat/stream, media
  agent.py            PydanticAI agent: Portkey model, tools, shopper deps, streaming
  tools.py            read-only catalogue / inventory lookups used by the agent and the API
  models.py           Pydantic types: chat, product cards, tool results, audit entries
  prompts/prompt.md   system prompt: voice, honesty rules, tools, store info, safety
  auth.py             create account / log in (PBKDF2-SHA256, session cookie, lockout)
  chat_history.py     saves and reloads logged-in shoppers' chats (chat_messages table)
  safety.py           rate limits, card/SSN/password redaction, injection log
  audit_trail.py      append-only output/audit_trail.json of every agent run
frontend/             React + Vite + TypeScript site
output/
  harness.md          design notes: database, models, tools, safety, specs
  app_check.html      live test of the running site, with screenshots
  audit_trail.json    agent loop activity (created when the agent runs)
AI_prompts.md         log of every prompt given to the AI coding assistant
```

Not in this repo on purpose (see `.gitignore`): `data/` (the `campus_customs.db` database,
product photos and home-page media) and `.env` (API keys).

## Run it

1. Put the course `data/` folder (with `campus_customs.db` and `products/`) in the project root.
2. Copy `.env.example` to `.env` and fill in your Portkey key.
3. Backend:
   ```
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --port 8000
   ```
4. Front end (second terminal, project root):
   ```
   cd frontend
   npm install
   npm run dev
   ```
   Open http://localhost:5173. The dev server forwards `/api` and `/media` to the backend.

## Highlights

- **Honest answers**: prices and stock come only from tool calls on the database; product cards
  are built from the database, so made-up products can't appear.
- **Dynamic results**: "what hoodies do you have?" fills the page with matching product cards;
  every card opens the product page (large image, description, stock per size).
- **Context**: the agent knows the product page you're on ("does this come in gray?") and, when
  you're logged in, your name, email and saved chat history.
- **Usability**: seasonal suggestion chips, live "what the agent is doing" status, compact chat
  on phones.
- **Safety**: rate limits (HTTP 429), sensitive data removed before it reaches the AI, read-only
  tools, prompt-injection logging, OWASP-based safety rules, append-only audit trail.
