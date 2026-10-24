# Campus Customs Site Design

> Draft of what was built (written with the AI assistant). 🛑 **Adrian:** marks my own notes.

---

## Brand and look

- **Based on the real store**, yalebulldogblue.com: a Yale-blue "Officially Licensed Merchandise" bar, a white header with a YALE / BULLDOG BLUE wordmark, and uppercase menu links.
- **Colors:** Yale blue `#00356b` for headings, buttons and the chat; white and light gray surfaces; **fall orange `#c8742b`** used only for small seasonal accents.
- **Fonts:** **Open Sans** for everything (matches the real site); **Showcard Gothic** for the "Boola Boola" graffiti tag (falls back to Bungee where Showcard isn't installed).

🛑 **Adrian:**

## Pages

| Page | What's on it |
|---|---|
| **Home** | Muted, looping clip from the Campus Customs ad behind "Wear the Blue."; a New Haven graffiti band with the seasonal tag; Shop Products button |
| **Products** | All 102 items as cards: photo, name, price |
| **Product page** | Large image on one side; type, name, price, description, colors and stock per size on the other |
| **About Us / Log In / Create Account** | Store blurb; login and sign-up forms (confirm password, error messages) |
| **Chat (every page)** | Floating panel, bottom right; results also appear as cards at the top of the page |

🛑 **Adrian:**

## Seasonal, slightly urban touches (kept subtle)

- **Angled lines:** the footer is a Yale-blue band with a slanted top edge and faint orange diagonal stripes; two angled orange and white stripes cross the hero's corner.
- **Graffiti tag:** "Boola Boola" in a spray-paint style with three slowly drifting leaves, on a band of **New Haven street graffiti** under the video. It changes with the season (leaves in fall, snowflakes in winter, petals in spring) and stays still for people who turn on "reduce motion".
- **Home video:** a 1 MB web version of the 9-second ad (from 11.5 MB), with the wide crew shot as the still image.

🛑 **Adrian:**

## Phones and small windows

- Product page columns stack; nav links wrap.
- The chat becomes a **compact 280×340 box in the lower right** (about 30% of a phone screen instead of nearly all of it), so the page and its cards stay visible.

🛑 **Adrian:**

## Media and privacy

- Product photos, the ad clip and the graffiti photo live in `data/` and are served by FastAPI; they're **not in the GitHub repo** (`.gitignore`), as the assignment requires for product images.
