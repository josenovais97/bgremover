# Chrome Web Store listing copy

Paste-ready text for each field in the developer dashboard. Kept in the repo so
the next submission does not start from a blank form, and so the permission
justifications stay in step with `manifest.json` — a mismatch between the two is
a rejection.

---

## Store listing tab

**Title** (max 75 chars, ~45 shown in search results)

```
ClearBG — right-click image tools
```

**Summary** (max 132 chars — must match `manifest.json` description)

```
Right-click any image to remove its background, crop, compress or convert it. Runs in your browser — nothing is uploaded.
```

**Detailed description**

```
Right-click any image on the web and send it straight to the tool you need — no
saving to your desktop, no re-uploading, no drag and drop.

Seven tools, one click away:

• Remove the background — AI cutout, transparent PNG
• Crop
• Compress
• Convert format — PNG, JPG, WebP, AVIF
• Resize
• Blur / redact
• Strip EXIF & location data

The image opens on clearbg.pt with the file already loaded, ready to edit.

YOUR IMAGES NEVER LEAVE YOUR COMPUTER

There is no upload, and no server sees your image. The extension reads the image
from the page you are on and hands it to the tool page locally. The background
removal AI runs on your own device, in your browser. That is not a promise about
what we do with your files — it is that we never receive them.

WHY IT ASKS FOR SO LITTLE

Installing shows no "read your data on all websites" warning. The extension
reads the image you right-clicked by the narrowest route that works, using the
one-tab access that your right-click already granted. Broader access is offered
on the options page for the rare site where that fails — never demanded up front,
and the extension works without it.

Free, no account, no sign-up.
```

**Category** — pick `Tools` (`Privacy & Security` is defensible, but the store
surfaces utilities under Tools and that is what people browse for here).

**Language** — English.

---

## Privacy tab

**Single purpose** — say it in one sentence. A description that reads as several
unrelated features is the most common rejection.

```
Sends an image the user right-clicks to the matching image tool on clearbg.pt with the file already loaded.
```

**Permission justifications** — one field each. These must describe what
`background.js` actually does.

| Field | Justification |
|---|---|
| `contextMenus` | Adds the right-click menu on images, which is the extension's entire user interface. |
| `storage` | Holds the image in `chrome.storage.session` between the right-click and the new tab finishing load. A Manifest V3 service worker can be terminated in between, which would otherwise lose the image. Session storage is in memory and never written to disk. |
| `activeTab` | Reads the right-clicked image from the page when a direct fetch is refused by the image host's CORS policy. The right-click itself grants this for that one tab only. |
| `scripting` | Runs the small in-page function that performs that read. |
| `host_permissions` (`https://clearbg.pt/*`) | Runs the content script that delivers the image into the tool page's file input. |
| `*://*/*` (optional) | Requested from the options page, only for sites where neither route above can read the image. Not requested at install and not required for the extension to work. |

**Are you using remote code?** — **No.** All code is in the package. (The tool
*pages* load libraries from a CDN, but that is the website, not the extension —
answering "yes" here invites a review of code that isn't in the upload.)

**Data usage** — declare **no** data collected, and tick all three
certifications. All three are true: no sale of data, no use unrelated to the
single purpose, no use to determine creditworthiness.

**Privacy policy URL**

```
https://clearbg.pt/privacy/
```

---

## Images

All built by `scripts/make-store-assets.py` into `dist/store/`, at the exact
canvases the dashboard demands and as **24-bit PNG with no alpha channel** —
transparency makes the store reject the upload.

| File | Canvas | Field | Real or composed |
|---|---|---|---|
| `shot-1-right-click.png` | 1280×800 | Screenshot 1 | composed |
| `shot-2-in-the-tool.png` | 1280×800 | Screenshot 2 | **real capture** |
| `shot-3-nothing-uploaded.png` | 1280×800 | Screenshot 3 | composed |
| `tile-small.png` | 440×280 | Small promo tile | composed |
| `tile-marquee.png` | 1400×560 | Marquee promo tile | composed |
| `store-icon-128.png` | 128×128 | Store icon (keeps alpha) | — |

Upload the screenshots in numbered order; shot 1 is the one that explains the
product, so it must be first.

**Shot 2 is a genuine screenshot** — the script runs the real removal on the real
page, so the timing figure in it is a real measurement, not artwork.

**Shot 1 draws its own copy of the context menu.** A native OS menu is not part
of the page and no screenshot API can capture it, so it is recreated in HTML. Its
seven entries are generated from the `TOOLS` list in `background.js`, so the
picture cannot drift from the menu a user really sees — but it is a rendering of
that menu, not a photograph of it, and the store's rule is that screenshots
represent actual functionality. This one does. If you would rather ship a literal
capture, take it with an OS screen-capture on a timer (the menu closes when any
in-page tool tries to grab it) and drop it in as `shot-1`.

---

## Trader declaration

**Declare Trader.** clearbg.pt serves AdSense, so the extension promotes a site
you monetise — that is "purposes relating to your trade or business" under the
EU rule, whatever the extension itself charges (nothing). Being a Trader means
your legal name, physical address, email and an SMS-capable phone number are
**publicly visible on the listing to EEA users**, so use a business address you
are willing to publish. Declaring Non-Trader to avoid that is a self-declaration
Google can act on later.
