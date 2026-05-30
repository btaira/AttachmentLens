# Deploy AttachmentLens to GitHub Pages

GitHub Pages can host a read-only snapshot of your AttachmentLens data. This guide covers the setup.

## Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - **Source:** Deploy from a branch
   - **Branch:** `main` (or your default branch)
   - **Folder:** `/docs`
4. Click **Save**

Your site will be available at: `https://yourusername.github.io/AttachmentLens`

### Step 2: Export Your Data

The export script generates a JSON file that GitHub Pages can serve:

```bash
# From your project root, run:
python scripts/export_to_json.py docs/posts.json

# This creates docs/posts.json with your posts and insights
```

### Step 3: Commit & Push

```bash
git add docs/posts.json
git commit -m "Export posts snapshot for GitHub Pages"
git push
```

Your data is now live on GitHub Pages! (It may take 1-2 minutes to appear.)

---

## Viewing Your Data

### As JSON
Visit: `https://yourusername.github.io/AttachmentLens/posts.json`

### Create a Custom HTML Viewer (Optional)

For a prettier interface, create `docs/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>AttachmentLens</title>
  <style>
    body { font-family: system-ui; max-width: 900px; margin: 0 auto; padding: 20px; background: #0f1117; color: #e8eaf6; }
    .post { background: #1a1d27; padding: 20px; margin: 10px 0; border-radius: 10px; border: 1px solid #2e3147; }
    .category { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .anxious { background: rgba(247,124,106,.2); color: #f77c6a; }
    .avoidant { background: rgba(106,180,247,.2); color: #6ab4f7; }
    .fearful { background: rgba(201,106,247,.2); color: #c96af7; }
    .secure { background: rgba(93,217,156,.2); color: #5dd99c; }
    .healing { background: rgba(247,201,106,.2); color: #f7c96a; }
    .text { margin: 10px 0; line-height: 1.6; }
  </style>
</head>
<body>
  <h1>AttachmentLens 📖</h1>
  <p id="stats"></p>
  <div id="posts"></div>

  <script>
    fetch('posts.json')
      .then(r => r.json())
      .then(data => {
        const stats = data.stats;
        document.getElementById('stats').innerHTML = 
          `<strong>${stats.total_posts}</strong> posts · 
           <strong>${stats.total_insights}</strong> highlights · 
           <strong>${stats.total_analyses}</strong> analyses`;
        
        const postsHtml = data.posts.map(p => `
          <div class="post">
            <span class="category ${p.category.toLowerCase().replace(/\s/g, '')}">${p.category}</span>
            <p class="text">${p.original_text}</p>
            <small style="color: #8a8fa8;">
              ${p.date_label || 'undated'} · ${p.likes || 0} likes · ${p.comments || 0} comments
            </small>
          </div>
        `).join('');
        document.getElementById('posts').innerHTML = postsHtml;
      })
      .catch(e => console.error('Error loading posts:', e));
  </script>
</body>
</html>
```

This creates a simple browsable interface at `https://yourusername.github.io/AttachmentLens/`

---

## Keeping It Updated

### Automated Updates with GitHub Actions

Create `.github/workflows/export-posts.yml` to auto-export whenever you push:

```yaml
name: Export Posts

on:
  push:
    branches: [main]
    paths: ['posts.db', 'app.py']

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: python scripts/export_to_json.py docs/posts.json
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'Auto-export posts snapshot'
```

This automatically exports after you push database changes.

### Manual Export (Simpler)

```bash
# Before pushing, export manually:
python scripts/export_to_json.py docs/posts.json
git add docs/posts.json
git commit -m "Update posts snapshot"
git push
```

---

## Sharing

Once live, you can share your analyses:

- **Full snapshot:** `https://yourusername.github.io/AttachmentLens/`
- **Raw JSON:** `https://yourusername.github.io/AttachmentLens/posts.json`
- **In README:** Link to your GitHub Pages site

---

## Privacy

⚠️ **Important:** Your posts will be **publicly readable** on GitHub Pages.

### Before Publishing
1. Review your data for sensitive information
2. Consider anonymizing passages if sharing widely
3. Remember: Once published, search engines may cache it

### To Keep Data Private
- Don't push to GitHub Pages
- Deploy to a private server instead (see DEPLOYMENT.md)
- Use GitHub's private repositories (Pages works for public repos only)

---

## Troubleshooting

**"GitHub Pages is not enabled"**
- Go to Settings → Pages
- Make sure "Build and deployment" has a branch and folder selected
- Wait 1-2 minutes, refresh

**"404 - Page not found"**
- Ensure `docs/` folder exists: `mkdir -p docs`
- Run export script: `python scripts/export_to_json.py docs/posts.json`
- Push: `git add docs/ && git commit -m "Add docs" && git push`

**"JSON file is empty"**
- Ensure `posts.db` exists (run the app at least once)
- Check SQLite isn't locked: `fuser posts.db` (macOS/Linux)
- Try exporting manually: `python scripts/export_to_json.py docs/posts.json`

**"Site still showing old data"**
- GitHub Pages caches — force a refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
- Or clear browser cache
- Wait up to 5 minutes for GitHub to rebuild

---

## Custom Domain (Optional)

If you own a domain, point it to GitHub Pages:

1. In your domain registrar, create a CNAME record pointing to `yourusername.github.io`
2. In repo Settings → Pages → Custom domain, enter your domain
3. GitHub handles the SSL certificate automatically

Example: `attachmentlens.yourdomain.com` → `yourusername.github.io/AttachmentLens`

---

## Next Steps

- Use GitHub Pages for **reading your analyses** publicly
- Use Heroku/Railway for **interactive features** (if you want to add highlights while online)
- See DEPLOYMENT.md for full deployment options
