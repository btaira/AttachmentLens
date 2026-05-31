# Attachment Lens — Feature Roadmap

## High Priority



- [ ] **[Requested by Brent, 2026-05-31]** Add logo
- [ ] **[Requested by admin, 2026-05-31]** User customization - 6 different backgrounds, choice of fonts and size of fonts.
- [ ] **Multi-user support** — login system with per-user favorites, insights, AI insights, and modeled posts; user switcher dropdown in the upper-right nav bar; admin role for managing users and import/bulk-label
- [ ] **Export to PDF** — generate a shareable PDF of AI analyses and highlights to bring to a therapy session or keep for personal records
- [ ] **Browser extension scraper** — replace the fragile console script with an extension that captures posts as you naturally browse; Facebook changes its DOM regularly and the script will break again

## Medium Priority

- [ ] **Post date filtering** — filter the library by date range (e.g. "last 30 days", "this year") using the date_label field now captured from Facebook
- [ ] **Comment count accuracy** — for high-engagement posts Facebook shows "View all X comments" but collapses the count; investigate fetching the full comment count via the post URL
- [ ] **Category confidence score** — show how certain the keyword classifier is; flag posts near the boundary between two styles for manual review
- [ ] **Attachment style trend chart** — line chart on the Stats page showing which styles Derek posts about most over time, week by week
- [ ] **Duplicate detection** — flag near-duplicate posts (same text, slightly different formatting) before import; show a diff and let user decide which to keep

## Longer Term

- [ ] **Semantic search** — embed posts with a small model and search by meaning rather than keywords ("posts about fear of abandonment") instead of just substring match
- [ ] **Therapist export pack** — one-click export of favorites + insights + AI analysis formatted as a structured PDF for use in a session
- [ ] **Mobile-friendly layout** — the current design works on desktop; a responsive mobile layout would allow browsing and annotating on the go

## Already Built ✅

- [x] Import posts via Facebook scraper (console script)
- [x] Attachment style auto-classifier
- [x] Post detail with edit / personalize / word diff
- [x] Favorites with section on home page
- [x] Likes & comments tracking and sorting
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
- [x] Date capture from Facebook posts — resolves relative timestamps ("3h" → "May 30, 2026")
- [x] All Posts sort by newest/oldest using real post date
- [x] Admin dropdown in nav — Import Posts and Bulk Label moved to right-side admin menu with emojis
