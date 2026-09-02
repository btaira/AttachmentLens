const statusEl = document.getElementById('status');
const notFbEl = document.getElementById('not-fb');
const targetInput = document.getElementById('target');
const scrapeBtn = document.getElementById('scrape-btn');
const importBtn = document.getElementById('import-btn');
const copyBtn = document.getElementById('copy-btn');
const optionsLink = document.getElementById('options-link');

let posts = [];

function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = kind || '';
}

function scaledMaxStale(n) {
  return n <= 100 ? 15 : n <= 300 ? 20 : 30;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function getOptions() {
  const { appUrl, defaultTarget } = await chrome.storage.sync.get(['appUrl', 'defaultTarget']);
  return {
    appUrl: appUrl || 'http://localhost:5000',
    defaultTarget: defaultTarget || 20,
  };
}

(async function init() {
  const opts = await getOptions();
  targetInput.value = opts.defaultTarget;

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

    posts = result || [];
    if (!posts.length) {
      setStatus('No posts found — make sure the profile feed is visible and try again.', 'error');
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
    setStatus('Set a valid AttachmentLens URL in Options first.', 'error');
    return;
  }

  const has = await chrome.permissions.contains({ origins: [origin] });
  if (!has) {
    const granted = await chrome.permissions.request({ origins: [origin] });
    if (!granted) {
      setStatus('Permission denied — can\'t reach ' + base + '.', 'error');
      return;
    }
  }

  importBtn.disabled = true;
  setStatus('Importing to AttachmentLens…');
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
    let msg = `Imported ${data.imported} new posts`;
    if (data.updated) msg += `, updated ${data.updated}`;
    msg += `, ${data.skipped} skipped.`;
    setStatus(msg, 'success');
    await chrome.storage.local.remove(['attachmentLensScrapedPosts', 'attachmentLensScrapedAt', 'attachmentLensScrapeDone']);
  } catch (e) {
    setStatus('Import failed: ' + e.message + ' — is ' + base + ' running and are you logged in?', 'error');
    importBtn.disabled = false;
  }
});

optionsLink.addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});
