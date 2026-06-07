# AttachmentLens — Functional Test Cases

This file contains manual functional test cases covering implemented AttachmentLens features (Flask routes + UI behaviors).

## Conventions

- **Priority:** P0 = critical (auth/data loss), P1 = major, P2 = normal, P3 = minor polish.
- **Expected Result** includes UI behavior + API response where applicable.
- **Postconditions** are included to satisfy “preconditions and postconditions” coverage.

## Common Test Data / Setup (reference)

- App running locally (default `http://localhost:5000`).
- Two users exist: `admin/admin` (default) and a non-admin test user `user1/pass1` (create during tests).
- Library contains at least:
  - `Post A` with a valid `date_label` (e.g., `June 01, 2026`) and non-zero likes/comments.
  - `Post B` with **no** `date_label`.
  - `Post C` with a different category than `Post A`.
- Anthropic features:
  - To test AI flows, the `anthropic` Python package is installed and an API key is available (or use negative tests when absent).
- GitHub integration:
  - To test GitHub flows, a valid PAT with `repo` scope is available (or use negative tests when absent).

---

# Authentication & Sessions

### Test ID: AL-FUNC-001
- Title: Login — happy path
- Preconditions: User account exists (e.g., `admin/admin`); user is logged out.
- Steps:
  1. Navigate to `/login`.
  2. Enter valid username and password.
  3. Submit.
- Expected Result: User is redirected to `/` and sees authenticated navigation (user switcher visible).
- Priority: P0
- Postconditions: Session cookie is set; subsequent GET to `/` succeeds without redirect.

### Test ID: AL-FUNC-002
- Title: Login — invalid credentials validation
- Preconditions: User is logged out.
- Steps:
  1. Navigate to `/login`.
  2. Enter a valid username with wrong password (or nonexistent username).
  3. Submit.
- Expected Result: Login page re-renders with error “Invalid username or password.”; no session is created.
- Priority: P0
- Postconditions: User remains logged out; GET `/` redirects to `/login`.

### Test ID: AL-FUNC-003
- Title: Register — happy path (auto-login)
- Preconditions: Logged out; username does not already exist.
- Steps:
  1. Navigate to `/register`.
  2. Enter a new username and a password of at least 4 characters.
  3. Submit.
- Expected Result: User is created, automatically logged in, and redirected to `/`.
- Priority: P0
- Postconditions: New user appears in user switcher list; session is active.

### Test ID: AL-FUNC-004
- Title: Register — required fields validation
- Preconditions: Logged out.
- Steps:
  1. Navigate to `/register`.
  2. Leave username empty and/or password empty.
  3. Submit.
- Expected Result: Registration page shows “Username and password are required.”; user is not created.
- Priority: P1
- Postconditions: No new user exists for the attempted username.

### Test ID: AL-FUNC-005
- Title: Register — password length validation
- Preconditions: Logged out; username does not already exist.
- Steps:
  1. Navigate to `/register`.
  2. Enter a new username.
  3. Enter a password shorter than 4 characters.
  4. Submit.
- Expected Result: Registration page shows “Password must be at least 4 characters.”; user is not created.
- Priority: P1
- Postconditions: No new user exists for the attempted username.

### Test ID: AL-FUNC-006
- Title: Register — duplicate username alternative flow
- Preconditions: Logged out; username already exists.
- Steps:
  1. Navigate to `/register`.
  2. Enter an existing username with any password (>=4).
  3. Submit.
- Expected Result: Registration page shows “Username already taken.”; existing user unchanged.
- Priority: P1
- Postconditions: No duplicate user created.

### Test ID: AL-FUNC-007
- Title: Logout — session cleared
- Preconditions: Logged in.
- Steps:
  1. Click “Logout” (or navigate to `/logout`).
- Expected Result: Session is cleared; browser is redirected to `/login`.
- Priority: P0
- Postconditions: GET `/` redirects to `/login`.

### Test ID: AL-FUNC-008
- Title: Auth guard — GET redirects, POST returns JSON 401
- Preconditions: Logged out.
- Steps:
  1. Navigate to `/` in the browser.
  2. Send a POST to a protected endpoint (e.g., `/post/1/favorite`) using browser devtools `fetch`.
- Expected Result: (1) Browser is redirected to `/login`. (2) POST returns HTTP 401 JSON with `error` about session expired.
- Priority: P0
- Postconditions: User remains logged out.

---

# Multi-User Switching

### Test ID: AL-FUNC-009
- Title: Switch user — happy path
- Preconditions: Logged in; at least two users exist.
- Steps:
  1. Use the user switcher in nav to switch from `admin` to `user1`.
  2. Return to `/`.
- Expected Result: Session changes to selected user; username in nav updates; per-user data (favorites/insights) reflects the new user.
- Priority: P1
- Postconditions: Subsequent actions apply to the switched user’s data.

