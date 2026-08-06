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

/**
 * Read an image URL into a data URL, or null if it cannot be read.
 *
 * Runs here rather than on the page because of the canvas taint rule: if
 * clearbg.pt fetched the URL itself, any image whose host does not send CORS
 * headers would load but refuse to export, and the failure would surface much
 * later as a broken download. Reading the bytes here and handing over a real
 * File sidesteps the whole question — the page sees a local file, exactly as if
 * it had been dragged in.
 */
async function readImage(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const blob = await res.blob();
    if (!blob.type.startsWith('image/')) return null;
    if (blob.size > MAX_BYTES) return null;
    return await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(blob);
    });
  } catch {
    return null; // blocked by CORS, offline, or a permission we do not have
  }
}

/** Ask for read access to one origin, only when we are about to use it. */
async function ensureAccess(url) {
  try {
    const origin = `${new URL(url).origin}/*`;
    if (await chrome.permissions.contains({ origins: [origin] })) return true;
    return await chrome.permissions.request({ origins: [origin] });
  } catch {
    return false;
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

  // A data: or blob: URL is already the bytes — no host permission involved.
  if (info.srcUrl.startsWith('data:')) {
    dataUrl = info.srcUrl.length <= MAX_BYTES * 1.4 ? info.srcUrl : null;
  } else if (await ensureAccess(info.srcUrl)) {
    dataUrl = await readImage(info.srcUrl);
  }

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
