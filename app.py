from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
import re
from datetime import datetime
try:
    import anthropic
    _has_anthropic = True
except ImportError:
    _has_anthropic = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
DB = 'posts.db'

# ---------------------------------------------------------------------------
# Attachment-style keyword classifier
# ---------------------------------------------------------------------------
CATEGORIES = {
    "Anxious / Preoccupied": [
        "abandon", "anxious", "anxiety", "panic", "reassure", "reassurance",
        "hypervigilant", "clingy", "chase", "chasing", "desperate", "need you",
        "fear of losing", "please don't leave", "attachment wound", "pursue",
        "protest behavior", "overthink", "spiral", "text back", "why won't you",
        "scared you'll leave", "insecure", "people pleasing", "fawn",
    ],
    "Avoidant / Dismissive": [
        "shut down", "wall up", "walls up", "emotionally unavailable", "distant",
        "space", "need space", "withdraw", "withdrawal", "stonewalling",
        "dismiss", "dismissive", "deactivate", "avoid", "avoidant",
        "i don't need", "independence", "self-sufficient", "don't rely",
        "silent treatment", "pull away", "detach", "cold", "numbing",
        "suppress", "logic over feelings", "vulnerability is weakness",
    ],
    "Fearful / Disorganized": [
        "trauma", "traumatized", "inner child", "nervous system",
        "freeze", "fight or flight", "fawn", "dysregulate", "dysregulation",
        "push and pull", "push-pull", "hot and cold", "triggered", "trigger",
        "hyperarousal", "hypoarousal", "dissociate", "overwhelmed", "chaotic",
        "fearful", "disorganized", "unresolved", "childhood wound",
        "complex trauma", "cptsd", "ptsd",
    ],
    "Secure": [
        "secure", "safety", "safe space", "healthy communication",
        "repair", "rupture and repair", "emotional safety", "boundaries",
        "i statements", "calm conversation", "trust", "mutual",
        "earned secure", "consistent", "reliability", "show up",
        "communicate needs", "vulnerability", "regulated",
    ],
    "Healing & Growth": [
        "heal", "healing", "therapy", "therapist", "self-work",
        "shadow work", "growth", "awareness", "journey", "breaking patterns",
        "reparenting", "somatic", "mindfulness", "nervous system regulation",
        "rewire", "self-love", "self-worth", "self-compassion",
        "progress", "pattern", "cycle breaking", "generational",
    ],
}
DEFAULT_CATEGORY = "General Relationship"


def classify(text: str) -> str:
    text_lower = text.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else DEFAULT_CATEGORY


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                revised_text TEXT,
                date_label TEXT,
                post_url TEXT,
                category TEXT NOT NULL,
                is_revised INTEGER DEFAULT 0,
                popularity INTEGER DEFAULT 0,
                imported_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                highlighted_text TEXT NOT NULL,
                my_thoughts TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        # Migrate: add columns if they don't exist yet
        for col, defn in [
            ('popularity', 'INTEGER DEFAULT 0'),
            ('is_favorite', 'INTEGER DEFAULT 0'),
            ('likes', 'INTEGER DEFAULT 0'),
            ('comments', 'INTEGER DEFAULT 0'),
        ]:
            try:
                conn.execute(f'ALTER TABLE posts ADD COLUMN {col} {defn}')
            except Exception:
                pass
        # Settings table for API key and AI prompt
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # AI analysis history
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_text TEXT NOT NULL,
                prompt_used TEXT,
                feedback TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        conn.commit()


def get_setting(key, default=''):
    with get_db() as conn:
        row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    return row['value'] if row else default


def set_setting(key, value):
    with get_db() as conn:
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()


DEFAULT_THERAPIST_PROMPT = """You are a warm, insightful therapist specializing in attachment theory and relationship psychology. I'm going to share a collection of passages that someone highlighted while reading about attachment styles and relationships — things that resonated with them deeply enough to save.

Your task is to provide a compassionate, personalized analysis. Please structure your response as follows:

**What your highlights reveal about you**
Look across everything highlighted and identify the 2–3 most prominent emotional themes or patterns. What keeps coming up? What are they drawn to, and what might that reflect about their inner world or relational history?

**Your attachment style — what the evidence suggests**
Based on the specific content they were drawn to (not a generic description), what does their pattern of highlights suggest about how they tend to show up in relationships? Be specific and grounded in what they actually highlighted.

**Your strengths and self-awareness**
What do their highlights reveal that's already working in their favor? What self-awareness is already present that they can build on?

**Areas inviting deeper exploration**
Gently name 2–3 themes that seem to be asking for more attention — patterns, wounds, or beliefs that their highlights point to but that may still be unresolved. Be specific, not generic.

**Suggested next steps**
Offer 3 concrete, actionable suggestions — things they can actually do this week to begin working on what the highlights reveal. These should feel grounded and accessible, not overwhelming.

Speak directly to the person using "you." Be specific to what they actually highlighted — avoid vague platitudes. Lead with warmth and curiosity, not diagnosis."""