### Test ID: AL-FUNC-010
- Title: Switch user — invalid target user ID
- Preconditions: Logged in.
- Steps:
  1. POST to `/switch-user/999999` (a non-existent user).
  2. Navigate to `/`.
- Expected Result: No crash; user remains the same as before; redirect occurs back to referrer or `/`.
- Priority: P2
- Postconditions: Session user unchanged.

---

# Library (Home / All Posts)

### Test ID: AL-FUNC-011
- Title: Home page loads with sidebar categories and library table
- Preconditions: Logged in; at least 1 post exists.
- Steps:
  1. Navigate to `/`.
- Expected Result: Page renders “Latest Posts”, categories list with counts, and a library table of posts.
- Priority: P0
- Postconditions: None.

### Test ID: AL-FUNC-012
- Title: Latest posts ordering — date-based sorting behavior
- Preconditions: Logged in; at least one post has a parseable `date_label`; another post has no date.
- Steps:
  1. Navigate to `/`.
  2. Observe “Latest Posts” cards order.
- Expected Result: Cards are ordered by parsed `date_label` descending; posts without parseable dates appear after dated posts.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-013
- Title: Library search — happy path
- Preconditions: Logged in; at least one post contains a unique phrase in `original_text` or `revised_text`.
- Steps:
  1. Enter the unique phrase in the search box.
  2. Submit.
- Expected Result: Library shows only matching posts; the query persists in the input field.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-014
- Title: Search redirect route — `/search` forwards to `/`
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/search?q=test`.
- Expected Result: Browser redirects to `/?q=test` (or equivalent), showing search results state.
- Priority: P3
- Postconditions: None.

### Test ID: AL-FUNC-015
- Title: Category view — filter by category
- Preconditions: Logged in; posts exist in at least two categories.
- Steps:
  1. Click a category in the sidebar.
- Expected Result: Category page shows posts only in that category; category list remains visible.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-016
- Title: Library sort — popularity/newest/oldest (client-side)
- Preconditions: Logged in; multiple posts exist with differing popularity and dates.
- Steps:
  1. On `/`, change “Sort by” to Popularity, Newest, and Oldest.
  2. Refresh the page.
- Expected Result: Rows reorder immediately; selected sort persists across refresh via local storage.
- Priority: P2
- Postconditions: Local storage contains saved sort preference.

### Test ID: AL-FUNC-017
- Title: Read filter chips — All/Read/Unread (client-side)
- Preconditions: Logged in; at least one post is marked read and one is unread for the current user.
- Steps:
  1. Click “Read” filter chip.
  2. Click “Unread” filter chip.
  3. Click “All”.
- Expected Result: Table rows show/hide based on read state for the current user; no server request required.
- Priority: P2
- Postconditions: None.

### Test ID: AL-FUNC-018
- Title: Favorites section (Latest 5 Favorites) — per-user isolation
- Preconditions: Two users exist; same post exists for both; User A favorites a post; User B does not.
- Steps:
  1. As User A, favorite a post and go to `/`.
  2. Switch to User B and go to `/`.
- Expected Result: User A sees the favorited post in favorites section; User B does not.
- Priority: P1
- Postconditions: Favorite state remains per-user after switching back.

---

# Import / Update Posts

### Test ID: AL-FUNC-019
- Title: Import page loads with scraper script panel
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/import`.
- Expected Result: “Import / Update Posts” page loads; instructions and copy-to-clipboard script section are visible; import textarea is available.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-020
- Title: Import via `/import` — happy path (small JSON)
- Preconditions: Logged in; prepare valid JSON array with at least one item containing `text` length >= 30.
- Steps:
  1. Paste JSON into import textarea.
  2. Submit import.
- Expected Result: App imports posts, skips duplicates/short texts, and redirects to `/` with `imported` and `skipped` query params.
- Priority: P0
- Postconditions: Imported posts appear in library.

### Test ID: AL-FUNC-021
- Title: Import via `/import` — invalid JSON validation
- Preconditions: Logged in.
- Steps:
  1. Paste invalid JSON (e.g., `{`) into textarea.
  2. Submit import.
- Expected Result: Import page re-renders with “JSON parse error: …”.
- Priority: P1
- Postconditions: No posts imported.

### Test ID: AL-FUNC-022
- Title: Import via `/import_json` — happy path (large payload)
- Preconditions: Logged in; prepare a valid JSON array string in `json_data` that includes new posts and duplicates.
- Steps:
  1. From browser console, POST JSON to `/import_json` with body `{ "json_data": "<stringified json array>" }`.
- Expected Result: Endpoint returns JSON `{ imported, updated, skipped }`; posts are inserted/updated as appropriate.
- Priority: P0
- Postconditions: Library reflects imported posts; duplicates are not duplicated.

### Test ID: AL-FUNC-023
- Title: Import via `/import_json` — validation: non-array payload
- Preconditions: Logged in.
- Steps:
  1. POST to `/import_json` where `json_data` parses to an object (not an array).
