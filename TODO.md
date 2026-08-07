# AttachmentLens — Feature Roadmap

**See [ROADMAP_ENHANCED.md](ROADMAP_ENHANCED.md) for the full 6-month vision and strategic direction.**

---

## 🚀 SPRINT NOW (Next 2 Weeks) — Quick Wins

- [ ] **Keyboard shortcuts** — `j`/`k` navigate posts, `f` favorite, `m` mark read, `h` highlight mode
- [ ] **Post preview tooltips** — Hover over post title to see first 2-3 sentences
- [ ] **Infinite scroll on library** — Load 50 posts at a time (replace pagination)
- [ ] **Color-coded highlights** — Different colors per category (anxious→red, avoidant→blue, secure→green)
- [ ] **Quick Insight button** — One-click "Generate Insight" on any post card
- [ ] **Single post PDF export** — Download any post as PDF with annotations

---

## 🔥 NEXT SPRINT (Weeks 3-6) — Game-Changers

### Therapeutic Exports (High Priority)
- [ ] **PDF Batch Export with TOC**
  - Export insights collection (all, by category, by date range)
  - Table of contents, pretty formatting
  - Include metadata: category, date, reflection

- [ ] **Therapist Session Packet**
  - One-click export: favorites + insights + analyses
  - Structured PDF for therapy discussion
  - Progress summary included

### Analytics & Growth Tracking
- [ ] **Attachment Style Progress Chart** — Weekly category breakdown over time
- [ ] **Insight Evolution Timeline** — Interactive timeline of insights created
- [ ] **Growth Metrics Dashboard** — Insights/week trend, categories explored %, read ratio
- [ ] **Pattern Detection** — Most common themes, emotional triggers, category co-occurrence

### Smart Features
- [ ] **Smart Recommendations** — "Based on your insights, these posts match your patterns"
- [ ] **Emotion Tracking** — Rate mood 1-5 when creating insights; mood heatmap calendar
- [ ] **Email Insight to Therapist** — One-click email with metadata

---

## 📱 PHASE 3 (Weeks 7-10) — Mobile + Collaboration

### Mobile Experience
- [ ] **Responsive Mobile Layout** — Mobile-first redesign
- [ ] **Progressive Web App (PWA)** — Installable, offline-first, push notifications
- [ ] **Mobile Annotation** — Touch-optimized highlight, voice note reflections

### Therapist Collaboration (Consent-Based)
- [ ] **Share Insight URL** — Generate read-only shareable link to insight
- [ ] **Invite Therapist** — Secure token-based invite, granular permissions
- [ ] **Discussion Thread** — Add notes/feedback per insight
- [ ] **Session Notes Integration** — Attach notes from therapy sessions

### Advanced AI
- [ ] **Personal AI Coach** — Chat interface for pattern questions
- [ ] **Daily Reflection Prompt** — Customizable time, contextual suggestions

---

## 🌟 PHASE 4 (Months 4-6) — Community & Intelligence

### Community Learning (Opt-In, Anonymized)
- [ ] **Guided Modules** — "Understanding Your Anxious Side", attachment curriculum
- [ ] **Peer Discussion** — Moderated comments on posts, study circles
- [ ] **Community Insights** — Anonymized aggregated patterns (research-ready)

### Intelligent Search & Discovery
- [ ] **Semantic Search** — "Posts about fear of abandonment" (embedding-based)
- [ ] **Relationship Map** — Interactive graph of themes and connections
- [ ] **Predictive Patterns** — ML confidence scores on post classification

### Integrations
- [ ] **Calendar Sync** — Mark therapy sessions, milestones
- [ ] **Fitness Tracker Integration** — Correlate stress (Oura/Apple Watch) with reading
- [ ] **Note App Bridge** — Sync insights to Obsidian/Roam/OneNote (bi-directional)

---

## 💎 PREMIUM FEATURES (6+ Months)

### Voice, Video, Gamification
- [ ] **Voice Journaling** — Record reflections, Whisper transcription, audio library
- [ ] **Insight Streaks** — Track days with insights, badges, leaderboards
- [ ] **Attachment Growth Quest** — Narrative-driven quests, character progression
- [ ] **AI Companion** — Proactive check-ins, celebrates breakthroughs

### Professional Tools (Licensed Therapists)
- [ ] **Therapist Dashboard** — Multi-client progress view (with consent)
- [ ] **Clinical Protocols** — Attachment-focused CBT worksheets, EFT exercises
- [ ] **Outcome Measurement** — GAD-7, PCL-5 integrations, progress scales

### Native Apps
- [ ] **React Native Mobile App** — iOS + Android, offline-first, biometric unlock
- [ ] **Apple Watch Integration** — Mood check-in complications, reading streak

