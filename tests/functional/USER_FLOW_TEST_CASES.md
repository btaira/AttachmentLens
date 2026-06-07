# AttachmentLens — User Flow Test Cases

**Document Version**: 1.0  
**Last Updated**: 2026-06-07  
**Status**: Active - User flows defined and ready for testing

---

## Overview

This document defines **end-to-end user flow test cases** covering complete workflows through AttachmentLens. Each flow includes:
- Step-by-step progression
- Navigation validation
- Data persistence checks
- Error handling scenarios
- Exit points and cancellation paths

---

## Test Case Numbering Convention

### Format: `UF-FLOWID-STEPID-SCENARIO`

**Examples**:
- `UF-IMPORT-001-HAPPY` - Post Import Flow, step 1, happy path
- `UF-INSIGHTS-002-ERROR` - Insights Creation Flow, step 2, error scenario
- `UF-ANALYSIS-003-CANCEL` - Analysis Flow, step 3, cancellation path

**Components**:
- `UF` - User Flow prefix
- `FLOWID` - Flow identifier (IMPORT, INSIGHTS, ANALYSIS, COLLAB, ORGANIZE, GENERATE, BACKUP)
- `STEPID` - Step number (001-999)
- `SCENARIO` - HAPPY, ERROR, CANCEL, PERSIST, NAV

---

# User Flow 1: Post Import Flow

**Flow ID**: IMPORT  
**Priority**: P0 (Critical)  
**Typical Duration**: 3-5 minutes  
**Key Personas**: Content Curator, Researcher

## Flow Summary
User imports posts from external source (JSON), applies initial categorization, saves to library.

## Step 1: Access Import Page

### UF-IMPORT-001-HAPPY
- **Title**: Navigate to import page
- **Preconditions**: User logged in
- **Steps**:
  1. Click "Import / Update Posts" in navigation
  2. Observe import page loads
- **Expected Result**: Import page displays with textarea, instructions, and copy-to-clipboard script
- **Data Verification**: None (first step)
- **Postconditions**: Ready to paste JSON data

### UF-IMPORT-001-ERROR
- **Title**: Access import page when not authenticated
- **Preconditions**: User logged out
- **Steps**:
  1. Navigate to `/import` directly
- **Expected Result**: Redirect to login page
- **Postconditions**: User remains logged out

## Step 2: Prepare and Validate Import Data

### UF-IMPORT-002-HAPPY
- **Title**: Prepare valid JSON for import
- **Preconditions**: On import page, JSON ready to paste
- **Steps**:
  1. Paste valid JSON array with at least 2 posts
  2. Each post contains `text` field with 30+ characters
  3. Optional fields: `date`, `category`, `tags`
  4. Validate syntax in editor
- **Expected Result**: JSON appears in textarea without errors
- **Data Verification**: 
  - Text field contains pasted JSON
  - Character count visible (if UI shows it)
- **Postconditions**: Ready to submit import

### UF-IMPORT-002-ERROR-INVALID-JSON
- **Title**: Attempt import with invalid JSON
- **Preconditions**: Import page open
- **Steps**:
  1. Paste invalid JSON (e.g., `{`, `[1,2,`, malformed object)
  2. Submit import
- **Expected Result**: Error message "JSON parse error: ..." displayed
- **Postconditions**: No posts imported, user can correct and retry

### UF-IMPORT-002-ERROR-SHORT-TEXT
- **Title**: Attempt import with text < 30 characters
- **Preconditions**: Import page open
- **Steps**:
  1. Paste JSON with post containing `"text": "short"`
  2. Submit import
- **Expected Result**: Post skipped, success message shows "skipped: 1"
- **Postconditions**: Short posts filtered out silently

### UF-IMPORT-002-ERROR-DUPLICATES
- **Title**: Attempt import with duplicate text
- **Preconditions**: Library already contains a post with specific text
- **Steps**:
  1. Prepare import JSON with same text as existing post
  2. Submit import
- **Expected Result**: Duplicate detected, skipped in import
- **Data Verification**: Post count unchanged for duplicates
- **Postconditions**: No duplicate created in DB

## Step 3: Submit Import Request

### UF-IMPORT-003-HAPPY
- **Title**: Successfully submit import
- **Preconditions**: Valid JSON in textarea, ready to submit
- **Steps**:
  1. Click "Import Posts" button
  2. Wait for server response
- **Expected Result**: 
  - Response: `{ imported: N, skipped: M, updated: K }`
  - Success message displayed
  - Redirect to library with query params
- **Data Verification**: 
  - URL contains `?imported=N&skipped=M`
  - New posts visible in library
- **Postconditions**: Posts added to DB, import complete

### UF-IMPORT-003-CANCEL
- **Title**: Cancel import operation
- **Preconditions**: JSON in textarea, before submit
- **Steps**:
  1. Click browser back button or navigate away
  2. Confirm navigation
- **Expected Result**: Import cancelled, no posts imported
- **Postconditions**: No data loss, user back at previous page

## Step 4: Verify Import Results

### UF-IMPORT-004-HAPPY
- **Title**: Verify imported posts appear in library
- **Preconditions**: Import completed, redirected to library
- **Steps**:
  1. Observe library displays new posts
  2. Open one imported post to verify content
  3. Check metadata (category, date if provided)
- **Expected Result**: 
  - All imported posts visible in table
  - Content matches import JSON
  - Default category applied if not specified
- **Data Verification**:
  - Post count increased by `imported` number
  - Text content matches original
  - Category defaults to "General Relationship"
- **Postconditions**: Posts successfully persisted and queryable

### UF-IMPORT-004-DATA-PERSIST
- **Title**: Verify data persists across page navigation
- **Preconditions**: Posts imported and visible
- **Steps**:
  1. Navigate away from library (e.g., to insights)
  2. Return to library
  3. Search for imported post by text
