# Homework 4 AI Prompt Log

This file records prompts provided by the user and the corresponding responses.

## Prompt 1

**User prompt:**

Homework 4 AI Class Campus Custom Shop + Chatbott

**Assistant response:**

Created the `HMW 4` folder with a `CLAUDE.md` (prompt-log rules, working style, zip checklist) and this prompt log. Noted that Homework 4 likely builds on the Homework 3 Campus Customs Agent, and asked for the first part of the assignment instructions before building anything.

## Prompt 2

**User prompt:**

[Screenshot of the Homework 4 Scenario: Campus Customs needs a customer website with a chatbot, built with a React + Vite TypeScript front end and a Python FastAPI backend run by a PydanticAI agent. Given `campus_customs.db` (catalogue, inventory by size, users with hashed passwords); research yalebulldogblue.com for style; use `PORTKEY_API_KEY` (OpenAI 5.6 or 6 series models); work one problem at a time; push to a public GitHub repo without the database or product images.] I need to do

**Assistant response:**

Explained the scenario: the parts of the system (React front end, FastAPI backend, PydanticAI agent, SQLite database) and how they connect. Checked the setup: Node, npm, Python and git are installed, the GitHub CLI is not, and `campus_customs.db` is not on this computer yet. Asked for the database and Problem 1. No files built.

## Prompt 3

**User prompt:**

downloaded data.zip for the assignment

**Assistant response:**

Extracted the new download (`Downloads/data (1).zip`, not the older Homework 3 `data.zip`) into `HMW 4/data/`: `campus_customs.db` and 102 product images in `data/products/`. Explained the database's four tables (catalogue, inventory, users, chat_messages), the hash format `pbkdf2_sha256$salt$hash`, and that `data/` must stay out of the public repo.

## Prompt 4

**User prompt:**

what about this?

**Assistant response:**

The user then pasted the earlier note: "The GitHub CLI (gh) isn't installed, but you don't need it: you can create the repo on github.com and push with plain git. I couldn't find campus_customs.db… put it in HMW 4…" Explained that the database note is already resolved (Prompt 3), and that `gh` is optional: the repo can be created on github.com and pushed with plain git at the end, or `gh` can be installed with winget. Nothing installed or changed.

## Prompt 5

**User prompt:**

[Screenshot of assignment instruction: create `AI_prompts.md` at the start of the assignment and keep it updated as you work; it is the log of what you typed to your vibe coder.]

**Assistant response:**

Confirmed this requirement is already covered: `AI_prompts.md` was created at Prompt 1 and gets a new entry after every prompt. The rules are written in `CLAUDE.md` so the log stays updated in future sessions too. No new files.

## Prompt 6

**User prompt:**

yes install

**Assistant response:**

Installed the GitHub CLI with winget (gh 2.103.2) and confirmed it runs. It is not signed in yet; the user will run `gh auth login` themselves before the push problem.

## Prompt 7

**User prompt:**

then: do you see it? [Screenshot of instruction: look at the database `data/campus_customs.db` and understand the fields of each table]

**Assistant response:**

Confirmed the database is at `data/campus_customs.db` and read every table's fields and row counts. Answered together with Prompts 8–9 (see Prompt 9).

## Prompt 8

**User prompt:**

I need to understand this- [Screenshot of instruction: at a minimum you should understand `catalogue`, `inventory`, and `users`]

**Assistant response:**

Answered together with Prompt 9.

## Prompt 9

**User prompt:**

what can you give me so I can review it?

**Assistant response:**

Created `notes/database_review.md`, a study sheet with a diagram of how the tables link, each field of `catalogue`, `inventory`, `users` (plus `chat_messages`) with type, example and why it matters for the shop or chatbot, the traps (inconsistent `garment_type` labels, JSON stored as text, size sort order, sold-out sizes, the `pbkdf2_sha256$salt$hash` format), and six self-check questions.

## Prompt 10

**User prompt:**

