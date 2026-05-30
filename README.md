# AttachmentLens

A personal research tool for exploring attachment styles, relationship patterns, and emotional growth through AI-powered analysis of curated content.

## Overview

AttachmentLens helps you build self-awareness around attachment patterns by:

- **Importing** posts about attachment theory and relationships from various sources
- **Auto-classifying** content into attachment styles (Anxious, Avoidant, Fearful, Secure, Healing & Growth)
- **Highlighting & annotating** passages that resonate with you
- **Analyzing** your collective highlights with Claude AI to uncover personal patterns
- **Tracking** favorites, reading progress, and analysis history

This is a personal journaling and research tool inspired by attachment theory frameworks. It's designed to support self-reflection and conversations with therapists or counselors.

## Features

✨ **Smart Classification**
- Automatic keyword-based categorization of posts into 6 attachment-related categories
- Manual override capability for posts (coming soon)
- Search and filter by category

📝 **Annotation & Insights**
- Highlight text from any post and save with personal reflections
- Searchable insights library
- Track which posts have been read

🧠 **AI-Powered Analysis**
- Generate personalized insights from your highlights using Claude API
- Customizable AI prompt (default: attachment-aware therapist persona)
- Analysis history with feedback tracking
- Past reflections feed into future analyses for contextual continuity

⭐ **Organization & Tracking**
- Favorite posts for quick access
- Like/comment metrics for social relevance
- Edit and personalize post content
- Full-text search across your library

🎨 **User Experience**
- Dark theme optimized for comfort and focus
- Adjustable font sizes (80%–200%)
- Sticky navigation bar
- Responsive design for desktop and tablet
- Clean, accessibility-minded UI

## Getting Started

### Prerequisites