- Expected Result: HTTP 400 JSON with `error: "Expected a JSON array."`.
- Priority: P1
- Postconditions: No new posts imported.

### Test ID: AL-FUNC-024
- Title: Imported date locking — imported dates should not be overwritten
- Preconditions: Logged in; a post already exists with `date_label_locked = 1` and a known `date_label`.
- Steps:
  1. Re-import the same post text via `/import_json` with a different `date`.
- Expected Result: Post’s date remains unchanged when locked; likes/comments may update.
- Priority: P1
- Postconditions: Date remains locked.

---

# Post Detail (View / Edit / Metadata)

### Test ID: AL-FUNC-025
- Title: View post detail — happy path
- Preconditions: Logged in; at least one post exists.
- Steps:
  1. Open a post from the library (e.g., click its title).
- Expected Result: Post page renders; category/date/tags controls are present; saved highlights (if any) are visually marked.
- Priority: P0
- Postconditions: None.

### Test ID: AL-FUNC-026
- Title: View post detail — invalid post ID
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/post/999999`.
- Expected Result: HTTP 404 with “Post not found”.
- Priority: P2
- Postconditions: None.

### Test ID: AL-FUNC-027
- Title: Edit post — set personalized text (happy path)
- Preconditions: Logged in; post exists.
- Steps:
  1. On post page, open edit mode.
  2. Enter revised text that differs from original.
  3. Save.
- Expected Result: Revised text is saved and indicated as “Personalized/Revised”; switching versions shows updated content.
- Priority: P1
- Postconditions: Post has `is_revised = 1` and `revised_text` stored.

### Test ID: AL-FUNC-028
- Title: Edit post — validation/alternative: empty or identical clears revision
- Preconditions: Logged in; post exists with a prior revision saved.
- Steps:
  1. Edit the post again and set revised text to empty (or exactly original text).
  2. Save.
- Expected Result: Revision is cleared (no personalized version); badge indicates original.
- Priority: P2
- Postconditions: Post has `is_revised = 0` and `revised_text` is null.

### Test ID: AL-FUNC-029
- Title: Revert post — clears personalization
- Preconditions: Logged in; post has a revision.
- Steps:
  1. Click “Revert” on the post page.
- Expected Result: Personalized text is removed; user returns to post view showing original.
- Priority: P2
- Postconditions: Post is no longer marked revised.

### Test ID: AL-FUNC-030
- Title: Favorite toggle (post) — happy path
- Preconditions: Logged in; post exists; post is not favorited for current user.
- Steps:
  1. Click favorite star/button.
  2. Click again to un-favorite.
- Expected Result: Favorite UI toggles immediately; API returns JSON `is_favorite` 1 then 0.
- Priority: P1
- Postconditions: Favorite state persists on refresh (per-user).

### Test ID: AL-FUNC-031
- Title: Read/unread toggle — happy path
- Preconditions: Logged in; post exists.
- Steps:
  1. Click “Mark Read” (or read toggle) on post page.
  2. Refresh and verify state.
  3. Toggle back to unread.
- Expected Result: API returns JSON `is_read` toggling 1/0; UI reflects the state and persists after refresh.
- Priority: P1
- Postconditions: Read state persists per-user.

### Test ID: AL-FUNC-032
- Title: Update category — validation for empty category
- Preconditions: Logged in; post exists.
- Steps:
  1. POST to `/post/<id>/category` with `{ "category": "" }`.
- Expected Result: HTTP 400 JSON with `error: "No category"`.
- Priority: P2
- Postconditions: Category remains unchanged.

### Test ID: AL-FUNC-033
- Title: Update category — happy path
- Preconditions: Logged in; post exists.
- Steps:
  1. Change category on post page to another valid label.
- Expected Result: Category updates and persists on refresh; API returns `{ ok: true, category: "<value>" }`.
- Priority: P2
- Postconditions: Post’s `category` field matches the new value.

### Test ID: AL-FUNC-034
- Title: Update date — set and lock date (happy path)
- Preconditions: Logged in; post exists.
- Steps:
  1. Enter a date label (e.g., `June 01, 2026`) and save.
- Expected Result: Date displays on the post; API returns `{ ok: true, date_label: "..." }`.
- Priority: P2
- Postconditions: `date_label_locked` is set for the post when date is non-empty.

### Test ID: AL-FUNC-035
- Title: Update date — clear date (alternative flow)
- Preconditions: Logged in; post has a date set.
- Steps:
  1. Clear the date input and save.
- Expected Result: Date is removed from display; API returns `{ ok: true, date_label: "" }`.
- Priority: P3
- Postconditions: `date_label_locked` becomes 0 when date cleared.

### Test ID: AL-FUNC-036
- Title: Update tags — accepts list; non-list coerces to empty list
- Preconditions: Logged in; post exists.
- Steps:
  1. POST to `/post/<id>/tags` with `{ "tags": ["foo","bar"] }`.
  2. POST again with `{ "tags": "not-a-list" }`.
- Expected Result: (1) API returns `{ ok: true, tags: ["foo","bar"] }`. (2) API returns `{ ok: true, tags: [] }` without crashing.
- Priority: P2
- Postconditions: Stored tags match the last accepted value.

### Test ID: AL-FUNC-037
- Title: Delete post — happy path
- Preconditions: Logged in; post exists; user understands this is destructive.
- Steps:
  1. Click delete on the post page (confirm if prompted by UI).
- Expected Result: Post is removed; user is redirected to `/`; post no longer appears in library.
- Priority: P0
- Postconditions: Post is absent from DB; related views no longer find it.

---

# Insights (Highlights + Reflections)

### Test ID: AL-FUNC-038
- Title: Create insight by highlighting text — happy path
- Preconditions: Logged in; post exists; no insight exists for the selected snippet.
- Steps:
  1. On a post page, select a short text span.
  2. Click the floating “Save to Insights” button.
- Expected Result: Request succeeds; page reloads (or updates) and the selected text is highlighted in golden yellow.
- Priority: P0
- Postconditions: New insight row exists for current user and post.

### Test ID: AL-FUNC-039
- Title: Create insight — validation for empty highlight
- Preconditions: Logged in.
- Steps:
  1. POST to `/insights/add` with `{ "post_id": <id>, "highlighted_text": "" }`.
- Expected Result: HTTP 400 JSON with `error: "No text"`.
- Priority: P2
- Postconditions: No insight is created.

### Test ID: AL-FUNC-040
- Title: Insights library page — displays saved highlights
- Preconditions: Logged in; at least one insight exists for current user.
- Steps:
  1. Navigate to `/insights`.
- Expected Result: Insights list shows newest-first; each entry shows highlighted text, category (when available), and associated metadata.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-041
- Title: Update insight “my thoughts” — happy path
- Preconditions: Logged in; at least one insight exists.
- Steps:
  1. Add or edit “my thoughts” for an insight and save.
- Expected Result: API returns `{ ok: true }`; text persists after refresh.
- Priority: P1
- Postconditions: Insight record has updated `my_thoughts`.

### Test ID: AL-FUNC-042
- Title: Delete insight — happy path
- Preconditions: Logged in; at least one insight exists.
- Steps:
  1. Delete an insight from `/insights`.
- Expected Result: API returns `{ ok: true }`; the insight disappears from the list; highlight no longer appears on the post after refresh.
- Priority: P1
- Postconditions: Insight row deleted for current user.

---

# AI Quick Summary (Per-Post)

### Test ID: AL-FUNC-043
- Title: Quick Summary — validation when API key is missing
- Preconditions: Logged in; `anthropic` available (or not); no API key configured in settings/env.
- Steps:
  1. Click “Quick Insight” / “Quick Summary” on a post card or post page.
- Expected Result: UI indicates an error; API returns HTTP 400 JSON `error: "No API key configured"` (or a 500 if AI package missing).
- Priority: P1
- Postconditions: No insight created.

### Test ID: AL-FUNC-044
- Title: Quick Summary — happy path and Save to Insights
- Preconditions: Logged in; Anthropic API key configured; at least one post exists.
- Steps:
  1. Trigger quick summary for a post.
  2. Confirm a summary panel appears with generated text.
  3. Click “Save to Insights”.
- Expected Result: Summary is generated; saving returns `{ ok: true, id: <insight_id> }` and navigates to `/insights#insight-<id>`.
- Priority: P0
- Postconditions: New insight exists containing the summary text.