- **Expected Result**: Imported posts still visible
- **Data Verification**: Same posts visible, no data loss
- **Postconditions**: Data persisted in database

## Step 5: Optional - Re-import and Update

### UF-IMPORT-005-HAPPY-UPDATE
- **Title**: Re-import same posts with metadata updates
- **Preconditions**: Posts already imported once, import again with different metadata
- **Steps**:
  1. Prepare new import JSON with same text but different `date` or `likes`
  2. Submit import
- **Expected Result**: Posts updated (not duplicated), metadata refreshed
- **Data Verification**: 
  - Post count unchanged
  - New metadata reflected in library
  - Date updated (if not locked)
- **Postconditions**: Posts updated, not duplicated

---

# User Flow 2: Insights Creation Flow

**Flow ID**: INSIGHTS  
**Priority**: P0 (Critical)  
**Typical Duration**: 5-10 minutes  
**Key Personas**: Reader, Analyst, Student

## Flow Summary
User highlights text in posts, creates insights, adds personal notes, organizes insights library.

## Step 1: Browse Library and Select Post

### UF-INSIGHTS-001-HAPPY
- **Title**: Navigate to post for highlighting
- **Preconditions**: User logged in, library contains posts
- **Steps**:
  1. View library (home page)
  2. Click on a post title to open detail page
- **Expected Result**: Post detail page displays with full text
- **Data Verification**: Post content renders correctly
- **Postconditions**: Ready to highlight

### UF-INSIGHTS-001-ERROR-NO-POSTS
- **Title**: Attempt insights creation when no posts available
- **Preconditions**: User logged in, library empty
- **Steps**:
  1. Navigate to insights page or try to create insight
- **Expected Result**: Message "No posts available. Import posts first."
- **Postconditions**: User guided to import flow

## Step 2: Select Text for Highlighting

### UF-INSIGHTS-002-HAPPY
- **Title**: Select text span in post content
- **Preconditions**: Post detail page open, post content visible
- **Steps**:
  1. Select 5-50 character span of text
  2. Observe floating "Save to Insights" button appears
  3. Click button
- **Expected Result**: Selection captured, ready to save
- **Data Verification**: Selected text displayed in popup/form
- **Postconditions**: Ready to confirm save

### UF-INSIGHTS-002-ERROR-EMPTY-SELECTION
- **Title**: Attempt to save empty selection
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click "Save to Insights" without selecting text
  2. Or submit with empty highlighted_text field
- **Expected Result**: 
  - Error message: "No text selected" or "No text provided"
  - HTTP 400 response
- **Postconditions**: No insight created

### UF-INSIGHTS-002-ERROR-LONG-SELECTION
- **Title**: Attempt to save very long text selection
- **Preconditions**: Post detail page open with large post
- **Steps**:
  1. Select 5000+ characters
  2. Attempt to save
- **Expected Result**: Either accepted (if no limit) or truncated with warning
- **Postconditions**: Insight created with appropriate text

## Step 3: Add Personal Thoughts to Insight

### UF-INSIGHTS-003-HAPPY
- **Title**: Add personal notes to saved insight
- **Preconditions**: Insight created, on insights page
- **Steps**:
  1. Find created insight in list
  2. Click "Edit thoughts" or similar
  3. Enter personal note (e.g., "This relates to attachment theory")
  4. Save thoughts
- **Expected Result**: 
  - Thoughts saved with insight
  - Displayed when viewing insight
- **Data Verification**: 
  - `my_thoughts` field updated in DB
  - Persists on page refresh
- **Postconditions**: Insight enriched with personal context

### UF-INSIGHTS-003-CANCEL
- **Title**: Cancel editing thoughts
- **Preconditions**: On insight edit form
- **Steps**:
  1. Enter thoughts but click cancel/back
- **Expected Result**: Changes discarded
- **Postconditions**: Original thoughts (if any) unchanged

## Step 4: Navigate and View Insights Library

### UF-INSIGHTS-004-HAPPY
- **Title**: View all saved insights
- **Preconditions**: Multiple insights created
- **Steps**:
  1. Navigate to `/insights` page
  2. Observe list of all insights
  3. Check ordering (newest first)
- **Expected Result**: 
  - All user's insights displayed
  - Ordered by creation date (newest first)
  - Text, source post, thoughts visible
- **Data Verification**: 
  - Insight count matches created count
  - Text matches saved selection
- **Postconditions**: None

### UF-INSIGHTS-004-NAV-BACK-TO-POST
- **Title**: Navigate from insight back to source post
- **Preconditions**: Viewing insights list
- **Steps**:
  1. Click insight to view detail
  2. Click "View in Post" or source post link
  3. Return to post detail page
- **Expected Result**: 
  - Post detail page opens
  - Previously highlighted text visually marked
- **Data Verification**: 
  - Correct post displayed
  - Highlight persists visually
- **Postconditions**: User can continue with post

## Step 5: Manage Insights

### UF-INSIGHTS-005-HAPPY-DELETE
- **Title**: Delete an insight
- **Preconditions**: Viewing insights list
- **Steps**:
  1. Find insight to delete
  2. Click delete button
  3. Confirm deletion
- **Expected Result**: 
  - Insight removed from list
  - Highlight removed from post
- **Data Verification**: 
  - Insight row deleted from DB
  - Post's insights count decreased
- **Postconditions**: Insight permanently deleted

### UF-INSIGHTS-005-DATA-PERSIST
- **Title**: Verify insights persist across sessions
- **Preconditions**: Insights created, viewed
- **Steps**:
  1. Navigate away from insights page
  2. Switch users (if multi-user)
  3. Switch back to original user
  4. Return to insights page
- **Expected Result**: Same insights visible
- **Data Verification**: 
  - Per-user isolation maintained
  - No data loss
- **Postconditions**: Per-user isolation confirmed

---

