# ClearBG browser extension

Right-click any image on the web → pick a tool → it opens on clearbg.pt with that
image already loaded.

## What it is (and deliberately is not)

The extension is a **courier**. It carries one image from the page you are on to
the matching tool on the site, and performs no image processing of its own.

That is forced by Manifest V3, which forbids remotely hosted code. Every tool on
the site loads its library from a CDN at runtime — `@imgly/background-removal`,
`pdf.js`, `tesseract.js` and eight others. Running the processing inside the
extension would mean vendoring all eleven, introducing a JS bundler the project
does not currently have, and then maintaining a second copy of every tool
forever. Handing the file to the page that already works costs nothing and cannot
drift out of sync.

**The image still never reaches a server.** The extension reads the bytes
locally, the page receives them locally, and the AI runs on your device exactly
as it does when you use the site directly.

## How the handoff works

1. `background.js` builds the right-click menu (`contexts: ["image"]`).
2. On click it fetches the image URL into a data URL, requesting read access to
   that one origin first if it does not already have it.
3. The payload is parked in `chrome.storage.session` — in memory, never written
   to disk — because an MV3 service worker can be terminated between the click
   and the new tab loading.
4. The new tab opens; `content.js` (which runs only on clearbg.pt) asks for the
   pending payload, and the worker hands it over **and deletes it**, so one
   right-click feeds exactly one navigation.
5. `content.js` writes the file into `[data-chain-input]` — an attribute the site
   already puts on the primary file input of all 27 tools that take one, for its
   own cross-tool "keep editing" bar. No site changes were needed, and a tool
   added later is picked up for free.

### Why the extension fetches the image rather than passing the URL

If the page fetched the URL itself, any image whose host does not send CORS
headers would load but refuse to export — the canvas would be tainted, and the
failure would surface much later as a broken download. Reading the bytes in the
extension and handing over a real `File` sidesteps the question entirely: the
page sees a local file, exactly as if it had been dragged in.

## Permissions

| Permission | Why |
|---|---|
| `contextMenus` | the right-click menu |
| `storage` | parking the image between the click and the tab load |
| `https://clearbg.pt/*` | running the content script that delivers it |
| `*://*/*` *(optional)* | reading the image you right-clicked |

The wildcard is an **optional** permission, requested per-origin at the moment
you first use the extension on a site — so installing it does not present a
"read your data on all websites" prompt. Given that the whole product is built
around not touching your files, that mattered more than the convenience of
asking once up front.

## Limits

- **6 MB per image.** `chrome.storage.session` is capped near 10 MB and base64
  inflates by about a third. Above that the tool still opens, just empty —
  preferable to a silent truncation, and almost nothing on the web is served
  this large.
- **Chromium only** as written. Firefox needs `browser_specific_settings` and
  uses an event page rather than a service worker; the logic ports, the manifest
  needs a variant.
- The payload expires after 60 seconds so an abandoned right-click cannot
  resurface later in the session.

## Loading it locally

```
chrome://extensions → Developer mode → Load unpacked → select this folder
```

To test against a local dev server, temporarily add a port-less match pattern
to `manifest.json` — Chrome match patterns **cannot contain a port**, so
`http://127.0.0.1/*` is correct and `http://127.0.0.1:8877/*` is silently
rejected (the extension will fail to load with no obvious error):

```jsonc
"host_permissions": ["https://clearbg.pt/*", "http://127.0.0.1/*"],
"content_scripts": [{ "matches": ["https://clearbg.pt/*", "http://127.0.0.1/*"], ... }]
```

Remove both before packaging.

## Publishing

The Chrome Web Store listing needs: a 128px icon (included), at least one
1280×800 screenshot, a short and a long description, and a privacy disclosure.
The disclosure is the easy part — the extension collects nothing, and the
justification for the optional host permission is "reading the image the user
explicitly right-clicked".
