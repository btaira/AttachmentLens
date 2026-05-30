# Deployment Guide for AttachmentLens

This guide covers several ways to deploy AttachmentLens online.

## Quick Start Options

### 1. **Heroku** (Easiest for Full App)

Perfect if you want the full interactive app online with a database.

#### Setup

```bash
# Install Heroku CLI
# (visit https://devcenter.heroku.com/articles/heroku-cli)

# Create a Heroku app
heroku create your-app-name

# Add Procfile (already included)
# Already included: Procfile

# Deploy
git push heroku main

# Visit your app
heroku open
```

**Cost:** Free tier available (limited), paid plans start at $5/month

**Pros:**
- Full functionality (database, API keys, etc.)
- One-command deployment
- Free tier available
- Easy to update

**Cons:**
- Free tier has limitations (sleeping, limited hours)
- Shared PostgreSQL needed for production
- Database not persisted on free tier

---

### 2. **Netlify** (Recommended for Production)

Great for scalability with serverless functions and built-in CI/CD.

#### Setup

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Connect GitHub (in Netlify web dashboard)
# https://app.netlify.com/

# Deploy from dashboard
# Or via CLI:
netlify deploy --prod
```

**Cost:** Free tier generous, paid plans start at $19/month

**Pros:**
- Automatic deployments on git push
- Better free tier than Heroku
- Serverless (scales automatically)
- Great for static + dynamic content

**Cons:**
- Requires conversion to serverless functions
- Database needs external service (e.g., MongoDB Atlas)

**For Netlify + Database:**
1. Get free MongoDB Atlas account (500MB free)
2. Update `app.py` to use MongoDB instead of SQLite
3. Add environment variables in Netlify dashboard
4. Deploy

---

### 3. **GitHub Pages** (Read-Only Snapshot)

Best if you just want to share your analyses publicly in read-only form.

#### Setup

```bash
# Export your database to JSON
python scripts/export_to_json.py docs/posts.json

# Commit and push
git add docs/
git commit -m "Export posts snapshot"
git push

# In GitHub repo settings:
# Settings → Pages → Source: Deploy from a branch
# Branch: main, Folder: docs
```

Then visit `https://yourusername.github.io/AttachmentLens`

**Cost:** Free

**Pros:**
- Completely free
- No server needed
- Simple to update

**Cons:**
- Read-only (no new highlights/annotations)
- Manual exports needed
- Doesn't have interactive features

---

### 4. **Railway.app** (Modern Alternative)

Similar to Heroku but newer, with better free tier.

#### Setup

```bash
# Visit https://railway.app
# Sign up with GitHub

# Connect GitHub repo
# Railway auto-detects Flask
# Deploy one-click

# Add environment variables as needed
```

**Cost:** $5 free credit/month, then pay-as-you-go

**Pros:**
- Modern platform
- Better free tier than Heroku
- Works with Flask/SQLite out of box
- Good documentation

---

### 5. **PythonAnywhere**

Simple for beginners, Python-focused hosting.

#### Setup

```bash
# Visit https://www.pythonanywhere.com
# Sign up (free tier available)

# Upload files via web interface
# Or git clone in a Bash console
# Create web app pointing to app.py

# Reload web app
# Visit your app URL
```

**Cost:** Free tier available, paid from $5/month

**Pros:**
- Python-native
- Beginner-friendly
- Free tier works well

**Cons:**
- Slower than other options
- Limited customization
- Manual file uploads

---

## Environment Variables

If deploying with an API key, set these environment variables:

### Heroku
```bash
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=... # if using external DB
```

### Netlify
Dashboard → Site settings → Build & deploy → Environment → Add variables
```
FLASK_ENV=production
DATABASE_URL=... (if needed)
```

### Railway
Dashboard → Project → Variables

---

## Database Options

### Local SQLite (Simplest, Data Lost on Redeploy)
- Current setup — works for personal use
- Data stored in `posts.db`
- **Not recommended for production** (file-based, not persisted on serverless)

### PostgreSQL (Production-Ready)
- Heroku: Use Heroku Postgres add-on
- Railway: Built-in PostgreSQL option
- Update `app.py` to use `psycopg2` instead of SQLite

### MongoDB (Serverless-Friendly)
- Free tier: MongoDB Atlas (500MB)
- Update `app.py` to use `pymongo`
- Set `DATABASE_URL` environment variable

### Choice Recommendation
- **Personal / Testing:** SQLite (current)
- **Small Production:** PostgreSQL on Heroku/Railway
- **Serverless/Scalable:** MongoDB Atlas + Netlify Functions

---

## Keeping Data Safe

### Backup Your Database

```bash
# Export before deploying
python scripts/export_to_json.py backup-$(date +%Y-%m-%d).json

# Commit to git
git add *.json
git commit -m "Backup posts"
```

### Git Safety

The `.gitignore` file **excludes** `posts.db` so you don't accidentally commit it.

If you want to version your data:
```bash
# Export manually
python scripts/export_to_json.py
git add posts.json
git commit -m "Update posts snapshot"
```

---

## Troubleshooting

### "Port already in use" locally
```bash
# Use a different port
python app.py --port 5001
# Or kill the process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
```

### Database errors on deployed app
- **Heroku:** Check logs: `heroku logs --tail`
- **Netlify:** Check build logs in dashboard
- **Ensure `posts.db` is in `.gitignore`** so you don't sync stale copies

### API key not working
- Ensure Anthropic API key is set correctly
- Check that anthropic package is installed: `pip install anthropic`
- Verify you're using a valid API key from https://console.anthropic.com

---

## Choosing Your Deployment

| Platform | Type | Cost | Setup Time | Best For |
|----------|------|------|------------|----------|
| **Heroku** | PaaS | Free (limited) | 5 min | Simple full app |
| **Netlify** | Serverless | Free (generous) | 10 min | Production with scale |
| **Railway** | PaaS | $5/mo | 5 min | Modern alternative |
| **GitHub Pages** | Static | Free | 5 min | Read-only sharing |
| **PythonAnywhere** | PaaS | Free (limited) | 10 min | Beginners |

**Recommendation for Most Users:** Start with Heroku free tier, graduate to Railway when you need more resources.

---

## Additional Resources

- [Heroku Python Support](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Railway Documentation](https://docs.railway.app/)
- [GitHub Pages Setup](https://pages.github.com/)
- [PythonAnywhere Help](https://www.pythonanywhere.com/help/)
