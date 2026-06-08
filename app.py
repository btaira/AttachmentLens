from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import json
import re
import os
import hashlib
import secrets
from datetime import datetime
from functools import wraps
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
try:
    import anthropic
    _has_anthropic = True
except ImportError:
    _has_anthropic = False

try:
    import zipfile
    from io import BytesIO
    _has_zipfile = True
except ImportError:
    _has_zipfile = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Fix UTF-8 template loading on Windows
from jinja2 import FileSystemLoader
app.jinja_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'), encoding='utf-8')

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = None

DB = os.getenv('DB_PATH', 'posts.db')


def _load_secret_key():
    """Persist secret key in a file so sessions survive restarts."""
    fixed = os.getenv('SECRET_KEY')
    if fixed:
        return fixed
    # Store next to the DB file (same directory)
    db_dir = os.path.dirname(os.path.abspath(DB))
    key_path = os.path.join(db_dir, '.secret_key')
    try:
        with open(key_path, 'r') as f:
            key = f.read().strip()
        if key:
            return key
    except FileNotFoundError:
        pass
    key = secrets.token_hex(32)
    os.makedirs(db_dir, exist_ok=True)
    with open(key_path, 'w') as f:
        f.write(key)
    return key


app.secret_key = _load_secret_key()

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


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    # Ensure directory exists for database file
    db_dir = os.path.dirname(DB) or '.'
    os.makedirs(db_dir, exist_ok=True)

    with get_db() as conn:
        # ── Core posts (shared across all users) ────────────────────────
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
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                imported_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        # Migrate legacy columns on posts
        for col, defn in [
            ('popularity', 'INTEGER DEFAULT 0'),
            ('likes', 'INTEGER DEFAULT 0'),
            ('comments', 'INTEGER DEFAULT 0'),
            ('date_label', 'TEXT'),
            ('post_url', 'TEXT'),
            ('date_label_locked', 'INTEGER DEFAULT 0'),
        ]:
            try:
                conn.execute(f'ALTER TABLE posts ADD COLUMN {col} {defn}')
            except Exception:
                pass

        # ── Users ────────────────────────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # ── Per-user post preferences ─────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_post_prefs (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                is_favorite INTEGER DEFAULT 0,
                is_read INTEGER DEFAULT 0,
                tags TEXT DEFAULT '',
                PRIMARY KEY (user_id, post_id)
            )
        ''')

        # ── Insights (per user) ───────────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_id INTEGER,
                highlighted_text TEXT NOT NULL,
                my_thoughts TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        try:
            conn.execute('ALTER TABLE insights ADD COLUMN user_id INTEGER')
        except Exception:
            pass

        # ── Settings (per user) ───────────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER NOT NULL DEFAULT 1,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY (user_id, key)
            )
        ''')
        # migrate old single-key settings table
        try:
            conn.execute('ALTER TABLE settings ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1')
        except Exception:
            pass

        # ── AI analysis history (per user) ────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                analysis_text TEXT NOT NULL,
                prompt_used TEXT,
                feedback TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        try:
            conn.execute('ALTER TABLE ai_analyses ADD COLUMN user_id INTEGER')
        except Exception:
            pass

        # ── Modeled posts (per user) ──────────────────────────────────────
        conn.execute('''
            CREATE TABLE IF NOT EXISTS modeled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_text TEXT NOT NULL,
                attachment_style TEXT,
                topic TEXT,
                is_favorite INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        try:
            conn.execute('ALTER TABLE modeled_posts ADD COLUMN user_id INTEGER')
        except Exception:
            pass

        # ── Seed default admin user if no users exist ─────────────────────
        existing_users = conn.execute('SELECT COUNT(*) as n FROM users').fetchone()['n']
        if existing_users == 0:
            conn.execute(
                'INSERT INTO users (id, username, password_hash) VALUES (1, ?, ?)',
                ('admin', hash_password('admin'))
            )
            # Migrate any existing data to user_id=1
            conn.execute('UPDATE insights SET user_id = 1 WHERE user_id IS NULL')
            conn.execute('UPDATE ai_analyses SET user_id = 1 WHERE user_id IS NULL')
            conn.execute('UPDATE modeled_posts SET user_id = 1 WHERE user_id IS NULL')
            # Migrate is_favorite, is_read, tags from posts → user_post_prefs
            # (only applies to pre-multi-user databases; fresh installs won't have these columns)
            try:
                legacy = conn.execute(
                    'SELECT id, is_favorite, is_read, tags FROM posts WHERE (is_favorite=1 OR is_read=1 OR (tags IS NOT NULL AND tags != ""))'
                ).fetchall()
                for row in legacy:
                    conn.execute('''
                        INSERT OR IGNORE INTO user_post_prefs (user_id, post_id, is_favorite, is_read, tags)
                        VALUES (1, ?, ?, ?, ?)
                    ''', (row['id'], row['is_favorite'] or 0, row['is_read'] or 0, row['tags'] or ''))
            except Exception:
                pass  # Fresh install — legacy columns don't exist, nothing to migrate

        conn.commit()


def current_user_id():
    return session.get('user_id', 1)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            # POST/PUT/DELETE = API fetch call → return JSON so JS can handle it
            # GET = page navigation → redirect to login
            if request.method != 'GET':
                return jsonify({'error': 'Session expired — please reload the page and log in again.'}), 401
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def get_setting(key, default='', user_id=None):
    uid = user_id if user_id is not None else current_user_id()
    # Check environment variables first (for secrets)
    if key == 'anthropic_api_key':
        env_val = os.getenv('ANTHROPIC_API_KEY')
        if env_val:
            return env_val
    elif key == 'github_token':
        env_val = os.getenv('GITHUB_TOKEN')
        if env_val:
            return env_val
    # Fall back to database
    with get_db() as conn:
        row = conn.execute('SELECT value FROM settings WHERE user_id = ? AND key = ?', (uid, key)).fetchone()
        if not row:
            # fall back to legacy single-key row (migration)
            row = conn.execute('SELECT value FROM settings WHERE key = ? AND user_id = 1', (key,)).fetchone()
    return row['value'] if row else default


def set_setting(key, value, user_id=None):
    uid = user_id if user_id is not None else current_user_id()
    with get_db() as conn:
        conn.execute('INSERT OR REPLACE INTO settings (user_id, key, value) VALUES (?, ?, ?)', (uid, key, value))
        conn.commit()


def get_all_users():
    with get_db() as conn:
        return conn.execute('SELECT id, username FROM users ORDER BY username').fetchall()


DEFAULT_THERAPIST_PROMPT = """You are a warm, insightful therapist specializing in attachment theory and relationship psychology. I'm going to share a collection of passages someone highlighted while reading about attachment and relationships — things that resonated deeply enough to save. For many of these, they've also written their own personal thoughts and feelings in response to what they read.

**The personal thoughts and feelings they've written are the most important input.** Treat them as direct windows into their inner world — weigh them heavily alongside the highlights themselves. If they've shared what something brought up for them, that is primary data for your analysis.

Your task is to provide a compassionate, personalized analysis. Please structure your response as follows:

**What your highlights — and your own words — reveal about you**
Look across everything, especially the personal reflections they've written. What themes keep surfacing? What emotional patterns are showing up in both what they chose to highlight and what they said about it?

**Your attachment style — what the evidence suggests**
Based on their highlights and personal reflections together (not a generic description), what does the pattern suggest about how they show up in relationships? Be specific and grounded in their actual words.

**Your strengths and self-awareness**
What do their highlights and reflections reveal that's already working in their favor? What self-awareness is clearly present that they can build on?

**Areas inviting deeper exploration**
Gently name 2–3 themes that seem to be asking for more attention — drawn from both the passages they saved and the feelings they expressed. Be specific, not generic.

**Suggested next steps**
Offer 3 concrete, actionable suggestions grounded in what they actually shared — things they can do this week. Make them feel accessible, not overwhelming.

Speak directly to the person using "you." Reference their specific words and reflections where possible. Lead with warmth and curiosity, not diagnosis."""


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


@app.context_processor
def inject_globals():
    try:
        users = get_all_users()
    except Exception as e:
        users = []
    return {'users': users, 'session': session}


init_db()


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ? AND password_hash = ?',
                (username, hash_password(password))
            ).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(request.args.get('next') or url_for('index'))
        error = 'Invalid username or password.'
    return render_template('login.html', error=error, mode='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if not username or not password:
            error = 'Username and password are required.'
        elif len(password) < 4:
            error = 'Password must be at least 4 characters.'
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                        (username, hash_password(password))
                    )
                    conn.commit()
                    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('index'))
            except Exception:
                error = 'Username already taken.'
    return render_template('login.html', error=error, mode='register')


@app.route('/switch-user/<int:user_id>', methods=['POST'])
@login_required
def switch_user(user_id):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
    return redirect(request.referrer or url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
@login_required
def index():
    uid = current_user_id()
    search = request.args.get('q', '').strip()
    # Base query joins user_post_prefs for per-user is_favorite/is_read/tags
    PREFS_JOIN = '''
        LEFT JOIN user_post_prefs up ON up.post_id = p.id AND up.user_id = {uid}
    '''.format(uid=uid)
    PREFS_COLS = '''
        p.*, COALESCE(up.is_favorite,0) as is_favorite,
        COALESCE(up.is_read,0) as is_read,
        COALESCE(up.tags,'') as tags
    '''
    with get_db() as conn:
        all_posts_for_latest = conn.execute(
            f'SELECT {PREFS_COLS} FROM posts p {PREFS_JOIN} ORDER BY p.id DESC'
        ).fetchall()
        if search:
            library = conn.execute(
                f"SELECT {PREFS_COLS} FROM posts p {PREFS_JOIN} WHERE p.original_text LIKE ? OR p.revised_text LIKE ? ORDER BY p.popularity DESC, p.id DESC",
                (f'%{search}%', f'%{search}%')
            ).fetchall()
        else:
            library = conn.execute(
                f'SELECT {PREFS_COLS} FROM posts p {PREFS_JOIN} ORDER BY p.popularity DESC, p.id DESC'
            ).fetchall()
        cats = conn.execute(
            'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category ORDER BY cnt DESC'
        ).fetchall()
        total = conn.execute('SELECT COUNT(*) as n FROM posts').fetchone()['n']
        all_favorites = conn.execute(
            f'SELECT {PREFS_COLS} FROM posts p {PREFS_JOIN} WHERE up.is_favorite = 1 ORDER BY p.id DESC'
        ).fetchall()
    def parse_post_date(p):
        dl = p['date_label'] or ''
        if dl:
            for fmt in ('%B %d, %Y', '%b %d, %Y', '%B %d %Y'):
                try:
                    return datetime.strptime(dl.strip(), fmt)
                except ValueError:
                    pass
        return datetime(1970, 1, 1)

    latest = sorted(all_posts_for_latest, key=parse_post_date, reverse=True)[:5]
    favorites = sorted(all_favorites, key=parse_post_date, reverse=True)[:5]

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
@login_required
def category_view(cat_name):
    uid = current_user_id()
    PREFS_JOIN = f'LEFT JOIN user_post_prefs up ON up.post_id = p.id AND up.user_id = {uid}'
    PREFS_COLS = 'p.*, COALESCE(up.is_favorite,0) as is_favorite, COALESCE(up.is_read,0) as is_read, COALESCE(up.tags,\'\') as tags'
    with get_db() as conn:
        posts = conn.execute(
            f'SELECT {PREFS_COLS} FROM posts p {PREFS_JOIN} WHERE p.category = ? ORDER BY p.popularity DESC, p.id DESC',
            (cat_name,)
        ).fetchall()
        cats = conn.execute(
            'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category ORDER BY cnt DESC'
        ).fetchall()
    return render_template('category.html', posts=posts, category=cat_name, categories=cats)


@app.route('/search')
@login_required
def search_route():
    return redirect(url_for('index', q=request.args.get('q', '')))


@app.route('/import_json', methods=['POST'])
@login_required
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
                # Always update date_label and post_url if we have them now (may have been missing on first import)
                # But respect locked dates (don't overwrite if already locked by any prior import or user)
                date_label = item.get('date', '')
                post_url = item.get('url', '')
                if likes > 0 or comments > 0 or date_label or post_url:
                    conn.execute(
                        '''UPDATE posts SET likes = ?, comments = ?, popularity = ?,
                           date_label = CASE WHEN date_label_locked = 1 THEN date_label
                                            WHEN ? != '' THEN ?
                                            ELSE date_label END,
                           date_label_locked = CASE WHEN date_label_locked = 1 THEN 1
                                                    WHEN ? != '' THEN 1
                                                    ELSE date_label_locked END,
                           post_url   = CASE WHEN ? != '' THEN ? ELSE post_url   END
                           WHERE id = ?''',
                        (likes, comments, popularity,
                         date_label, date_label,
                         date_label,
                         post_url, post_url,
                         existing['id'])
                    )
                    updated += 1
                else:
                    skipped += 1
                continue
            category = classify(text)
            date_label = item.get('date', '')
            # Auto-lock all imported dates (only manual edits will have locked=1 if date is empty, otherwise all imports are locked)
            conn.execute(
                'INSERT INTO posts (original_text, date_label, post_url, category, popularity, likes, comments, date_label_locked) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (text, date_label, item.get('url', ''), category, popularity, likes, comments, 1 if date_label else 0)
            )
            imported += 1
        conn.commit()
    return jsonify({'imported': imported, 'updated': updated, 'skipped': skipped})


@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_posts():
    _gh = bool(get_setting('github_token', '', user_id=1))
    if request.method == 'POST':
        raw = request.form.get('json_data', '')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            return render_template('import.html', error=f"JSON parse error: {e}", github_token_set=_gh)

        if not isinstance(data, list):
            return render_template('import.html', error="Expected a JSON array.", github_token_set=_gh)

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
    return render_template('import.html', github_token_set=bool(get_setting('github_token', '', user_id=1)))


@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    uid = current_user_id()
    with get_db() as conn:
        post = conn.execute('''
            SELECT p.*,
                   COALESCE(up.is_favorite,0) as is_favorite,
                   COALESCE(up.is_read,0) as is_read,
                   COALESCE(up.tags,'') as tags
            FROM posts p
            LEFT JOIN user_post_prefs up ON up.post_id = p.id AND up.user_id = ?
            WHERE p.id = ?
        ''', (uid, post_id)).fetchone()
        saved_highlights = conn.execute(
            'SELECT highlighted_text FROM insights WHERE post_id = ? AND user_id = ? ORDER BY id',
            (post_id, uid)
        ).fetchall()
    if not post:
        return "Post not found", 404
    highlights = [r['highlighted_text'] for r in saved_highlights]
    return render_template('post.html', post=post, highlights=highlights)


@app.route('/post/<int:post_id>/edit', methods=['POST'])
@login_required
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
@login_required
def toggle_favorite(post_id):
    uid = current_user_id()
    conn = get_db()
    try:
        current = conn.execute(
            'SELECT is_favorite FROM user_post_prefs WHERE user_id = ? AND post_id = ?',
            (uid, post_id)
        ).fetchone()
        new_val = 0 if (current and current['is_favorite']) else 1
        conn.execute('''
            INSERT INTO user_post_prefs (user_id, post_id, is_favorite)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, post_id) DO UPDATE SET is_favorite = excluded.is_favorite
        ''', (uid, post_id, new_val))
        conn.commit()
        return jsonify({'is_favorite': new_val})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/post/<int:post_id>/revert', methods=['POST'])
@login_required
def revert_post(post_id):
    with get_db() as conn:
        conn.execute(
            'UPDATE posts SET revised_text = NULL, is_revised = 0 WHERE id = ?',
            (post_id,)
        )
        conn.commit()
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    with get_db() as conn:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
    return redirect(url_for('index'))


@app.route('/insights')
@login_required
def insights_page():
    uid = current_user_id()
    with get_db() as conn:
        rows = conn.execute('''
            SELECT i.id, i.post_id, i.highlighted_text, i.my_thoughts, i.created_at,
                   p.category, p.post_url
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            WHERE i.user_id = ?
            ORDER BY i.id DESC
        ''', (uid,)).fetchall()
    return render_template('insights.html', insights=rows)


@app.route('/insights/add', methods=['POST'])
@login_required
def add_insight():
    uid = current_user_id()
    data = request.get_json(force=True)
    post_id = data.get('post_id')
    text = (data.get('highlighted_text') or '').strip()
    if not text:
        return jsonify({'error': 'No text'}), 400
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO insights (user_id, post_id, highlighted_text) VALUES (?, ?, ?)',
            (uid, post_id, text)
        )
        conn.commit()
        row = conn.execute('SELECT last_insert_rowid() as id').fetchone()
        return jsonify({'id': row['id'], 'ok': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/quick-summary/<int:post_id>', methods=['POST'])
@login_required
def quick_summary(post_id):
    """Generate AI summary of a post (without saving to insights)"""
    if not _has_anthropic:
        return jsonify({'error': 'AI analysis not available'}), 500

    api_key = get_setting('anthropic_api_key', '')
    if not api_key:
        return jsonify({'error': 'No API key configured'}), 400

    conn = get_db()
    try:
        # Get the post
        post = conn.execute(
            'SELECT original_text, category FROM posts WHERE id = ?', (post_id,)
        ).fetchone()
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        # Generate AI summary
        client = anthropic.Anthropic(api_key=api_key)
        prompt = """You are a compassionate attachment theory expert.
Analyze the following post about relationships and attachment in 2-3 sentences.
Focus on what attachment pattern or insight it reveals, and why it might resonate with someone working on their attachment style."""

        message = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=300,
            system=prompt,
            messages=[{
                'role': 'user',
                'content': f"Category: {post['category']}\n\nPost text:\n{post['original_text']}"
            }]
        )
        ai_summary = message.content[0].text

        return jsonify({
            'ok': True,
            'post_id': post_id,
            'summary': ai_summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/save-summary/<int:post_id>', methods=['POST'])
@login_required
def save_summary(post_id):
    """Save AI summary as an insight"""
    uid = current_user_id()
    data = request.get_json(force=True) or {}
    summary = (data.get('summary') or '').strip()

    if not summary:
        return jsonify({'error': 'No summary provided'}), 400

    conn = get_db()
    try:
        # Check if identical insight already exists
        exists = conn.execute(
            'SELECT id FROM insights WHERE user_id = ? AND post_id = ? AND highlighted_text = ?',
            (uid, post_id, summary)
        ).fetchone()

        if exists:
            return jsonify({'id': exists['id'], 'ok': True, 'message': 'Summary already saved'})

        # Create insight with just the AI summary
        conn.execute(
            'INSERT INTO insights (user_id, post_id, highlighted_text) VALUES (?, ?, ?)',
            (uid, post_id, summary)
        )
        conn.commit()
        insight_row = conn.execute('SELECT last_insert_rowid() as id').fetchone()

        return jsonify({
            'id': insight_row['id'],
            'ok': True,
            'message': 'Summary saved to insights!'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/insights/<int:insight_id>/thoughts', methods=['POST'])
@login_required
def update_thoughts(insight_id):
    uid = current_user_id()
    data = request.get_json(force=True)
    thoughts = (data.get('thoughts') or '').strip()
    conn = get_db()
    try:
        conn.execute('UPDATE insights SET my_thoughts = ? WHERE id = ? AND user_id = ?', (thoughts, insight_id, uid))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/insights/<int:insight_id>/delete', methods=['POST'])
@login_required
def delete_insight(insight_id):
    uid = current_user_id()
    conn = get_db()
    try:
        conn.execute('DELETE FROM insights WHERE id = ? AND user_id = ?', (insight_id, uid))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/posts/clear', methods=['POST'])
@login_required
def clear_posts():
    with get_db() as conn:
        conn.execute('DELETE FROM posts')
        conn.commit()
    return jsonify({'cleared': True})


@app.route('/insights/clear', methods=['POST'])
@login_required
def clear_insights():
    uid = current_user_id()
    with get_db() as conn:
        conn.execute('DELETE FROM insights WHERE user_id = ?', (uid,))
        conn.commit()
    return jsonify({'cleared': True})


@app.route('/ai-insights/clear', methods=['POST'])
@login_required
def clear_ai_analyses():
    uid = current_user_id()
    with get_db() as conn:
        conn.execute('DELETE FROM ai_analyses WHERE user_id = ?', (uid,))
        conn.commit()
    return jsonify({'cleared': True})


@app.route('/modeled-posts/clear', methods=['POST'])
@login_required
def clear_modeled_posts():
    uid = current_user_id()
    with get_db() as conn:
        conn.execute('DELETE FROM modeled_posts WHERE user_id = ?', (uid,))
        conn.commit()
    return jsonify({'cleared': True})


@app.route('/api/stats')
@login_required
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
@login_required
def ai_insights_page():
    uid = current_user_id()
    search = request.args.get('q', '').strip()
    with get_db() as conn:
        rows = conn.execute('''
            SELECT i.id, i.post_id, i.highlighted_text, i.my_thoughts, i.created_at,
                   p.category, p.post_url
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            WHERE i.user_id = ?
            ORDER BY i.id DESC
        ''', (uid,)).fetchall()
        if search:
            history = conn.execute(
                "SELECT * FROM ai_analyses WHERE user_id = ? AND (analysis_text LIKE ? OR feedback LIKE ?) ORDER BY id DESC",
                (uid, f'%{search}%', f'%{search}%')
            ).fetchall()
        else:
            history = conn.execute(
                'SELECT * FROM ai_analyses WHERE user_id = ? ORDER BY id DESC', (uid,)
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
@login_required
def save_api_key():
    key = (request.get_json(force=True) or {}).get('api_key', '').strip()
    if key:
        set_setting('anthropic_api_key', key)
    return jsonify({'ok': True})


@app.route('/ai-insights/delete-key', methods=['POST'])
@login_required
def delete_api_key():
    uid = current_user_id()
    with get_db() as conn:
        conn.execute("DELETE FROM settings WHERE user_id = ? AND key = 'anthropic_api_key'", (uid,))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/ai-insights/save-prompt', methods=['POST'])
@login_required
def save_ai_prompt():
    prompt = (request.get_json(force=True) or {}).get('prompt', '').strip()
    if prompt:
        set_setting('ai_therapist_prompt', prompt)
    return jsonify({'ok': True})


@app.route('/ai-insights/analyze', methods=['POST'])
@login_required
def ai_analyze():
    if not _has_anthropic:
        return jsonify({'error': 'anthropic package not installed. Run: pip install anthropic'}), 500

    api_key = get_setting('anthropic_api_key', '')
    if not api_key:
        return jsonify({'error': 'No API key set. Enter your Anthropic API key above.'}), 400

    data = request.get_json(force=True) or {}
    prompt = data.get('prompt', '').strip() or DEFAULT_THERAPIST_PROMPT
    current_feelings = (data.get('current_feelings') or '').strip()

    uid = current_user_id()
    with get_db() as conn:
        insight_rows = conn.execute('''
            SELECT i.highlighted_text, i.my_thoughts, p.category
            FROM insights i
            LEFT JOIN posts p ON i.post_id = p.id
            WHERE i.user_id = ?
            ORDER BY i.id DESC
        ''', (uid,)).fetchall()
        # Pull past feedback for context
        past_feedback = conn.execute(
            "SELECT feedback, created_at FROM ai_analyses WHERE user_id = ? AND feedback != '' AND feedback IS NOT NULL ORDER BY id DESC LIMIT 5",
            (uid,)
        ).fetchall()

    if not insight_rows:
        return jsonify({'error': 'No insights saved yet. Highlight text on any post first.'}), 400

    # Build the user message
    parts = []
    for idx, row in enumerate(insight_rows, 1):
        cat = row['category'] or 'General'
        entry = f"[{idx}] ({cat})\nHighlighted: \"{row['highlighted_text']}\""
        if row['my_thoughts'] and row['my_thoughts'].strip():
            entry += f"\n\nMY OWN THOUGHTS & FEELINGS ABOUT THIS:\n{row['my_thoughts'].strip()}"
        parts.append(entry)

    user_message = (
        f"Here are {len(insight_rows)} passages I highlighted while reading about attachment and relationships:\n\n"
        + "\n\n".join(parts)
    )

    # Append current feelings/thoughts if provided
    if current_feelings:
        user_message += (
            "\n\n---\nWhat I'm experiencing right now — my current thoughts and feelings:\n"
            + current_feelings
            + "\n\nPlease weave this current context into your analysis."
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
                'INSERT INTO ai_analyses (user_id, analysis_text, prompt_used) VALUES (?, ?, ?)',
                (uid, result, prompt)
            )
            conn.commit()
            row = conn.execute('SELECT last_insert_rowid() as id').fetchone()
        return jsonify({'analysis': result, 'analysis_id': row['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ai-insights/<int:analysis_id>/feedback', methods=['POST'])
@login_required
def save_analysis_feedback(analysis_id):
    uid = current_user_id()
    data = request.get_json(force=True) or {}
    feedback = (data.get('feedback') or '').strip()
    with get_db() as conn:
        conn.execute('UPDATE ai_analyses SET feedback = ? WHERE id = ? AND user_id = ?', (feedback, analysis_id, uid))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/ai-insights/<int:analysis_id>/delete', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    uid = current_user_id()
    with get_db() as conn:
        conn.execute('DELETE FROM ai_analyses WHERE id = ? AND user_id = ?', (analysis_id, uid))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/post/<int:post_id>/category', methods=['POST'])
@login_required
def update_category(post_id):
    data = request.get_json(force=True) or {}
    category = (data.get('category') or '').strip()
    if not category:
        return jsonify({'error': 'No category'}), 400
    conn = get_db()
    try:
        conn.execute('UPDATE posts SET category = ? WHERE id = ?', (category, post_id))
        conn.commit()
        return jsonify({'ok': True, 'category': category})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/post/<int:post_id>/date', methods=['POST'])
@login_required
def update_date(post_id):
    data = request.get_json(force=True) or {}
    date_label = (data.get('date_label') or '').strip()
    conn = get_db()
    try:
        # Mark date as locked when user manually sets it
        conn.execute('UPDATE posts SET date_label = ?, date_label_locked = ? WHERE id = ?',
                     (date_label or None, 1 if date_label else 0, post_id))
        conn.commit()
        return jsonify({'ok': True, 'date_label': date_label})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/post/<int:post_id>/tags', methods=['POST'])
@login_required
def update_tags(post_id):
    uid = current_user_id()
    data = request.get_json(force=True) or {}
    tags = data.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    tags_str = json.dumps(tags)
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO user_post_prefs (user_id, post_id, tags)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, post_id) DO UPDATE SET tags = excluded.tags
        ''', (uid, post_id, tags_str))
        conn.commit()
        return jsonify({'ok': True, 'tags': tags})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/post/<int:post_id>/read', methods=['POST'])
