/**
 * ClearBG extension — service worker.
 *
 * The whole extension is a courier. It carries one image from wherever you
 * right-clicked it to the matching tool on clearbg.pt, and does no image work
 * of its own.
 *
 * That is a deliberate design rather than a first cut. Manifest V3 forbids
 * remotely hosted code, and every tool on the site loads its library
 * (@imgly/background-removal, pdf.js, tesseract.js and eight others) from a CDN
 * at runtime. Porting the processing in here would mean vendoring all of them
 * and introducing a bundler the project does not have — and then maintaining a
 * second copy of every tool forever. Handing the file to the page that already
 * works costs nothing and cannot drift.
 *
 * The image still never reaches a server: the fetch below reads the bytes into
 * this worker, the page receives them locally, and the processing happens on the
 * device exactly as it does when you use the site directly.
 */

const SITE = 'https://clearbg.pt';

// Menu items, in the order they appear. `path` is the tool's URL on the site;
// every one of these pages carries a [data-chain-input] file input, which is the
// hook content.js hands the image to.
const TOOLS = [
  { id: 'remove-bg', path: '/', title: 'Remove the background' },
  { id: 'crop', path: '/crop/', title: 'Crop' },
  { id: 'compress', path: '/compress/', title: 'Compress' },
  { id: 'convert', path: '/convert/', title: 'Convert format' },
  { id: 'resize', path: '/resize-image/', title: 'Resize' },
  { id: 'redact', path: '/redact-image/', title: 'Blur / redact' },
  { id: 'exif', path: '/exif-remover/', title: 'Strip EXIF & location' },
];

const BY_ID = Object.fromEntries(TOOLS.map((t) => [t.id, t]));

/**
 * Ceiling on what we will carry, in bytes of raw image.
 *
 * The handoff parks the image in chrome.storage.session, which is capped around
 * 10 MB, and base64 inflates by roughly a third on the way in. 6 MB of image is
 * therefore about as much as fits with room to spare. Anything larger falls back
 * to opening the tool without it — better than a silent truncation, and rare:
 * almost nothing on the web is served above this.
 */
const MAX_BYTES = 6 * 1024 * 1024;

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: 'clearbg',
      title: 'ClearBG',
      contexts: ['image'],
    });
    for (const tool of TOOLS) {
      chrome.contextMenus.create({
        id: tool.id,
        parentId: 'clearbg',
        title: tool.title,
        contexts: ['image'],
      });
    }
  });
});

/** Blob → data URL, or null if it is not a usable image. */
async function toDataUrl(blob) {
  if (!blob || !blob.type.startsWith('image/') || blob.size > MAX_BYTES) return null;
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => resolve(null);
    reader.readAsDataURL(blob);
  });
}

/**
 * Read the image, trying the cheapest route that needs no permission prompt.
 *
 * 1. Straight fetch from this worker. Cross-origin fetches succeed whenever the
 *    host sends permissive CORS headers, which a great many image CDNs do — so
 *    this alone covers a large share of the web and costs the user nothing.
 * 2. Failing that, run the fetch inside the page itself. A context-menu click
 *    grants `activeTab` for that tab, so this needs no host permission either,
 *    and from the page's own origin a same-origin image always reads.
 * 3. Only if both fail is broad host access needed — offered from the options
 *    page, for the reason given in the click handler.
 *
 * The first version of this asked for a host permission up front and never got
 * one. `chrome.permissions.request()` requires an unspent user gesture, and the
 * `await` on `permissions.contains()` before it spent the one from the menu
 * click. It threw "must be called during a user gesture" every single time, the
 * error was swallowed, and the tool opened with no image — which from the
 * outside looked exactly like "it just opens the page and does nothing".
 */
async function readImage(url, tabId) {
  try {
    const res = await fetch(url);
    if (res.ok) {
      const direct = await toDataUrl(await res.blob());
      if (direct) return direct;
    }
  } catch { /* no CORS headers, or no host permission — try the page next */ }

  if (tabId == null) return null;
  try {
    const [hit] = await chrome.scripting.executeScript({
      target: { tabId },
      args: [url, MAX_BYTES],
      func: async (src, max) => {
        try {
          const r = await fetch(src);
          if (!r.ok) return null;
          const b = await r.blob();
          if (!b.type.startsWith('image/') || b.size > max) return null;
          return await new Promise((ok) => {
            const fr = new FileReader();
            fr.onload = () => ok(fr.result);
            fr.onerror = () => ok(null);
            fr.readAsDataURL(b);
          });
        } catch { return null; }
      },
    });
    return hit?.result || null;
  } catch {
    return null;
  }
}

/** Best guess at a filename, since the page's own name is the useful one. */
function nameFrom(url) {
  try {
    const last = new URL(url).pathname.split('/').pop() || '';
    // Query-string image URLs often have no extension at all in the path.
    return /\.(png|jpe?g|webp|gif|bmp|avif)$/i.test(last) ? last : 'image.png';
  } catch {
    return 'image.png';
  }
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const tool = BY_ID[info.menuItemId];
  if (!tool || !info.srcUrl) return;

  let dataUrl = null;

  // A data: URL is already the bytes — nothing to fetch.
  if (info.srcUrl.startsWith('data:')) {
    dataUrl = info.srcUrl.length <= MAX_BYTES * 1.4 ? info.srcUrl : null;
  } else {
    dataUrl = await readImage(info.srcUrl, tab?.id);
  }

  // Broad host access is offered from the options page rather than requested
  // here: chrome.permissions.request() needs an unspent user gesture, and any
  // await in this handler spends it. A button the user actually clicks is the
  // only place that call reliably works.

  if (dataUrl) {
    // Session storage, not a variable: this worker can be terminated between
    // the click and the new tab finishing its load, and a module-scoped value
    // would not survive that. Session storage is in-memory and cleared when the
    // browser closes, so the image is never written to disk.
    await chrome.storage.session.set({
      pending: { dataUrl, name: nameFrom(info.srcUrl), at: Date.now() },
    });
  }

  chrome.tabs.create({
    url: `${SITE}${tool.path}`,
    index: tab ? tab.index + 1 : undefined,
  });
});

/**
 * Hand the pending image to the content script and immediately forget it.
 *
 * Consumed on read so a later visit to the site never picks up an image from a
 * previous right-click — the payload belongs to exactly one navigation.
 */
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type !== 'clearbg:take-pending') return false;
  chrome.storage.session.get('pending', (stored) => {
    const pending = stored?.pending || null;
    // 60 seconds is long enough for a slow tab to finish loading and short
    // enough that an abandoned click cannot resurface later in the session.
    const fresh = pending && Date.now() - pending.at < 60_000;
    chrome.storage.session.remove('pending');
    sendResponse(fresh ? pending : null);
  });
  return true; // response is async
});
