const appUrlEl = document.getElementById('app-url');
const targetEl = document.getElementById('default-target');
const fbUrlEl = document.getElementById('facebook-url');
const savedEl = document.getElementById('saved');

(async function init() {
  const { appUrl, defaultTarget, facebookUrl } = await chrome.storage.sync.get(['appUrl', 'defaultTarget', 'facebookUrl']);
  appUrlEl.value = appUrl || 'http://localhost:5000';
  targetEl.value = defaultTarget || 20;
  fbUrlEl.value = facebookUrl || 'https://www.facebook.com/derek.michael.hart';
})();

document.getElementById('save-btn').addEventListener('click', async () => {
  const appUrl = appUrlEl.value.trim().replace(/\/+$/, '') || 'http://localhost:5000';
  const defaultTarget = Math.max(1, Math.min(500, parseInt(targetEl.value, 10) || 20));
  const facebookUrl = fbUrlEl.value.trim() || 'https://www.facebook.com/derek.michael.hart';
  await chrome.storage.sync.set({ appUrl, defaultTarget, facebookUrl });
  savedEl.style.display = 'inline';
  setTimeout(() => { savedEl.style.display = 'none'; }, 2000);
});