@login_required
def toggle_read(post_id):
    uid = current_user_id()
    conn = get_db()
    try:
        # Check current state
        current = conn.execute(
            'SELECT is_read FROM user_post_prefs WHERE user_id = ? AND post_id = ?',
            (uid, post_id)
        ).fetchone()
        new_val = 0 if (current and current['is_read']) else 1

        # Delete old record if exists (simpler than ON CONFLICT)
        conn.execute(
            'DELETE FROM user_post_prefs WHERE user_id = ? AND post_id = ?',
            (uid, post_id)
        )

        # Insert new record
        conn.execute(
            'INSERT INTO user_post_prefs (user_id, post_id, is_read) VALUES (?, ?, ?)',
            (uid, post_id, new_val)
        )

        # Make sure we commit
        conn.commit()
        return jsonify({'is_read': new_val})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/stats')
@login_required
def stats_page():
    try:
        from flask import Response
        import traceback as tb

        # Get data
        uid = current_user_id()
        with get_db() as conn:
            cats = conn.execute(
                'SELECT category, COUNT(*) as cnt FROM posts GROUP BY category ORDER BY cnt DESC'
            ).fetchall()
            total = conn.execute('SELECT COUNT(*) as n FROM posts').fetchone()['n']
            read_result = conn.execute(
                'SELECT COUNT(DISTINCT up.post_id) as n FROM user_post_prefs up WHERE up.user_id = ? AND up.is_read = 1',
                (uid,)
            ).fetchone()
            read_count = read_result['n'] if read_result else 0
            revised_count = conn.execute('SELECT COUNT(*) as n FROM posts WHERE is_revised = 1').fetchone()['n']
            fav_result = conn.execute(
                'SELECT COUNT(DISTINCT up.post_id) as n FROM user_post_prefs up WHERE up.user_id = ? AND up.is_favorite = 1',
                (uid,)
            ).fetchone()
            fav_count = fav_result['n'] if fav_result else 0
            insight_result = conn.execute(
                'SELECT COUNT(*) as n FROM insights WHERE user_id = ?', (uid,)
            ).fetchone()
            insight_count = insight_result['n'] if insight_result else 0
            analysis_result = conn.execute(
                'SELECT COUNT(*) as n FROM ai_analyses WHERE user_id = ?', (uid,)
            ).fetchone()
            analysis_count = analysis_result['n'] if analysis_result else 0
            modeled_result = conn.execute(
                'SELECT COUNT(*) as n FROM modeled_posts WHERE user_id = ?', (uid,)
            ).fetchone()
            modeled_count = modeled_result['n'] if modeled_result else 0
            timeline = [dict(r) for r in conn.execute(
                "SELECT substr(imported_at, 1, 10) as day, COUNT(*) as cnt FROM posts GROUP BY day ORDER BY day"
            ).fetchall()]
            top_posts = conn.execute(
                'SELECT id, original_text, category, popularity, likes, comments FROM posts ORDER BY popularity DESC LIMIT 10'
            ).fetchall()
            cats = [dict(r) for r in cats]

        # Render template
        html = render_template('stats.html',
            cats=cats, total=total, read_count=read_count,
            revised_count=revised_count, fav_count=fav_count,
            insight_count=insight_count, analysis_count=analysis_count,
            modeled_count=modeled_count, timeline=timeline, top_posts=top_posts,
        )

        # Return as Response object
        response = Response(html, content_type='text/html; charset=utf-8')
        response.status_code = 200
        return response
    except Exception as e:
        import traceback as tb
        error_html = f"<html><body><h1>Stats Page Error</h1><pre>{tb.format_exc()}</pre></body></html>"
        return error_html, 500


