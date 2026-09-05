# AttachmentLens Post Importer (Chrome extension)

Replaces the "copy script → paste into DevTools console → copy console command →
paste into Import page" workflow with a popup: click **Scrape Recent Posts** on
a Facebook profile tab, then **Import to AttachmentLens**.

## Install (unpacked)

1. Go to `chrome://extensions`, enable **Developer mode** (top right).
2. Click **Load unpacked**, select this `extension/` folder.
3. Click the extension icon → **Options**, and set:
   - **AttachmentLens URL** — where your app runs (`http://localhost:5000` by
     default; change this if you're using Docker on a different port or a
     deployed URL).
   - **Default posts to scrape**.

## Use

1. Open the Facebook profile to scrape, log in to AttachmentLens in another
   tab (the extension reuses that browser session — no separate login step).
2. Click the extension icon, adjust the post count if needed, click
   **Scrape Recent Posts**. Leave the Facebook tab open until it finishes —
   large scrapes (100+ posts) take a few minutes since Facebook has to be
   scrolled and given time to load each batch.
3. Click **Import to AttachmentLens** to send the results straight to the
   app's `/import_json` endpoint (same dedupe/update logic as the manual
   paste flow). First time importing to a given URL, Chrome will ask you to
   grant the extension permission to reach it. On success, any open
   AttachmentLens tab is automatically reloaded so the new posts show up
   without a manual refresh.
4. **Copy JSON** is there as a fallback if you'd rather paste into the
   Import page manually (e.g. the app isn't reachable from this browser).

If the popup is closed mid-scrape, the in-progress results are saved to
`chrome.storage.local` — reopening the popup picks them up (marked
"interrupted" if the scrape didn't finish) so nothing is lost.

## How it works

`scraper-fn.js` is the same DOM-scraping logic as the console script embedded
in `templates/import.html`, adapted to run via
[`chrome.scripting.executeScript`](https://developer.chrome.com/docs/extensions/reference/api/scripting)
instead of being pasted into DevTools. It returns the collected posts to the
popup rather than copying JSON to the clipboard itself. The console-paste
method in the Import page still works and remains the fallback if you'd
rather not install an extension.

## Files

- `manifest.json` — MV3 manifest. Requests `https://www.facebook.com/*` up
  front; the AttachmentLens app origin is requested at runtime via
  `optional_host_permissions`, since that URL is user-configured.
- `popup.html` / `popup.js` — the toolbar popup UI and orchestration.
- `options.html` / `options.js` — stores `appUrl` / `defaultTarget` in
  `chrome.storage.sync`.
- `scraper-fn.js` — the scraper, injected into the Facebook tab.