### Test ID: AL-FUNC-045
- Title: Save summary — validation: empty summary rejected
- Preconditions: Logged in; post exists.
- Steps:
  1. POST to `/save-summary/<post_id>` with `{ "summary": "" }`.
- Expected Result: HTTP 400 JSON `error: "No summary provided"`.
- Priority: P2
- Postconditions: No insight created.

### Test ID: AL-FUNC-046
- Title: Save summary — alternative: duplicate summary returns existing ID
- Preconditions: Logged in; an identical summary insight already exists for the same post.
- Steps:
  1. POST to `/save-summary/<post_id>` with the same `summary` text.
- Expected Result: API returns `{ ok: true, message: "Summary already saved", id: <existing_id> }`.
- Priority: P3
- Postconditions: No duplicate insight created.

---

# AI Insights (Aggregate Analysis + History)

### Test ID: AL-FUNC-047
- Title: AI Insights page loads and shows history + prompt
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/ai-insights`.
- Expected Result: Page displays saved insights list and analysis history; indicates whether API key is set; prompt area is visible.
- Priority: P1
- Postconditions: None.

### Test ID: AL-FUNC-048
- Title: Save Anthropic API key — happy path
- Preconditions: Logged in; valid API key available.
- Steps:
  1. Save API key on AI Insights page (or POST to `/ai-insights/save-key` with `{ api_key: "..." }`).
- Expected Result: API returns `{ ok: true }`; UI indicates key is set.
- Priority: P1
- Postconditions: Key persists across page refresh for that user (unless env var overrides).

### Test ID: AL-FUNC-049
- Title: Delete Anthropic API key — happy path
- Preconditions: Logged in; API key previously saved in DB (not only via env var).
- Steps:
  1. Click delete key (or POST to `/ai-insights/delete-key`).
- Expected Result: API returns `{ ok: true }`; page indicates key is not set.
- Priority: P2
- Postconditions: DB setting removed for current user.

### Test ID: AL-FUNC-050
- Title: Save custom therapist prompt — happy path
- Preconditions: Logged in.
- Steps:
  1. Save a non-empty custom prompt (or POST to `/ai-insights/save-prompt`).
- Expected Result: API returns `{ ok: true }`; prompt persists on refresh.
- Priority: P2
- Postconditions: Setting stored for current user.

### Test ID: AL-FUNC-051
- Title: Analyze — validation: no insights saved
- Preconditions: Logged in; current user has zero insights.
- Steps:
  1. Trigger analysis on `/ai-insights`.
- Expected Result: HTTP 400 JSON `error: "No insights saved yet. Highlight text on any post first."`
- Priority: P1
- Postconditions: No analysis history created.

### Test ID: AL-FUNC-052
- Title: Analyze — happy path creates analysis history entry
- Preconditions: Logged in; current user has at least 1 insight; Anthropic package installed; API key set.
- Steps:
  1. Trigger analysis with default prompt.
  2. Wait for completion.
- Expected Result: API returns JSON with `analysis` text and `analysis_id`; analysis appears in history list on refresh.
- Priority: P0
- Postconditions: `ai_analyses` contains a new row for current user.

### Test ID: AL-FUNC-053
- Title: Analyze — alternative flow with “current feelings” included
- Preconditions: Same as AL-FUNC-052.
- Steps:
  1. Enter non-empty “current feelings”.
  2. Trigger analysis.
- Expected Result: Analysis completes successfully; result reflects inclusion of the current context.
- Priority: P2
- Postconditions: Analysis history entry stored.

### Test ID: AL-FUNC-054
- Title: Analysis feedback save — happy path
- Preconditions: Logged in; an analysis exists in history for current user.
- Steps:
  1. Submit feedback text for the analysis (or POST to `/ai-insights/<id>/feedback`).
- Expected Result: API returns `{ ok: true }`; feedback is displayed/persisted on refresh.
- Priority: P2
- Postconditions: `ai_analyses.feedback` updated for current user’s analysis.

### Test ID: AL-FUNC-055
- Title: Delete analysis — happy path
- Preconditions: Logged in; an analysis exists for current user.
- Steps:
  1. Delete the analysis from history (or POST to `/ai-insights/<id>/delete`).
- Expected Result: API returns `{ ok: true }`; analysis disappears from history on refresh.
- Priority: P2
- Postconditions: Analysis row deleted for current user.

### Test ID: AL-FUNC-056
- Title: AI Insights history search — happy path
- Preconditions: Logged in; at least two analyses exist with distinct text or feedback.
- Steps:
  1. Search on `/ai-insights?q=<term>`.
- Expected Result: Only matching history entries display; insights list remains visible.
- Priority: P3
- Postconditions: None.

---

# Modeled Posts (AI-generated Derek Hart voice)

### Test ID: AL-FUNC-057
- Title: Modeled posts page loads
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/modeled-posts`.
- Expected Result: Page renders; shows any saved modeled posts; shows topic suggestions; indicates API availability.
- Priority: P2
- Postconditions: None.