@app.route('/export-collection/<collection_type>')
@login_required
def export_collection(collection_type):
    """Export a specific collection (insights, ai-analyses, or modeled-posts) as JSON"""
    uid = current_user_id()

    if collection_type == 'insights':
        with get_db() as conn:
            rows = conn.execute(
                'SELECT * FROM insights WHERE user_id = ? ORDER BY id',
                (uid,)
            ).fetchall()
        data = [dict(r) for r in rows]
        filename = 'insights.json'
    elif collection_type == 'ai-analyses':
        with get_db() as conn:
            rows = conn.execute(
                'SELECT * FROM ai_analyses WHERE user_id = ? ORDER BY id',
                (uid,)
            ).fetchall()
        data = [dict(r) for r in rows]
        filename = 'ai-analyses.json'
    elif collection_type == 'modeled-posts':
        with get_db() as conn:
            rows = conn.execute(
                'SELECT * FROM modeled_posts WHERE user_id = ? ORDER BY id',
                (uid,)
            ).fetchall()
        data = [dict(r) for r in rows]
        filename = 'modeled-posts.json'
    else:
        return jsonify({'error': 'Unknown collection type'}), 400

    payload = json.dumps({
        'version': 1,
        'exported_at': datetime.utcnow().isoformat(),
        'collection_type': collection_type,
        'count': len(data),
        'data': data
    }, indent=2)

    from flask import Response
    return Response(
        payload,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/restore-collection/<collection_type>', methods=['POST'])
@login_required
def restore_collection(collection_type):
    """Restore a collection from exported JSON"""
    uid = current_user_id()
    body = request.get_json(force=True) or {}

    if not isinstance(body, dict):
        return jsonify({'error': 'Expected JSON object'}), 400

    # Handle both direct array format and wrapped format
    data = body.get('data', body) if 'data' in body else body
    if not isinstance(data, list):
        data = [data] if isinstance(data, dict) else []

    if not data:
        return jsonify({'error': 'No data to restore'}), 400

    imported = 0
    skipped = 0

    with get_db() as conn:
        if collection_type == 'insights':
            for item in data:
                # Check for duplicates based on user_id, post_id, and highlighted_text
                existing = conn.execute(
                    'SELECT id FROM insights WHERE user_id = ? AND post_id = ? AND highlighted_text = ?',
                    (uid, item.get('post_id'), item.get('highlighted_text'))
                ).fetchone()
                if existing:
                    skipped += 1
                    continue
                conn.execute(
                    'INSERT INTO insights (user_id, post_id, highlighted_text, my_thoughts, created_at) VALUES (?, ?, ?, ?, ?)',
                    (uid, item.get('post_id'), item.get('highlighted_text'),
                     item.get('my_thoughts', ''), item.get('created_at', datetime.utcnow().isoformat()))
                )
                imported += 1
        elif collection_type == 'ai-analyses':
            for item in data:
                # Check for duplicates based on analysis_text
                existing = conn.execute(
                    'SELECT id FROM ai_analyses WHERE user_id = ? AND analysis_text = ?',
                    (uid, item.get('analysis_text'))
                ).fetchone()
                if existing:
                    skipped += 1
                    continue
                conn.execute(
                    'INSERT INTO ai_analyses (user_id, analysis_text, prompt_used, feedback, created_at) VALUES (?, ?, ?, ?, ?)',
                    (uid, item.get('analysis_text'), item.get('prompt_used', ''),
                     item.get('feedback', ''), item.get('created_at', datetime.utcnow().isoformat()))
                )
                imported += 1
        elif collection_type == 'modeled-posts':
            for item in data:
                # Check for duplicates based on post_text
                existing = conn.execute(
                    'SELECT id FROM modeled_posts WHERE user_id = ? AND post_text = ?',
                    (uid, item.get('post_text'))
                ).fetchone()
                if existing:
                    skipped += 1
                    continue
                conn.execute(
                    'INSERT INTO modeled_posts (user_id, post_text, attachment_style, topic, is_favorite, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                    (uid, item.get('post_text'), item.get('attachment_style'),
                     item.get('topic'), item.get('is_favorite', 0), item.get('created_at', datetime.utcnow().isoformat()))
                )
                imported += 1
        else:
            return jsonify({'error': 'Unknown collection type'}), 400

        conn.commit()

    return jsonify({
        'ok': True,
        'imported': imported,
        'skipped': skipped,
        'collection_type': collection_type
    })


