<p align="center">
  <img src="static/images/logo.png" alt="AttachmentLens" width="480">
</p>

# AttachmentLens

A personal research tool for exploring attachment styles, relationship patterns, and emotional growth through AI-powered analysis of curated content.

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
- Sessions persist across app restarts (secret key stored in `./data/`)

🔍 **Smart Classification**
- Automatic keyword-based categorization of posts into 6 attachment-related categories
- Manual override on any post detail page
- Multi-tag support alongside the primary category
- Search and filter by category, read status, keyword, or date

📝 **Annotation & Insights**
- Highlight text from any post and save with personal reflections
- Floating "Save to Insights" button appears on text selection
- Searchable insights library
- Track which posts have been read (read/unread toggle + filter)

🧠 **AI-Powered Analysis**
- Generate personalized insights from your highlights using Claude API
- Customizable AI prompt (default: attachment-aware therapist persona)
- Analysis history with feedback tracking
- Past reflections and current feelings feed into future analyses for contextual continuity

🎭 **Modeled Posts**
- Generate new posts in Derek Hart's attachment style using AI
- Choose attachment style + topic; get a post that mirrors his voice

⭐ **Organization & Tracking**
- Favorite posts for quick access from the home page
- Like/comment metrics captured from Facebook; sort by popularity, likes, or comments
- Post dates captured and resolved from Facebook's relative timestamps ("3h" → real date)
- Sort library by newest, oldest, popularity, likes, or comments
- Full-text search across your library
- Edit and personalize post content with word-diff view

📊 **Stats Dashboard**
- Charts: category breakdown, read vs. unread, import timeline, top posts by popularity

💡 **Feature Requests**
- Submit feature requests directly from the nav bar using the 💡 Request button
- Requests are committed to the GitHub repository's `TODO.md` automatically
- Requires a GitHub Personal Access Token with `repo` scope (configured in ⚙️ Admin → Import/Update Posts)

⚙️ **Admin Tools** (in nav dropdown)
- Import Posts — Facebook console scraper with copy-to-clipboard, auto-scroll, bulk import
- Bulk Re-Label — table view with quick category dropdown per row; filter by category/read status/keyword
- Backup & Restore — export full database to JSON; re-import to restore
- GitHub Integration — connect your PAT to enable feature request commits
- Danger Zone — clear your personal insights, AI analysis history, or modeled posts

🎨 **User Experience**
- Dark theme optimized for comfort and focus
- Adjustable font sizes (80%–200%) via 🔤 Text control in nav
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

### Local Installation (Docker) — Recommended

```bash
git clone https://github.com/btaira/AttachmentLens.git
cd AttachmentLens
docker-compose up
```

Visit `http://localhost:5000` — your database and session key persist in `./data/`.

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

1. **Log in** — Visit `http://localhost:5000`; you'll be redirected to the login page. Default admin credentials: `admin` / `admin`
2. **Import posts** — Open ⚙️ Admin → 📥 Import/Update Posts; follow the steps to run the Facebook console scraper and paste the JSON
3. **Explore & annotate** — Browse posts, mark favorites, highlight passages
4. (Optional) **Set up AI** — Add your Anthropic API key on the 🧠 AI Insights page
5. (Optional) **Set up GitHub integration** — Add a GitHub PAT in ⚙️ Admin → Import/Update Posts to enable feature requests

---

## Importing Data

### Facebook Scraper

The Import Posts page provides a console script you paste into your browser's developer tools while on Derek Hart's Facebook profile. It:

- Auto-scrolls to collect posts up to your target count
- Captures post text, date, URL, likes, and comment count
- Resolves relative timestamps ("3h ago") to real dates
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

---

## Roadmap

**High Priority**
- [ ] User customization — 6 different background themes, choice of fonts and sizes
- [ ] Export to PDF — analyses and highlights formatted for therapy sessions
- [ ] Browser extension scraper — replaces fragile console script

**Medium Priority**
- [ ] Date range filtering in the library
- [ ] Category confidence score and boundary-case flagging
- [ ] Attachment style trend chart over time
- [ ] Duplicate detection on import

**Longer Term**
- [ ] Semantic search by meaning
- [ ] Therapist export pack (PDF)
- [ ] Mobile-friendly layout

---

## Project Structure

```
AttachmentLens/
├── app.py                 # Flask application & all routes
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile
├── restart.bat            # Windows: rebuild & restart Docker container
├── data/
│   ├── posts.db          # SQLite database (created on first run)
│   └── .secret_key       # Session secret key (persists across restarts)
├── static/
│   └── images/
│       └── logo.png      # App logo
├── templates/
│   ├── base.html         # Base layout, nav, styles, feature request modal
│   ├── login.html        # Login & register pages
│   ├── index.html        # Home + All Posts library
│   ├── post.html         # Post detail view
│   ├── category.html     # Category filter view
│   ├── insights.html     # User highlights
│   ├── ai_insights.html  # AI analysis interface
│   ├── modeled_posts.html # AI post generator
│   ├── stats.html        # Stats dashboard
│   ├── bulk_label.html   # Admin: bulk re-label
│   └── import.html       # Admin: import posts, GitHub integration, danger zone
└── README.md
```

---

## Security & Privacy

- Data stored **locally** in SQLite — no cloud, no telemetry
- API keys stored in the database (plaintext) — keep your database file secure
- Session-based authentication with per-user data isolation
- Session secret key persisted in `./data/.secret_key` so logins survive container restarts
- All routes require authentication; unauthenticated requests redirect to the login page

For therapy/medical contexts, consult your therapist before using any AI tools.

---

## Acknowledgments

- Inspired by attachment theory research (Bowlby, Ainsworth, Main, Levine & Heller)
- Built with Flask and SQLite
- AI features powered by Anthropic's Claude API

---

Made with care for self-reflection and healing. 💜
