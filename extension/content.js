/**
 * ClearBG extension — the page half of the handoff.
 *
 * Runs on clearbg.pt only. Asks the service worker whether an image is waiting
 * for this navigation and, if one is, drops it into the tool's file input as
 * though the visitor had chosen it themselves.
 *
 * It uses [data-chain-input], which the site already puts on the primary file
 * input of all 27 tools that take one — the same hook its own cross-tool "keep
 * editing" bar uses. So this needs no cooperation from the site, no new markup,
 * and no per-tool knowledge: a tool added later is picked up for free.
 */

(async () => {
  const pending = await chrome.runtime.sendMessage({ type: 'clearbg:take-pending' });
  if (!pending) return;

  // The tools boot on DOMContentLoaded and some build their dropzone from JS, so
  // the input can arrive a moment after this script does. Poll briefly rather
  // than racing it; give up quietly rather than hanging around forever.
  const input = await waitFor('[data-chain-input]', 4000);
  if (!input) return;

  const file = toFile(pending.dataUrl, pending.name);
  if (!file) return;

  // A DataTransfer is the only way to write to input.files — the property is
  // read-only, and the tools listen for a real change event.
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
})();

function waitFor(selector, timeoutMs) {
  return new Promise((resolve) => {
    const found = document.querySelector(selector);
    if (found) return resolve(found);

    const obs = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) {
        obs.disconnect();
        clearTimeout(timer);
        resolve(el);
      }
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });

    const timer = setTimeout(() => {
      obs.disconnect();
      resolve(null);
    }, timeoutMs);
  });
}

/** data: URL → File, or null if it is malformed. */
function toFile(dataUrl, name) {
  try {
    const [head, b64] = dataUrl.split(',');
    const type = (head.match(/data:([^;]+)/) || [])[1] || 'image/png';
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
    return new File([bytes], name, { type });
  } catch {
    return null;
  }
}