@app.route('/export-all-collections')
@login_required
def export_all_collections():
    """Export all three collections (insights, ai-analyses, modeled-posts) as a ZIP file"""
    if not _has_zipfile:
        return jsonify({'error': 'ZIP support not available'}), 500

    uid = current_user_id()

    # Collect all three collections
    collections = {}
    with get_db() as conn:
        insights = [dict(r) for r in conn.execute(
            'SELECT * FROM insights WHERE user_id = ? ORDER BY id', (uid,)
        ).fetchall()]
        collections['insights'] = {
            'version': 1,
            'exported_at': datetime.utcnow().isoformat(),
            'collection_type': 'insights',
            'count': len(insights),
            'data': insights
        }

        ai_analyses = [dict(r) for r in conn.execute(
            'SELECT * FROM ai_analyses WHERE user_id = ? ORDER BY id', (uid,)
        ).fetchall()]
        collections['ai-analyses'] = {
            'version': 1,
            'exported_at': datetime.utcnow().isoformat(),
            'collection_type': 'ai-analyses',
            'count': len(ai_analyses),
            'data': ai_analyses
        }

        modeled_posts = [dict(r) for r in conn.execute(
            'SELECT * FROM modeled_posts WHERE user_id = ? ORDER BY id', (uid,)
        ).fetchall()]
        collections['modeled-posts'] = {
            'version': 1,
            'exported_at': datetime.utcnow().isoformat(),
            'collection_type': 'modeled-posts',
            'count': len(modeled_posts),
            'data': modeled_posts
        }

    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, data in collections.items():
            json_content = json.dumps(data, indent=2)
            zip_file.writestr(f'{filename}.json', json_content)

    zip_buffer.seek(0)

    from flask import Response
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': 'attachment; filename=personal-collections.zip'}
    )