def first_sentence(text):
    """Return the first sentence of a post for display."""
    if not text:
        return ''
    for sep in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
        idx = text.find(sep)
        if idx != -1 and idx < 300:
            return text[:idx + 1]
    return text[:200]


app.jinja_env.globals['first_sentence'] = first_sentence


init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    search = request.args.get('q', '').strip()
    with get_db() as conn:
        latest = conn.execute(
            'SELECT * FROM posts ORDER BY id DESC LIMIT 5'
        ).fetchall()
        if search:
            library = conn.execute(
                "SELECT * FROM posts WHERE original_text LIKE ? OR revised_text LIKE ? ORDER BY popularity DESC, id DESC",
                (f'%{search}%', f'%{search}%')
            ).fetchall()
        else:
            library = conn.execute(
                'SELECT * FROM posts ORDER BY popularity DESC, id DESC'
            ).fetchall()
        cats = conn.execute(
            'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category ORDER BY cnt DESC'
        ).fetchall()
        total = conn.execute('SELECT COUNT(*) as n FROM posts').fetchone()['n']
        favorites = conn.execute(
            'SELECT * FROM posts WHERE is_favorite = 1 ORDER BY category, popularity DESC'
        ).fetchall()
    return render_template(
        'index.html',
        latest=latest,
        library=library,
        categories=cats,
        selected_category='',
        search=search,
        total=total,
        favorites=favorites,
    )


@app.route('/category/<path:cat_name>')
def category_view(cat_name):
    with get_db() as conn:
        posts = conn.execute(
            'SELECT * FROM posts WHERE category = ? ORDER BY popularity DESC, id DESC',
            (cat_name,)
        ).fetchall()
        cats = conn.execute(
            'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category ORDER BY cnt DESC'
        ).fetchall()
    return render_template('category.html', posts=posts, category=cat_name, categories=cats)


@app.route('/search')
def search_route():
    return redirect(url_for('index', q=request.args.get('q', '')))


@app.route('/import_json', methods=['POST'])
def import_json():
    """Accepts large JSON payloads via fetch() to bypass browser form size limits."""
    try:
        body = request.get_json(force=True)
        raw = body.get('json_data', '')
        data = json.loads(raw)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a JSON array.'}), 400
    imported = 0
    updated = 0
    skipped = 0
    with get_db() as conn:
        for item in data:
            text = (item.get('text') or '').strip()
            if not text or len(text) < 30:
                skipped += 1
                continue
            likes = int(item.get('likes', 0))
            comments = int(item.get('comments', 0))
            popularity = likes + comments
            existing = conn.execute(
                'SELECT id, likes, comments FROM posts WHERE original_text = ?', (text,)
            ).fetchone()
            if existing:
                # Update likes/comments if new data has values and they differ
                if likes > 0 or comments > 0:
                    if likes != existing['likes'] or comments != existing['comments']:
                        conn.execute(
                            'UPDATE posts SET likes = ?, comments = ?, popularity = ? WHERE id = ?',
                            (likes, comments, popularity, existing['id'])
                        )
                        updated += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1
                continue
            category = classify(text)
            conn.execute(
                'INSERT INTO posts (original_text, date_label, post_url, category, popularity, likes, comments) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (text, item.get('date', ''), item.get('url', ''), category, popularity, likes, comments)
            )
            imported += 1
        conn.commit()
    return jsonify({'imported': imported, 'updated': updated, 'skipped': skipped})


@app.route('/import', methods=['GET', 'POST'])
def import_posts():
    if request.method == 'POST':
        raw = request.form.get('json_data', '')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            return render_template('import.html', error=f"JSON parse error: {e}")

        if not isinstance(data, list):
            return render_template('import.html', error="Expected a JSON array.")

        imported = 0
        skipped = 0
        with get_db() as conn:
            for item in data:
                text = (item.get('text') or '').strip()
                if not text or len(text) < 30:
                    skipped += 1
                    continue
                # Skip duplicates
                exists = conn.execute(
                    'SELECT 1 FROM posts WHERE original_text = ?', (text,)
                ).fetchone()
                if exists:
                    skipped += 1
                    continue
                category = classify(text)
                conn.execute(
                    'INSERT INTO posts (original_text, date_label, post_url, category) VALUES (?, ?, ?, ?)',
                    (text, item.get('date', ''), item.get('url', ''), category)
                )
                imported += 1
            conn.commit()
        return redirect(url_for('index') + f'?imported={imported}&skipped={skipped}')
    return render_template('import.html')


