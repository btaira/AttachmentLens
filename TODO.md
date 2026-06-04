# Attachment Lens — Feature Roadmap

## High Priority

- [ ] **[Requested by Brent, 2026-05-31]** Video reading of posts - HeyGen
- [ ] **Duplicate detection** — flag near-duplicate posts (same text, slightly different formatting) before import; keep newest
- [ ] **[Requested by Brent, 2026-05-31]** Video reading of posts - HeyGen
- [ ] **Export to PDF** — generate a shareable PDF of AI analyses and highlights to bring to a therapy session or keep for personal records
- [ ] **Browser extension scraper** — replace the fragile console script with an extension that captures posts as you naturally browse; Facebook changed its DOM in May 2026 and timestamp links no longer expose date metadata — a browser extension can intercept network requests to get reliable post dates

## Medium Priority

- [ ] **Post date range filtering** — filter the library by date range (e.g. "last 30 days", "this year") using the date_label field
- [ ] **Comment count accuracy** — for high-engagement posts Facebook shows "View all X comments" but collapses the count; investigate fetching the full comment count via the post URL
- [ ] **Category confidence score** — show how certain the keyword classifier is; flag posts near the boundary between two styles for manual review
- [ ] **Attachment style trend chart** — line chart on the Stats page showing which styles Derek posts about most over time, week by week

## Longer Term

- [ ] **Semantic search** — embed posts with a small model and search by meaning rather than keywords ("posts about fear of abandonment") instead of just substring search
- [ ] **Therapist export pack** — one-click export of favorites + insights + AI analysis formatted as a structured PDF for use in a session
- [ ] **Mobile-friendly layout** — the current design works on desktop; a responsive mobile layout would allow browsing and annotating on the go

## Already Built ✅
- [x] **Static Date** After the date for a post has been saved, it should remain permanent. Posts imported with dates are auto-locked and won't be overwritten by future imports.
- [x] **[Requested by Brent, 2026-06-01]** Bug - after saving to insights, the text should change to golden yellow. Page now reloads after saving to show golden highlight immediately.
- [x] **[Requested by admin, 2026-05-31]** User customization - 6 different backgrounds, choice of fonts and size of fonts. 🎨 Customize button in nav.
- [x] Import posts via Facebook scraper (console script)
- [x] Attachment style auto-classifier
- [x] Post detail with edit / personalize / word diff
- [x] Favorites with section on home page
- [x] Likes & comments tracking and sorting — split into separate columns, center-aligned
- [x] Highlights / Insights — highlight text on any post, save with personal thoughts
- [x] AI Insights — Claude analysis of all highlights, editable therapist prompt
- [x] AI analysis history — searchable, with per-entry reflections that feed future analyses
- [x] Delete API key button
- [x] Font size adjuster (🔤 Text), sticky nav, dark theme
- [x] Modeled Posts — AI-generated posts in Derek Hart's style with attachment style + topic selector
- [x] Improved Facebook scraper — fallback selectors, longer waits, stale-round patience
- [x] "Save to Insights" floating button repositioned to left of selected text
- [x] Current thoughts & feelings field on AI Insights page fed into analysis
- [x] Personal "My Thoughts & Feelings" per insight weighted heavily in AI analysis
- [x] Manual category override on post detail page
- [x] Multi-category tagging (tags field)
- [x] Read / Unread status toggle and filter
- [x] Stats & progress dashboard — charts showing category breakdown, read vs unread, import timeline, top posts
- [x] Backup & restore — export full database to JSON and re-import
- [x] Bulk re-labeling view — table with quick category dropdown per row (moved to ⚙️ Admin menu)
- [x] Date capture from Facebook posts — resolves relative timestamps ("3h" → "May 30, 2026"); falls back to today's date for very recent posts where Facebook no longer exposes date metadata in the DOM
- [x] All Posts sort by newest/oldest using real post date; undated posts sort as recent
- [x] Admin dropdown in nav — Import Posts and Bulk Label moved to right-side admin menu with emojis
- [x] **Multi-user support** — login/register system, session-based auth, per-user favorites/insights/analyses/modeled posts, user switcher dropdown in nav, admin role
- [x] **Session persistence across restarts** — secret key stored in `./data/.secret_key` (Docker volume); logins survive container rebuilds
- [x] **Route protection** — all routes require login; unauthenticated page loads redirect to login; unauthenticated API calls return JSON 401
- [x] **Per-user clear data** — Clear My Insights, Clear AI Analysis History, Clear Modeled Posts buttons in Danger Zone (Admin → Import/Update Posts)
- [x] **GitHub Integration** — store a PAT token, test connection, commit feature requests to the repo's TODO.md
- [x] **Feature request button** — 💡 Request in nav bar opens a modal; approved requests are committed to GitHub TODO.md
- [x] **App logo** — two interlocking rings logo displayed in nav bar, login page, and README; 50% larger in nav with increased nav height
- [x] **Manual date editing on post detail** — pencil button next to date in the post meta row lets you set or correct any post's date inline
- [x] **Bulk date assignment** — Bulk Re-Label page now has a Date column with a "No date" filter, sortable by date, and checkbox row selection for bulk-applying a date to multiple posts at once
- [x] **Latest 5 posts sorted by date** — home page "Latest Posts" cards now show the 5 most recently dated posts rather than the 5 most recently imported
