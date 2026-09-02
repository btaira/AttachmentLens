<p align="center">
  <img src="static/images/logo.png" alt="AttachmentLens" width="480">
</p>

# AttachmentLens

A personal research tool for exploring attachment styles, relationship patterns, and emotional growth through AI-powered analysis of curated content.

# Disclaimer

This service/content is provided for general informational and educational purposes only. I am not a licensed therapist, mental health professional, or medical provider. I operate as an independent entity and am not affiliated with, endorsed by, or connected to any specific therapist, clinic, or mental health company.This information is not a substitute for professional mental health, psychological, or psychiatric advice, diagnosis, or treatment. Always seek the advice of your physician, licensed therapist, or other qualified health provider with any questions you may have regarding a medical or mental health condition.

## Overview

AttachmentLens helps you build self-awareness around attachment patterns by:

- **Importing** posts about attachment theory and relationships from Facebook via a browser console scraper
- **Auto-classifying** content into attachment styles (Anxious, Avoidant, Fearful, Secure, Healing & Growth)
- **Highlighting & annotating** passages that resonate with you
- **Analyzing** your collective highlights with Claude AI to uncover personal patterns
- **Tracking** favorites, reading progress, post dates, and analysis history

This is a personal journaling and research tool inspired by attachment theory frameworks. It's designed to support self-reflection and conversations with therapists or counselors.

## Features

👤 **Multi-User Support**
- Login and registration system (session-based authentication)
- Per-user favorites, insights, AI analyses, and modeled posts
- User switcher dropdown in the top-right nav bar
- Admin role for managing users, imports, and bulk-label
- Sessions persist across app restarts (secret key stored next to the database)

🔍 **Smart Classification**
- Automatic keyword-based categorization of posts into 6 attachment-related categories
- Manual override on any post detail page
- Multi-tag support alongside the primary category
- Search and filter by category, read status, keyword, or date