and by the way, good morning. We need to pull of this one like two bad ass bandits! I've had a wild two weeks and this puppy is due in 6.66 hours.. Lets rock and roll & crush it!

**Assistant response:**

Said good morning and noted the deadline (about 6.5 hours from this message), so the remaining work will move faster with shorter explanations.

## Prompt 11

**User prompt:**

Next once these prompts are done I want to start the file output/ harness.md I need to write down each table and why each field matters for the shop or the chatbot. Remind me to do this once we have reviewed the tables.

**Assistant response:**

Added the reminder to `CLAUDE.md` so it carries over, and reminded the user that once they've reviewed the tables, the next step is writing `output/harness.md` (each table and why each field matters) in their own words.

## Prompt 12

**User prompt:**

harness file is for later problems, (models, tools, safety, and specs) like our last assignments. cool?

**Assistant response:**

Agreed: `output/harness.md` grows as the project grows. The database section comes first, and models, tools, safety and specs sections are added in later problems, as in Homework 2 and 3. Updated the reminder in `CLAUDE.md` to match.

## Prompt 13

**User prompt:**

is the install going oK?

**Assistant response:**

Confirmed the GitHub CLI install finished successfully (gh 2.103.2 runs). The only step left is signing in with `gh auth login`, which the user does themselves before pushing.

## Prompt 14

**User prompt:**

I thought I did that last class but you didn't find it?

**Assistant response:**

Checked: Windows has a saved Git sign-in for github.com (Git Credential Manager), so the user did sign in last class, through git rather than the GitHub CLI, which was never installed before. Plain `git push` should work without signing in again; `gh` needs its own one-time sign-in only if used. Also found that git has no name/email set yet, which is needed before the first commit.

## Prompt 15

**User prompt:**

yes I'm ready to review

**Assistant response:**

Asked the user to answer the six self-check questions in `notes/database_review.md` in their own words before checking them, then to start the database section of `output/harness.md`.

## Prompt 16

**User prompt:**

Scaffold a React + Vite + TypeScript front end for the Campus Customs. Put a nav bar at the top that links to the main pages:

**Assistant response:**

Created `frontend/` with Vite's React + TypeScript template and added React Router. Checked yalebulldogblue.com for style (Yale-blue announcement bar, white header, Open Sans, uppercase menu) and built `components/NavBar.tsx` and the page routes in `App.tsx` to match. Removed the template's demo files and added a root `.gitignore` that keeps `data/`, `.env` and `node_modules/` out of git.

## Prompt 17

**User prompt:**

for Home, products, About us, Log In, Create Account

**Assistant response:**

Made those five pages in `frontend/src/pages/` and linked them in the nav bar. The active page is underlined. Log In and Create Account are forms only for now; signing in is connected to the backend in a later problem.

## Prompt 18

**User prompt:**

On the products page, show product images from the catalougue. Use the image path from the data base.

**Assistant response:**

The browser can't read SQLite, so added a small FastAPI backend (`backend/main.py`): `GET /api/products` reads `catalogue` and `inventory` (read-only) and adds `image_url = "/media/" + image_file_path`. Only `data/products/` is served at `/media/products`, so the database file can't be downloaded. The Vite dev server forwards `/api` and `/media` to port 8000. `ProductsPage.tsx` shows all 102 products with image, name and price. Verified in the browser: 102 cards, no broken images, and `/media/campus_customs.db` returns 404.

## Prompt 19

**User prompt:**

Then make each propduct open a sinigle-item page (Large image on one side, full product next on the other - description, price, sizes/ stock when we have them) Clicking a card on the products should take the shopper there. Any quesitons?

**Assistant response:**

No questions needed. Added `ProductDetailPage.tsx` at `/products/:productId`, fed by `GET /api/products/{product_id}`: large image on the left; type, name, price, description, colors and stock per size on the right (sizes in XS→XXL order, sold-out sizes crossed out). Product cards are now links to it. On phones the two columns stack.

## Prompt 20

**User prompt:**