**Option 1 (Recommended): Docker**
- Docker Desktop ([download](https://www.docker.com/products/docker-desktop))

**Option 2: Python**
- Python 3.8+
- Flask 3.0+

**Optional:**
- Anthropic API key for AI analysis features

### Local Installation (Python)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AttachmentLens.git
   cd AttachmentLens
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

   The app will start at `http://localhost:5000`

### Local Installation (Docker) — Recommended

Fastest way to get started with persistent data:

```bash
# Clone the repository
git clone https://github.com/yourusername/AttachmentLens.git
cd AttachmentLens

# Start with Docker Compose
docker-compose up
```

Visit `http://localhost:5000` — your database will be saved to `./data/posts.db` and persist across restarts.

**Benefits of Docker:**
- ✅ No Python setup needed
- ✅ Data persists in `./data/` folder
- ✅ Isolated environment
- ✅ One-command startup: `docker-compose up`

See [DOCKER.md](DOCKER.md) for more details.

### First Time Setup

1. **Import posts** — Visit `/import` to upload JSON data from your sources
2. **Explore & annotate** — Browse posts, mark favorites, and highlight passages
3. (Optional) **Set up AI analysis** — Add your Anthropic API key in the AI Insights page to unlock AI analysis

## Importing Data

### JSON Format

Posts should be a JSON array with this structure:

```json
[
  {
    "text": "The full text of the post or article excerpt",
    "date": "2024-05-15",
    "url": "https://source.com/post-id",
    "likes": 42,
    "comments": 18
  }
]
```

**Minimum requirements:**
- `text`: At least 30 characters
- Other fields are optional

### Sources

You can import from:
- **Facebook posts** — use browser console to export posts (see `scraper.js` if available)
- **Blog articles** — manually copy excerpts
- **Tweets/social** — export and format as JSON
- **Personal notes** — copy/paste as needed

## AI Insights

The AI Insights feature analyzes all your saved highlights together to identify patterns about your attachment style and relational patterns.

### Setup

1. Get an API key from [Anthropic](https://console.anthropic.com)
2. Visit the 🧠 **AI Insights** tab
3. Paste your API key (stored locally in the database, never sent elsewhere)
4. Generate an analysis whenever you want

### Customizing the Prompt

The default prompt is a warm, therapist-inspired persona. You can customize it:
- Click **Edit Prompt** to modify the system instructions
- Your custom prompt is saved and used for future analyses
- Reset to default at any time

### How It Works

Each analysis:
1. Collects all your highlighted passages
2. Groups them with their attachment categories
3. Includes your personal reflections on each highlight
4. References your 5 most recent feedback notes for context
5. Sends to Claude for personalized analysis
6. Saves the full analysis + optionally your reflections for history

## Database

The app uses SQLite (`posts.db`) with these tables:

- **posts** — imported content with categories, revisions, favorites, metrics
- **insights** — highlighted text + personal reflections
- **ai_analyses** — generated analyses + feedback history
- **settings** — API keys, custom prompts

All data is stored locally. Back up `posts.db` regularly if this is important to you.

## Roadmap

**High Priority**
- [ ] Manual category override on post detail pages
- [ ] Multi-category tagging (posts can span multiple styles)
- [ ] Read/Unread status with reading queue

**Medium Priority**
- [ ] Export to PDF (analyses, highlights)
- [ ] Stats dashboard (charts on attachment patterns, reading pace)
- [ ] Backup & restore (JSON export/import of full database)

**Longer Term**
- [ ] Browser extension for native scraping
- [ ] Bulk re-labeling view for cleanup

## Deployment to GitHub Pages

While AttachmentLens is primarily a server-side Flask app, you can deploy a static read-only version to GitHub Pages for sharing insights, or set up continuous deployment with a serverless backend.

### Option 1: Export & Static Hosting

For a **read-only view** of your analyses:

```bash
# Export your database to JSON
python -c "
import sqlite3, json
conn = sqlite3.connect('posts.db')
conn.row_factory = sqlite3.Row
posts = [dict(r) for r in conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()]
with open('docs/posts.json', 'w') as f:
    json.dump(posts, f, indent=2)
"

# Commit and push
git add docs/
git commit -m "Export posts snapshot"
git push
```

Then enable GitHub Pages in repo settings pointing to the `docs/` folder.

### Option 2: Full App with Netlify Functions (Recommended)

Deploy the full Flask app with Netlify Functions:

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Create `netlify.toml`** in the project root:
   ```toml
   [build]
   command = "pip install -r requirements.txt"
   functions = "functions"
   
   [functions]
   directory = "functions"
   
   [[redirects]]
   from = "/*"
   to = "/.netlify/functions/api"
   status = 200
   ```

3. **Convert app to serverless function** — Create `functions/api.py`:
   ```python
   from functions.app import app
   
   def handler(event, context):
       return {
           'statusCode': 200,
           'body': 'AttachmentLens is running!'
       }
   ```

4. **Deploy**
   ```bash
   netlify deploy --prod
   ```

### Option 3: Heroku Deployment (Alternative)

1. **Add `Procfile`** to project root:
   ```
   web: python app.py
   ```

2. **Ensure `requirements.txt` is up-to-date**:
   ```bash
   pip freeze > requirements.txt
   ```

3. **Deploy to Heroku**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

Visit `https://your-app-name.herokuapp.com`

## Development

### Project Structure

```
AttachmentLens/
├── app.py                 # Flask application & routes
├── requirements.txt       # Python dependencies
├── posts.db              # SQLite database (created on first run)
├── templates/            # HTML templates
│   ├── base.html         # Base layout with styling
│   ├── index.html        # Home page
│   ├── post.html         # Post detail view
│   ├── category.html     # Category filter view
│   ├── insights.html     # User highlights view
│   ├── ai_insights.html  # AI analysis interface
│   └── import.html       # Data import form
└── README.md
```

### Adding Features

1. **New route** — Add a route in `app.py` and corresponding template
2. **Database changes** — Modify `init_db()` to add migrations
3. **Styling** — Add CSS to `<style>` block in `templates/base.html`

### Running Tests

```bash
# Run the development server with debug mode
python app.py

# Verify routes
curl http://localhost:5000/
curl http://localhost:5000/api/stats
```

## Security & Privacy

⚠️ **Important Notes:**

- This app stores data **locally** in SQLite
- API keys are stored in the database (plaintext) — keep your database secure
- No built-in authentication — intended for single-user/personal use
- Not suitable for multi-user or sensitive production environments without hardening:
  - Add user authentication
  - Encrypt stored API keys
  - Add CSRF protection
  - Rate limit API calls
  - Add request validation & sanitization

For therapy/medical contexts, consult your therapist before using any AI tools.

## Contributing

This is a personal project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-idea`)
3. Commit changes with clear messages
4. Push and open a Pull Request

## License

MIT License — feel free to use, modify, and share.

## Support

- **Issues** — Report bugs or request features on [GitHub Issues](https://github.com/yourusername/AttachmentLens/issues)
- **Feedback** — DM or email if you have questions
- **Therapy Note** — This tool is a personal research aid, not a substitute for professional mental health care

## Acknowledgments

- Inspired by attachment theory research (Bowlby, Ainsworth, Main, Amir Levine, Rachel Heller)
- Built with Flask and SQLite
- UI powered by Claude and Anthropic's API
- Community of people exploring relationships & personal growth

---

Made with care for self-reflection and healing. 💜
