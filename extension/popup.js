const statusEl = document.getElementById('status');
const notFbEl = document.getElementById('not-fb');
const targetInput = document.getElementById('target');
const scrapeBtn = document.getElementById('scrape-btn');
const importBtn = document.getElementById('import-btn');
const copyBtn = document.getElementById('copy-btn');
const optionsLink = document.getElementById('options-link');
const fbLink = document.getElementById('fb-link');
const appLink = document.getElementById('app-link');
const importResultEl = document.getElementById('import-result');

let posts = [];

function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = kind || '';
}

function setImportResult(text, kind) {
  importResultEl.textContent = text;
  importResultEl.className = kind || '';
  importResultEl.style.display = text ? 'block' : 'none';
}

function setBadge(text, color) {
  try {
    chrome.action.setBadgeText({ text });
    if (color) chrome.action.setBadgeBackgroundColor({ color });
  } catch (e) {}
}

function scaledMaxStale(n) {
  return n <= 100 ? 15 : n <= 300 ? 20 : 30;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function getOptions() {
  const { appUrl, defaultTarget, facebookUrl } = await chrome.storage.sync.get(['appUrl', 'defaultTarget', 'facebookUrl']);
  return {
    appUrl: appUrl || 'http://localhost:5000',
    defaultTarget: defaultTarget || 20,
    facebookUrl: facebookUrl || 'https://www.facebook.com/derek.michael.hart',
  };
}

(async function init() {
  const opts = await getOptions();
  targetInput.value = opts.defaultTarget;
  fbLink.href = opts.facebookUrl;
  appLink.href = opts.appUrl;

  const tab = await getActiveTab();
  const onFacebook = !!tab?.url && /^https:\/\/www\.facebook\.com\//.test(tab.url);
  notFbEl.style.display = onFacebook ? 'none' : 'block';
  scrapeBtn.disabled = !onFacebook;

  const stored = await chrome.storage.local.get([
    'attachmentLensScrapedPosts', 'attachmentLensScrapedAt', 'attachmentLensScrapeDone',
  ]);
  if (stored.attachmentLensScrapedPosts?.length) {
    posts = stored.attachmentLensScrapedPosts;
    importBtn.disabled = false;
    copyBtn.disabled = false;
    const ageMin = Math.round((Date.now() - (stored.attachmentLensScrapedAt || 0)) / 60000);
    const doneNote = stored.attachmentLensScrapeDone ? '' : ' (scrape was interrupted)';
    setStatus(`Loaded ${posts.length} posts from ${ageMin}m ago${doneNote}.`);
  }
})();

chrome.runtime.onMessage.addListener((msg) => {
  if (msg?.type === 'attachmentlens-progress') {
    setStatus(`Scraping… ${msg.collected}/${msg.target} posts found`);
  }
});

scrapeBtn.addEventListener('click', async () => {
  const target = Math.max(1, Math.min(500, parseInt(targetInput.value, 10) || 20));
  const maxStale = scaledMaxStale(target);

  scrapeBtn.disabled = true;
  importBtn.disabled = true;
  copyBtn.disabled = true;
  setImportResult('');
  setBadge('');
  setStatus('Scraping… this can take a minute or two. Keep this tab open.');

  try {
    const tab = await getActiveTab();
    if (!tab?.url || !/^https:\/\/www\.facebook\.com\//.test(tab.url)) {
      throw new Error('Switch to a Facebook profile tab first.');
    }

    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: scrapeFacebookPosts,
      args: [target, 7000, maxStale],
    });

    const diag = result?.diag;
    posts = result?.posts || [];
    if (!posts.length) {
      let msg = 'No posts found.';
      if (diag) {
        msg += ` Checked ${diag.rounds} scroll round(s); DOM matches — comment-preview: ${diag.commentPreviewCount}, ad-preview: ${diag.adPreviewCount}, role=article: ${diag.articleRoleCount}.`;
        if (diag.commentPreviewCount === 0 && diag.adPreviewCount === 0 && diag.articleRoleCount === 0) {
          msg += ' Facebook may not have finished loading the feed — wait a moment and try again.';
        } else {
          msg += ' Facebook\'s post markup may have changed — this needs an update to the scraper selectors.';
        }
      }
      console.log('AttachmentLens scrape diagnostics:', diag);
      setStatus(msg, 'error');
    } else {
      setStatus(`Done — ${posts.length} posts scraped.`, 'success');
      importBtn.disabled = false;
      copyBtn.disabled = false;
    }
  } catch (e) {
    setStatus('Scrape failed: ' + e.message, 'error');
  } finally {
    scrapeBtn.disabled = false;
  }
});

copyBtn.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(posts));
    setStatus(`Copied ${posts.length} posts as JSON.`, 'success');
  } catch (e) {
    setStatus('Copy failed: ' + e.message, 'error');
  }
});

importBtn.addEventListener('click', async () => {
  const opts = await getOptions();
  const base = opts.appUrl.replace(/\/+$/, '');
  let origin;
  try {
    origin = new URL(base).origin + '/*';
  } catch (e) {
    setImportResult('Set a valid AttachmentLens URL in Options first.', 'error');
    return;
  }

  const has = await chrome.permissions.contains({ origins: [origin] });
  if (!has) {
    const granted = await chrome.permissions.request({ origins: [origin] });
    if (!granted) {
      setImportResult('Permission denied — can\'t reach ' + base + '.', 'error');
      return;
    }
  }

  importBtn.disabled = true;
  setImportResult('⏳ Importing to AttachmentLens…');
  setBadge('…', '#9aa0aa');
  try {
    const resp = await fetch(base + '/import_json', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ json_data: JSON.stringify(posts) }),
    });
    const data = await resp.json();
    if (!resp.ok || data.error) {
      throw new Error(data.error || `HTTP ${resp.status}`);
    }
    let msg = `✅ Imported ${data.imported} new posts`;
    if (data.updated) msg += `, updated ${data.updated}`;
    msg += `, ${data.skipped} skipped.`;
    setImportResult(msg, 'success');
    setBadge('✓', '#2e7d52');
    await chrome.storage.local.remove(['attachmentLensScrapedPosts', 'attachmentLensScrapedAt', 'attachmentLensScrapeDone']);

    // Reload any open AttachmentLens tabs so the new posts show up without
    // a manual refresh (a tab opened before the import shows a stale
    // server-rendered snapshot otherwise).
    try {
      const tabs = await chrome.tabs.query({ url: origin });
      await Promise.all(tabs.filter(t => t.id != null).map(t => chrome.tabs.reload(t.id)));
    } catch (e) {}
  } catch (e) {
    setImportResult('❌ Import failed: ' + e.message + ' — is ' + base + ' running and are you logged in?', 'error');
    setBadge('!', '#c0392b');
    importBtn.disabled = false;
  }
});

optionsLink.addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});
