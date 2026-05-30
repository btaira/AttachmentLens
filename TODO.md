# Attachment Lens — Feature Roadmap

## High Priority

- [ ] **Manual category override** — dropdown on post detail page to correct misclassified posts; the keyword classifier is a starting point, not gospel
- [ ] **Multi-category tagging** — some posts span multiple attachment styles; allow more than one label per post
- [ ] **Read / Unread status** — toggle on each post, filter in the library; turns the app from a passive archive into an active reading queue

## Medium Priority

- [ ] **Export to PDF** — generate a shareable PDF of AI analyses and highlights to bring to a therapy session or keep for personal records
- [ ] **Stats & progress dashboard** — charts showing which attachment styles dominate your highlights, reading pace over time, posts read vs unread; make the patterns visible
- [ ] **Backup & restore** — export the full database to JSON and re-import it; protects against data loss if `posts.db` is corrupted or you switch computers

## Longer Term

- [ ] **Browser extension scraper** — replace the fragile console script with an extension that captures posts as you naturally browse; Facebook changes its DOM regularly and the script will break again
- [ ] **Bulk re-labeling view** — a table showing all posts with a quick category dropdown per row; lets you clean up the initial import in one sitting

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
- [x] Font size adjuster, sticky nav, dark theme