### Test ID: AL-FUNC-058
- Title: Generate modeled post — validation: missing topic
- Preconditions: Logged in; Anthropic package installed; API key set.
- Steps:
  1. Attempt generation with empty topic.
- Expected Result: HTTP 400 JSON `error: "Please enter a topic."`
- Priority: P2
- Postconditions: No modeled post created.

### Test ID: AL-FUNC-059
- Title: Generate modeled post — validation: no library posts to learn style
- Preconditions: Logged in; API key set; posts table is empty.
- Steps:
  1. Attempt to generate a modeled post.
- Expected Result: HTTP 400 JSON `error` indicating to import posts first.
- Priority: P2
- Postconditions: No modeled post created.

### Test ID: AL-FUNC-060
- Title: Generate modeled post — happy path
- Preconditions: Logged in; API key set; at least 1 post exists in library.
- Steps:
  1. Select attachment style and enter a topic.
  2. Generate.
- Expected Result: API returns `{ id, post_text }`; modeled post appears in the saved list after refresh.
- Priority: P1
- Postconditions: New modeled post stored for current user.

### Test ID: AL-FUNC-061
- Title: Modeled post favorite toggle
- Preconditions: Logged in; at least one modeled post exists.
- Steps:
  1. Favorite the modeled post.
  2. Unfavorite it.