📝 **Annotation & Insights**
- Highlight text from any post and save with personal reflections
- Floating "Save to Insights" button appears on text selection (one line below, to the left)
- Text highlights in golden yellow (#c8a200) on the post view after saving
- Page automatically reloads after saving to display the golden highlight immediately
- Searchable insights library
- Track which posts have been read (read/unread toggle + filter)

🧠 **AI-Powered Analysis**
- Generate personalized insights from your highlights using Claude API
- Customizable AI prompt (default: attachment-aware therapist persona)
- Analysis history with feedback tracking
- Past reflections and current feelings feed into future analyses for contextual continuity
- ✨ **Quick Summary** — one-click AI summary of any individual post, without saving it as an insight

🎭 **Modeled Posts**
- Generate new posts in Derek Hart's attachment style using AI
- Choose attachment style + topic; get a post that mirrors his voice

⭐ **Organization & Tracking**
- Favorite posts for quick access from the home page
- Home page "Latest Posts" shows the 5 most recently dated posts
- Like/comment metrics captured from Facebook; sort by popularity, likes, or comments
- Post dates captured from Facebook; undated posts left blank for manual entry rather than guessing
- Imported dates are automatically locked to prevent re-imports from overwriting them
- Manually set or correct any post's date from the post detail page (manual dates are also locked)
- Sort library by newest, oldest, popularity, likes, or comments; undated posts treated as recent
- Full-text search across your library
- Edit and personalize post content with word-diff view

💡 **Feature Requests**
- Submit feature requests directly from the nav bar using the 💡 Request button
- Requests are committed to the GitHub repository's `TODO.md` automatically
- Requires a GitHub Personal Access Token with `repo` scope (configured in ⚙️ Admin → Import Posts)

⚙️ **Admin Tools** (in nav dropdown)
- Import Posts — Facebook console scraper with copy-to-clipboard, auto-scroll, bulk import
- Bulk Re-Label — table view with category dropdown, date column, date filter, sortable by date; select rows to bulk-apply a date to multiple posts at once
- Backup & Restore — export full database to JSON; re-import to restore
- GitHub Integration — connect a PAT to enable feature request commits and 🚀 **Push to GitHub**, which exports all current posts as `posts-database.json` directly to the repo (a shareable "best" starting dataset)
- Danger Zone — clear your personal insights, AI analysis history, or modeled posts

🎨 **User Experience**
- Dark theme optimized for comfort and focus
- Customizable appearance via 🎨 Customize button in nav:
  - 6 background themes: Dark, Ocean, Forest, Sunset, Twilight, Slate
  - 3 font families: Sans-Serif, Serif, Monospace
  - 3 font sizes: Normal (15px), Large (17px), X-Large (19px)
  - Preferences saved locally and synced to server
- Adjustable zoom levels (80%–200%) via 🔤 Text control in nav
- Sticky navigation bar with admin dropdown on the right
- Responsive design for desktop and tablet

---

## Getting Started

### Prerequisites

**Option 1 (Recommended): Docker**
- Docker Desktop ([download](https://www.docker.com/products/docker-desktop))

**Option 2: Python**
- Python 3.8+
- Flask 3.0+

**Optional:**
- Anthropic API key for AI analysis and Modeled Posts features
- GitHub Personal Access Token (`repo` scope) for feature request commits

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for a template):

```bash
# Anthropic API Key - get from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-...

# GitHub Personal Access Token - create at https://github.com/settings/tokens
# Use classic token with 'repo' scope (recommended) or fine-grained token with Contents → Read and write
GITHUB_TOKEN=ghp_... or github_pat_...
```

**Note:** Environment variables take precedence over database-stored values. This is the recommended way to manage sensitive credentials.

### Local Installation (Docker) — Recommended

```bash
git clone https://github.com/btaira/AttachmentLens.git
cd AttachmentLens
docker-compose up
```

Visit `http://localhost:5000` — your database (`posts.db`) and session key (`.secret_key`) persist in the project root via a Docker volume mount.

### Local Installation (Python)

```bash
git clone https://github.com/btaira/AttachmentLens.git
cd AttachmentLens
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app starts at `http://localhost:5000`.

### First Time Setup

1. **Configure environment variables** (optional but recommended)
   - Copy `.env.example` to `.env` and add your API keys:
     - `ANTHROPIC_API_KEY` for AI analysis
     - `GITHUB_TOKEN` for feature requests
   - Alternatively, you can enter these through the web UI (stored encrypted in the database)

2. **Log in** — Visit `http://localhost:5000`; you'll be redirected to the login page. Default admin credentials: `admin` / `admin`

3. **Import posts** — Open ⚙️ Admin → 📥 Import Posts; follow the steps to run the Facebook console scraper and paste the JSON

4. **Explore & annotate** — Browse posts, mark favorites, highlight passages

5. (Optional) **Set up AI** — If not using environment variables, add your Anthropic API key on the 🧠 AI Insights page

6. (Optional) **Set up GitHub integration** — If not using environment variables, add a GitHub PAT in ⚙️ Admin → Import Posts to enable feature requests

---

## Importing Data

### Chrome Extension (recommended)

`extension/` is an unpacked Chrome extension that replaces the console-paste
workflow below with a popup click. It scrapes the same way the console
script does, then sends the result straight to `/import_json` using your
browser's existing AttachmentLens session — no DevTools, no copy/paste.

**Install:**
1. Go to `chrome://extensions`, enable **Developer mode** (top right).
2. **Load unpacked** → select the `extension/` folder in this repo.
3. Click the extension icon → **Options** → set **AttachmentLens URL**
   (`http://localhost:5000` by default — change it if you're on a different
   port, Docker host, or a deployed URL) and a default post count.

**Use:**
1. Log in to AttachmentLens in one tab; open the Facebook profile to scrape
   in another.
2. Click the extension icon on the Facebook tab, adjust the post count if
   needed, click **Scrape Recent Posts**. Leave the tab open until it
   finishes — large scrapes (100+ posts) take a few minutes since Facebook
   needs time to load each scrolled batch.
3. Click **Import to AttachmentLens** to send the results directly (first
   time importing to a given URL, Chrome will prompt for permission to
   reach it). **Copy JSON** is there as a fallback if you'd rather paste
   into the Import page manually.

If the popup gets closed mid-scrape, progress is checkpointed to
`chrome.storage.local` — reopening it picks up where it left off (marked
"interrupted" if the scrape didn't finish). See `extension/README.md` for
more detail on how it works internally.

### Facebook Scraper (console fallback)

The Import Posts page also provides a console script you paste into your browser's developer tools while on Derek Hart's Facebook profile. It:

- Auto-scrolls to collect posts up to your target count
- Captures post text, date, URL, likes, and comment count
- Resolves relative timestamps ("3h ago", "Just now") to real dates
- Outputs JSON you paste back into the import form

### JSON Format

```json
[
  {
    "text": "The full text of the post",
    "date": "May 30, 2026",
    "url": "https://www.facebook.com/derek.michael.hart/posts/...",
    "likes": 42,
    "comments": 8
  }
]
```

Re-importing existing posts updates likes, comments, date, and URL without creating duplicates.

---

## AI Insights

Analyzes all your saved highlights together to identify patterns in your attachment style and relational tendencies.

### Setup

1. Get an API key from [Anthropic](https://console.anthropic.com)
2. Visit 🧠 **AI Insights**
3. Paste your API key (stored locally, never sent elsewhere)
4. Generate an analysis whenever you want

### How It Works

Each analysis collects all highlighted passages, groups them with their categories, includes your personal reflections and current feelings, references recent feedback notes, and sends everything to Claude for a personalized response. Full history is saved and searchable.

---

## Database

SQLite (`posts.db`) with these tables:

- **users** — accounts with hashed passwords and admin flag
- **user_post_prefs** — per-user favorites, read status, and tags (junction table)
- **posts** — imported content with categories, revisions, likes, comments, dates
- **insights** — highlighted text + personal reflections (per user)
- **ai_analyses** — generated analyses + feedback history (per user)
- **modeled_posts** — AI-generated posts in Derek Hart's style (per user)
- **settings** — API keys, custom prompts (per user)

All data is stored locally. Back up via ⚙️ Admin → 💾 Backup & Restore regularly.

`posts.db` is intentionally committed to this git repo (it's this personal instance's actual
data, not a generated artifact) — see `CLAUDE.md` for the rationale.

---

## Roadmap

**High Priority**
- [ ] Export to PDF — analyses and highlights formatted for therapy sessions
- [x] **Browser extension scraper** (Sept 2026) — `extension/` replaces the console script; scrapes and imports directly via `/import_json`, no DevTools paste needed

**Medium Priority**
- [ ] Date range filtering in the library
- [ ] Category confidence score and boundary-case flagging
- [ ] Attachment style trend chart over time
- [ ] Duplicate detection on import

**Longer Term**
- [ ] Semantic search by meaning
- [ ] Therapist export pack (PDF)
- [ ] Mobile-friendly layout

**Recently Completed** ✅
- [x] **Static Date** (June 2026) — Imported dates are auto-locked and won't be overwritten by future imports; user manual edits also lock dates
- [x] **Golden Yellow Insight Highlighting** (June 2026) — Saved insights display immediately in golden yellow; page reloads after save
- [x] **User Customization** (June 2026) — 6 background themes, 3 font families, 3 font sizes; all preferences persist across sessions

---

## Project Structure

```
AttachmentLens/
├── app.py                 # Flask application & all routes
├── dev_server.py          # Alternative dev server (see file docstring for why)
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Container image definition
├── Procfile               # Process entry point (Heroku-style platforms)
├── render.yaml            # Render.com deployment config
├── netlify.toml           # Netlify deployment config
├── posts.db               # SQLite database (tracked in git; see Database section)
├── CLAUDE.md              # Guidance for AI coding assistants working in this repo
├── TODO.md                # Feature roadmap; feature requests are committed here
├── docs/                  # Deployment/setup docs, published via GitHub Pages
│   ├── DEPLOYMENT.md
│   ├── DOCKER.md
│   ├── GITHUB_PAGES.md
│   ├── ROADMAP_ENHANCED.md
│   ├── SETUP_SUMMARY.md
│   └── STRATEGIC_VISION.md
├── scripts/               # One-off setup/utility scripts
│   ├── rebuild-docker.bat # Windows: rebuild & restart Docker
│   ├── start-docker.bat   # Start Docker container
│   ├── stop-docker.bat    # Stop Docker container
│   ├── logs-docker.bat    # View Docker logs
│   ├── open-browser.bat   # Open app in browser
│   ├── restart.bat / run.bat
│   ├── push_to_github.bat
│   ├── detect-secrets.bat # Secret-scanning check
│   ├── export_to_json.py  # Local CLI export of posts.db to JSON
│   └── DOCKER_QUICK_START.md
├── tests/                 # Test case docs (functional/) and runners (runners/)
├── static/
│   └── images/
│       └── logo.png       # App logo
├── templates/
│   ├── base.html          # Base layout, nav, styles, feature request modal
│   ├── login.html         # Login & register pages
│   ├── index.html         # Home + All Posts library
│   ├── post.html          # Post detail view
│   ├── category.html      # Category filter view
│   ├── insights.html      # User highlights
│   ├── ai_insights.html   # AI analysis interface
│   ├── modeled_posts.html # AI post generator
│   ├── bulk_label.html    # Admin: bulk re-label
│   └── import.html        # Admin: import posts, GitHub integration, danger zone
└── README.md
```

---

## Security & Privacy

- Data stored **locally** in SQLite — no cloud, no telemetry
- API keys stored in the database (plaintext) — keep your database file secure
- Session-based authentication with per-user data isolation
- Session secret key persisted in `.secret_key` (next to the database) so logins survive container restarts
- All routes require authentication; unauthenticated requests redirect to the login page

For therapy/medical contexts, consult your therapist before using any AI tools.

---

## Acknowledgments

- Inspired by attachment theory research (Bowlby, Ainsworth, Main, Levine & Heller)
- Built with Flask and SQLite
- AI features powered by Anthropic's Claude API

---

Made with care for self-reflection and healing. 💜
