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
2. On click it reads the image into a data URL — first by fetching it directly,
   and if that is refused, by running the fetch inside the page via `activeTab`.
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
| `activeTab` + `scripting` | reading the image from the page you right-clicked, when a plain fetch cannot |
| `https://clearbg.pt/*` | running the content script that delivers it |
| `*://*/*` *(optional)* | only for sites where neither route above works |

**Installing shows no "read your data on all websites" prompt.** The image is
read by the cheapest route that works:

1. A plain fetch from the service worker. This succeeds whenever the image host
   sends permissive CORS headers, which a great many image CDNs do.
2. Otherwise, the fetch runs inside the page itself. A context-menu click grants
   `activeTab` for that tab, so no host permission is needed and a same-origin
   image always reads.
3. Only if both fail does broad access help — and it is offered from the
   extension's options page, never demanded at install.

### Why the permission is requested from the options page

`chrome.permissions.request()` requires an *unspent* user gesture. The
context-menu handler must await the image fetch before it can know whether a
permission is even needed, and that await spends the gesture — the call then
throws `must be called during a user gesture` every time. A button the user
clicks has a gesture that has not been spent on anything, so the request works
there and nowhere else.

This is not theoretical: the first version of this extension asked for the
permission inside the click handler, the call threw on every single use, the
error was swallowed, and the tool opened with no image. From the outside it
looked exactly like "it just opens the page and does nothing".

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