- Expected Result: API returns `is_favorite` toggling 1/0; UI reflects state.
- Priority: P3
- Postconditions: Favorite state stored for modeled post.

### Test ID: AL-FUNC-062
- Title: Modeled post delete
- Preconditions: Logged in; at least one modeled post exists.
- Steps:
  1. Delete a modeled post.
- Expected Result: API returns `{ ok: true }`; post disappears from list after refresh.
- Priority: P2
- Postconditions: Modeled post removed for current user.

---

# Stats & Reporting

### Test ID: AL-FUNC-063
- Title: Stats API — `/api/stats` returns totals and category breakdown
- Preconditions: Logged in; posts exist in multiple categories.
- Steps:
  1. Navigate to `/api/stats` in the browser.
- Expected Result: JSON contains `total`, `revised`, and `categories` array with counts.
- Priority: P2
- Postconditions: None.

### Test ID: AL-FUNC-064
- Title: Stats dashboard page loads and renders charts/tables
- Preconditions: Logged in; posts exist.
- Steps:
  1. Navigate to `/stats`.
- Expected Result: Dashboard loads; charts/timeline/top posts appear without JS errors.
- Priority: P2
- Postconditions: None.

---

# Export / Restore Collections

### Test ID: AL-FUNC-065
- Title: Export insights collection — happy path
- Preconditions: Logged in; at least one insight exists for current user.
- Steps:
  1. Navigate to `/export-collection/insights`.
- Expected Result: Browser downloads `insights.json` containing only current user’s insights.
- Priority: P1
- Postconditions: Export file contains expected `collection_type` and `count`.

### Test ID: AL-FUNC-066
- Title: Export AI analyses collection — happy path
- Preconditions: Logged in; at least one analysis exists for current user.
- Steps:
  1. Navigate to `/export-collection/ai-analyses`.
- Expected Result: Browser downloads `ai-analyses.json` containing only current user’s analyses.
- Priority: P2
- Postconditions: Export file contains expected `collection_type` and `count`.

### Test ID: AL-FUNC-067
- Title: Export modeled posts collection — happy path
- Preconditions: Logged in; at least one modeled post exists for current user.
- Steps:
  1. Navigate to `/export-collection/modeled-posts`.
- Expected Result: Browser downloads `modeled-posts.json` containing only current user’s modeled posts.
- Priority: P2
- Postconditions: Export file contains expected `collection_type` and `count`.

### Test ID: AL-FUNC-068
- Title: Export collection — validation: unknown type
- Preconditions: Logged in.
- Steps:
  1. Navigate to `/export-collection/unknown`.
- Expected Result: HTTP 400 JSON `error: "Unknown collection type"`.
- Priority: P3
- Postconditions: None.

### Test ID: AL-FUNC-069
- Title: Restore collection — insights happy path with duplicate skipping
- Preconditions: Logged in; an exported `insights.json` exists; at least one insight in the file already exists in DB.
- Steps:
  1. Restore insights via UI (upload) or POST JSON to `/restore-collection/insights`.
- Expected Result: Response indicates items imported and duplicates skipped; no duplicates created.
- Priority: P1
- Postconditions: Only new insights are added for current user.

### Test ID: AL-FUNC-070
- Title: Restore collection — validation: no data provided
- Preconditions: Logged in.
- Steps:
  1. POST `{}` to `/restore-collection/insights`.
- Expected Result: HTTP 400 JSON `error: "No data to restore"`.
- Priority: P2
- Postconditions: No changes.

---

# Backup / Restore Full Database

### Test ID: AL-FUNC-071
- Title: Backup downloads a full JSON backup
- Preconditions: Logged in; posts exist.
- Steps:
  1. Navigate to `/backup`.
- Expected Result: Browser downloads `attachmentlens_backup.json` containing keys: `posts`, `insights`, `ai_analyses`, `modeled_posts`.
- Priority: P1
- Postconditions: Backup file is valid JSON.

### Test ID: AL-FUNC-072
- Title: Restore — validation: missing `posts` key
- Preconditions: Logged in.
- Steps:
  1. POST JSON without `posts` to `/restore`.
- Expected Result: HTTP 400 JSON `error` indicating missing posts key.
- Priority: P1
- Postconditions: No data restored.

### Test ID: AL-FUNC-073
- Title: Restore — happy path imports new posts and attaches prefs for current user
- Preconditions: Logged in; have a valid backup JSON containing posts not currently in DB.
- Steps:
  1. POST the backup JSON to `/restore`.
- Expected Result: Response returns `{ imported, skipped }`; posts appear in library; per-user prefs are created for restored posts.
- Priority: P0
- Postconditions: New posts exist; current user has prefs rows for them.

---