# User Flow 3: AI Analysis Flow

**Flow ID**: ANALYSIS  
**Priority**: P1 (Major)  
**Typical Duration**: 3-5 minutes  
**Key Personas**: Therapist, Analyst, Self-Reflector  
**Prerequisites**: Anthropic API key configured

## Flow Summary
User configures API key, reviews saved insights, triggers AI analysis, receives generated analysis, saves feedback.

## Step 1: Access AI Insights Page and Check API Configuration

### UF-ANALYSIS-001-HAPPY
- **Title**: Navigate to AI Insights page
- **Preconditions**: User logged in
- **Steps**:
  1. Click "AI Insights" in navigation
  2. Observe page loads
- **Expected Result**: Page displays with:
  - API key status indicator
  - List of saved insights
  - Custom prompt textarea
  - Analyze button
- **Data Verification**: None (info page)
- **Postconditions**: Ready to configure or analyze

### UF-ANALYSIS-001-ERROR-NO-KEY
- **Title**: Attempt analysis without API key
- **Preconditions**: AI Insights page, no API key configured
- **Steps**:
  1. Click "Analyze" button without API key
- **Expected Result**: 
  - Error message: "No API key configured"
  - Button disabled or error popup
- **Postconditions**: User prompted to set API key

## Step 2: Configure Anthropic API Key (if needed)

### UF-ANALYSIS-002-HAPPY
- **Title**: Save Anthropic API key
- **Preconditions**: AI Insights page, key not configured
- **Steps**:
  1. Locate API key input field
  2. Paste valid API key
  3. Click "Save API Key"
- **Expected Result**: 
  - Response: `{ ok: true }`
  - UI shows key is set (e.g., "Key configured" indicator)
- **Data Verification**: 
  - Key persisted per user in settings
  - Validated on save (optional basic validation)
- **Postconditions**: Ready to use AI features

### UF-ANALYSIS-002-ERROR-INVALID-KEY
- **Title**: Save invalid API key
- **Preconditions**: AI Insights page, on key input
- **Steps**:
  1. Paste invalid/malformed key
  2. Click "Save API Key"
- **Expected Result**: Either accepted (tested at use time) or basic format validation error
- **Postconditions**: User can retry with valid key

### UF-ANALYSIS-002-ERROR-NO-INSIGHTS
- **Title**: Attempt analysis with no insights saved
- **Preconditions**: API key configured, user has zero insights
- **Steps**:
  1. Click "Analyze" button
- **Expected Result**: 
  - Error: "No insights saved yet. Highlight text on any post first."
  - HTTP 400 response
- **Postconditions**: User guided to create insights

## Step 3: Review Insights Before Analysis

### UF-ANALYSIS-003-HAPPY
- **Title**: View insights that will be analyzed
- **Preconditions**: AI Insights page, insights visible
- **Steps**:
  1. Scroll through insights preview section
  2. Observe all insights to be included in analysis
- **Expected Result**: All user's insights displayed in list
- **Data Verification**: Insight count matches DB
- **Postconditions**: Ready to proceed with analysis

## Step 4: Customize Analysis Prompt (Optional)

### UF-ANALYSIS-004-HAPPY
- **Title**: Provide custom analysis prompt
- **Preconditions**: AI Insights page, API configured
- **Steps**:
  1. Scroll to "Custom Prompt" textarea
  2. Enter custom instruction (e.g., "Focus on attachment patterns")
  3. Leave "Current Feelings" empty initially
- **Expected Result**: Prompt text captured
- **Data Verification**: Text persists in textarea
- **Postconditions**: Ready to analyze with custom context

### UF-ANALYSIS-004-EMPTY
- **Title**: Use default prompt (no customization)
- **Preconditions**: AI Insights page
- **Steps**:
  1. Leave custom prompt empty
  2. Click "Analyze"
- **Expected Result**: Default therapist prompt used
- **Postconditions**: Analysis proceeds with defaults

## Step 5: Trigger Analysis

### UF-ANALYSIS-005-HAPPY
- **Title**: Submit analysis request and receive results
- **Preconditions**: API key set, insights exist
- **Steps**:
  1. (Optional) Enter current feelings
  2. Click "Analyze" button
  3. Wait for API response (5-15 seconds)
- **Expected Result**: 
  - Analysis text generated and displayed
  - New analysis appears in history
  - Response: `{ analysis: "...", analysis_id: 123 }`
- **Data Verification**: 
  - Analysis saved to DB with user_id and timestamp
  - Analysis text reflects insights provided
- **Postconditions**: Analysis complete, ready to review

### UF-ANALYSIS-005-CANCEL
- **Title**: Cancel analysis while in progress
- **Preconditions**: Analysis request submitted, waiting for response
- **Steps**:
  1. Click cancel button or navigate away
- **Expected Result**: Request cancelled, no duplicate analysis created
- **Postconditions**: User can retry

### UF-ANALYSIS-005-ERROR-API-FAIL
- **Title**: Handle API error during analysis
- **Preconditions**: API key invalid or API service down
- **Steps**:
  1. Click "Analyze" with invalid key
  2. Wait for response
- **Expected Result**: 
  - Error message displayed
  - HTTP 400 or 500 with error details
- **Data Verification**: No analysis saved
- **Postconditions**: User can retry with corrected key

## Step 6: Review and Save Analysis

### UF-ANALYSIS-006-HAPPY
- **Title**: Review generated analysis
- **Preconditions**: Analysis displayed
- **Steps**:
  1. Read analysis text
  2. Scroll through full analysis
  3. Review relevance to saved insights
- **Expected Result**: Analysis text readable and coherent
- **Data Verification**: Timestamp shows current time
- **Postconditions**: Ready to save feedback or run new analysis

## Step 7: Provide Feedback on Analysis