---

## 🏗️ Technical Infrastructure (Parallel)

- [ ] **Database Optimization** — Indexes on user_id, post_id, date_label
- [ ] **Caching Layer** — Redis for insights/analyses
- [ ] **Search Engine** — Elasticsearch for semantic search
- [ ] **Async Processing** — Celery + Redis for AI, PDF generation
- [ ] **Error Monitoring** — Sentry integration
- [ ] **Analytics** — Privacy-preserving event tracking (Plausible)
- [ ] **API Documentation** — Prepare for mobile app integration

---

## ✅ ALREADY BUILT

### Core Functionality
- [x] Import posts via Facebook console scraper
- [x] Attachment style auto-classifier (keyword-based)
- [x] Post detail with edit/personalize/word diff
- [x] Highlight text and save as insights
- [x] AI-powered pattern analysis (Claude)
- [x] AI analysis history with feedback tracking
- [x] AI Modeled Posts (posts in Derek Hart's style)
- [x] Favorites with home page display
- [x] Read/Unread toggle and filtering
- [x] Multi-tag support per post
- [x] Bulk re-label tool (category + date assignment)
- [x] Full-text search across library

### User Experience
- [x] Multi-user support with login/register
- [x] Per-user favorites, insights, analyses, modeled posts
- [x] User switcher dropdown in nav
- [x] Admin role for user management
- [x] Session persistence across app restarts
- [x] Dark theme with 6 customizable background themes
- [x] 3 font families, 3 font sizes (all persist)
- [x] Zoom levels (80-200%)
- [x] Sticky nav with admin dropdown
- [x] Responsive design (desktop/tablet)

### Organization & Tracking
- [x] Latest 5 posts sorted by date (not import order)
- [x] Latest 5 favorites displayed in grid (newest left)
- [x] Like counts on post cards
- [x] Like/comment metrics captured and sortable
- [x] Post dates captured from Facebook; manual edit with lock
- [x] Bulk date assignment for multiple posts
- [x] Date range filtering in library
- [x] Category confidence and boundary-case flagging
- [x] Stats dashboard with charts (category breakdown, read/unread, import timeline, top posts)
- [x] Static dates (locked after manual set or import)

### Data Management
- [x] Backup & restore (full database JSON export/import)
- [x] Personal collections download/restore (ZIP: insights, analyses, modeled posts)
- [x] Export all collections ZIP (one-click backup/restore)
- [x] Per-user data clearing (danger zone)
- [x] Duplicate detection on restore (skip existing insights)

### GitHub Integration
- [x] Feature request button (💡 Request)
- [x] Request modal with PR title/description
- [x] GitHub PAT storage and validation
- [x] Feature requests committed to TODO.md
- [x] Settings page for API management

### UI Refinements
- [x] Floating "Save to Insights" button on text selection
- [x] Golden highlight (#c8a200) for saved insights
- [x] Category badges with attachment style colors
- [x] "Read" / "Unread" status badges
- [x] Revised/personalized post badge
- [x] Popularity metrics in cards
- [x] Mobile-optimized sort/filter bars

### Recent Fixes & Polish
- [x] Read/unread toggle working reliably (database commit fix)
- [x] Insights save persisting correctly (database transaction fix)
- [x] Restore function separating post data from user preferences (no schema errors)
- [x] Favorites section displaying like post cards with like counts
- [x] All endpoints using proper try/finally transaction handling

---

## 📌 Backlog Notes

- **Browser Extension Scraper:** Facebook DOM changes in May 2026 broke timestamp extraction; browser extension can intercept network requests for reliable dates
- **Duplicate Detection:** Flag near-duplicates before import (same text, different formatting)
- **Comment Count Accuracy:** High-engagement posts collapse counts; investigate full count via post URL
- **Semantic Search:** Embed posts with small model; search by meaning not keywords
- **Therapist Export Pack:** Multi-format (PDF, Markdown, JSON) with structured templates
- **Mobile App:** React Native for iOS/Android with offline-first sync and biometric unlock
- **Community Features:** Moderated discussion, study circles, anonymized insights library

---

## 🎯 Success Metrics

Track these to validate feature impact:
- Daily active users, insights created/week, sessions/week
- Average reflection length, insights before first analysis
- Category coverage %, mood trend improvement
- PDF exports sent, therapist collaborations active
- Keyboard shortcut adoption %, feature request volume

---

**For detailed strategic roadmap, see [ROADMAP_ENHANCED.md](ROADMAP_ENHANCED.md) — covers 6-month vision, technical architecture, and phased rollout plan.**

Made with care for self-reflection and healing. 💜

- [ ] **[Requested by admin, 2026-08-07]** did this work