# Danger Zone (Data Clearing)

### Test ID: AL-FUNC-074
- Title: Clear insights — only affects current user
- Preconditions: Logged in as User A; User A has insights; User B has different insights.
- Steps:
  1. As User A, invoke “Clear Insights” (POST `/insights/clear`).
  2. Switch to User B and view `/insights`.
- Expected Result: User A insights cleared; User B insights remain.
- Priority: P0
- Postconditions: `insights` rows removed only for User A.

### Test ID: AL-FUNC-075
- Title: Clear AI analyses — only affects current user
- Preconditions: Logged in; current user has AI analyses.
- Steps:
  1. POST `/ai-insights/clear`.
- Expected Result: API returns `{ cleared: true }`; AI history list becomes empty.
- Priority: P1
- Postconditions: `ai_analyses` rows removed for current user.

### Test ID: AL-FUNC-076
- Title: Clear modeled posts — only affects current user
- Preconditions: Logged in; current user has modeled posts.
- Steps:
  1. POST `/modeled-posts/clear`.
- Expected Result: API returns `{ cleared: true }`; modeled posts list becomes empty.
- Priority: P1
- Postconditions: `modeled_posts` rows removed for current user.

### Test ID: AL-FUNC-077
- Title: Clear posts — destructive and global
- Preconditions: Logged in; posts exist; user acknowledges this clears the shared library.
- Steps:
  1. POST `/posts/clear`.
  2. Navigate to `/`.
- Expected Result: API returns `{ cleared: true }`; library is empty for all users.
- Priority: P0
- Postconditions: `posts` table is empty; dependent views handle empty state.

---

# Bulk Re-Label

### Test ID: AL-FUNC-078
- Title: Bulk label page loads and lists posts
- Preconditions: Logged in; posts exist.
- Steps:
  1. Navigate to `/bulk-label`.
- Expected Result: Page displays a table of posts with category/date fields and bulk actions.
- Priority: P2
- Postconditions: None.

---

# GitHub Integration (Settings + Feature Requests)

### Test ID: AL-FUNC-079
- Title: Save GitHub token — happy path
- Preconditions: Logged in; valid GitHub PAT available.
- Steps:
  1. Save token in Import page GitHub section (or POST to `/settings/github-token`).
- Expected Result: API returns `{ ok: true }`; UI indicates token saved.
- Priority: P1
- Postconditions: Token persists (stored in settings for `user_id=1`).

### Test ID: AL-FUNC-080
- Title: GitHub token test — invalid token alternative flow
- Preconditions: Logged in; an invalid token is saved.
- Steps:
  1. Use “Test token” (POST `/github/test`).
- Expected Result: Response returns `{ ok: false, error: "HTTP ..." }`.
- Priority: P2
- Postconditions: Token remains stored (until deleted).

### Test ID: AL-FUNC-081
- Title: Export posts to GitHub — validation when token missing
- Preconditions: Logged in; no token configured.
- Steps:
  1. Click “Push to GitHub (posts-database.json)” on Import page.
- Expected Result: HTTP 400 JSON error indicating no GitHub token configured.
- Priority: P2
- Postconditions: No GitHub changes made.

### Test ID: AL-FUNC-082
- Title: Feature request — happy path commits to `TODO.md`
- Preconditions: Logged in; valid GitHub token configured; network connectivity available.
- Steps:
  1. Click the 💡 Request button in nav.
  2. Enter a short request and submit.
- Expected Result: API returns `{ ok: true, commit: "<url>" }`; the request appears under “## High Priority” in `TODO.md` on GitHub.
- Priority: P2
- Postconditions: GitHub commit created; local file may remain unchanged.

### Test ID: AL-FUNC-083
- Title: Feature request — validation: empty request
- Preconditions: Logged in.
- Steps:
  1. Submit the feature request form with empty text.
- Expected Result: HTTP 400 JSON `error: "No text provided"`.
- Priority: P3
- Postconditions: No GitHub call made.

---

# Customization & Zoom (UX)

### Test ID: AL-FUNC-084
- Title: Zoom control — persists across refresh
- Preconditions: Logged in.
- Steps:
  1. Use A-/A+ controls to change zoom on any page.
  2. Refresh.
- Expected Result: Content zoom remains at the chosen percentage; display label matches saved level.
- Priority: P3
- Postconditions: `localStorage.zoomIdx` is set.

### Test ID: AL-FUNC-085
- Title: Theme/font customization — persists and applies across pages
- Preconditions: Logged in.
- Steps:
  1. Open customization modal.
  2. Choose a non-default theme and font.
  3. Save.
  4. Navigate to another page (e.g., `/insights`) and refresh.
- Expected Result: Selected theme and font remain applied; UI options show active selection.
- Priority: P3
- Postconditions: `localStorage.custTheme` and `localStorage.custFont` are set; server receives `/settings/customization` POST.

---

# Additional Coverage (Imports, Exports, Bulk Tools)