### UF-ANALYSIS-007-HAPPY
- **Title**: Add feedback to analysis
- **Preconditions**: Analysis displayed
- **Steps**:
  1. Scroll to feedback section
  2. Enter feedback (e.g., "Insightful, focuses on core issue")
  3. Click "Save Feedback"
- **Expected Result**: 
  - Feedback saved
  - Response: `{ ok: true }`
  - Feedback persists on refresh
- **Data Verification**: 
  - `feedback` field updated in DB
  - Displayed with analysis
- **Postconditions**: Feedback recorded for future reference

### UF-ANALYSIS-007-CANCEL
- **Title**: Clear feedback without saving
- **Preconditions**: On feedback form
- **Steps**:
  1. Enter feedback
  2. Click cancel or navigate away
- **Expected Result**: Feedback not saved
- **Postconditions**: Original analysis unchanged

## Step 8: View Analysis History

### UF-ANALYSIS-008-HAPPY
- **Title**: Navigate through analysis history
- **Preconditions**: Multiple analyses created
- **Steps**:
  1. Scroll down to "Analysis History"
  2. Click on different analyses in list
  3. View each analysis and feedback
- **Expected Result**: 
  - History displays all analyses
  - Newest first
  - Each shows timestamp, text, feedback
- **Data Verification**: 
  - Analysis count matches DB
  - Ordering correct
- **Postconditions**: None

### UF-ANALYSIS-008-NAV-MANAGE
- **Title**: Delete or manage historical analysis
- **Preconditions**: Viewing analysis history
- **Steps**:
  1. Find analysis to delete
  2. Click delete button
  3. Confirm deletion
- **Expected Result**: 
  - Analysis removed from history
  - Response: `{ ok: true }`
- **Data Verification**: Analysis deleted from DB
- **Postconditions**: History updated

---

# User Flow 4: Multi-User Collaboration Flow

**Flow ID**: COLLAB  
**Priority**: P1 (Major)  
**Typical Duration**: 5-10 minutes  
**Key Personas**: Admin, Team Lead, Individual User

## Flow Summary
Admin creates users, manages user switching, verifies per-user data isolation.

## Step 1: Admin Accesses User Management

### UF-COLLAB-001-HAPPY
- **Title**: Navigate to user switcher in navigation
- **Preconditions**: User logged in
- **Steps**:
  1. Look for user menu in top navigation (username button)
  2. Click on user menu
- **Expected Result**: Dropdown shows current user and list of other users
- **Data Verification**: User list displayed with all created users
- **Postconditions**: Ready to switch users

## Step 2: Create New Test User

### UF-COLLAB-002-HAPPY
- **Title**: Register new user for testing
- **Preconditions**: Logged out or on registration page
- **Steps**:
  1. Click "Register" or navigate to `/register`
  2. Enter new username (e.g., "testuser2")
  3. Enter password (4+ characters)
  4. Click "Register"
- **Expected Result**: 
  - New user created
  - Auto-logged in
  - Redirected to home page
- **Data Verification**: 
  - New user appears in user switcher
  - Empty library (no posts for new user)
- **Postconditions**: New user ready for testing

### UF-COLLAB-002-ERROR-DUPLICATE
- **Title**: Attempt to create user with duplicate username
- **Preconditions**: User "testuser1" already exists
- **Steps**:
  1. Register with username "testuser1"
  2. Submit
- **Expected Result**: Error "Username already taken"
- **Postconditions**: No duplicate created

## Step 3: Switch Between Users

### UF-COLLAB-003-HAPPY
- **Title**: Switch to different user
- **Preconditions**: Logged in as User A, other users exist
- **Steps**:
  1. Click user menu (username button)
  2. Select User B from list
  3. Confirm switch
- **Expected Result**: 
  - Session switches to User B
  - Username in nav updates to User B
  - Library shows User B's posts
- **Data Verification**: 
  - Session user_id changed
  - Per-user data (favorites, insights) reflects User B
- **Postconditions**: User B now active

### UF-COLLAB-003-NAV-BACK
- **Title**: Switch back to original user
- **Preconditions**: Switched to User B
- **Steps**:
  1. Click user menu
  2. Select User A from list
- **Expected Result**: 
  - Session switches back to User A
  - User A's data restored
- **Data Verification**: User A's favorites/insights visible again
- **Postconditions**: User A active again

## Step 4: Verify Data Isolation

### UF-COLLAB-004-HAPPY-POSTS
- **Title**: Verify posts are global (not per-user)
- **Preconditions**: Two users created, posts imported
- **Steps**:
  1. As User A, view library
  2. Note post count and specific posts
  3. Switch to User B
  4. View library
- **Expected Result**: 
  - Both users see same posts
  - Same post counts
- **Data Verification**: Post IDs identical for both users
- **Postconditions**: Posts are shared, not user-specific

### UF-COLLAB-004-HAPPY-FAVORITES
- **Title**: Verify favorites are per-user
- **Preconditions**: Two users, same posts visible
- **Steps**:
  1. As User A, favorite a post
  2. Note favorite count or visual indicator
  3. Switch to User B
  4. Check same post
- **Expected Result**: 
  - Post NOT favorited for User B
  - User A still sees it favorited (after switching back)
- **Data Verification**: 
  - Favorite records per-user in DB
  - `is_favorite` differs by user
- **Postconditions**: Favorites isolated per-user

### UF-COLLAB-004-HAPPY-INSIGHTS
- **Title**: Verify insights are per-user
- **Preconditions**: Two users, posts with highlights available
- **Steps**:
  1. As User A, create insight from post highlight
  2. Go to insights page
  3. Switch to User B
  4. Go to insights page
- **Expected Result**: 
  - User A sees their insight
  - User B sees empty insights list
- **Data Verification**: 
  - Insight records linked to user_id
  - User isolation enforced in queries
- **Postconditions**: Insights isolated per-user