@app.route('/post/<int:post_id>')
def view_post(post_id):
    with get_db() as conn:
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        return "Post not found", 404
    return render_template('post.html', post=post)


@app.route('/post/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    revised = request.form.get('revised_text', '').strip()
    with get_db() as conn:
        # Fetch original to check if text actually changed
        post = conn.execute('SELECT original_text FROM posts WHERE id = ?', (post_id,)).fetchone()
        if revised and post and revised != post['original_text']:
            conn.execute(
                'UPDATE posts SET revised_text = ?, is_revised = 1 WHERE id = ?',
                (revised, post_id)
            )
        else:
            # Same as original or empty — clear revision
            conn.execute(
                'UPDATE posts SET revised_text = NULL, is_revised = 0 WHERE id = ?',
                (post_id,)
            )
        conn.commit()
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/post/<int:post_id>/favorite', methods=['POST'])
def toggle_favorite(post_id):
    with get_db() as conn:
        current = conn.execute('SELECT is_favorite FROM posts WHERE id = ?', (post_id,)).fetchone()
        if current:
            new_val = 0 if current['is_favorite'] else 1
            conn.execute('UPDATE posts SET is_favorite = ? WHERE id = ?', (new_val, post_id))
            conn.commit()
            return jsonify({'is_favorite': new_val})
    return jsonify({'error': 'not found'}), 404


@app.route('/post/<int:post_id>/revert', methods=['POST'])
def revert_post(post_id):
    with get_db() as conn:
        conn.execute(
            'UPDATE posts SET revised_text = NULL, is_revised = 0 WHERE id = ?',
            (post_id,)
        )
        conn.commit()
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    with get_db() as conn:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
    return redirect(url_for('index'))


@app.route('/insights')
def insights_page():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT i.id, i.post_id, i.highlighted_text, i.my_thoughts, i.created_at,
                   p.category, p.post_url
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            ORDER BY i.id DESC
        ''').fetchall()
    return render_template('insights.html', insights=rows)


@app.route('/insights/add', methods=['POST'])
def add_insight():
    data = request.get_json(force=True)
    post_id = data.get('post_id')
    text = (data.get('highlighted_text') or '').strip()
    if not text:
        return jsonify({'error': 'No text'}), 400
    with get_db() as conn:
        conn.execute(
            'INSERT INTO insights (post_id, highlighted_text) VALUES (?, ?)',
            (post_id, text)
        )
        conn.commit()
        row = conn.execute('SELECT last_insert_rowid() as id').fetchone()
    return jsonify({'id': row['id'], 'ok': True})


@app.route('/insights/<int:insight_id>/thoughts', methods=['POST'])
def update_thoughts(insight_id):
    data = request.get_json(force=True)
    thoughts = (data.get('thoughts') or '').strip()
    with get_db() as conn:
        conn.execute('UPDATE insights SET my_thoughts = ? WHERE id = ?', (thoughts, insight_id))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/insights/<int:insight_id>/delete', methods=['POST'])
def delete_insight(insight_id):
    with get_db() as conn:
        conn.execute('DELETE FROM insights WHERE id = ?', (insight_id,))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/posts/clear', methods=['POST'])
def clear_posts():
    with get_db() as conn:
        conn.execute('DELETE FROM posts')
        conn.commit()
    return jsonify({'cleared': True})


@app.route('/api/stats')
def api_stats():
    with get_db() as conn:
        cats = conn.execute(
            'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category'
        ).fetchall()
        total = conn.execute('SELECT COUNT(*) as n FROM posts').fetchone()['n']
        revised = conn.execute('SELECT COUNT(*) as n FROM posts WHERE is_revised = 1').fetchone()['n']
    return jsonify({
        'total': total,
        'revised': revised,
        'categories': [dict(r) for r in cats],
    })


@app.route('/ai-insights')
def ai_insights_page():
    search = request.args.get('q', '').strip()
    with get_db() as conn:
        rows = conn.execute('''
            SELECT i.id, i.post_id, i.highlighted_text, i.my_thoughts, i.created_at,
                   p.category, p.post_url
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            ORDER BY i.id DESC
        ''').fetchall()
        if search:
            history = conn.execute(
                "SELECT * FROM ai_analyses WHERE analysis_text LIKE ? OR feedback LIKE ? ORDER BY id DESC",
                (f'%{search}%', f'%{search}%')
            ).fetchall()
        else:
            history = conn.execute(
                'SELECT * FROM ai_analyses ORDER BY id DESC'
            ).fetchall()
    api_key = get_setting('anthropic_api_key', '')
    saved_prompt = get_setting('ai_therapist_prompt', DEFAULT_THERAPIST_PROMPT)
    return render_template('ai_insights.html',
                           insights=rows,
                           history=history,
                           search=search,
                           api_key_set=bool(api_key),
                           saved_prompt=saved_prompt,
                           default_prompt=DEFAULT_THERAPIST_PROMPT,
                           has_anthropic=_has_anthropic)


@app.route('/ai-insights/save-key', methods=['POST'])
def save_api_key():
    key = (request.get_json(force=True) or {}).get('api_key', '').strip()
    if key:
        set_setting('anthropic_api_key', key)
    return jsonify({'ok': True})


@app.route('/ai-insights/delete-key', methods=['POST'])
def delete_api_key():
    with get_db() as conn:
        conn.execute("DELETE FROM settings WHERE key = 'anthropic_api_key'")
        conn.commit()
    return jsonify({'ok': True})


@app.route('/ai-insights/save-prompt', methods=['POST'])
def save_ai_prompt():
    prompt = (request.get_json(force=True) or {}).get('prompt', '').strip()
    if prompt:
        set_setting('ai_therapist_prompt', prompt)
    return jsonify({'ok': True})


@app.route('/ai-insights/analyze', methods=['POST'])
def ai_analyze():
    if not _has_anthropic:
        return jsonify({'error': 'anthropic package not installed. Run: pip install anthropic'}), 500

    api_key = get_setting('anthropic_api_key', '')
    if not api_key:
        return jsonify({'error': 'No API key set. Enter your Anthropic API key above.'}), 400

    data = request.get_json(force=True) or {}
    prompt = data.get('prompt', '').strip() or DEFAULT_THERAPIST_PROMPT

    with get_db() as conn:
        insight_rows = conn.execute('''
            SELECT i.highlighted_text, i.my_thoughts, p.category
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            ORDER BY i.id DESC
        ''').fetchall()
        # Pull past feedback for context
        past_feedback = conn.execute(
            "SELECT feedback, created_at FROM ai_analyses WHERE feedback != '' AND feedback IS NOT NULL ORDER BY id DESC LIMIT 5"
        ).fetchall()

    if not insight_rows:
        return jsonify({'error': 'No insights saved yet. Highlight text on any post first.'}), 400

    # Build the user message
    parts = []
    for idx, row in enumerate(insight_rows, 1):
        cat = row['category'] or 'General'
        entry = f"[{idx}] ({cat})\n\"{row['highlighted_text']}\""
        if row['my_thoughts'] and row['my_thoughts'].strip():
            entry += f"\n  My reflection: {row['my_thoughts'].strip()}"
        parts.append(entry)

    user_message = (
        f"Here are {len(insight_rows)} passages I highlighted while reading about attachment and relationships:\n\n"
        + "\n\n".join(parts)
    )

    # Append past feedback as context
    if past_feedback:
        fb_parts = []
        for fb in past_feedback:
            if fb['feedback'] and fb['feedback'].strip():
                fb_parts.append(f"- {fb['feedback'].strip()} (from session on {fb['created_at'][:10]})")
        if fb_parts:
            user_message += (
                "\n\n---\nContext from my previous reflections on past analyses:\n"
                + "\n".join(fb_parts)
                + "\n\nPlease factor in this growth context when giving your analysis."
            )

    user_message += "\n\nPlease provide your analysis."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=2000,
            system=prompt,
            messages=[{'role': 'user', 'content': user_message}]
        )
        result = message.content[0].text
        # Save to history
        with get_db() as conn:
            conn.execute(
                'INSERT INTO ai_analyses (analysis_text, prompt_used) VALUES (?, ?)',
                (result, prompt)
            )
            conn.commit()
            row = conn.execute('SELECT last_insert_rowid() as id').fetchone()
        return jsonify({'analysis': result, 'analysis_id': row['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai-insights/<int:analysis_id>/feedback', methods=['POST'])
def save_analysis_feedback(analysis_id):
    data = request.get_json(force=True) or {}
    feedback = (data.get('feedback') or '').strip()
    with get_db() as conn:
        conn.execute('UPDATE ai_analyses SET feedback = ? WHERE id = ?', (feedback, analysis_id))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/ai-insights/<int:analysis_id>/delete', methods=['POST'])
def delete_analysis(analysis_id):
    with get_db() as conn:
        conn.execute('DELETE FROM ai_analyses WHERE id = ?', (analysis_id,))
        conn.commit()
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
