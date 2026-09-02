const appUrlEl = document.getElementById('app-url');
const targetEl = document.getElementById('default-target');
const savedEl = document.getElementById('saved');

(async function init() {
  const { appUrl, defaultTarget } = await chrome.storage.sync.get(['appUrl', 'defaultTarget']);
  appUrlEl.value = appUrl || 'http://localhost:5000';
  targetEl.value = defaultTarget || 20;
})();

document.getElementById('save-btn').addEventListener('click', async () => {
  const appUrl = appUrlEl.value.trim().replace(/\/+$/, '') || 'http://localhost:5000';
  const defaultTarget = Math.max(1, Math.min(500, parseInt(targetEl.value, 10) || 20));
  await chrome.storage.sync.set({ appUrl, defaultTarget });
  savedEl.style.display = 'inline';
  setTimeout(() => { savedEl.style.display = 'none'; }, 2000);
});