### UF-COLLAB-004-HAPPY-ANALYSES
- **Title**: Verify AI analyses are per-user
- **Preconditions**: Two users, analyses created
- **Steps**:
  1. As User A, run analysis
  2. Check analysis history
  3. Switch to User B
  4. Check analysis history
- **Expected Result**: 
  - User B's analysis history empty (or contains only User B's analyses)
  - User A's analyses not visible to User B
- **Data Verification**: Analysis records filtered by user_id
- **Postconditions**: Analyses isolated per-user

### UF-COLLAB-004-HAPPY-MODELED-POSTS
- **Title**: Verify modeled posts are per-user
- **Preconditions**: Two users, modeled posts created
- **Steps**:
  1. As User A, generate modeled post
  2. View modeled posts list
  3. Switch to User B
  4. View modeled posts list
- **Expected Result**: 
  - User A sees their modeled post
  - User B's list empty
- **Data Verification**: Modeled posts filtered by user_id
- **Postconditions**: Modeled posts isolated

## Step 5: Verify Read/Unread State Isolation

### UF-COLLAB-005-HAPPY
- **Title**: Verify read state is per-user
- **Preconditions**: Two users, same posts
- **Steps**:
  1. As User A, mark a post as read
  2. Switch to User B
  3. Check same post's read status
- **Expected Result**: 
  - Post NOT marked read for User B
  - User A still sees it as read (after switching back)
- **Data Verification**: `is_read` differs by user in preferences
- **Postconditions**: Read state isolated per-user

## Step 6: Test Invalid User Switch

### UF-COLLAB-006-ERROR
- **Title**: Attempt to switch to non-existent user
- **Preconditions**: On user menu
- **Steps**:
  1. Attempt to POST to `/switch-user/999999`
  2. Or try to select invalid user
- **Expected Result**: 
  - Switch fails gracefully
  - Remain on current user
  - Error message or no-op
- **Postconditions**: User unchanged, no crash

---

# User Flow 5: Post Organization Flow

**Flow ID**: ORGANIZE  
**Priority**: P1 (Major)  
**Typical Duration**: 10-15 minutes  
**Key Personas**: Librarian, Organizer, Content Manager

## Flow Summary
User imports posts, applies metadata (category, date, tags), organizes library with filters and search, and manages post states.

## Step 1: Import Posts

### UF-ORGANIZE-001-HAPPY
- **Title**: Import initial set of posts
- **Preconditions**: User logged in
- **Steps**:
  1. Navigate to import page
  2. Paste JSON with 5+ posts
  3. Submit import
- **Expected Result**: Posts imported successfully
- **Data Verification**: New posts visible in library
- **Postconditions**: Posts ready for organization

(See User Flow 1: Post Import Flow for detailed import test cases)

## Step 2: Apply Initial Categorization

### UF-ORGANIZE-002-HAPPY-AUTO-CATEGORIZE
- **Title**: Posts auto-categorized based on keywords
- **Preconditions**: Posts imported
- **Steps**:
  1. View library
  2. Observe categories of imported posts
  3. Open a post to check category field
- **Expected Result**: 
  - Posts with attachment keywords auto-categorized
  - Example: text containing "anxious abandon reassure" → "Anxious / Preoccupied"
  - Posts without matches → "General Relationship"
- **Data Verification**: Category field set per post
- **Postconditions**: Initial categorization complete

### UF-ORGANIZE-002-HAPPY-MANUAL-UPDATE
- **Title**: Manually update post category
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click category field
  2. Select different category from dropdown
  3. Click save
- **Expected Result**: 
  - Category updated in DB
  - Library view reflects change
  - Response: `{ ok: true, category: "..." }`
- **Data Verification**: 
  - Category field updated in DB
  - Persists on page refresh
- **Postconditions**: Post recategorized

## Step 3: Apply Date Labels

### UF-ORGANIZE-003-HAPPY
- **Title**: Add date label to posts
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click date input field
  2. Enter date (e.g., "June 01, 2026")
  3. Click save
- **Expected Result**: 
  - Date saved to post
  - Displays on post card
  - Latest posts ordered by date
- **Data Verification**: 
  - Date locked for future imports
  - Persists on refresh
- **Postconditions**: Post dated

### UF-ORGANIZE-003-PERSIST
- **Title**: Verify date lock prevents overwrite on re-import
- **Preconditions**: Post with date label saved
- **Steps**:
  1. Re-import same post with different `date` field
  2. Check post detail
- **Expected Result**: Date unchanged (locked)
- **Data Verification**: `date_label_locked` flag is true
- **Postconditions**: Date protected from overwrite

## Step 4: Add Tags to Posts

### UF-ORGANIZE-004-HAPPY
- **Title**: Add tags to categorize posts by topic
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click tags field
  2. Enter tags (e.g., ["family", "parent", "communication"])
  3. Save
- **Expected Result**: 
  - Tags saved with post
  - Displayed as chips/badges
  - Searchable
- **Data Verification**: 
  - Tags array stored in DB
  - Persists on refresh
- **Postconditions**: Post tagged

### UF-ORGANIZE-004-CLEAR
- **Title**: Remove tags from post
- **Preconditions**: Post has tags
- **Steps**:
  1. Open tags field
  2. Clear all tags or remove specific ones
  3. Save
- **Expected Result**: 
  - Tags removed
  - Display cleared
- **Data Verification**: Tags array empty in DB
- **Postconditions**: Post untagged

## Step 5: Use Library Filters and Search

### UF-ORGANIZE-005-HAPPY-SEARCH
- **Title**: Search library by text
- **Preconditions**: Library with multiple posts
- **Steps**:
  1. Click search box on home page
  2. Enter search term (e.g., "attachment", "family")
  3. Press enter or click search button
- **Expected Result**: 
  - Library filtered to matching posts only
  - Search term highlighted in results (optional)
  - Search term persists in box
