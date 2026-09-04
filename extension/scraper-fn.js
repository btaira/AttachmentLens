// Injected into the Facebook tab via chrome.scripting.executeScript.
// Must be fully self-contained — no references to anything outside this
// function body, since Chrome serializes it and re-runs it in the page.
// Ported from templates/import.html's console scraper script; the only
// behavioral difference is the ending (returns the array instead of
// copying it to the clipboard) and periodic progress messages.
async function scrapeFacebookPosts(TARGET, SCROLL_WAIT, MAX_STALE) {
  let collected = [], seen = new Set(), staleRounds = 0;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const diag = {
    url: location.href,
    readyState: document.readyState,
    commentPreviewCount: 0,
    adPreviewCount: 0,
    articleRoleCount: 0,
    bodiesFoundLastRound: 0,
    rounds: 0,
  };

  const report = (partial) => {
    try {
      chrome.runtime.sendMessage({
        type: 'attachmentlens-progress',
        collected: collected.length,
        target: TARGET,
      });
    } catch (e) {}
    if (partial) {
      try {
        chrome.storage.local.set({
          attachmentLensScrapedPosts: collected,
          attachmentLensScrapedAt: Date.now(),
          attachmentLensScrapeDone: false,
        });
      } catch (e) {}
    }
  };

  async function expandSeeMore() {
    [...document.querySelectorAll('[role="button"]')]
      .filter(el => el.innerText?.trim() === 'See more')
      .forEach(btn => { try { btn.click(); } catch (e) {} });
    await wait(1500);
  }

  // Walk up N levels from el to reach the post container.
  function getPostScope(el, levels = 5) {
    let n = el;
    for (let i = 0; i < levels && n.parentElement; i++) n = n.parentElement;
    return n;
  }

  function resolveRelativeDate(rel) {
    if (!rel) return '';
    const now = new Date();
    const s = rel.trim();

    if (/^(just\s*now|now)$/i.test(s)) return fmtDate(now);

    let m = s.match(/^(\d+)\s*m$/i);
    if (m) return fmtDate(new Date(now - parseInt(m[1]) * 60000));

    m = s.match(/^(\d+)\s*h$/i);
    if (m) return fmtDate(new Date(now - parseInt(m[1]) * 3600000));

    m = s.match(/^(\d+)\s*d$/i);
    if (m) return fmtDate(new Date(now - parseInt(m[1]) * 86400000));

    m = s.match(/^(\d+)\s*w$/i);
    if (m) return fmtDate(new Date(now - parseInt(m[1]) * 604800000));

    m = s.match(/^(\d+)\s*y$/i);
    if (m) return fmtDate(new Date(now - parseInt(m[1]) * 31536000000));

    if (/^yesterday$/i.test(s)) return fmtDate(new Date(now - 86400000));

    const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayIdx = DAYS.findIndex(d => new RegExp('^' + d, 'i').test(s));
    if (dayIdx >= 0) {
      const diff = (now.getDay() - dayIdx + 7) % 7 || 7;
      return fmtDate(new Date(now - diff * 86400000));
    }

    return s;
  }

  function fmtDate(d) {
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  function isLikelyDate(str) {
    if (!str) return false;
    const s = str.toLowerCase().trim();
    const datePatterns = /\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b|\d{1,2}[,\s]\s*\d{4}|\d{1,2}\s*(days?|hours?|minutes?|seconds?|weeks?|months?|years?)|\b(yesterday|today|tomorrow)\b/i;
    if (/^[A-Z][a-z]+\s+[A-Z][a-z]+$/.test(str) && !/\d/.test(str)) return false;
    if (/^(marketplace|home|feed|share|comment|like|love|post)$/i.test(s)) return false;
    return datePatterns.test(str);
  }

  function parseKM(s) {
    s = (s || '').replace(/,/g, '').trim();
    if (/[Kk]$/.test(s)) return Math.round(parseFloat(s) * 1000);
    if (/[Mm]$/.test(s)) return Math.round(parseFloat(s) * 1000000);
    return parseInt(s) || 0;
  }

  function getPostBodies() {
    diag.commentPreviewCount = document.querySelectorAll('[data-ad-comet-preview="message"]').length;
    diag.adPreviewCount = document.querySelectorAll('[data-ad-preview="message"]').length;
    diag.articleRoleCount = document.querySelectorAll('[role="article"]').length;

    let nodes = [...document.querySelectorAll('[data-ad-comet-preview="message"]')]
      .filter(n => !n.parentElement?.closest('[data-ad-comet-preview="message"]'));
    if (nodes.length === 0)
      nodes = [...document.querySelectorAll('[data-ad-preview="message"]')]
        .filter(n => !n.parentElement?.closest('[data-ad-preview="message"]'));
    if (nodes.length === 0) {
      nodes = [...document.querySelectorAll('[role="article"]')]
        .map(art => art.querySelector('[dir="auto"]'))
        .filter(Boolean);
    }
    diag.bodiesFoundLastRound = nodes.length;
    return nodes;
  }

  function harvest() {
    for (let body of getPostBodies()) {
      if (collected.length >= TARGET) break;
      [...body.querySelectorAll('[role="button"]')]
        .filter(el => el.innerText?.trim() === 'See more')
        .forEach(btn => { try { btn.click(); } catch (e) {} });

      const artScope = getPostScope(body, 5);
      let postUrl = '', dateLabel = '';

      const TS_PAT = /^(just\s*now|now|\d+\s*[smhdwy]|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i;

      let allLinks = [...artScope.querySelectorAll('a[href]')];
      let tsLnk = null;

      for (let scopeLevel = 5; scopeLevel <= 30; scopeLevel += 10) {
        tsLnk = null;
        if (scopeLevel === 5) {
          allLinks = [...artScope.querySelectorAll('a[href]')];
        } else if (scopeLevel === 15) {
          allLinks = [...getPostScope(body, 15).querySelectorAll('a[href]')];
        } else {
          allLinks = [...document.querySelectorAll('a[href]')];
        }

        tsLnk = allLinks.find(a => {
          const attr = (a.getAttribute('title') || a.getAttribute('aria-label') || '').trim();
          return attr.length > 0 && attr.length <= 30 && TS_PAT.test(attr);
        });
        if (tsLnk) break;

        tsLnk = allLinks.find(a => {
          try {
            const t = (a.innerText || '').replace(/[^\x20-\x7E]/g, '').replace(/\s+/g, ' ').trim();
            return t.length > 0 && t.length <= 25 && TS_PAT.test(t);
          } catch (e) { return false; }
        });
        if (tsLnk) break;

        tsLnk = allLinks.find(a => a.getAttribute('data-utime'));
        if (tsLnk) break;

        tsLnk = allLinks.find(a => {
          const href = (a.href || '');
          return /\/story\.php|[?&]fbid=|\d{13,}/.test(href);
        });
        if (tsLnk) break;
      }

      if (tsLnk) {
        postUrl = tsLnk.href;
        let titleAttr = tsLnk.getAttribute('title') || tsLnk.getAttribute('aria-label') || '';
        const relText = (tsLnk.innerText || '').replace(/\s+/g, ' ').trim();
        const utime = tsLnk.getAttribute('data-utime');

        if (titleAttr && TS_PAT.test(titleAttr)) {
          const candidate = resolveRelativeDate(titleAttr) || titleAttr;
          if (isLikelyDate(candidate)) dateLabel = candidate;
        }
        if (!dateLabel && relText && TS_PAT.test(relText)) {
          const candidate = resolveRelativeDate(relText) || relText;
          if (isLikelyDate(candidate)) dateLabel = candidate;
        }
        if (!dateLabel && utime) {
          const ts = parseInt(utime) * 1000;
          const now = Date.now();
          if (ts > 1420000000000 && ts <= now + 86400000) {
            dateLabel = fmtDate(new Date(ts));
          }
        }
      }

      if (!dateLabel) {
        const FULL_DATE_RE = /\b(january|february|march|april|may|june|july|august|september|october|november|december)\b.{1,6}\d{1,2}.{0,4}\d{4}/i;
        const now = Date.now();
        let candidates = [];

        for (const el of document.querySelectorAll('[data-utime]')) {
          const ts = parseInt(el.getAttribute('data-utime')) * 1000;
          if (ts > 1420000000000 && ts <= now + 86400000) {
            candidates.push({ el, date: fmtDate(new Date(ts)) });
          }
        }
        for (const el of document.querySelectorAll('time[datetime]')) {
          const val = el.getAttribute('datetime') || '';
          const d = new Date(val);
          if (!isNaN(d) && d.getFullYear() > 2010) {
            candidates.push({ el, date: fmtDate(d) });
          }
        }
        for (const el of document.querySelectorAll('[aria-label],[title]')) {
          const v = el.getAttribute('aria-label') || el.getAttribute('title') || '';
          if (FULL_DATE_RE.test(v)) {
            const clean = v.replace(/\s+at\s+\d{1,2}:\d{2}\s*(AM|PM)?/i, '').trim();
            candidates.push({ el, date: clean });
          }
        }

        if (candidates.length) {
          let closestDist = Infinity, closestDate = '';
          for (const { el, date } of candidates) {
            let dist = 0, n = body, found = false;
            while (n && dist <= 20) {
              if (n === el) {
                found = true;
                if (dist < closestDist) { closestDist = dist; closestDate = date; }
                break;
              }
              n = n.parentElement;
              dist++;
            }
          }
          if (closestDate) dateLabel = closestDate;
        }
      }

      if (!dateLabel) {
        const FULL_DATE_RE = /\b(january|february|march|april|may|june|july|august|september|october|november|december)\b.{1,6}\d{1,2}.{0,4}\d{4}/i;
        if (postUrl && FULL_DATE_RE.test(postUrl)) {
          const match = postUrl.match(FULL_DATE_RE);
          if (match) dateLabel = match[0];
        }
        if (!dateLabel) {
          const expandedScope = getPostScope(body, 8);
          for (const el of expandedScope.querySelectorAll('*')) {
            if (el.children.length > 0) continue;
            const text = (el.innerText || '').trim();
            if (text.length > 50) continue;
            if (FULL_DATE_RE.test(text)) {
              dateLabel = text.match(FULL_DATE_RE)[0];
              break;
            }
          }
        }
      }

      if (!postUrl) {
        const PERMALINK_RE = /\/(posts|permalink|story_fbid|videos|photos|events)[\/?]/i;
        for (const a of artScope.querySelectorAll('a[href]')) {
          const h = a.href || '';
          if (PERMALINK_RE.test(h) && !h.includes('comment_id')) { postUrl = h; break; }
        }
      }
      if (!postUrl) {
        for (const a of artScope.querySelectorAll('a[href]')) {
          const h = a.href || '';
          if (h && !h.includes(location.pathname.split('/')[1] || ' ') && h.startsWith('https://www.facebook.com')) {
            postUrl = h; break;
          }
        }
      }

      const key = postUrl || body.innerText?.trim().substring(0, 60);
      if (seen.has(key)) continue;
      seen.add(key);

      // Facebook keeps the collapsed-preview text in the DOM (hidden) after
      // "See more" expands the full text, so [dir="auto"] often yields BOTH
      // renders of the same post back to back — plus the "See more"/"See
      // less" toggle label itself as its own paragraph. Drop toggle labels
      // outright, and drop any paragraph whose text already appeared earlier
      // in this post (longer ones only, so short repeated-for-emphasis
      // lines like "Breathe." aren't mistaken for the same bug).
      const paras = [...body.querySelectorAll('[dir="auto"]')]
        .map(el => el.innerText?.trimEnd() ?? '');
      const seenParas = new Set();
      const deduped = [];
      for (let i = 0; i < paras.length; i++) {
        const t = paras[i];
        if (t === '') { deduped.push(t); continue; }
        if (t === paras[i - 1]) continue; // original adjacent-duplicate check
        if (/^see (more|less)$/i.test(t.trim())) continue;
        const key = t.trim().toLowerCase().replace(/\s+/g, ' ');
        if (t.length > 25 && seenParas.has(key)) continue;
        if (t.length > 25) seenParas.add(key);
        deduped.push(t);
      }
      const text = deduped.join('\n\n').replace(/(\n\n){3,}/g, '\n\n\n').trim();
      if (!text || text.length < 30) continue;

      let likes = 0, comments = 0;
      const artEl = artScope;

      for (const el of artEl.querySelectorAll('[aria-label]')) {
        const lbl = (el.getAttribute('aria-label') || '').trim();
        const mType = lbl.match(/^(Like|Love|Care|Haha|Wow|Sad|Angry):\s*([\d,.]+[KkMm]?)\s*people/i);
        if (mType) { likes += parseKM(mType[2]); continue; }
        if (!likes) {
          const mAgg = lbl.match(/([\d,.]+[KkMm]?)\s*(?:people\s+)?react(?:ed|ions?)?/i);
          if (mAgg) likes = parseKM(mAgg[1]);
        }
        if (!comments) {
          const mCmt = lbl.match(/^([\d,.]+[KkMm]?)\s*[Cc]omments?$/);
          if (mCmt) comments = parseKM(mCmt[1]);
        }
      }

      if (!comments) {
        for (const el of artEl.querySelectorAll('a, span, button')) {
          const t = (el.innerText || '').replace(/[ \s]+/g, ' ').trim();
          const m = t.match(/\b([\d,.]+[KkMm]?)\s*[Cc]omments?\b/i);
          if (m) { comments = parseKM(m[1]); break; }
        }
      }

      if (!comments) {
        for (const el of artEl.querySelectorAll('span, a')) {
          const t = (el.innerText || '').trim();
          if (!/^\d[\d,.]*[KkMm]?$/.test(t)) continue;
          const pText = (el.parentElement?.innerText || '').replace(/[ \s]+/g, ' ').trim();
          if (/\bcomments?\b/i.test(pText) && pText.length < 80) {
            comments = parseKM(t); break;
          }
        }
      }

      if (!comments) {
        for (const el of artEl.querySelectorAll('*')) {
          if (el.children.length > 3) continue;
          const t = (el.innerText || '').replace(/[\s\xa0]+/g, ' ').trim();
          if (t.length > 60) continue;
          const m = t.match(/\b([\d,.]+[KkMm]?)\s*[Cc]omments?\b/) ||
                    t.match(/[Vv]iew\s+(?:all\s+)?([\d,.]+[KkMm]?)\s*[Cc]omments?/);
          if (m) { comments = parseKM(m[1]); break; }
        }
      }

      if (!comments) {
        comments = artEl.querySelectorAll('[aria-label^="Comment by"]').length;
      }

      const popularity = likes + comments;

      collected.push({ date: dateLabel, url: postUrl, text, likes, comments, popularity });
      report(true);
    }
  }

  for (let round = 0; collected.length < TARGET; round++) {
    diag.rounds = round + 1;
    await expandSeeMore();
    const prev = collected.length;
    await harvest(); await wait(1000); await harvest();
    if (collected.length === prev) {
      staleRounds++;
      if (staleRounds >= MAX_STALE) break;
    } else {
      staleRounds = 0;
    }
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    await wait(SCROLL_WAIT);
  }

  try {
    await chrome.storage.local.set({
      attachmentLensScrapedPosts: collected,
      attachmentLensScrapedAt: Date.now(),
      attachmentLensScrapeDone: true,
    });
  } catch (e) {}

  return { posts: collected, diag };
}
