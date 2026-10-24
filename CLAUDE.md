# Homework 4 — Campus Custom Shop + Chatbot

Builds on Homework 3 (Campus Customs Agent in `../HMW 3`: product catalogue, PydanticAI agent, Portkey model calls). Reuse that work only where the Homework 4 instructions call for it.

## Prompt log (required for the assignment)

`AI_prompts.md` must record every prompt the user enters for this homework.

- After each user prompt, append a new `## Prompt N` entry (next number in sequence) with:
  - **User prompt:** the user's text verbatim (typos included). For screenshots, describe them in brackets, e.g. `[Screenshot of Problem 3 instructions]`.
  - **Assistant response:** a short summary (1–3 sentences) of what was explained or changed, naming any files edited.
- Never renumber, delete, or rewrite earlier entries. If later work corrects something from an earlier prompt, add a line to that earlier entry: `**Later correction (Prompt N):** <what changed>`.
- Never invent a prompt that wasn't actually entered. Mark unknown entries as not recorded.

## Working style

The user is learning. Explain the reasoning behind a change, not just the change. Assignment screenshots are sometimes cut off on purpose; don't ask for the rest.

## Running the app

In two terminals:
- Backend, from the `backend` folder: `cd backend` then `uvicorn main:app --reload --port 8000` (plain imports like `from auth import ...`; there's no package, so don't run it as `backend.main`)
- Frontend, from `HMW 4`: `npm run dev --prefix frontend` → http://localhost:5173

## To-do list (keep updated)

- [ ] **Expand Safety** in `backend/prompts/prompt.md` (currently "Safety basics") and write the harness Safety section.
- [ ] **Expand Tools**: more agent tools as problems need them; document them in the harness Tools section.
- [ ] Harness Models section (Portkey, `gpt-6-luna`, structured `ShopReply`, request cap).
- [ ] Save chat history to `chat_messages` for logged-in shoppers (suggested).
- [ ] Test-question script for the chatbot (suggested).
- [ ] Rate limit on `/api/chat` to protect the Portkey bill (suggested).
- [ ] Ask the user for the given accounts' hash iteration count (`LEGACY_ITERATIONS` in `backend/auth.py`).
- [ ] 15 empty 🛑 Adrian cells in the harness database section (user's own words).
- [ ] Final: public GitHub repo, push, file-tree problem.

## AV style for answer files (`output/harness.md`)

- Every answer the user writes is marked `🛑 **Adrian:**`; empty answer cells keep that marker so they know where to type.
- Make answers quick to read with headers, `---` dividers and **bold** key phrases. Formatting only: never change the user's words (typos stay).
- Keep the file UTF-8; Notepad/Word may re-save it as Windows-1252, so check and convert back after the user edits.

## Reminders

- After the user reviews the tables (`notes/database_review.md`), remind them to start `output/harness.md` with its first section: each table and why each field matters for the shop or the chatbot, written by the user. Later problems add sections for models, tools, safety and specs (as in HMW 2 and HMW 3), so leave room for them.
- Deadline: about 6.5 hours from the morning of 2026-10-24. Keep explanations short.
- `gh` is installed but not signed in; the user runs `gh auth login` before pushing.
- Password security (Prompt 40): when building the chatbot agent, its tools must only read `catalogue` and `inventory` (and the current user's own chat history), never the `users` table or `password_hash`, so a prompt-injected or curious AI can't reach the hashes. Put this in the harness Safety section.

## Before submitting (zip checklist)

- Make sure `AI_prompts.md` and any `.md` outputs are UTF-8 (Word re-saves them as UTF-16 or Windows-1252).
- Don't include `.env` (API keys); include `.env.example` instead.