- **Data Verification**: Only posts with matching text displayed
- **Postconditions**: Results shown

### UF-ORGANIZE-005-HAPPY-CATEGORY-FILTER
- **Title**: Filter posts by category
- **Preconditions**: Library with posts in multiple categories
- **Steps**:
  1. Click category in sidebar
  2. View filtered results
- **Expected Result**: 
  - Only posts in selected category displayed
  - Category highlighted/active in sidebar
- **Data Verification**: Category filter applied correctly
- **Postconditions**: Category view shown

### UF-ORGANIZE-005-HAPPY-SORT
- **Title**: Sort posts by different criteria
- **Preconditions**: Library loaded
- **Steps**:
  1. Click "Sort by" dropdown
  2. Select "Newest" → observe order by date descending
  3. Select "Oldest" → observe order by date ascending
  4. Select "Popularity" → observe order by likes/comments
  5. Refresh page
- **Expected Result**: 
  - Posts reorder instantly
  - Selected sort persists after refresh (localStorage)
- **Data Verification**: Correct order maintained across pages
- **Postconditions**: Library sorted

### UF-ORGANIZE-005-HAPPY-READ-FILTER
- **Title**: Filter posts by read status
- **Preconditions**: Some posts marked read, others unread
- **Steps**:
  1. Click "Read" filter chip
  2. Observe only read posts displayed
  3. Click "Unread" chip
  4. Observe only unread posts displayed
  5. Click "All" chip
  6. Observe all posts displayed
- **Expected Result**: 
  - Filters applied client-side without server call
  - No page reload
- **Data Verification**: Correct posts visible per filter
- **Postconditions**: Filter applied

## Step 6: Mark Posts as Read/Unread

### UF-ORGANIZE-006-HAPPY
- **Title**: Toggle read status on post
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click "Mark as Read" button
  2. Observe status change
  3. Click again to mark unread
- **Expected Result**: 
  - Status toggles visually
  - API updates: `{ is_read: 1 }` then `{ is_read: 0 }`
  - Library view reflects status (visual indicator)
  - Persists on refresh
- **Data Verification**: 
  - `is_read` field toggled in DB (per-user)
  - Status in library matches
- **Postconditions**: Read state tracked

## Step 7: Bulk Organization (Optional Advanced)

### UF-ORGANIZE-007-HAPPY-BULK
- **Title**: Apply metadata to multiple posts at once
- **Preconditions**: Posts selected in bulk label page
- **Steps**:
  1. Navigate to bulk-label page
  2. Select multiple posts
  3. Apply category to selection
  4. Apply date to selection
  5. Save
- **Expected Result**: 
  - All selected posts updated
  - Changes visible in library
- **Data Verification**: Metadata applied to all selected
- **Postconditions**: Bulk operation complete

## Step 8: Organize with Favorites

### UF-ORGANIZE-008-HAPPY
- **Title**: Use favorites to organize important posts
- **Preconditions**: Post detail page open
- **Steps**:
  1. Click favorite/star icon
  2. Post added to favorites
  3. Navigate to home page
  4. Check "Latest 5 Favorites" section
- **Expected Result**: 
  - Post appears in favorites section (if in top 5)
  - Visual indication (star filled)
- **Data Verification**: 
  - Favorite state per-user in DB
  - Displayed in library
- **Postconditions**: Post favorited

---

# User Flow 6: AI Generation Flow

**Flow ID**: GENERATE  
**Priority**: P2 (Normal)  
**Typical Duration**: 3-5 minutes  
**Key Personas**: Creative Writer, Therapist, Content Creator  
**Prerequisites**: Anthropic API key configured, posts in library

## Flow Summary
User generates AI-written posts in personal style, saves to modeled posts, manages collection.

## Step 1: Access Modeled Posts Page

### UF-GENERATE-001-HAPPY
- **Title**: Navigate to modeled posts page
- **Preconditions**: User logged in
- **Steps**:
  1. Click "AI Generation" or similar in navigation
  2. Or navigate to `/modeled-posts`
- **Expected Result**: Page loads with:
  - Topic input field
  - Style selection (attachment style)
  - List of saved modeled posts
  - Generate button
- **Data Verification**: Page renders without errors
- **Postconditions**: Ready to generate

### UF-GENERATE-001-ERROR-NO-KEY
- **Title**: Attempt generation without API key
- **Preconditions**: Modeled posts page, no API key
- **Steps**:
  1. Click "Generate" button
- **Expected Result**: 
  - Error: "No API key configured"
  - Directed to set API key
- **Postconditions**: User prompted to configure key

### UF-GENERATE-001-ERROR-NO-POSTS
- **Title**: Attempt generation with no library posts
- **Preconditions**: Library empty
- **Steps**:
  1. Try to generate post
- **Expected Result**: 
  - Error: "No posts in library. Import posts first to learn your style."
- **Postconditions**: User guided to import

## Step 2: Choose Generation Style

### UF-GENERATE-002-HAPPY
- **Title**: Select attachment style for generation
- **Preconditions**: Modeled posts page, API configured
- **Steps**:
  1. Click style dropdown
  2. Select attachment style (e.g., "Anxious / Preoccupied")
  3. Observe description
- **Expected Result**: Style selected and displayed
- **Data Verification**: Style choice captured
- **Postconditions**: Ready to enter topic

## Step 3: Enter Topic and Generate

### UF-GENERATE-003-HAPPY
- **Title**: Generate post on specific topic
- **Preconditions**: Style selected
- **Steps**:
  1. Click topic input
  2. Enter topic (e.g., "managing conflict in relationships")
  3. Click "Generate"
  4. Wait for response (10-30 seconds)
- **Expected Result**: 
  - Generated post text displayed
  - Response: `{ id: N, post_text: "..." }`
  - New post appears in saved list