@app.route('/restore-all-collections', methods=['POST'])
@login_required
def restore_all_collections():
    """Restore all three collections from a ZIP file"""
    if not _has_zipfile:
        return jsonify({'error': 'ZIP support not available'}), 500

    uid = current_user_id()

    if 'zipfile' not in request.files:
        return jsonify({'error': 'No ZIP file provided'}), 400

    zip_file = request.files['zipfile']
    if not zip_file or zip_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    results = {}

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            filelist = zip_ref.namelist()

            conn = get_db()
            try:
                for filename in filelist:
                    if not filename.endswith('.json'):
                        continue

                    # Determine collection type from filename
                    if 'insights' in filename:
                        collection_type = 'insights'
                    elif 'ai-analyses' in filename or 'ai_analyses' in filename:
                        collection_type = 'ai-analyses'
                    elif 'modeled-posts' in filename or 'modeled_posts' in filename:
                        collection_type = 'modeled-posts'
                    else:
                        continue

                    # Read and parse JSON
                    json_content = zip_ref.read(filename).decode('utf-8')
                    body = json.loads(json_content)
                    data = body.get('data', body) if 'data' in body else body
                    if not isinstance(data, list):
                        data = [data] if isinstance(data, dict) else []

                    imported = 0
                    skipped = 0

                    if collection_type == 'insights':
                        for item in data:
                            existing = conn.execute(
                                'SELECT id FROM insights WHERE user_id = ? AND post_id = ? AND highlighted_text = ?',
                                (uid, item.get('post_id'), item.get('highlighted_text'))
                            ).fetchone()
                            if existing:
                                skipped += 1
                                continue
                            conn.execute(
                                'INSERT INTO insights (user_id, post_id, highlighted_text, my_thoughts, created_at) VALUES (?, ?, ?, ?, ?)',
                                (uid, item.get('post_id'), item.get('highlighted_text'),
                                 item.get('my_thoughts', ''), item.get('created_at', datetime.utcnow().isoformat()))
                            )
                            imported += 1
                    elif collection_type == 'ai-analyses':
                        for item in data:
                            existing = conn.execute(
                                'SELECT id FROM ai_analyses WHERE user_id = ? AND analysis_text = ?',
                                (uid, item.get('analysis_text'))
                            ).fetchone()
                            if existing:
                                skipped += 1
                                continue
                            conn.execute(
                                'INSERT INTO ai_analyses (user_id, analysis_text, prompt_used, feedback, created_at) VALUES (?, ?, ?, ?, ?)',
                                (uid, item.get('analysis_text'), item.get('prompt_used', ''),
                                 item.get('feedback', ''), item.get('created_at', datetime.utcnow().isoformat()))
                            )
                            imported += 1
                    elif collection_type == 'modeled-posts':
                        for item in data:
                            existing = conn.execute(
                                'SELECT id FROM modeled_posts WHERE user_id = ? AND post_text = ?',
                                (uid, item.get('post_text'))
                            ).fetchone()
                            if existing:
                                skipped += 1
                                continue
                            conn.execute(
                                'INSERT INTO modeled_posts (user_id, post_text, attachment_style, topic, is_favorite, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                                (uid, item.get('post_text'), item.get('attachment_style'),
                                 item.get('topic'), item.get('is_favorite', 0), item.get('created_at', datetime.utcnow().isoformat()))
                            )
                            imported += 1

                    results[collection_type] = {
                        'imported': imported,
                        'skipped': skipped
                    }

                conn.commit()
            finally:
                conn.close()

        return jsonify({
            'ok': True,
            'insights': results.get('insights', {'imported': 0, 'skipped': 0}),
            'ai-analyses': results.get('ai-analyses', {'imported': 0, 'skipped': 0}),
            'modeled-posts': results.get('modeled-posts', {'imported': 0, 'skipped': 0})
        })

    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid ZIP file'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/backup')
