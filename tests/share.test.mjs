/**
 * Unit tests for the Web Share helpers in static/js/kit.js.
 *
 * Two things here are invisible in a browser until they are wrong in the field:
 *
 *  1. `navigator.share` needs transient activation, so ANY `await` between the
 *     click and the call spends the gesture and the sheet rejects with
 *     NotAllowedError. On a desktop dev machine there is usually no share sheet
 *     at all, so the regression cannot be reproduced where it is written — only
 *     on the phones that are the entire point of the feature.
 *  2. Some targets accept files, or text, but not the pair. Attaching the
 *     caption unconditionally loses the image on those, which is the one
 *     outcome worse than shipping no caption.
 *
 * kit.js is an IIFE with no exports, so — following sw-cache.test.mjs — the
 * three helpers are extracted from the source text and evaluated against a fake
 * navigator, and the test therefore exercises exactly the code that ships.
 *
 * Run: node tests/share.test.mjs   (exit code 0 = pass)
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, '..', 'static', 'js', 'kit.js'), 'utf8');

function extract(re, label) {
  const m = src.match(re);
  if (!m) throw new Error(`Could not find ${label} in kit.js — did it get renamed?`);
  return m[0];
}

// Each helper's inner braces are indented, so the first `\n  }` closes it.
const parts = [
  extract(/function asFile\([\s\S]*?\n  }/, 'asFile'),
  extract(/function canShare\([\s\S]*?\n  }/, 'canShare'),
  extract(/async function share\([\s\S]*?\n  }/, 'share'),
].join('\n');

/** A Blob stand-in: only `.type` is read, and File only has to remember it. */
const blob = (type = 'image/png') => ({ type });

class FakeFile {
  constructor(bits, name, opts) { this.name = name; this.type = (opts || {}).type; }
}

/**
 * Build the helpers against a fake navigator.
 *
 * `canShareImpl(data)` stands in for the browser's own answer, so a test can
 * say "this target takes files but not text" — the case the fallback exists
 * for. `shareImpl` records what it was actually handed.
 */
function load({ share: shareImpl, canShare: canShareImpl, hasShare = true, hasCanShare = true } = {}) {
  const toasts = [];
  const calls = [];
  const navigator = {};
  if (hasShare) navigator.share = (data) => { calls.push(data); return shareImpl(data); };
  if (hasCanShare) navigator.canShare = canShareImpl || (() => true);

  const api = new Function(
    'navigator', 'File', 'Toast', 't',
    `${parts}\nreturn { asFile, canShare, share };`,
  )(navigator, FakeFile, { show: (msg, kind) => toasts.push([msg, kind]) }, (s) => s);
  return { ...api, toasts, calls };
}

let failures = 0;
function check(name, cond) {
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`);
  if (!cond) failures++;
}

/* ---------------------------------------------------------------- asFile */
{
  const { asFile } = load();
  check('asFile keeps the blob type', asFile(blob('image/webp'), 'a.webp').type === 'image/webp');
  check('asFile names the file', asFile(blob(), 'sticker.png').name === 'sticker.png');
  check('asFile falls back to a png name', asFile(blob()).name === 'image.png');
  // A canvas toBlob failure can yield a typeless blob; a File with no type is
  // rejected by every share target, so it must not reach one unlabelled.
  check('asFile falls back to a png type', asFile({}).type === 'image/png');
}

/* -------------------------------------------------------------- canShare */
{
  check('canShare is false without navigator.share',
    load({ hasShare: false }).canShare(blob(), 'a.png') === false);
  check('canShare is false without navigator.canShare',
    load({ hasCanShare: false }).canShare(blob(), 'a.png') === false);
  check('canShare is false for a missing blob',
    load().canShare(null, 'a.png') === false);
  check('canShare is true when the browser says so',
    load().canShare(blob(), 'a.png') === true);
  check('canShare is false when the browser says no',
    load({ canShare: () => false }).canShare(blob(), 'a.png') === false);

  // Per-blob, not once at load: this is why the check is not cached. A browser
  // that shares a PNG may still refuse the video converter's MP4.
  const byType = load({ canShare: (d) => d.files[0].type !== 'video/mp4' });
  check('canShare is decided per blob (png ok)', byType.canShare(blob('image/png'), 'a.png') === true);
  check('canShare is decided per blob (mp4 refused)', byType.canShare(blob('video/mp4'), 'a.mp4') === false);

  // Safari has shipped a canShare that throws on some payloads. A throw here
  // would take down the whole bar, not just the share button.
  check('canShare survives a throwing browser',
    load({ canShare: () => { throw new Error('nope'); } }).canShare(blob(), 'a.png') === false);
}

/* ------------------------------------------------- the gesture (no await) */
{
  // The regression this file exists for: share() must reach navigator.share in
  // its FIRST synchronous run, before yielding to the microtask queue. If an
  // `await` is ever added above the call, `calls` is still empty at this point
  // and the sheet would reject with NotAllowedError on a real phone.
  const kit = load({ share: () => Promise.resolve() });
  const pending = kit.share(blob(), 'a.png');
  check('share calls navigator.share synchronously (keeps the gesture)', kit.calls.length === 1);
  await pending;
}

/* ---------------------------------------------------------- the caption */
{
  const kit = load({ share: () => Promise.resolve() });
  await kit.share(blob(), 'a.png');
  check('share attaches the caption when the target takes both',
    kit.calls[0].text === 'Made with clearbg.pt');
  check('share always sends the file', kit.calls[0].files.length === 1);
}
{
  // Files-or-text targets: the caption is dropped rather than the image.
  const kit = load({
    share: () => Promise.resolve(),
    canShare: (d) => !('text' in d),
  });
  const ok = await kit.share(blob(), 'a.png');
  check('share drops the caption when the target refuses the pair',
    kit.calls[0].text === undefined);
  check('share still sends the file without the caption', kit.calls[0].files.length === 1);
  check('share reports success', ok === true);
}
{
  // canShare({files}) passes but canShare({files, text}) throws — the caption
  // probe must not take the share down with it.
  const kit = load({
    share: () => Promise.resolve(),
    canShare: (d) => { if ('text' in d) throw new Error('nope'); return true; },
  });
  const ok = await kit.share(blob(), 'a.png');
  check('share survives a throwing caption probe', ok === true && kit.calls.length === 1);
}

/* ------------------------------------------------------------- rejection */
{
  // Backing out of the sheet is the normal way to say no. Toasting an error at
  // someone who simply changed their mind is the most annoying thing this
  // feature could do.
  const err = Object.assign(new Error('cancelled'), { name: 'AbortError' });
  const kit = load({ share: () => Promise.reject(err) });
  const ok = await kit.share(blob(), 'a.png');
  check('a cancelled share returns false', ok === false);
  check('a cancelled share raises no toast', kit.toasts.length === 0);
}
{
  // Anything else is a real failure and stays visible — swallowing it would
  // leave a button that silently does nothing.
  const kit = load({ share: () => Promise.reject(new Error('boom')) });
  const ok = await kit.share(blob(), 'a.png');
  check('a failed share returns false', ok === false);
  check('a failed share raises an error toast',
    kit.toasts.length === 1 && kit.toasts[0][1] === 'error');
}
{
  const kit = load({ canShare: () => false, share: () => Promise.resolve() });
  const ok = await kit.share(blob(), 'a.png');
  check('share is a no-op where the browser cannot share',
    ok === false && kit.calls.length === 0 && kit.toasts.length === 0);
}

console.log(failures ? `\n${failures} check(s) failed` : '\nAll share tests passed');
process.exit(failures ? 1 : 0);