- **Data Verification**: 
  - Modeled post saved to DB with user_id
  - Contains user's attachment style
  - Related to entered topic
- **Postconditions**: Post generated and saved

### UF-GENERATE-003-ERROR-EMPTY-TOPIC
- **Title**: Attempt generation without topic
- **Preconditions**: Style selected
- **Steps**:
  1. Leave topic field empty
  2. Click "Generate"
- **Expected Result**: 
  - Error: "Please enter a topic."
  - HTTP 400 response
- **Postconditions**: No post generated

### UF-GENERATE-003-CANCEL
- **Title**: Cancel generation in progress
- **Preconditions**: Generation submitted, waiting
- **Steps**:
  1. Click cancel button or navigate away
- **Expected Result**: Request cancelled, no post created
- **Postconditions**: Can retry generation

### UF-GENERATE-003-ERROR-API-FAIL
- **Title**: Handle API error during generation
- **Preconditions**: API key invalid
- **Steps**:
  1. Attempt generation
- **Expected Result**: 
  - Error message with API details
  - HTTP 500 or similar
- **Data Verification**: No modeled post created
- **Postconditions**: User can retry with fixed key

## Step 4: Review Generated Post

### UF-GENERATE-004-HAPPY
- **Title**: Review and read generated post
- **Preconditions**: Post generated and displayed
- **Steps**:
  1. Read generated text
  2. Evaluate quality and relevance
  3. Review tone and style match
- **Expected Result**: Generated text readable and coherent
- **Data Verification**: Text matches requested topic
- **Postconditions**: Ready to save or regenerate

## Step 5: Manage Modeled Posts

### UF-GENERATE-005-HAPPY-FAVORITE
- **Title**: Favorite a modeled post
- **Preconditions**: Viewing modeled posts list
- **Steps**:
  1. Click favorite/star on a modeled post
  2. Observe status change
- **Expected Result**: 
  - Post marked as favorite
  - Visual indicator updated
- **Data Verification**: Favorite flag set per-user
- **Postconditions**: Post favorited

### UF-GENERATE-005-HAPPY-DELETE
- **Title**: Delete a modeled post
- **Preconditions**: Viewing modeled posts list
- **Steps**:
  1. Find modeled post to delete
  2. Click delete button
  3. Confirm deletion
- **Expected Result**: 
  - Post removed from list
  - Response: `{ ok: true }`
- **Data Verification**: Post deleted from DB
- **Postconditions**: Modeled post removed

### UF-GENERATE-005-DATA-PERSIST
- **Title**: Verify modeled posts persist across sessions
- **Preconditions**: Modeled posts generated and saved
- **Steps**:
  1. Navigate away from page
  2. Return to modeled posts page
  3. Check list
- **Expected Result**: Same posts visible
- **Data Verification**: All posts recovered from DB
- **Postconditions**: Data persisted

---

# User Flow 7: Export and Backup Flow

**Flow ID**: BACKUP  
**Priority**: P1 (Major)  
**Typical Duration**: 5-10 minutes  
**Key Personas**: Data Manager, Archivist, Backup Admin

## Flow Summary
User exports collections (insights, analyses, modeled posts), backs up full database, and restores from backup if needed.

## Step 1: Access Export Page

### UF-BACKUP-001-HAPPY
- **Title**: Navigate to import/export page (collections)
- **Preconditions**: User logged in
- **Steps**:
  1. Navigate to `/import` page (contains export section)
  2. Or navigate to dedicated export page
- **Expected Result**: Export options visible
- **Data Verification**: None (info page)
- **Postconditions**: Ready to export

## Step 2: Export Insights Collection

### UF-BACKUP-002-HAPPY
- **Title**: Export insights as JSON
- **Preconditions**: User has insights saved
- **Steps**:
  1. Click "Export Insights" button
  2. Observe download starts
- **Expected Result**: 
  - File downloaded: `insights.json` or `insights-YYYY-MM-DD.json`
  - File contains JSON array of insights
  - Only current user's insights included
- **Data Verification**: 
  - JSON parses correctly
  - Insight count matches
  - User_id filtering applied
- **Postconditions**: Export complete

### UF-BACKUP-002-ERROR-NO-DATA
- **Title**: Attempt to export with no insights
- **Preconditions**: User has no insights
- **Steps**:
  1. Click "Export Insights"
- **Expected Result**: 
  - Error or empty file
  - Message: "No insights to export"
- **Postconditions**: No file downloaded (or empty)

## Step 3: Export AI Analyses Collection

### UF-BACKUP-003-HAPPY
- **Title**: Export analyses as JSON
- **Preconditions**: User has analyses saved
- **Steps**:
  1. Click "Export AI Analyses" button
  2. Observe download
- **Expected Result**: 
  - File: `ai-analyses.json`
  - Contains analyses with timestamp, text, feedback
  - Per-user only
- **Data Verification**: 
  - All analyses included
  - User isolation maintained
- **Postconditions**: Export complete

## Step 4: Export Modeled Posts Collection

### UF-BACKUP-004-HAPPY
- **Title**: Export modeled posts as JSON
- **Preconditions**: User has modeled posts
- **Steps**:
  1. Click "Export Modeled Posts" button
  2. Observe download
- **Expected Result**: 
  - File: `modeled-posts.json`
  - Contains generated posts with metadata
- **Data Verification**: All posts included
- **Postconditions**: Export complete

## Step 5: Export All Collections as ZIP

### UF-BACKUP-005-HAPPY
- **Title**: Export all collections in single ZIP file
- **Preconditions**: User has insights, analyses, modeled posts
- **Steps**:
  1. Click "Export All Collections (ZIP)"
  2. Observe download
- **Expected Result**: 
  - File: `collections-YYYY-MM-DD.zip`
  - Contains 3 JSON files (insights, analyses, modeled-posts)
  - Per-user data only