@login_required
def backup():
    with get_db() as conn:
        posts = [dict(r) for r in conn.execute('SELECT * FROM posts').fetchall()]
        insights = [dict(r) for r in conn.execute('SELECT * FROM insights').fetchall()]
        ai_analyses = [dict(r) for r in conn.execute('SELECT * FROM ai_analyses').fetchall()]
        modeled = [dict(r) for r in conn.execute('SELECT * FROM modeled_posts').fetchall()]
    payload = json.dumps({
        'version': 1,
        'exported_at': datetime.utcnow().isoformat(),
        'posts': posts,
        'insights': insights,
        'ai_analyses': ai_analyses,
        'modeled_posts': modeled,
    }, indent=2)
    from flask import Response
    return Response(
        payload,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=attachmentlens_backup.json'}
    )


@app.route('/restore', methods=['POST'])
@login_required
def restore():
    uid = current_user_id()
    try:
        body = request.get_json(force=True)
        if not body or 'posts' not in body:
            return jsonify({'error': 'Invalid backup file — missing posts key.'}), 400
        imported = 0
        skipped = 0
        conn = get_db()
        try:
            for p in body.get('posts', []):
                text = (p.get('original_text') or '').strip()
                if not text:
                    skipped += 1
                    continue
                exists = conn.execute('SELECT 1 FROM posts WHERE original_text = ?', (text,)).fetchone()
                if exists:
                    skipped += 1
                    continue
                # Insert post data only (not user preferences)
                conn.execute('''INSERT INTO posts
                    (original_text, revised_text, date_label, post_url, category, is_revised,
                     popularity, imported_at, likes, comments)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (text, p.get('revised_text'), p.get('date_label'), p.get('post_url'),
                     p.get('category', DEFAULT_CATEGORY), p.get('is_revised', 0),
                     p.get('popularity', 0), p.get('imported_at'),
                     p.get('likes', 0), p.get('comments', 0)))

                # Get the post ID we just inserted
                post_id = conn.execute('SELECT last_insert_rowid() as id').fetchone()['id']

                # Insert user preferences if they exist
                tags_str = p.get('tags', '')
                if isinstance(tags_str, list):
                    tags_str = json.dumps(tags_str)
                elif not tags_str:
                    tags_str = ''

                conn.execute('''
                    INSERT INTO user_post_prefs (user_id, post_id, is_read, is_favorite, tags)
                    VALUES (?, ?, ?, ?, ?)
                ''', (uid, post_id, p.get('is_read', 0), p.get('is_favorite', 0), tags_str))

                imported += 1
            conn.commit()
            return jsonify({'imported': imported, 'skipped': skipped})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/bulk-label')
@login_required
def bulk_label():
    with get_db() as conn:
        posts = conn.execute(
            'SELECT id, original_text, category, is_read, is_favorite, imported_at, date_label FROM posts ORDER BY id DESC'
        ).fetchall()
    return render_template('bulk_label.html', posts=posts,
                           categories=list(CATEGORIES.keys()) + [DEFAULT_CATEGORY])


SUGGESTED_TOPICS = [
    "The anxious spiral — and how to find your way out",
    "What avoidants are really afraid of",
    "When love feels like danger",
    "Creating safety in your own nervous system",
    "The push-pull dynamic, explained from the inside",
    "Reparenting the part of you that never felt enough",
    "Breaking generational patterns in love",
    "What earned security actually looks like",
    "Nervous system regulation in relationships",
    "Learning to receive love without bracing for loss",
    "The difference between connection and enmeshment",
    "Healing doesn't mean never getting triggered",
    "When you're the one who always reaches first",
    "Grieving the relationship you never had as a child",
    "Building trust after betrayal",
]

MODELED_PERSONA_SYSTEM = """You are Derek Hart, a relationship writer and attachment coach with a warm, poetic voice. You write directly to people who are quietly struggling — people who recognize themselves in what you describe. Your tone is intimate, never clinical. You speak as someone who has done their own work and knows the terrain.

Your style:
- Short, punchy opening lines that immediately name something true
- Personal and direct — you address the reader as "you"
- Paragraphs that breathe — often 1–3 sentences, with intentional white space
- You name emotions precisely without diagrams or bullet points
- You alternate between validation and gentle challenge
- You close posts with something quietly hopeful — not toxic positivity, but real possibility
- You never lecture. You witness.
- Length: 150–350 words. No headers, no lists. Just prose with pauses.

Example posts from your library (for voice and style reference):
{examples}
"""


@app.route('/modeled-posts')
@login_required
def modeled_posts_page():
    uid = current_user_id()
    with get_db() as conn:
        saved = conn.execute(
            'SELECT * FROM modeled_posts WHERE user_id = ? ORDER BY id DESC', (uid,)
        ).fetchall()
        total_posts = conn.execute('SELECT COUNT(*) as n FROM posts').fetchone()['n']
    api_key = get_setting('anthropic_api_key', '')
    return render_template(
        'modeled_posts.html',
        saved=saved,
        total_posts=total_posts,
        api_key_set=bool(api_key),
        suggested_topics=SUGGESTED_TOPICS,
        attachment_styles=list(CATEGORIES.keys()) + ['General Relationship'],
        has_anthropic=_has_anthropic,
    )


@app.route('/modeled-posts/generate', methods=['POST'])
@login_required
def modeled_posts_generate():
    if not _has_anthropic:
        return jsonify({'error': 'anthropic package not installed. Run: pip install anthropic'}), 500
    api_key = get_setting('anthropic_api_key', '')
    if not api_key:
        return jsonify({'error': 'No API key set. Add it on the AI Insights page first.'}), 400

    data = request.get_json(force=True) or {}
    attachment_style = (data.get('attachment_style') or 'General Relationship').strip()
    topic = (data.get('topic') or '').strip()
    if not topic:
        return jsonify({'error': 'Please enter a topic.'}), 400

    # Pull top posts as voice examples (up to 12, sorted by popularity)
    with get_db() as conn:
        example_rows = conn.execute(
            'SELECT original_text FROM posts ORDER BY popularity DESC, id DESC LIMIT 12'
        ).fetchall()

    if not example_rows:
        return jsonify({'error': 'No posts in your library yet. Import some posts first so I can learn the style.'}), 400

    examples = '\n\n---\n\n'.join(
        r['original_text'][:800] for r in example_rows
    )
    system_prompt = MODELED_PERSONA_SYSTEM.format(examples=examples)

    user_msg = (
        f"Write a new post in your style.\n\n"
        f"Topic: {topic}\n"
        f"Attachment style lens: {attachment_style}\n\n"
        "Make it feel true. Make it feel like you."
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=1000,
            system=system_prompt,
            messages=[{'role': 'user', 'content': user_msg}]
        )
        post_text = message.content[0].text.strip()

        uid = current_user_id()
        with get_db() as conn:
            conn.execute(
                'INSERT INTO modeled_posts (user_id, post_text, attachment_style, topic) VALUES (?, ?, ?, ?)',
                (uid, post_text, attachment_style, topic)
            )
            conn.commit()
            row = conn.execute('SELECT last_insert_rowid() as id').fetchone()

        return jsonify({'post_text': post_text, 'id': row['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/modeled-posts/<int:post_id>/favorite', methods=['POST'])
@login_required
def modeled_post_favorite(post_id):
    uid = current_user_id()
    with get_db() as conn:
        current = conn.execute('SELECT is_favorite FROM modeled_posts WHERE id = ? AND user_id = ?', (post_id, uid)).fetchone()
        if current:
            new_val = 0 if current['is_favorite'] else 1
            conn.execute('UPDATE modeled_posts SET is_favorite = ? WHERE id = ? AND user_id = ?', (new_val, post_id, uid))
            conn.commit()
            return jsonify({'is_favorite': new_val})
    return jsonify({'error': 'not found'}), 404


@app.route('/modeled-posts/<int:post_id>/delete', methods=['POST'])
@login_required
def modeled_post_delete(post_id):
    uid = current_user_id()
    with get_db() as conn:
        conn.execute('DELETE FROM modeled_posts WHERE id = ? AND user_id = ?', (post_id, uid))
        conn.commit()
    return jsonify({'ok': True})


@app.route('/settings/github-token', methods=['POST'])
@login_required
def save_github_token():
    token = (request.get_json(force=True) or {}).get('token', '').strip()
    if token:
        set_setting('github_token', token, user_id=1)
    return jsonify({'ok': True})


@app.route('/settings/github-token/delete', methods=['POST'])
@login_required
def delete_github_token():
    with get_db() as conn:
        conn.execute("DELETE FROM settings WHERE user_id = 1 AND key = 'github_token'")
        conn.commit()
    return jsonify({'ok': True})


@app.route('/github/test', methods=['POST'])
@login_required
def github_test():
    """Verify the saved token can read the TODO.md from GitHub."""
    import urllib.request as urlreq
    import base64

    github_token = get_setting('github_token', '', user_id=1)
    if not github_token:
        return jsonify({'ok': False, 'error': 'No token saved yet'})

    API = 'https://api.github.com/repos/btaira/AttachmentLens/contents/TODO.md'
    HEADERS = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    try:
        req = urlreq.Request(API)
        for k, v in HEADERS.items():
            req.add_header(k, v)
        with urlreq.urlopen(req, timeout=10) as resp:
            file_data = json.loads(resp.read().decode())
        return jsonify({'ok': True, 'sha': file_data.get('sha', '')[:8], 'size': file_data.get('size')})
    except urlreq.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('message', body[:200])
        except Exception:
            msg = body[:200]
        return jsonify({'ok': False, 'error': f'HTTP {e.code}: {msg}'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/export-posts-to-github', methods=['POST'])
@login_required
def export_posts_to_github():
    """Export all posts as JSON to GitHub as posts-database.json"""
    import urllib.request as urlreq
    import base64

    github_token = get_setting('github_token', '', user_id=1)
    if not github_token:
        return jsonify({'error': 'No GitHub token configured. Add one under GitHub Integration above.'}), 400

    with get_db() as conn:
        posts = [dict(r) for r in conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()]

    if not posts:
        return jsonify({'error': 'No posts to export'}), 400

    payload_json = json.dumps({
        'version': 1,
        'exported_at': datetime.utcnow().isoformat(),
        'posts': posts
    }, indent=2)

    OWNER = 'btaira'
    REPO = 'AttachmentLens'
    PATH = 'posts-database.json'
    API = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'

    def gh_request(url, data=None, method=None):
        req = urlreq.Request(url, data=data, method=method)
        req.add_header('Authorization', f'token {github_token}')
        req.add_header('Accept', 'application/vnd.github+json')
        req.add_header('X-GitHub-Api-Version', '2022-11-28')
        if data:
            req.add_header('Content-Type', 'application/json')
        return req

    try:
        # Try to get existing file SHA
        file_sha = None
        try:
            with urlreq.urlopen(gh_request(API), timeout=15) as resp:
                file_data = json.loads(resp.read().decode())
                file_sha = file_data.get('sha')
        except urlreq.HTTPError as e:
            if e.code != 404:
                raise
            # File doesn't exist yet, that's okay

        # Create/update the file
        payload = json.dumps({
            'message': f'chore: update posts database ({len(posts)} posts)',
            'content': base64.b64encode(payload_json.encode('utf-8')).decode(),
            'sha': file_sha
        }).encode('utf-8')

        with urlreq.urlopen(gh_request(API, data=payload, method='PUT'), timeout=15) as resp:
            result = json.loads(resp.read().decode())

        commit_url = result.get('commit', {}).get('html_url', '')
        return jsonify({
            'ok': True,
            'count': len(posts),
            'commit': commit_url,
            'message': f'Exported {len(posts)} posts to posts-database.json'
        })

    except urlreq.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('message', body)
        except Exception:
            msg = body[:200]
        return jsonify({'error': f'GitHub {e.code}: {msg}'}), 500
    except Exception as e:
        return jsonify({'error': f'{type(e).__name__}: {e}'}), 500


@app.route('/feature-request', methods=['POST'])
@login_required
def feature_request():
    import urllib.request as urlreq
    import base64

    data = request.get_json(force=True) or {}
    text = (data.get('text') or '').strip()
    username = (session.get('username') or 'unknown').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    github_token = get_setting('github_token', '', user_id=1)
    if not github_token:
        return jsonify({'error': 'No GitHub token configured. Ask an admin to add one in ⚙️ Admin → Import Posts.'}), 400

    OWNER = 'btaira'
    REPO  = 'AttachmentLens'
    PATH  = 'TODO.md'
    API   = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'

    def gh_request(url, data=None, method=None):
        """Build a GitHub API request using add_header (more reliable than dict constructor)."""
        req = urlreq.Request(url, data=data, method=method)
        req.add_header('Authorization', f'token {github_token}')
        req.add_header('Accept', 'application/vnd.github+json')
        req.add_header('X-GitHub-Api-Version', '2022-11-28')
        if data:
            req.add_header('Content-Type', 'application/json')
        return req

    try:
        # 1. GET current file to obtain sha + content
        with urlreq.urlopen(gh_request(API), timeout=15) as resp:
            file_data = json.loads(resp.read().decode())

        current_content = base64.b64decode(file_data['content']).decode('utf-8')
        file_sha = file_data['sha']

        # 2. Prepend entry under "## High Priority"
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        entry = f'- [ ] **[Requested by {username}, {date_str}]** {text}'

        marker = '## High Priority'
        if marker in current_content:
            idx = current_content.index(marker) + len(marker)
            insert_at = idx
            while insert_at < len(current_content) and current_content[insert_at] == '\n':
                insert_at += 1
            new_content = current_content[:insert_at] + '\n' + entry + '\n' + current_content[insert_at:]
        else:
            new_content = current_content.rstrip() + '\n\n' + entry + '\n'

        # 3. PUT updated file back
        payload = json.dumps({
            'message': f'feat: feature request from {username} — {text[:60]}',
            'content': base64.b64encode(new_content.encode('utf-8')).decode(),
            'sha': file_sha,
        }).encode('utf-8')

        with urlreq.urlopen(gh_request(API, data=payload, method='PUT'), timeout=15) as resp:
            result = json.loads(resp.read().decode())

        commit_url = result.get('commit', {}).get('html_url', '')
        return jsonify({'ok': True, 'commit': commit_url})

    except urlreq.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            msg = json.loads(body).get('message', body)
        except Exception:
            msg = body[:200]
        return jsonify({'error': f'GitHub {e.code}: {msg}'}), 500
    except Exception as e:
        return jsonify({'error': f'{type(e).__name__}: {e}'}), 500


@app.route('/settings/customization', methods=['POST'])
@login_required
def save_customization():
    uid = current_user_id()
    data = request.get_json(force=True) or {}
    theme = (data.get('theme') or '').strip()
    font = (data.get('font') or '').strip()
    fontSize = (data.get('fontSize') or '').strip()

    with get_db() as conn:
        for key, val in [('theme', theme), ('font', font), ('fontSize', fontSize)]:
            conn.execute('INSERT OR REPLACE INTO settings (user_id, key, value) VALUES (?, ?, ?)',
                        (uid, f'customization_{key}', val))
        conn.commit()
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