Add a chat interface on the bottom right on the site. (floating chat panel works fine) It doesn't need to chat to the agent yet. it can be a stub that will call the backend later is enough for this problem.

**Assistant response:**

Added `components/ChatWidget.tsx`, a floating Chat button at the bottom right of every page that opens a panel with a greeting, message bubbles, a typing indicator and an input box. Replies come from `sendChatMessage()` in `src/api/chat.ts`, a stub that will later POST to `/api/chat` without changing the panel. Tested in the browser: sending a message shows it and the stub reply. Type check and lint pass.

## Prompt 21

**User prompt:**

I have logged into my github account fyi. Its on my browser

**Assistant response:**

Explained that a browser sign-in lets them create the public repo on github.com, while `git push` from this computer uses the separate GitHub sign-in already saved in Windows. Suggested starting git in `HMW 4` now (set name/email, first commit) so work is saved as it goes. Nothing changed.

## Prompt 22

**User prompt:**

Yes, start git in HMW 4 and make a first commit. My git name is ___ and my GitHub email is ___.

**Assistant response:**

Started git in `HMW 4` (branch `main`) and staged 33 files. Checked that `.gitignore` keeps out the database, product images, `node_modules`, build output and `__pycache__`. The name and email blanks weren't filled in, so the commit is waiting for them.

## Prompt 23

**User prompt:**

Name: <your name>, Email: <your GitHub email>

**Assistant response:**

The placeholders came through unfilled again (the reply button sends its text as-is). Offered a filled-in option, the name from the user's coursework files and the email on their Claude account, for the user to confirm before committing, since both will be public on GitHub.

## Prompt 24

**User prompt:**

Adrian Vellinga avdesign@live.com

**Assistant response:**

Set the git name and email for this project only (`git config` without `--global`) and made the first commit on `main` with the front end, backend, prompt log and notes. The database and images are not in it.

**Later correction (Prompt 25):** Git name changed to "Adrian V".

## Prompt 25

**User prompt:**

Actually can you change my name to Adrian V only

**Assistant response:**

Changed this project's git name to "Adrian V" and rewrote the first commit's author to match. That was safe because it hadn't been pushed yet. Email unchanged.

## Prompt 26

**User prompt:**

or too late?

**Assistant response:**

Not too late: the name change already went through. The commit hadn't been pushed, so its author could be rewritten. Only commits already on GitHub are effectively too late to change.

## Prompt 27

**User prompt:**

back to this prompt: I havent reviewed it and can't open the file

**Assistant response:**

Sent `notes/database_review.md` as a file card that opens in the side panel, and gave the full path for opening it in File Explorer. The review and the six self-check questions are still to do before writing the database section of `output/harness.md`.

## Prompt 28

**User prompt:**

[Screenshot of instruction: Look at the database `data/campus_customs.db`]

**Assistant response:**

Explained that a `.db` file can't be opened by double-clicking. It needs a SQLite viewer such as DB Browser for SQLite (free), or the study sheet sent at Prompt 27, which already lists every table and field. Offered to show sample rows from each table in chat.

## Prompt 29

**User prompt:**

what should I do?

**Assistant response:**

Gave a short plan for this problem: read the study sheet in the side panel (about 10 minutes), answer the six self-check questions in chat, then write the database section of `output/harness.md` in their own words. Installing a database viewer is optional.

## Prompt 30

**User prompt:**

Show me a few real rows from catalogue, inventory and users.

**Assistant response:**

Showed real rows read straight from the database: three catalogue rows plus the full description and tags for one, all six inventory rows for the Ice Hockey Left Chest Hoodie (M, L and XL sold out), and the three users with password hashes cut off after the salt. Pointed out what each example shows (JSON text, foreign key, sold-out sizes, salt per user).

## Prompt 31

**User prompt:**

where is the side panel? / I don

**Assistant response:**

Opened `notes/database_review.md` in the app's Files pane on the right side of the window, and gave the path for opening it in File Explorer or Notepad as a fallback.