- **Data Verification**: 
  - ZIP opens successfully
  - All 3 files present
  - Each file valid JSON
- **Postconditions**: Export complete

## Step 6: Full Database Backup

### UF-BACKUP-006-HAPPY
- **Title**: Back up entire database
- **Preconditions**: User logged in
- **Steps**:
  1. Click "Full Backup" or `/backup`
  2. Observe download
- **Expected Result**: 
  - File: `attachmentlens_backup.json`
  - Contains keys: `posts`, `insights`, `ai_analyses`, `modeled_posts`
  - All shared data included (posts, etc.)
  - All user's per-user data included
- **Data Verification**: 
  - JSON valid
  - All collections present
  - Data count matches expectations
- **Postconditions**: Backup available

## Step 7: Restore from Collection Export

### UF-BACKUP-007-HAPPY-RESTORE-INSIGHTS
- **Title**: Restore insights from export file
- **Preconditions**: Export file available, new user or clean state
- **Steps**:
  1. Navigate to restore section
  2. Upload or paste insights.json
  3. Click "Restore Insights"
- **Expected Result**: 
  - Insights imported
  - Response: `{ ok: true, insights: { imported: N, skipped: M } }`
  - Insights appear in insights page
- **Data Verification**: 
  - Per-user restoration (current user)
  - Duplicates skipped
  - Count matches expectations
- **Postconditions**: Insights restored

### UF-BACKUP-007-HAPPY-RESTORE-ALL-ZIP
- **Title**: Restore all collections from ZIP file
- **Preconditions**: ZIP file available
- **Steps**:
  1. Navigate to restore section
  2. Upload ZIP file
  3. Click "Restore All (ZIP)"
- **Expected Result**: 
  - All collections imported
  - Response: `{ ok: true, insights: {...}, ai_analyses: {...}, modeled_posts: {...} }`
  - All data visible in respective pages
- **Data Verification**: 
  - All collections restored
  - Duplicates handled
  - Per-user restoration applied
- **Postconditions**: Full restoration complete

### UF-BACKUP-007-ERROR-INVALID-ZIP
- **Title**: Attempt to restore invalid ZIP
- **Preconditions**: Non-ZIP or corrupted file available
- **Steps**:
  1. Upload invalid ZIP
  2. Click restore
- **Expected Result**: 
  - Error: "Invalid ZIP file"
  - HTTP 400 response
- **Data Verification**: No data restored
- **Postconditions**: User can retry with valid file

## Step 8: Full Database Restore

### UF-BACKUP-008-HAPPY
- **Title**: Restore full database from backup file
- **Preconditions**: Backup JSON file available
- **Steps**:
  1. Navigate to restore page
  2. Upload attachmentlens_backup.json
  3. Click "Restore Full Backup"
- **Expected Result**: 
  - All data restored
  - Response: `{ imported: N, skipped: M }`
  - Posts visible in library for current user
  - Per-user prefs created for all posts
- **Data Verification**: 
  - Post count matches backup
  - User can view restored posts
  - Favorites/read state preserved if included
- **Postconditions**: Database restored

### UF-BACKUP-008-ERROR-MISSING-POSTS
- **Title**: Attempt to restore backup with missing posts key
- **Preconditions**: Invalid backup file (no posts)
- **Steps**:
  1. Upload file without "posts" key
  2. Click restore
- **Expected Result**: 
  - Error: "Invalid backup file. Missing 'posts' key."
  - HTTP 400 response
- **Data Verification**: No data imported
- **Postconditions**: User must provide valid backup

## Step 9: Data Integrity After Restore

### UF-BACKUP-009-HAPPY-PERSIST
- **Title**: Verify restored data persists
- **Preconditions**: Data restored
- **Steps**:
  1. Navigate away from restore page
  2. Return to library/insights/etc.
  3. Verify data still present
  4. Close browser and reopen
  5. Verify data still exists
- **Expected Result**: All data persists
- **Data Verification**: 
  - No data loss on navigation
  - No data loss on session close/reopen
- **Postconditions**: Data integrity confirmed

---

## Test Execution Guidelines

### Running User Flow Tests

1. **Sequence**: Execute flows in order (IMPORT → INSIGHTS → ANALYSIS, etc.)
2. **State Management**: Each flow can start fresh or build on previous state
3. **Data**: Use consistent test data across related flows
4. **Documentation**: Log results per test case with evidence

### Test Report Format

For each user flow test:
- Run ID: `UF-FLOWID-RUNDATE`
- Example: `UF-IMPORT-20260607`
- Include: Start time, end time, test case count, pass/fail count
- Document any issues with screenshots/logs if available

### Architecture for Future Expansion

**Adding New User Flows**:
1. Choose unique FLOW ID (e.g., `SCHEDULE`, `REPORT`)
2. Follow UF-FLOWID-STEPID-SCENARIO numbering
3. Create section in this document
4. Define all steps with HAPPY, ERROR, NAV, PERSIST, CANCEL scenarios
5. Update test reports to include new flow category

**Test Categories in Reports**:
```markdown
## User Flow Test Results

### [Category] - N/N PASS
- Flow 1 ✓
- Flow 2 ✓
- ...
```

---

## Summary

**Total User Flows**: 7  
**Total Test Scenarios**: 70+  
**Categories**:
1. Post Import Flow (5 steps, 10+ scenarios)
2. Insights Creation Flow (5 steps, 11+ scenarios)
3. AI Analysis Flow (8 steps, 12+ scenarios)
4. Multi-User Collaboration (6 steps, 11+ scenarios)
5. Post Organization Flow (8 steps, 13+ scenarios)
6. AI Generation Flow (5 steps, 10+ scenarios)
7. Export & Backup Flow (9 steps, 14+ scenarios)

**Architecture**: Extensible with clear naming conventions for adding flows

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-07  
**Status**: Ready for testing