### Test ID: AL-FUNC-086
- Title: Import classification — keyword-based category assignment
- Preconditions: Logged in; prepare import JSON array containing a post with an “Anxious” keyword (e.g., includes “abandon” and “reassure”) and length >= 30.
- Steps:
  1. Import the JSON via `/import` or `/import_json`.
  2. Open the imported post.
- Expected Result: Post category auto-sets to the matching attachment category (e.g., “Anxious / Preoccupied”) when keywords match; otherwise defaults to “General Relationship”.
- Priority: P2
- Postconditions: Post `category` stored and visible in UI.

### Test ID: AL-FUNC-087
- Title: Import duplicate handling — same `original_text` is not duplicated
- Preconditions: Logged in; a post with specific `original_text` already exists.
- Steps:
  1. Import a payload that includes the same `text` again.
- Expected Result: Import reports the entry as skipped (or updated for `/import_json`); total post count does not increase for duplicates.
- Priority: P1
- Postconditions: Only one post exists with that `original_text`.

### Test ID: AL-FUNC-088
- Title: Export all collections (ZIP) — happy path
- Preconditions: Logged in; current user has at least one insight, analysis, and modeled post.
- Steps:
  1. Trigger “Export All Collections (ZIP)” from `/import` page (or navigate to `/export-all-collections`).
- Expected Result: Browser downloads a ZIP file containing three JSON files (insights, analyses, modeled posts) for the current user.
- Priority: P1
- Postconditions: ZIP can be opened; JSON files are valid.

### Test ID: AL-FUNC-089
- Title: Restore all collections (ZIP) — happy path
- Preconditions: Logged in; an export ZIP from AL-FUNC-088 exists; some items in the ZIP already exist in the DB.
- Steps:
  1. Upload the ZIP using “Restore All (ZIP)” on `/import`.
- Expected Result: API returns `{ ok: true, insights: {imported, skipped}, ai-analyses: {...}, modeled-posts: {...} }`; duplicates are skipped.
- Priority: P1
- Postconditions: Only non-duplicate items are added for current user.

### Test ID: AL-FUNC-090
- Title: Restore all collections (ZIP) — validation: invalid ZIP rejected
- Preconditions: Logged in.
- Steps:
  1. Upload a non-ZIP file (or corrupted ZIP) using “Restore All (ZIP)”.
- Expected Result: HTTP 400 JSON `error: "Invalid ZIP file"` (or a descriptive error).
- Priority: P2
- Postconditions: No collections are modified.

### Test ID: AL-FUNC-091
- Title: Restore AI analyses collection — duplicate skipping
- Preconditions: Logged in; have `ai-analyses.json` export with at least one analysis already present.
- Steps:
  1. Restore via `/restore-collection/ai-analyses`.
- Expected Result: Existing analysis texts are skipped; imported count reflects only new entries.
- Priority: P2
- Postconditions: No duplicate `analysis_text` entries for the same user.

### Test ID: AL-FUNC-092
- Title: Restore modeled posts collection — duplicate skipping
- Preconditions: Logged in; have `modeled-posts.json` export with at least one `post_text` already present for the user.
- Steps:
  1. Restore via `/restore-collection/modeled-posts`.
- Expected Result: Existing `post_text` entries are skipped; imported count reflects only new entries.
- Priority: P2
- Postconditions: No duplicate modeled posts for current user by `post_text`.

### Test ID: AL-FUNC-093
- Title: GitHub token delete — removes stored token
- Preconditions: Logged in; a GitHub token is saved in DB settings.
- Steps:
  1. Delete token via UI or POST `/settings/github-token/delete`.
  2. Attempt `/github/test`.
- Expected Result: Delete returns `{ ok: true }`; token test reports missing token.
- Priority: P2
- Postconditions: No `github_token` setting exists for `user_id=1`.

### Test ID: AL-FUNC-094
- Title: Export posts to GitHub — happy path creates/updates `posts-database.json`
- Preconditions: Logged in; valid GitHub token configured; posts exist.
- Steps:
  1. Trigger “Push to GitHub (posts-database.json)” on `/import`.
- Expected Result: API returns `{ ok: true, count, commit }`; GitHub file `posts-database.json` is created or updated.
- Priority: P2
- Postconditions: GitHub commit exists; exported count matches current DB posts count.

### Test ID: AL-FUNC-095
- Title: Bulk re-label — change category/date for multiple posts (end-to-end)
- Preconditions: Logged in; at least 3 posts exist in different categories/dates.
- Steps:
  1. Navigate to `/bulk-label`.
  2. Select multiple rows and apply a new category.
  3. Apply a date label to the selected rows.
  4. Navigate back to `/` and open one updated post.
- Expected Result: Updated posts show the new category/date in library and on detail page; changes persist on refresh.
- Priority: P2
- Postconditions: Posts have updated `category` and `date_label` values in DB.
