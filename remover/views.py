"""
Views for the background remover.

The heavy lifting (AI background removal) runs client-side, so these views only
render the single-page app and the SEO helper endpoints (robots.txt, sitemap).
"""
import ipaddress
import json
import logging
import time
import urllib.request
from datetime import date as _date
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import Resolver404, resolve, reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
# require_safe, not require_GET: the latter rejects HEAD, so every page on the
# live site answered a HEAD with 405 — uptime monitors, link checkers and any
# crawler that probes before fetching all saw the whole site as broken.
from django.views.decorators.http import require_safe

from .guides import GUIDES, GUIDES_BY_SLUG, guides_by_category, related_guides
from .page_content import USE_CASE_FAQS, deep_for
from .passport_data import COUNTRIES, COUNTRIES_BY_SLUG, FOLDED_COUNTRY_SLUGS, country_faqs
from .seo_content import (
    ALTERNATIVE_FAQS,
    BASE64_FAQS,
    BLUR_FAQS,
    BORDER_FAQS,
    COLLAGE_FAQS,
    COMPRESS_FAQS,
    CONVERT_FAQS,
    CROP_FAQS,
    ECOMMERCE_FAQS,
    EXIF_FAQS,
    FAVICON_FAQS,
    INDEX_FAQS,
    INSTAGRAM_FAQS,
    MEME_FAQS,
    PALETTE_FAQS,
    PASSPORT_FAQS,
    PDF_FAQS,
    QR_FAQS,
    REDACT_FAQS,
    RESIZE_FAQS,
    SCREENSHOT_FAQS,
    GIF_FAQS,
    VIDEO_GIF_FAQS,
    VIDEO_CONVERTER_FAQS,
    STICKER_FAQS,
    WATERMARK_FAQS,
    TEXTBEHIND_FAQS,
    REMOVE_OBJECT_FAQS,
    UPSCALE_FAQS,
    HEIC_FAQS,
    PDF_TO_IMAGE_FAQS,
    OCR_FAQS,
    SVG_TO_PNG_FAQS,
    PHOTO_FILTERS_FAQS,
    EXIF_PRIVACY,
    REDACT_PRIVACY,
    PASSPORT_PRIVACY,
    faq_jsonld,
)
from .translations import (
    LANGUAGES,
    localize_faqs,
    localize_use_case,
    path_language,
    strip_language,
)

logger = logging.getLogger(__name__)


# Output formats offered by the converter (all encodable via <canvas>.toBlob).
CONVERT_FORMATS = [
    {"mime": "image/png", "label": "PNG", "ext": "png", "lossy": False, "desc": "Lossless, supports transparency"},
    {"mime": "image/jpeg", "label": "JPG", "ext": "jpg", "lossy": True, "desc": "Small size, no transparency"},
    {"mime": "image/webp", "label": "WEBP", "ext": "webp", "lossy": True, "desc": "Modern, small, supports transparency"},
    {"mime": "image/avif", "label": "AVIF", "ext": "avif", "lossy": True, "desc": "Next-gen, smallest files (Chromium)"},
]

# Preset photo backgrounds a user can drop behind their cut-out (beyond solid
# colours / gradients / blur). Optimised WEBP live in static/img/backgrounds/ as
# bg-<slug>.webp (full, ≤1920px) + thumb-<slug>.webp (picker thumbnail). Ordered
# studio/neutral first (best for portraits & products), then colourful, then
# scenes. Adding one is a slug+label line here plus the two WEBP files.
# (slug, label, category). Category groups them in the picker so 17+ thumbnails
# read as a curated set rather than a wall. Order within = display order.
_BACKGROUND_SLUGS = [
    ("soft-white", "Soft white", "Studio"), ("linen", "Linen", "Studio"),
    ("concrete", "Concrete", "Studio"), ("charcoal", "Charcoal", "Studio"),
    ("white-brick", "White brick", "Studio"), ("blue-brick", "Blue brick", "Studio"),
    ("wood", "Wood", "Studio"),
    ("sky-wash", "Sky wash", "Colorful"), ("mint-bokeh", "Mint bokeh", "Colorful"),
    ("pink-cloud", "Pink cloud", "Colorful"), ("blue-gradient", "Blue gradient", "Colorful"),
    ("confetti", "Confetti", "Colorful"), ("nebula", "Nebula", "Colorful"),
    ("night-sky", "Night sky", "Colorful"),
    ("office", "Office", "Scenes"), ("deep-teal", "Deep teal", "Scenes"),
    ("floral", "Floral", "Scenes"),
]
BACKGROUNDS = [
    {
        "slug": slug,
        "label": label,
        "cat": cat,
        "full": f"img/backgrounds/bg-{slug}.webp",
        "thumb": f"img/backgrounds/thumb-{slug}.webp",
    }
    for slug, label, cat in _BACKGROUND_SLUGS
]
_BG_CATEGORY_ORDER = ["Studio", "Colorful", "Scenes"]
BACKGROUND_GROUPS = [
    {"label": cat, "items": [b for b in BACKGROUNDS if b["cat"] == cat]}
    for cat in _BG_CATEGORY_ORDER
]

# Instagram output formats: each sets a crop aspect and the exact pixel size
# Instagram recommends, so exports fill the frame and upload without recompression.
IG_FORMATS = [
    {"key": "post", "label": "Post", "sub": "1:1", "aspect": "1", "w": 1080, "h": 1080},
    {"key": "portrait", "label": "Portrait", "sub": "4:5", "aspect": "0.8", "w": 1080, "h": 1350},
    {"key": "story", "label": "Story / Reel", "sub": "9:16", "aspect": "0.5625", "w": 1080, "h": 1920},
    {"key": "landscape", "label": "Landscape", "sub": "1.91:1", "aspect": "1.91", "w": 1080, "h": 566},
    {"key": "profile", "label": "Profile", "sub": "1:1", "aspect": "1", "w": 320, "h": 320},
]

# Keyword-targeted landing pages. Each reuses the same in-browser tool but gives
# a specific audience tailored copy — this widens the number of search entry
# points without duplicating the app. Copy lives here so it is easy to edit and
# so the sitemap can be generated from the same source (see SITEMAP_PATHS).
USE_CASES = [
    {
        "slug": "product-photos",
        "nav": "Product photos",
        "title": "Remove Background from Product Photos — Free & Instant",
        "description": "Create clean white or transparent product photos for your online store. Free, private, and unlimited — the AI runs in your browser, so nothing is uploaded.",
        "h1": "Remove Backgrounds from Product Photos",
        "tagline": "Give your store a consistent, professional look with clean cut-outs — free, unlimited, and processed entirely on your device.",
        "intro": [
            "Marketplaces like Amazon, eBay, Etsy and Shopify convert better when every product sits on a clean, consistent background. This tool strips the background from your product shots in seconds so you can export a transparent PNG or drop in a pure-white backdrop.",
            "Because the AI runs locally in your browser, you can process an entire catalogue without uploading a single image, hitting an API limit, or paying per photo.",
        ],
        "benefits": [
            {"icon": "fa-store", "title": "Marketplace-ready", "text": "Export on pure white for Amazon-style listings, or transparent PNGs to composite anywhere."},
            {"icon": "fa-layer-group", "title": "Batch your catalogue", "text": "Drop in dozens of product shots at once and download them together as a ZIP."},
            {"icon": "fa-crop-simple", "title": "Full resolution", "text": "Keeps the original quality — no downscaling and no watermark on your product images."},
        ],
    },
    {
        "slug": "profile-picture",
        "nav": "Profile pictures",
        "title": "Profile Picture Background Remover — Free & Private",
        "description": "Remove the background from your profile picture or headshot for LinkedIn, a CV, or social media. 100% free and private — images never leave your browser.",
        "h1": "Remove the Background from Your Profile Picture",
        "tagline": "Perfect headshots and avatars for LinkedIn, CVs and social profiles — swap in any color, all in your browser.",
        "intro": [
            "A clean headshot makes your LinkedIn, CV or social profile look sharp. Upload your photo and the AI isolates you from the background, so you can keep it transparent or drop in a solid brand color.",
            "Everything happens on your device — your photo is never uploaded, which keeps a personal image completely private.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Flattering cut-outs", "text": "Trained to handle hair and soft edges, with a refine brush for the finishing touches."},
            {"icon": "fa-swatchbook", "title": "Any background color", "text": "Match a brand palette or a plain studio backdrop, then export PNG, JPG or WEBP."},
            {"icon": "fa-shield-halved", "title": "Private by design", "text": "Your face never leaves your browser — nothing is sent to a server."},
        ],
    },
    {
        "slug": "logo",
        "nav": "Logos",
        "title": "Remove Background from a Logo — Get a Transparent PNG",
        "description": "Turn a logo with a solid background into a clean transparent PNG. Free, unlimited, and processed privately in your browser — no sign-up.",
        "h1": "Make Your Logo Background Transparent",
        "tagline": "Turn a flat logo into a transparent PNG you can drop onto any color, slide or website — free and instant.",
        "intro": [
            "Got a logo trapped on a white or colored square? This tool removes that background and gives you a transparent PNG that sits cleanly on any website, document or presentation.",
            "It all runs in your browser at full resolution, so your brand assets stay crisp and never get uploaded anywhere.",
        ],
        "benefits": [
            {"icon": "fa-vector-square", "title": "Clean transparency", "text": "Removes solid backdrops so your mark drops onto any color without a halo."},
            {"icon": "fa-brush", "title": "Refine the edges", "text": "Tidy up leftover pixels or restore fine detail with the built-in edge brush."},
            {"icon": "fa-crop-simple", "title": "Full quality export", "text": "Download a lossless, full-resolution PNG — no watermark, ever."},
        ],
    },
    {
        "slug": "signature",
        "nav": "Signatures",
        "title": "Remove Background from a Signature — Transparent PNG",
        "description": "Turn a photo or scan of your handwritten signature into a clean transparent PNG for documents and contracts. Free and private — runs in your browser.",
        "h1": "Create a Transparent Signature",
        "tagline": "Turn a scan or photo of your handwritten signature into a clean transparent PNG for contracts and documents.",
        "intro": [
            "Sign a blank sheet of paper, photograph or scan it, then drop it here. The AI removes the paper background and leaves just the ink as a transparent PNG you can place onto any PDF or document.",
            "Since the whole process runs in your browser, your signature — a sensitive piece of information — is never uploaded to a server.",
        ],
        "benefits": [
            {"icon": "fa-stamp", "title": "Document-ready", "text": "Get transparent ink you can drop straight into PDFs, contracts and letters."},
            {"icon": "fa-shield-halved", "title": "Kept private", "text": "Your signature never leaves your device — nothing is sent anywhere."},
            {"icon": "fa-wand-magic-sparkles", "title": "Clean isolation", "text": "Separates ink from paper texture and shadows, with a brush to refine the result."},
        ],
    },
    {
        "slug": "car-photos",
        "nav": "Car photos",
        "title": "Remove Background from Car Photos — Free & Instant",
        "description": "Remove the background from car photos for dealer listings and marketplace ads. Put any vehicle on white or transparent — free, in your browser.",
        "h1": "Remove Backgrounds from Car Photos",
        "tagline": "Give every vehicle a clean, consistent listing shot for your dealership or marketplace ad — free, unlimited, and processed on your device.",
        "intro": [
            "Car listings sell faster when every vehicle sits on a clean, consistent backdrop instead of a cluttered forecourt. This tool cuts the background from your car photos in seconds, so you can drop in pure white or keep a transparent PNG for your template.",
            "Because the AI runs locally in your browser, you can process a whole lot of stock without uploading a single photo, hitting an API limit, or paying per image.",
        ],
        "benefits": [
            {"icon": "fa-square-full", "title": "Showroom-clean", "text": "Swap a messy forecourt for a spotless studio-style backdrop that keeps the focus on the car."},
            {"icon": "fa-layer-group", "title": "Whole-lot batches", "text": "Drop in dozens of shots at once and download them together as a ZIP."},
            {"icon": "fa-clock", "title": "Instant & free", "text": "No per-photo cost and no watermark — full-resolution output every time."},
        ],
    },
    {
        "slug": "clothing",
        "nav": "Clothing & fashion",
        "title": "Remove Background from Clothing Photos — Free for Resellers",
        "description": "Remove the background from clothing and fashion photos for Vinted, Depop, Poshmark or your own shop. Free white or transparent PNGs, in-browser.",
        "h1": "Remove the Background from Clothing Photos",
        "tagline": "Turn phone snaps of clothes into clean, sellable product shots for Vinted, Depop, Poshmark or your own store — free and unlimited.",
        "intro": [
            "Second-hand and boutique fashion sells faster when every item looks consistent and professional. Upload a photo of a garment and the AI isolates it from your carpet, hanger or wall, so you can place it on clean white or a transparent background.",
            "It all runs in your browser at full resolution, so you can prep an entire wardrobe of listings privately — no uploads, no per-photo fees.",
        ],
        "benefits": [
            {"icon": "fa-store", "title": "Sellable in seconds", "text": "Clean cut-outs of tops, dresses and shoes that look at home in any shop grid."},
            {"icon": "fa-bookmark", "title": "Consistent listings", "text": "Give every item the same tidy backdrop so your storefront looks professional."},
            {"icon": "fa-shield-halved", "title": "Private by design", "text": "Your photos never leave your device — nothing is uploaded to a server."},
        ],
    },
    {
        "slug": "pet-photos",
        "nav": "Pet photos",
        "title": "Remove Background from Pet Photos — Free & Private",
        "description": "Cut out your dog, cat or any pet from a photo for free. Make transparent PNGs for stickers, prints and memes — private and in your browser, nothing uploaded.",
        "h1": "Remove the Background from Pet Photos",
        "tagline": "Cut out your dog, cat or any furry friend for stickers, prints, mugs and memes — free, unlimited, and all in your browser.",
        "intro": [
            "Want your pet on a mug, a sticker or a custom print? Upload a photo and the AI separates your dog or cat from the background — handling fur and whiskers — so you get a clean transparent PNG to drop anywhere.",
            "Everything happens on your device, so you can experiment with as many photos as you like — no uploads, no limits, and no watermark.",
        ],
        "benefits": [
            {"icon": "fa-brush", "title": "Great with fur", "text": "Trained to handle soft edges, fur and whiskers for a natural-looking cut-out."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refine by hand", "text": "Tidy leftover background or restore fine detail with the built-in edge brush."},
            {"icon": "fa-note-sticky", "title": "Print & sticker ready", "text": "Full-resolution transparent PNGs for mugs, stickers, prints and memes."},
        ],
    },
    {
        "slug": "youtube-thumbnail",
        "nav": "YouTube thumbnails",
        "title": "Remove Background for YouTube Thumbnails — Free",
        "description": "Cut yourself out of a photo for a click-worthy YouTube thumbnail. Free transparent PNGs to drop over any background — private, in your browser.",
        "h1": "Remove Backgrounds for YouTube Thumbnails",
        "tagline": "Cut yourself or your subject out cleanly and drop it over a bold background for thumbnails that get the click — free and unlimited.",
        "intro": [
            "The best-performing thumbnails put a crisp cut-out of a person or product over a punchy background. Upload your shot and the AI removes the background in seconds, giving you a transparent PNG to composite in your thumbnail editor.",
            "It runs entirely in your browser at full resolution, so creators can turn thumbnails around fast — no uploads, no subscriptions, and no watermark.",
        ],
        "benefits": [
            {"icon": "fa-camera", "title": "Made for creators", "text": "Clean cut-outs of you or your subject to pop against any thumbnail background."},
            {"icon": "fa-clock", "title": "Fast turnaround", "text": "Removes the background in seconds so you can ship the thumbnail and hit publish."},
            {"icon": "fa-crop-simple", "title": "Full quality", "text": "Full-resolution transparent PNGs with no watermark, ready for any editor."},
        ],
    },
    {
        "slug": "ebay",
        "nav": "eBay listings",
        "title": "Remove Background from eBay Photos — Free & Instant",
        "description": "Give your eBay listings clean white or transparent backgrounds for free. Make items look professional — private, unlimited, in your browser.",
        "h1": "Remove Backgrounds from eBay Photos",
        "tagline": "Turn cluttered phone snaps into clean, professional eBay listing photos — free, unlimited, and processed on your device.",
        "intro": [
            "Listings with clean, consistent photos win more clicks and sell faster. Drop in a photo of your item and the AI strips the messy background so you can drop in pure white — the look buyers trust — or keep a transparent PNG for your template.",
            "Because the AI runs locally in your browser, you can prep an entire inventory without uploading a single photo, hitting an API limit, or paying per image.",
        ],
        "benefits": [
            {"icon": "fa-bookmark", "title": "Sell faster", "text": "Clean white backgrounds make items look professional and build buyer trust."},
            {"icon": "fa-layer-group", "title": "Batch your inventory", "text": "Drop in dozens of items at once and download them together as a ZIP."},
            {"icon": "fa-circle-check", "title": "Free & unlimited", "text": "No per-photo cost and no watermark — full-resolution output every time."},
        ],
    },
    {
        "slug": "discord-pfp",
        "nav": "Discord avatars",
        "title": "Discord Profile Picture Background Remover — Free",
        "description": "Make a clean Discord PFP by removing the background from your photo or avatar. Free transparent PNGs to drop on any color — in your browser.",
        "h1": "Remove the Background from Your Discord PFP",
        "tagline": "Cut yourself or your character out cleanly for a crisp Discord avatar — free, unlimited, and all in your browser.",
        "intro": [
            "A clean profile picture makes your Discord presence pop. Upload a photo, selfie or piece of art and the AI isolates the subject, so you can keep it transparent or drop in any solid color or gradient before you crop to a circle.",
            "Everything happens on your device, so you can try as many looks as you like — no uploads, no limits, and no watermark.",
        ],
        "benefits": [
            {"icon": "fa-user", "title": "Crisp avatars", "text": "Clean cut-outs that read well even at Discord's small avatar size."},
            {"icon": "fa-swatchbook", "title": "Any color or gradient", "text": "Drop your cut-out onto a solid color, gradient or blurred backdrop, then crop to a circle."},
            {"icon": "fa-shield-halved", "title": "Private by design", "text": "Your photo never leaves your browser — nothing is uploaded to a server."},
        ],
    },
    {
        "slug": "twitch",
        "nav": "Twitch & streaming",
        "title": "Remove Background for Twitch & Streaming — No Green Screen",
        "description": "Cut yourself out of a photo for Twitch panels, overlays and emotes — no green screen needed. Free transparent PNGs, private, in your browser.",
        "h1": "Remove Backgrounds for Twitch and Streaming",
        "tagline": "Make clean cut-outs for panels, overlays and emotes without a green screen — free, unlimited, and processed on your device.",
        "intro": [
            "Great channel branding starts with clean assets. Upload a photo and the AI removes the background so you get a transparent PNG for your Twitch panels, stream overlays, schedule graphics or emotes — no green screen or manual masking required.",
            "It all runs in your browser at full resolution, so you can build a whole set of on-brand graphics privately — no uploads, no per-image fees, no watermark.",
        ],
        "benefits": [
            {"icon": "fa-wand-magic-sparkles", "title": "No green screen", "text": "Get a clean cut-out from any photo — no chroma key or studio setup needed."},
            {"icon": "fa-images", "title": "Panels & emotes", "text": "Transparent PNGs ready for overlays, panels, schedules and emote art."},
            {"icon": "fa-crop-simple", "title": "Full quality", "text": "Full-resolution, watermark-free exports for any streaming layout tool."},
        ],
    },
]

USE_CASES_BY_SLUG = {case["slug"]: case for case in USE_CASES}

# Privacy-angle landing pages. ClearBG's one structural differentiator is that
# every tool runs on-device — no competitor that uploads can claim it — so these
# pages target that low-competition intent ("without uploading", "offline",
# "private"). Each is a hub-quality page: real copy, benefits, a curated set of
# featured tools (by TOOL_NAV name) and its own FAQ. `url_name` ties the page to
# its route so siblings can cross-link. Copy lives here beside USE_CASES.
PRIVACY_PAGES = [
    {
        "slug": "private-image-tools",
        "url_name": "priv_hub",
        "nav": "Private image tools",
        "title": "Private Image Tools — Edit Photos Without Uploading",
        "description": "A full toolkit of image tools that run entirely in your browser — remove backgrounds, compress, convert, resize and strip metadata. No upload, no account.",
        "h1": "Image tools that never upload your photos",
        "tagline": "Every tool here runs on your device. Your photos are processed in the browser and never sent to a server — no account, no cloud, no tracking.",
        "intro": [
            "Most \"free\" online image tools upload your photo to their servers to do the work. That means a private document, a customer's product shot or a picture of your family passes through — and is often stored on — someone else's computer. ClearBG is built the opposite way: the processing runs inside your own browser, so the image never leaves your device.",
            "That single design choice is what makes ClearBG genuinely private. There is nothing to sign up for, no image is transmitted, and there is no server-side copy to leak, cache or train on. You can use every tool below on sensitive images — IDs, bank statements, medical photos, unreleased designs — with none of the usual risk.",
        ],
        "benefits": [
            {"icon": "fa-shield-halved", "title": "Private by design", "text": "The AI and every edit run locally. Your photos are never uploaded, stored or seen by anyone — not even us."},
            {"icon": "fa-lock", "title": "Nothing to upload", "text": "No account, no cloud, no API keys. Drop an image in and it's processed on the spot, in the page."},
            {"icon": "fa-database", "title": "No data kept", "text": "Because nothing reaches a server, there's no history, no tracking pixel on the tools, and nothing to delete later."},
        ],
        "tools": ["index", "compress", "convert", "resize", "redact", "exif"],
        "faqs": [
            {"q": "Are my images really not uploaded?",
             "a": "Correct. The tools use your browser's own canvas and, for background removal, an AI model that runs on your device. The image data stays in the page — it is never sent to ClearBG or any third party."},
            {"q": "How can it be free if nothing is uploaded?",
             "a": "There are no servers doing the heavy lifting, so there's almost nothing to pay for. The tools are free and unlimited, with no watermark and no per-image cost."},
            {"q": "Is this safe for sensitive documents?",
             "a": "Yes — that's the main reason to use it. Because the file never leaves your device, redacting an ID, stripping GPS data from a photo or cleaning up a bank statement is far safer than on a tool that uploads."},
            {"q": "Do I need to install anything?",
             "a": "No. It runs in any modern browser. You can optionally install it as an app (PWA) so it opens in its own window and keeps working offline."},
        ],
        "cta": {"url_name": "index", "label": "Try the background remover"},
    },
    {
        "slug": "remove-background-without-uploading",
        "url_name": "priv_no_upload",
        "nav": "Remove background without uploading",
        "title": "Remove Background Without Uploading — 100% Private & Free",
        "description": "Remove an image background without uploading your photo. The AI runs entirely in your browser, so nothing is sent to a server. Free and unlimited.",
        "h1": "Remove a background without uploading your photo",
        "tagline": "The background-removal AI runs inside your browser. Your photo is never uploaded, so even sensitive images stay completely private.",
        "intro": [
            "Almost every background remover works by uploading your image to a server, removing the background there, and sending the result back. ClearBG doesn't. The AI model downloads to your browser once, then does the cut-out on your own device — your photo never travels across the internet.",
            "That makes it the right tool for anything you wouldn't want on someone else's server: a passport photo, a picture of your kids, an unreleased product, a scanned signature. You still get a clean, full-resolution transparent PNG — just without the privacy trade-off.",
        ],
        "benefits": [
            {"icon": "fa-shield-halved", "title": "On-device AI", "text": "The cut-out is computed in your browser. No upload step exists, so there's no server copy of your photo."},
            {"icon": "fa-download", "title": "Full-resolution output", "text": "Export a lossless transparent PNG (or JPG/WEBP) at the original size — no downscaling, no watermark."},
            {"icon": "fa-circle-check", "title": "Free & unlimited", "text": "No credits, no account, no per-image fee. Remove as many backgrounds as you like."},
        ],
        "tools": ["index", "ecommerce", "blur", "redact"],
        "faqs": [
            {"q": "How does it remove the background without uploading?",
             "a": "The first time you use it, a small AI segmentation model loads into your browser. After that, every cut-out is computed locally on your device — the image itself is never transmitted."},
            {"q": "Is the quality as good as tools that upload?",
             "a": "Yes. It handles hair and soft edges well and includes a refine brush to tidy edges. Exports are full-resolution and never watermarked."},
            {"q": "Does it work on my phone?",
             "a": "Yes, in any modern mobile browser. The image is still processed on the device — nothing is uploaded from your phone either."},
            {"q": "Can I process several images privately?",
             "a": "Yes. You can batch a set of photos and download them together as a ZIP, all without a single upload."},
        ],
        "cta": {"url_name": "index", "label": "Remove a background privately"},
    },
    {
        "slug": "offline-image-editor",
        "url_name": "priv_offline",
        "nav": "Offline image editor",
        "title": "Offline Image Editor — Edit Photos With No Internet",
        "description": "Compress, convert, resize, crop and remove image backgrounds offline, right in your browser. Install ClearBG as an app and edit with no connection.",
        "h1": "An image editor that works offline",
        "tagline": "Because the tools run on your device, they keep working with no connection. Install ClearBG once and edit images offline — privately, with nothing uploaded.",
        "intro": [
            "ClearBG is a browser-based toolkit that does all of its work locally, so it doesn't need a live connection to function. Install it as an app (it's a PWA) and the interface is cached on your device — you can then compress, convert, resize, crop or redact images with the internet switched off entirely.",
            "It's genuinely useful on a plane, on patchy hotel Wi-Fi, or any time you'd rather not send a photo over the network. Everything happens on-device, which is also why it stays private: no connection means there's nowhere for your images to go.",
        ],
        "benefits": [
            {"icon": "fa-globe", "title": "Works with no connection", "text": "Once loaded, the tools run entirely on your device — no live server call to compress, convert, resize or crop."},
            {"icon": "fa-lock", "title": "Installable app", "text": "Add ClearBG to your home screen or desktop and it opens in its own window, cached for offline use."},
            {"icon": "fa-shield-halved", "title": "Private, always", "text": "Offline by nature means private by nature — your images never leave the device they're on."},
        ],
        "tools": ["compress", "convert", "resize", "crop", "index"],
        "faqs": [
            {"q": "How do I use it offline?",
             "a": "Open ClearBG once online, then install it from your browser's menu (\"Install app\" / \"Add to Home Screen\"). The app shell is cached, so it opens and runs the client-side tools even with no connection."},
            {"q": "Do all the tools work offline?",
             "a": "The canvas-based tools — compress, convert, resize, crop, EXIF removal and more — work fully offline once loaded. Background removal needs its AI model downloaded once; after that first download it works offline too."},
            {"q": "Is anything uploaded when I'm back online?",
             "a": "No. Nothing is queued to upload and nothing syncs to a server, online or off. The images only ever exist on your device."},
            {"q": "Is it really free?",
             "a": "Yes — free and unlimited, no account and no watermark, online or offline."},
        ],
        "cta": {"url_name": "index", "label": "Open the toolkit"},
    },
]

PRIVACY_PAGES_BY_SLUG = {p["slug"]: p for p in PRIVACY_PAGES}

# Tool intent-variant landing pages: the words people actually search for a
# job, funnelling to the tool that does it. Same machinery as PRIVACY_PAGES
# (landing.html + curated tools + FAQ); `cta.url_name` names the destination.
TOOL_LANDINGS = [
    {
        "slug": "open-heic-on-windows",
        "url_name": "heic_windows",
        "nav": "Open HEIC on Windows",
        "title": "Can't Open HEIC on Windows? Convert to JPG Free — No Install",
        "description": "Windows can't open your iPhone's HEIC photos? Convert them to JPG free, right in your browser — no codec pack, no software, nothing uploaded.",
        "h1": "Open HEIC photos on Windows",
        "tagline": "No codec pack, no paid app from the Microsoft Store — drop the photos in your browser and download them as JPGs Windows opens natively.",
        "intro": [
            "iPhones save photos as HEIC by default, and a fresh Windows install can't open them — Photos asks you to buy a codec, and half the \"free\" converter sites push the photo through their servers. There is a simpler way: the conversion can run inside your own browser.",
            "Drop the HEIC files on the converter below and download JPGs (or PNGs) that open in Photos, Paint, Office and every website. The decoding happens on your PC — the photos are never uploaded, which matters when the camera roll you're converting is personal.",
        ],
        "benefits": [
            {"icon": "fa-mobile-screen", "title": "No codec, no install", "text": "Works in the browser you already have — nothing to buy from the Store, nothing to install."},
            {"icon": "fa-images", "title": "Whole folders at once", "text": "Drop a batch of HEICs and download them together as a ZIP of JPGs."},
            {"icon": "fa-shield-halved", "title": "Photos stay on your PC", "text": "The decoder runs locally — your camera roll never transits a stranger's server."},
        ],
        "tools": ["heic", "convert", "compress", "resize"],
        "cta": {"label": "Convert HEIC to JPG now", "url_name": "heic"},
        "cta_icon": "fa-mobile-screen",
        "faqs": [
            {"q": "Why can't Windows open HEIC files?",
             "a": "HEIC needs the HEVC codec, which Windows doesn't ship by default for licensing reasons — the Store sells it separately. Converting the photo to JPG sidesteps the codec entirely, and JPG opens everywhere."},
            {"q": "Do I need to install anything?",
             "a": "No. The converter runs in your browser using WebAssembly. Open the page, drop the files, download the JPGs."},
            {"q": "Are my photos uploaded to convert them?",
             "a": "No — decoding happens on your own machine. Nothing is sent to a server, stored or seen by anyone."},
            {"q": "Will the converted photos lose quality?",
             "a": "They're decoded at full resolution and re-encoded at high quality; the difference isn't visible. Choose PNG if you want a mathematically lossless export."},
        ],
    },
    {
        "slug": "convert-iphone-photos-to-jpg",
        "url_name": "heic_iphone",
        "nav": "iPhone photos to JPG",
        "title": "Convert iPhone Photos to JPG — Free &amp; Private",
        "description": "Turn iPhone HEIC photos into JPGs that open anywhere — free and in your browser, so your camera roll is never uploaded. Batch convert to a ZIP.",
        "h1": "Convert iPhone photos to JPG",
        "tagline": "AirDropped or copied photos that nothing can open? Convert the whole batch to JPG on your own device — free, private, no app to install.",
        "intro": [
            "Since iOS 11, iPhones shoot in HEIC — half the file size of JPG, but Android phones, Windows PCs, older Macs and most upload forms can't read it. The fix is a one-time convert to JPG, and it doesn't require handing your photos to a website's server.",
            "This converter decodes HEIC right in the browser and gives you back JPGs (or PNG / WEBP) at full resolution. Drop in one photo or a hundred; download them singly or as a ZIP.",
        ],
        "benefits": [
            {"icon": "fa-mobile-screen", "title": "Made for the iPhone default", "text": "Reads the HEIC/HEIF files iOS produces, including AirDropped and USB-copied ones."},
            {"icon": "fa-images", "title": "Batch + ZIP", "text": "Convert an entire trip's photos in one drop and grab a single ZIP."},
            {"icon": "fa-shield-halved", "title": "Nothing uploaded", "text": "Decoding runs on your device — personal photos never leave it."},
        ],
        "tools": ["heic", "compress", "resize", "index"],
        "cta": {"label": "Convert iPhone photos now", "url_name": "heic"},
        "cta_icon": "fa-mobile-screen",
        "faqs": [
            {"q": "How do I stop my iPhone shooting HEIC?",
             "a": "Settings → Camera → Formats → Most Compatible makes the camera shoot JPG directly. HEIC (High Efficiency) saves space though, so many people keep it and just convert the occasional photo that needs to be a JPG — which is what this tool is for."},
            {"q": "Can I convert many photos at once?",
             "a": "Yes — drop in a whole batch and download the results as a ZIP. There's no file limit."},
            {"q": "Is it really free and private?",
             "a": "Yes. Free, unlimited, watermark-free — and the conversion runs in your browser, so nothing is uploaded."},
        ],
    },
    {
        "slug": "extract-text-from-image",
        "url_name": "ocr_extract",
        "nav": "Extract text from image",
        "title": "Extract Text from an Image — Free OCR, Nothing Uploaded",
        "description": "Copy text out of a photo or screenshot with free on-device OCR — the image is read in your browser and never uploaded. Editable result, one click.",
        "h1": "Extract text from any image",
        "tagline": "Screenshots, photographed documents, whiteboards — on-device OCR turns them into editable text without the image ever leaving your browser.",
        "intro": [
            "Retyping text from a screenshot is busywork, but most OCR sites make you upload the image to their servers — and screenshots are exactly the kind of file you don't want uploaded: conversations, invoices, credentials, contracts. This tool runs the OCR engine on your own device instead.",
            "Drop in the image (or paste a screenshot straight from the clipboard), let the recogniser read it, then fix anything it got wrong in the editable box and copy the result. English, Portuguese, Spanish, French and German are supported.",
        ],
        "benefits": [
            {"icon": "fa-align-left", "title": "Editable result", "text": "The recognised text lands in a text box you can correct before copying — OCR is never 100%, so the last metre matters."},
            {"icon": "fa-globe", "title": "Five languages", "text": "English, Portuguese, Spanish, French and German packs, downloaded once and cached."},
            {"icon": "fa-shield-halved", "title": "Screenshots stay private", "text": "The Tesseract engine runs in your browser via WebAssembly — nothing is uploaded."},
        ],
        "tools": ["ocr", "redact", "exif", "pdf_to_image"],
        "cta": {"label": "Extract text now", "url_name": "ocr"},
        "cta_icon": "fa-align-left",
        "faqs": [
            {"q": "How accurate is the text recognition?",
             "a": "Very good on clean screenshots and printed documents; photos taken at an angle, handwriting and low light reduce accuracy. Sharp, straight-on images with good contrast recognise best — and the result box is editable, so fixes are quick."},
            {"q": "Is my screenshot uploaded for the OCR?",
             "a": "No. The engine (Tesseract, compiled to WebAssembly) runs on your device. The image never leaves your browser."},
            {"q": "What languages can it read?",
             "a": "English, Portuguese, Spanish, French and German. Pick the language before recognising; the language pack downloads once and is cached for offline use."},
            {"q": "Can I extract text from a PDF?",
             "a": "Turn the PDF's pages into images first with the PDF to Images tool, then run each page through the text extractor — both run entirely in your browser."},
        ],
    },
]
TOOL_LANDINGS_BY_SLUG = {p["slug"]: p for p in TOOL_LANDINGS}

# Compress intent-variants. Same in-browser compressor, but a page per search
# intent (by format, by target size, by use case) — "different intent, mostly the
# same functionality" is exactly what ranks. Each carries unique copy + FAQ so the
# pages aren't thin duplicates. Shared chrome (CTA to /compress/, section titles,
# featured tools) is injected by the compress_page view, so the data stays lean.
COMPRESS_PAGES = [
    # --- by format ---
    {
        "slug": "compress-png", "url_name": "compress_png", "nav": "Compress PNG",
        "title": "Compress PNG — Free Lossless & Lossy PNG Compressor",
        "description": "Compress PNG images to a smaller file size without visible quality loss, free and in your browser. Keeps transparency, no watermark, no upload.",
        "h1": "Compress a PNG without losing quality",
        "tagline": "Shrink PNG file size while keeping crisp edges and transparency — free, unlimited, and processed entirely on your device.",
        "intro": [
            "PNG is lossless, which keeps text and logos sharp but often makes files large. This compressor reduces a PNG's size by optimising its colours and encoding — so a screenshot, logo or graphic downloads and loads far faster while still looking clean.",
            "Transparency is preserved, there's no watermark, and because everything runs in your browser your image is never uploaded. Drop in one PNG or a whole batch.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Big size savings", "text": "Cuts PNG weight substantially — ideal for logos, icons, screenshots and UI assets."},
            {"icon": "fa-crop-simple", "title": "Keeps transparency", "text": "Alpha channels stay intact, so your PNG still drops cleanly onto any background."},
            {"icon": "fa-shield-halved", "title": "Private & free", "text": "Runs on your device — nothing uploaded, no watermark, no per-image cost."},
        ],
        "faqs": [
            {"q": "Will compressing a PNG lose quality?",
             "a": "PNG compression here focuses on reducing colour data and re-encoding, which for most graphics, logos and screenshots is visually lossless. For photographs, converting to WEBP or JPG usually saves far more."},
            {"q": "Does it keep transparency?",
             "a": "Yes. The alpha channel is preserved, so a transparent PNG stays transparent after compression."},
            {"q": "Is there a file limit or watermark?",
             "a": "No limits and no watermark. It's free and unlimited, and your images never leave your browser."},
        ],
    },
    {
        "slug": "compress-jpeg", "url_name": "compress_jpeg", "nav": "Compress JPEG",
        "title": "Compress JPEG — Free JPG Compressor, No Upload",
        "description": "Compress JPEG/JPG photos to a smaller size in your browser, free. Adjust quality, shrink for web or email, no watermark, nothing uploaded.",
        "h1": "Compress a JPEG to a smaller size",
        "tagline": "Reduce JPG photo file size with a simple quality slider — free, unlimited, and processed on your device with nothing uploaded.",
        "intro": [
            "JPEG is the standard for photos, and a small drop in quality can shrink the file dramatically with no visible difference. This compressor lets you slide the quality — or set a target size — and exports a smaller JPG in seconds.",
            "It's perfect for trimming camera photos before emailing them, uploading to a website, or attaching to a form. Nothing is uploaded, so even personal photos stay private.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Quality slider", "text": "Dial in exactly the balance you want, or set a target size and let it hit the number."},
            {"icon": "fa-images", "title": "Batch photos", "text": "Compress a whole set of JPGs at once and download them together as a ZIP."},
            {"icon": "fa-shield-halved", "title": "Nothing uploaded", "text": "Your photos are compressed in the browser — private, free, and watermark-free."},
        ],
        "faqs": [
            {"q": "How much can I compress a JPEG?",
             "a": "Often by 60–90% with little visible change. Photos with lots of smooth areas (skies, skin) compress the most. You control the trade-off with the quality slider."},
            {"q": "What's the difference between JPEG and JPG?",
             "a": "None — they're the same format, just two spellings of the file extension. This tool handles both."},
            {"q": "Is it really free and private?",
             "a": "Yes. It's free with no watermark, and the compression happens on your device, so nothing is uploaded."},
        ],
    },
    {
        "slug": "compress-webp", "url_name": "compress_webp", "nav": "Compress WEBP",
        "title": "Compress WEBP — Free WebP Compressor in Your Browser",
        "description": "Compress WEBP images or convert to WEBP for smaller files than PNG/JPG, free and private. Keeps transparency, no upload, no watermark.",
        "h1": "Compress and optimise WEBP images",
        "tagline": "Get smaller files than PNG or JPG with WEBP — compress or convert in your browser, free, with nothing uploaded.",
        "intro": [
            "WEBP produces noticeably smaller files than PNG or JPG at the same visual quality, and it supports transparency — which makes it ideal for fast-loading websites. This tool compresses existing WEBP images, and you can also convert PNG or JPG into WEBP to save even more.",
            "Everything runs locally in your browser, so there's no upload, no watermark and no limit on how many images you optimise.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Smaller than PNG/JPG", "text": "WEBP typically saves 25–35% over JPG and far more over PNG at matching quality."},
            {"icon": "fa-arrow-right-arrow-left", "title": "Convert too", "text": "Turn PNG or JPG into WEBP right here, or export back out to another format."},
            {"icon": "fa-shield-halved", "title": "Private by design", "text": "On-device processing — your images are never uploaded and never watermarked."},
        ],
        "faqs": [
            {"q": "Why use WEBP over JPG or PNG?",
             "a": "WEBP gives smaller files at the same quality and supports transparency like PNG. Smaller images mean faster page loads and better Core Web Vitals."},
            {"q": "Do all browsers support WEBP?",
             "a": "Yes — every modern browser supports WEBP. It's safe to use across the web today."},
            {"q": "Can I convert to WEBP as well as compress?",
             "a": "Yes. You can compress an existing WEBP, or use the converter to turn a PNG/JPG into an optimised WEBP."},
        ],
    },
    # --- by target size ---
    {
        "slug": "compress-image-under-1mb", "url_name": "compress_under_1mb", "nav": "Under 1MB",
        "title": "Compress Image to Under 1MB — Free & Instant",
        "description": "Compress any image to under 1MB in your browser, free. Set the target and it hits it automatically — no watermark, no upload, no sign-up.",
        "h1": "Compress an image to under 1MB",
        "tagline": "Set a 1MB target and the compressor hits it automatically — free, private, and processed entirely on your device.",
        "intro": [
            "Lots of forms, uploads and portals cap attachments at 1MB. Instead of guessing at a quality setting, set the target size to 1MB and this tool compresses your image to fit — while keeping it looking as good as possible at that budget.",
            "It works on JPG, PNG and WEBP, handles batches, and never uploads your image, so it's safe for documents and personal photos alike.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Hits the target", "text": "Enter 1MB and it optimises quality to land just under the limit — no trial and error."},
            {"icon": "fa-circle-check", "title": "Upload-ready", "text": "Great for job portals, government forms and sites that reject anything over 1MB."},
            {"icon": "fa-shield-halved", "title": "Private & free", "text": "Runs on your device — nothing uploaded, no watermark, unlimited use."},
        ],
        "faqs": [
            {"q": "How do I compress an image to exactly under 1MB?",
             "a": "Open the compressor, choose the target-size option and enter 1MB. It automatically adjusts the quality to produce a file just under that size."},
            {"q": "Which formats can I use?",
             "a": "JPG, PNG and WEBP. For photos, JPG or WEBP usually reach a small target with the least visible quality loss."},
            {"q": "Is my image uploaded?",
             "a": "No. The whole process runs in your browser, so your image is never sent anywhere."},
        ],
    },
    {
        "slug": "compress-image-under-500kb", "url_name": "compress_under_500kb", "nav": "Under 500KB",
        "title": "Compress Image to Under 500KB — Free Online Tool",
        "description": "Reduce any image to under 500KB in your browser, free. Set the target size and it compresses automatically — no upload, no watermark.",
        "h1": "Compress an image to under 500KB",
        "tagline": "Set a 500KB target and hit it automatically without guessing at quality — free, private, and on-device.",
        "intro": [
            "Plenty of upload forms and websites want images under 500KB for faster loading. Rather than repeatedly re-exporting, set the target to 500KB and let the compressor find the right quality to fit — automatically.",
            "It handles JPG, PNG and WEBP, works on batches, and processes everything in your browser, so nothing is uploaded.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Automatic quality", "text": "Enter 500KB and it tunes compression to land right under the cap."},
            {"icon": "fa-images", "title": "Batch friendly", "text": "Apply the same target to a set of images and export them together."},
            {"icon": "fa-shield-halved", "title": "Nothing uploaded", "text": "On-device compression — free, watermark-free and completely private."},
        ],
        "faqs": [
            {"q": "How do I get an image under 500KB?",
             "a": "Set the target-size option to 500KB in the compressor and it adjusts quality automatically to produce a file below that size."},
            {"q": "Will it look bad at 500KB?",
             "a": "Usually not. Most photos compress well below 500KB with little visible change; the tool preserves as much quality as the size budget allows."},
            {"q": "Is it free?",
             "a": "Yes — free and unlimited, with no watermark and nothing uploaded."},
        ],
    },
    {
        "slug": "compress-image-under-100kb", "url_name": "compress_under_100kb", "nav": "Under 100KB",
        "title": "Compress Image to Under 100KB — Free, No Upload",
        "description": "Compress an image to under 100KB in your browser, free. Ideal for thumbnails, avatars and strict upload limits — no watermark, nothing uploaded.",
        "h1": "Compress an image to under 100KB",
        "tagline": "Squeeze an image under a strict 100KB limit automatically — free, private, and processed on your device.",
        "intro": [
            "Some sites enforce a tight 100KB limit for avatars, thumbnails or ID uploads. Set the target to 100KB and the compressor works out the quality — and, if needed, you can resize the dimensions too for the smallest possible file.",
            "It's all done in the browser with no upload, so it's safe even for photos of documents and IDs.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Meets strict limits", "text": "Reaches tight 100KB caps used by avatars, thumbnails and some ID portals."},
            {"icon": "fa-expand", "title": "Resize to help", "text": "Pair with the resizer to shrink dimensions when compression alone isn't enough."},
            {"icon": "fa-shield-halved", "title": "Private & free", "text": "Everything runs on your device — no upload, no watermark, no limits."},
        ],
        "faqs": [
            {"q": "How can I get an image under 100KB?",
             "a": "Set the target to 100KB in the compressor. For very small limits, also reduce the pixel dimensions with the resizer — smaller dimensions make hitting 100KB much easier."},
            {"q": "Is 100KB enough for a clear image?",
             "a": "For avatars, thumbnails and small photos, yes. For large detailed photos you may need to reduce the dimensions as well to stay under 100KB while looking sharp."},
            {"q": "Does it upload my image?",
             "a": "No — it runs entirely in your browser, so nothing is uploaded."},
        ],
    },
    # --- by use case ---
    {
        "slug": "compress-image-for-email", "url_name": "compress_email", "nav": "For email",
        "title": "Compress Image for Email — Free, Fits Attachment Limits",
        "description": "Compress photos so they fit email attachment limits, free and in your browser. Shrink to under 1MB or 500KB, no watermark, nothing uploaded.",
        "h1": "Compress an image for email",
        "tagline": "Make photos small enough to email without hitting attachment limits — free, private, and processed on your device.",
        "intro": [
            "Camera photos are often several megabytes each, which quickly bumps into email attachment limits or makes messages slow to send and receive. Set a small target size — say 1MB or 500KB — and this tool compresses your photos so they attach and send easily.",
            "You can compress a batch at once and download them together, all without uploading a thing, which keeps personal photos private.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Fits attachment limits", "text": "Target 1MB or 500KB so several photos fit comfortably in one email."},
            {"icon": "fa-images", "title": "Send a batch", "text": "Compress a set of photos in one go and download them as a ZIP to attach."},
            {"icon": "fa-shield-halved", "title": "Stays private", "text": "Compressed in your browser — your photos are never uploaded to a server."},
        ],
        "faqs": [
            {"q": "What size should an email image be?",
             "a": "Aim for under 1MB per image so a few fit within typical 20–25MB mailbox limits and send quickly. For lots of photos, target 500KB each."},
            {"q": "Can I compress several photos for one email?",
             "a": "Yes. Drop in a batch, apply one target size to all of them, and download them together to attach."},
            {"q": "Is it free and private?",
             "a": "Yes — free, no watermark, and nothing is uploaded; the photos are compressed on your device."},
        ],
    },
    {
        "slug": "compress-photo-for-web", "url_name": "compress_web", "nav": "For websites",
        "title": "Compress Photo for Web — Faster Pages, Free & Private",
        "description": "Compress and optimise photos for your website in your browser, free. Smaller files, faster load times and better Core Web Vitals — nothing uploaded.",
        "h1": "Compress a photo for the web",
        "tagline": "Optimise images for fast-loading pages — smaller files, better Core Web Vitals — free, and processed on your device.",
        "intro": [
            "Large images are the most common cause of slow web pages. Compressing your photos — or converting them to WEBP — cuts their file size dramatically, which speeds up load times, improves Core Web Vitals and helps SEO, all without a visible drop in quality.",
            "This runs in your browser, so you can optimise a whole gallery for free without uploading anything or paying per image.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Faster load times", "text": "Smaller images render sooner and improve LCP — better UX and better rankings."},
            {"icon": "fa-arrow-right-arrow-left", "title": "WEBP for the web", "text": "Convert to WEBP for the best size-to-quality ratio on modern sites."},
            {"icon": "fa-shield-halved", "title": "Free & unlimited", "text": "Optimise a whole site's images on your device — no upload, no per-image fee."},
        ],
        "faqs": [
            {"q": "What's the best format for web images?",
             "a": "WEBP for most photos and graphics — it's smaller than JPG and PNG at the same quality and is supported by every modern browser. Use the converter to switch, then compress."},
            {"q": "How much should I compress web images?",
             "a": "Enough that they look clean but load fast — often 100–300KB for large photos. Balance the quality slider against the file size the tool shows."},
            {"q": "Is anything uploaded?",
             "a": "No. All optimisation happens in your browser, so your images stay on your device."},
        ],
    },
    {
        "slug": "compress-image-for-discord", "url_name": "compress_discord", "nav": "For Discord",
        "title": "Compress Image for Discord — Beat the Upload Limit, Free",
        "description": "Compress images to fit Discord's free upload limit in your browser, free. Shrink under 10MB (or 8MB) fast — no watermark, nothing uploaded.",
        "h1": "Compress an image for Discord",
        "tagline": "Get images under Discord's upload limit in seconds — free, private, and processed on your device.",
        "intro": [
            "Discord limits uploads on free accounts, so a high-resolution screenshot or photo can get rejected. Set a target size that fits your server's limit and this tool compresses the image to match — so it uploads first time.",
            "It's handy for sharing screenshots, art and memes without a Nitro subscription, and since nothing is uploaded to us, your images stay private.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Beats the limit", "text": "Target a size under Discord's cap so screenshots and photos upload without Nitro."},
            {"icon": "fa-images", "title": "Screenshots & art", "text": "Great for compressing PNG screenshots and high-res art down to a shareable size."},
            {"icon": "fa-shield-halved", "title": "Private & free", "text": "On-device compression — nothing uploaded, no watermark, unlimited use."},
        ],
        "faqs": [
            {"q": "What's Discord's upload limit?",
             "a": "Free accounts have a per-file limit (commonly 10MB, sometimes lower on older servers). Set a target under that in the compressor and your image will fit."},
            {"q": "How do I compress a screenshot for Discord?",
             "a": "Drop the screenshot in, set a target size below your server's limit, and download the smaller version to upload."},
            {"q": "Is it free?",
             "a": "Yes — free and unlimited, with no watermark and nothing uploaded."},
        ],
    },
    {
        # The only entry whose CTA points at the video converter rather than the
        # image compressor: "compress video online" is a far bigger query than
        # "video converter", and the converter's Small-file quality tier IS a
        # video compressor — this page just says so in the words people search.
        "slug": "compress-video", "url_name": "compress_video", "nav": "Compress Video",
        "cta_url_name": "video_converter",
        "title": "Compress Video Online — Free, Private &amp; No Watermark",
        "description": "Compress an MP4 or WebM video to a smaller file in your browser, free — pick a quality, trim the clip, nothing uploaded. No watermark, no sign-up.",
        "h1": "Compress a video to a smaller size",
        "tagline": "Shrink an MP4 or WebM for chat, email or the web — re-encoded entirely on your device, with nothing uploaded.",
        "intro": [
            "Video files balloon fast — a one-minute phone clip can be a hundred megabytes, far past what chat apps and email accept. This tool re-encodes the clip at a lower bitrate and, if you want, a smaller resolution, cutting the file down to a fraction of its size.",
            "Pick the Small-file quality tier for the biggest saving, cap the size at 720p, and trim away the seconds you don't need — every step runs in your browser, so the video is never uploaded anywhere.",
        ],
        "benefits": [
            {"icon": "fa-compress", "title": "Small-file mode", "text": "A dedicated low-bitrate tier roughly halves the balanced size — made for sharing in chat."},
            {"icon": "fa-crop-simple", "title": "Resize & trim", "text": "Cap the resolution at 720p or 480p and trim to just the part you need before encoding."},
            {"icon": "fa-shield-halved", "title": "Nothing uploaded", "text": "The whole re-encode runs on your device — private, free and watermark-free."},
        ],
        "faqs": [
            {"q": "How do I compress a video without uploading it?",
             "a": "Open the video tool, drop in your MP4, WebM or MOV, choose the Small-file quality tier and convert. The re-encoding runs in your browser — the clip never leaves your device."},
            {"q": "How much smaller will my video get?",
             "a": "The Small-file tier targets roughly half the bitrate of a typical phone recording, and capping the resolution at 720p shrinks it further — together they commonly cut a clip to a quarter of its size or less."},
            {"q": "Will there be a watermark or a time limit?",
             "a": "No watermark and no arbitrary clip limit — it's free and unlimited. Long clips simply take about as long as the trimmed clip runs, because the browser re-encodes in real time."},
        ],
    },
]

COMPRESS_PAGES_BY_SLUG = {p["slug"]: p for p in COMPRESS_PAGES}

# "ClearBG vs <competitor>" comparison pages. People search these queries exactly,
# and the privacy/free angle genuinely wins, so they convert well. Claims about
# competitors are kept general and hedged to each service's public free tier (the
# page also carries a "based on public free tier / not affiliated" disclaimer).
# The existing /remove-bg-alternative/ (views.alternative) stays as the remove.bg
# comparison; these four extend the set. Data-driven via views.comparison.
COMPARISONS = [
    {
        "slug": "tinypng-alternative", "url_name": "cmp_tinypng", "nav": "vs TinyPNG",
        "competitor": "TinyPNG", "cta_url_name": "compress", "cta_icon": "fa-compress",
        "cta_label": "Compress an image free", "cta_note": "No account. Nothing uploaded.",
        "title": "Free TinyPNG Alternative — Compress Images Without Uploading",
        "description": "A free TinyPNG alternative that compresses PNG, JPG and WEBP in your browser — no uploads, no batch limits, no sign-up. See how ClearBG compares.",
        "h1_lead": "The private", "h1_highlight": "TinyPNG alternative",
        "tagline": "Compress PNG, JPG and WEBP just as easily — but in your browser, with no upload, no batch caps and no account.",
        "intro": [
            "TinyPNG is a well-known image compressor, but like most online tools it uploads your images to its servers to shrink them, and its free web tier limits how many images you can do at once. ClearBG compresses right in your browser instead — so your images never leave your device and there's no per-batch limit.",
            "You also get more than compression: convert, resize, remove backgrounds, strip metadata and more, all free and all on-device.",
        ],
        "rows": [
            {"feature": "Your images", "us": "Never uploaded — compressed in-browser", "them": "Uploaded to their servers"},
            {"feature": "Price", "us": "Free & unlimited", "them": "Free tier with limits; paid for more"},
            {"feature": "Batch limit", "us": "No per-batch cap", "them": "Limited images per batch on the free web tool"},
            {"feature": "Formats", "us": "PNG, JPG, WEBP, AVIF", "them": "PNG, JPG, WEBP"},
            {"feature": "Target a file size", "us": "Yes — set an exact KB/MB target", "them": "Automatic only"},
            {"feature": "Other tools", "us": "12+ (background removal, convert, resize…)", "them": "Compression focused"},
            {"feature": "Sign-up", "us": "Never", "them": "Not for web; API needs a key"},
        ],
        "why": [
            {"icon": "fa-lock", "title": "Truly private", "text": "Images are compressed on your device and never uploaded — safe for client work and confidential files."},
            {"icon": "fa-circle-check", "title": "No batch limits", "text": "Compress as many images as you like in one go, free, with no daily or per-batch cap."},
            {"icon": "fa-layer-group", "title": "A whole toolkit", "text": "Convert, resize, remove backgrounds and strip metadata — all free and private, in one place."},
        ],
        "faqs": [
            {"q": "Is ClearBG a free TinyPNG alternative?",
             "a": "Yes. It compresses PNG, JPG and WEBP for free with no batch limits, and unlike TinyPNG it does it in your browser, so your images are never uploaded."},
            {"q": "Does compression quality match TinyPNG?",
             "a": "For most images the visible result is comparable, and ClearBG additionally lets you set an exact target size (e.g. under 500KB) rather than relying on automatic compression only."},
            {"q": "Do I need an account?",
             "a": "No. There's no sign-up and nothing to install — just open the compressor and drop an image."},
        ],
    },
    {
        "slug": "canva-alternative", "url_name": "cmp_canva", "nav": "vs Canva",
        "competitor": "Canva", "cta_url_name": "index", "cta_icon": "fa-wand-magic-sparkles",
        "cta_label": "Remove a background free", "cta_note": "No account. Nothing uploaded.",
        "title": "Free Canva Alternative for Image Tools — No Account, Private",
        "description": "Need Canva's background remover and image tools without a Pro subscription? ClearBG runs free in your browser with nothing uploaded.",
        "h1_lead": "The free, no-account", "h1_highlight": "Canva alternative",
        "tagline": "Remove backgrounds, resize, convert and compress without a Canva account or Pro subscription — all free and private in your browser.",
        "intro": [
            "Canva is a full design suite, but its background remover is a Pro (paid) feature, it requires an account, and your images are stored in its cloud. If you mainly need quick, private image tools, that's a lot of overhead.",
            "ClearBG focuses on doing those image jobs instantly and privately: no login, no subscription, and nothing uploaded. It won't design a poster for you — but for cut-outs, resizing, converting and compressing, it's faster and free.",
        ],
        "rows": [
            {"feature": "Background remover", "us": "Free & unlimited", "them": "Pro (paid) feature"},
            {"feature": "Account", "us": "Not required", "them": "Required"},
            {"feature": "Your images", "us": "Processed on your device", "them": "Stored in their cloud"},
            {"feature": "Price", "us": "Free & unlimited", "them": "Free tier; Pro for many tools"},
            {"feature": "Works offline", "us": "Yes (installable)", "them": "No"},
            {"feature": "Best for", "us": "Fast, private image tasks", "them": "Full graphic design"},
        ],
        "why": [
            {"icon": "fa-circle-check", "title": "No Pro needed", "text": "Background removal and every tool are free — no subscription, no credits, no watermark."},
            {"icon": "fa-lock", "title": "No account, private", "text": "Nothing to sign up for and nothing uploaded — your images stay on your device."},
            {"icon": "fa-globe", "title": "Works offline", "text": "Install it as an app and keep editing images with no connection."},
        ],
        "faqs": [
            {"q": "Is ClearBG's background remover free like Canva's?",
             "a": "ClearBG's is free and unlimited with no account. In Canva, the background remover is a Pro feature that requires a paid plan."},
            {"q": "Can ClearBG replace Canva entirely?",
             "a": "Not for full graphic design — Canva is a design suite. But for background removal, resizing, converting and compressing, ClearBG does those free, privately and often faster."},
            {"q": "Do I need to sign in?",
             "a": "No. There's no account and nothing is uploaded; everything runs in your browser."},
        ],
    },
    {
        "slug": "adobe-express-alternative", "url_name": "cmp_adobe", "nav": "vs Adobe Express",
        "competitor": "Adobe Express", "cta_url_name": "index", "cta_icon": "fa-wand-magic-sparkles",
        "cta_label": "Remove a background free", "cta_note": "No account. Nothing uploaded.",
        "title": "Free Adobe Express Alternative — No Login, No Upload",
        "description": "A free Adobe Express alternative for background removal and image tools — no Adobe account, no upload, in your browser. Compare ClearBG vs Adobe Express.",
        "h1_lead": "The no-login", "h1_highlight": "Adobe Express alternative",
        "tagline": "Remove backgrounds and edit images without an Adobe account — free, private, and entirely in your browser.",
        "intro": [
            "Adobe Express offers background removal and quick edits, but it requires an Adobe account and processes your images in the cloud. For a fast, private cut-out you shouldn't need to log in or hand your photo to a server.",
            "ClearBG does the common image jobs — remove background, convert, resize, compress — on your device, with no account and nothing uploaded.",
        ],
        "rows": [
            {"feature": "Account", "us": "Not required", "them": "Adobe account required"},
            {"feature": "Your images", "us": "Processed on your device", "them": "Uploaded to the cloud"},
            {"feature": "Background remover", "us": "Free & unlimited", "them": "Free tier with limits"},
            {"feature": "Works offline", "us": "Yes (installable)", "them": "No"},
            {"feature": "Sign-up / login", "us": "Never", "them": "Needed to use"},
            {"feature": "Best for", "us": "Quick, private image tasks", "them": "Templated content design"},
        ],
        "why": [
            {"icon": "fa-lock", "title": "No login, private", "text": "No Adobe account and no upload — your images never leave your device."},
            {"icon": "fa-circle-check", "title": "Free & unlimited", "text": "Remove backgrounds and edit as much as you want with no watermark or credits."},
            {"icon": "fa-globe", "title": "Offline capable", "text": "Install ClearBG and it keeps working with no internet connection."},
        ],
        "faqs": [
            {"q": "Can I remove backgrounds without an Adobe account?",
             "a": "Yes — with ClearBG there's no account at all. The AI runs in your browser, so you can remove a background instantly and privately."},
            {"q": "Is ClearBG really free?",
             "a": "Yes, free and unlimited with no watermark. There are no paid tiers gating the core image tools."},
            {"q": "Are my images uploaded like on Adobe Express?",
             "a": "No. Everything is processed on your device, so nothing is uploaded to a server."},
        ],
    },
    {
        "slug": "photoroom-alternative", "url_name": "cmp_photoroom", "nav": "vs Photoroom",
        "competitor": "Photoroom", "cta_url_name": "index", "cta_icon": "fa-wand-magic-sparkles",
        "cta_label": "Remove a background free", "cta_note": "No account. Nothing uploaded.",
        "title": "Free Photoroom Alternative — Full-Res Cut-Outs, No Upload",
        "description": "A free Photoroom alternative that removes backgrounds at full resolution in your browser — no account, no upload, no Pro paywall. Compare ClearBG vs Photoroom.",
        "h1_lead": "The private", "h1_highlight": "Photoroom alternative",
        "tagline": "Remove backgrounds and make clean product shots at full resolution — free, on your device, with no Pro subscription.",
        "intro": [
            "Photoroom is a popular background remover and product-photo app, but it uploads your images, and full-resolution exports, batch and many templates sit behind its Pro plan. ClearBG removes backgrounds at full resolution for free, and does it in your browser so nothing is uploaded.",
            "It includes an eCommerce mode for clean white product shots, plus convert, resize and compress — a private toolkit rather than a subscription app.",
        ],
        "rows": [
            {"feature": "Your images", "us": "Never uploaded — processed on device", "them": "Uploaded to their servers"},
            {"feature": "Full-resolution export", "us": "Free", "them": "Often requires Pro"},
            {"feature": "Price", "us": "Free & unlimited", "them": "Free tier; Pro for full use"},
            {"feature": "Account", "us": "Not required", "them": "Account required"},
            {"feature": "Product / white-background mode", "us": "Free (eCommerce presets)", "them": "Templates, many paid"},
            {"feature": "Works offline", "us": "Yes (installable)", "them": "No"},
        ],
        "why": [
            {"icon": "fa-lock", "title": "Truly private", "text": "Cut-outs are computed on your device — ideal for product shots and client images you can't upload."},
            {"icon": "fa-circle-check", "title": "Full-res, free", "text": "Export full-resolution transparent PNGs with no watermark and no Pro paywall."},
            {"icon": "fa-layer-group", "title": "More than removal", "text": "eCommerce white-background presets, convert, resize and compress — all included free."},
        ],
        "faqs": [
            {"q": "Is ClearBG a free Photoroom alternative?",
             "a": "Yes. It removes backgrounds at full resolution for free, with no account, and runs in your browser so your images aren't uploaded."},
            {"q": "Can I make white-background product photos?",
             "a": "Yes — the eCommerce mode centres your product on pure white at marketplace sizes (Amazon, Etsy, Shopify), free and private."},
            {"q": "Do I have to pay for full-resolution downloads?",
             "a": "No. Full-resolution, watermark-free exports are free in ClearBG."},
        ],
    },
    {
        "slug": "cloudconvert-alternative", "url_name": "cmp_cloudconvert", "nav": "vs CloudConvert",
        "competitor": "CloudConvert", "cta_url_name": "heic", "cta_icon": "fa-mobile-screen",
        "cta_label": "Convert a file free", "cta_note": "No account. Nothing uploaded.",
        "title": "Free CloudConvert Alternative — No Upload, No Limits",
        "description": "A private CloudConvert alternative for images: convert HEIC, PNG, JPG, WEBP and turn PDFs into images in your browser — no upload, no account.",
        "h1_lead": "The private", "h1_highlight": "CloudConvert alternative",
        "tagline": "Convert HEIC, PNG, JPG and WEBP, and turn PDFs into images — in your browser, with no upload, no conversion-minutes cap and no account.",
        "intro": [
            "CloudConvert handles a huge range of formats, but it does the work on its servers: your file is uploaded, the free tier caps how many conversions you can run per day, and an account is needed for more. For the common image jobs — opening iPhone HEIC photos, swapping between PNG/JPG/WEBP, or pulling images out of a PDF — that's more friction (and less privacy) than you need.",
            "ClearBG does those conversions right in your browser. Your files never leave your device, there's no daily minutes limit, and there's nothing to sign up for. It won't convert a spreadsheet or a video codec CloudConvert supports — but for images and PDF pages, it's instant, private and free.",
        ],
        "rows": [
            {"feature": "Your files", "us": "Never uploaded — converted in-browser", "them": "Uploaded to their servers"},
            {"feature": "HEIC → JPG", "us": "Yes, batch, on-device", "them": "Yes, uploaded"},
            {"feature": "PDF → images", "us": "Yes, every page, on-device", "them": "Yes, uploaded"},
            {"feature": "Daily limit", "us": "None", "them": "Free tier caps conversion minutes/day"},
            {"feature": "Account", "us": "Never", "them": "Needed beyond the free allowance"},
            {"feature": "Scope", "us": "Images, PDF pages, SVG, favicons…", "them": "Very broad (docs, audio, video…)"},
            {"feature": "Price", "us": "Free & unlimited", "them": "Free tier; paid packages"},
        ],
        "why": [
            {"icon": "fa-lock", "title": "Files stay on your device", "text": "Conversion runs in the browser — nothing is uploaded, so it's safe for personal photos and confidential documents."},
            {"icon": "fa-mobile-screen", "title": "Built for the iPhone HEIC problem", "text": "Decode the HEIC photos Windows and Android can't open, in a batch, without an account."},
            {"icon": "fa-circle-check", "title": "No daily cap", "text": "Convert as many images or PDF pages as you like, free, with no conversion-minutes limit."},
        ],
        "faqs": [
            {"q": "Is ClearBG a free CloudConvert alternative?",
             "a": "For image and PDF-page conversions, yes: it converts HEIC, PNG, JPG and WEBP and turns PDF pages into images for free, and unlike CloudConvert it does it in your browser so nothing is uploaded. It doesn't cover documents, audio or video formats."},
            {"q": "Can it convert HEIC without uploading?",
             "a": "Yes — the HEIC decoder runs on your device via WebAssembly, so your iPhone photos never leave the browser. Batch conversion and a ZIP download are included."},
            {"q": "Is there a daily conversion limit?",
             "a": "No. There's no per-day cap and no account — the work happens locally, so there's nothing to meter."},
        ],
    },
]

COMPARISONS_BY_SLUG = {p["slug"]: p for p in COMPARISONS}

# Static routes exposed in the sitemap, generated from the same source that
# defines the pages so a new landing page is indexed automatically.
TOOL_PATHS = ["/convert/", "/compress/", "/instagram/", "/crop/", "/favicon-generator/", "/sticker-maker/", "/meme-maker/", "/passport-photo/", "/ecommerce/", "/blur-background/", "/text-behind-image/", "/qr-code-generator/", "/redact-image/", "/exif-remover/", "/resize-image/", "/watermark-image/", "/gif-maker/", "/video-to-gif/", "/video-converter/", "/image-to-pdf/", "/color-palette/", "/collage/", "/add-border/", "/base64-image/", "/screenshot-beautifier/", "/remove-object/", "/photo-filters/", "/upscale/", "/heic-to-jpg/", "/pdf-to-image/", "/image-to-text/", "/svg-to-png/"]
INFO_PATHS = ["/about/", "/privacy/", "/terms/"]
PRIVACY_PATHS = [f"/{p['slug']}/" for p in PRIVACY_PAGES]
COMPRESS_LANDING_PATHS = [f"/{p['slug']}/" for p in COMPRESS_PAGES]
COMPARISON_PATHS = [f"/{p['slug']}/" for p in COMPARISONS]
TOOL_LANDING_PATHS = [f"/{p['slug']}/" for p in TOOL_LANDINGS]
LANDING_PATHS = ["/remove-bg-alternative/"] + PRIVACY_PATHS + COMPRESS_LANDING_PATHS + COMPARISON_PATHS + TOOL_LANDING_PATHS
GUIDE_PATHS = ["/guides/"] + [f"/guides/{g['slug']}/" for g in GUIDES]
SITEMAP_PATHS = (
    ["/"] + TOOL_PATHS
    + [f"/remove-background/{c['slug']}/" for c in USE_CASES]
    + [f"/passport-photo/{c['slug']}/" for c in COUNTRIES]
    + LANDING_PATHS
    + GUIDE_PATHS
    + INFO_PATHS
)

# Paths whose PAGE CONTENT is actually translated — not merely reachable under a
# language prefix. Every path is reachable in every language (i18n_patterns wraps
# the whole URLconf), but only these templates run their body through {% t %};
# the rest render English text inside translated chrome.
#
# This distinction is a ranking problem, not a cosmetic one. Declaring
# hreflang="es" for a page that serves English tells Google a translation exists
# where it doesn't, and lists a near-duplicate of the English page in the
# sitemap. So the alternate set, the sitemap and the canonical are all gated on
# this mapping: untranslated pages stay reachable and keep their translated
# chrome, but they are not advertised in that language and they canonicalise to
# their English twin.
#
# Keyed BY LANGUAGE, because coverage is per language and will diverge: a page
# translated into Spanish first must be advertised in Spanish only. The shared
# starting set is named once rather than repeated four times, so the common case
# stays a single edit and a divergence has to be written deliberately.
#
# ADD A PATH HERE ONLY AFTER ITS TEMPLATE IS TRANSLATED IN THAT LANGUAGE.
# `TranslationCoverageTests` renders each one and fails if the body is not
# actually translated, so an aspirational entry cannot ship.
_CORE_TRANSLATED = frozenset(
    ["/"] + [f"/remove-background/{c['slug']}/" for c in USE_CASES]
    # The seven 1.10 tool pages ship fully translated: body copy via {% t %},
    # FAQ accordion + JSON-LD via translations.localize_faqs.
    + ["/remove-object/", "/photo-filters/", "/upscale/", "/heic-to-jpg/",
       "/pdf-to-image/", "/image-to-text/", "/svg-to-png/"]
    # 1.11 adds the two highest-intent privacy/utility pages on the same terms.
    + ["/resize-image/", "/exif-remover/"]
)

TRANSLATED_PATHS = {lang: _CORE_TRANSLATED for lang in LANGUAGES}


def translated_languages(path):
    """The languages that really have content for `path`, in switcher order.

    `path` may carry a language prefix or not; it is stripped either way, so a
    page can ask this about itself without knowing which language it is being
    served in.
    """
    bare = strip_language(path)
    return [lang for lang in LANGUAGES if bare in TRANSLATED_PATHS[lang]]


def is_translated_path(path, lang=None):
    """True if `path` has real content in `lang`.

    `lang` defaults to the language the path's own prefix names. An unprefixed
    (English) path names none and answers False — English is the source, so
    "is it translated" is not a question about it. A caller holding a root URL
    almost always means "does a translation of this page exist anywhere", which
    is `translated_languages()`; keeping them apart is why one function with one
    language could not survive four.
    """
    lang = lang or path_language(path)
    if lang is None:
        return False
    return strip_language(path) in TRANSLATED_PATHS.get(lang, frozenset())


# --- PWA app shell ----------------------------------------------------------
# What the service worker precaches so the tools work offline. Both lists are
# DERIVED, not hand-written: a hand-maintained shell silently drifted behind the
# tool list (nine tool pages and their JS were missing while /offline-image-editor/
# advertised them as working offline).
SHELL_PAGES = ["/"] + TOOL_PATHS

# Web Workers spawned from a URL the module derives itself — `new URL(
# './compose-worker.js', import.meta.url)` — rather than from `{% static %}`.
# Django's manifest storage rewrites `import` specifiers but not that string, so
# these two are requested under their UNHASHED name; they are precached under
# that name (see shell_runtime_assets in sw.js) and left out of the hashed list,
# which nothing would ever ask for. Both have main-thread fallbacks, so a miss
# only costs speed — but offline exports worked before hashing, and still do.
SHELL_RUNTIME_ASSETS = ["js/compose-worker.js", "js/remove-object-worker.js"]

# Every tool module, found on disk — adding static/js/<tool>.js is enough.
_JS_DIR = Path(__file__).resolve().parent.parent / "static" / "js"
SHELL_ASSETS = (
    [
        f"js/{p.name}"
        for p in sorted(_JS_DIR.glob("*.js"))
        if f"js/{p.name}" not in SHELL_RUNTIME_ASSETS
    ]
    + [
        "css/tailwind.css",
        "css/fontawesome.css",
        "css/inter.css",
        "webfonts/fa-solid-900.woff2",
        "webfonts/fa-regular-400.woff2",
        "webfonts/fa-brands-400.woff2",
        "webfonts/inter/inter-latin.woff2",
        "img/favicon.svg",
        "img/icon-192.png",
        "img/icon-512.png",
    ]
)


# --- Sitemap freshness -------------------------------------------------------
# `lastmod` is only worth emitting if it is true. This used to be `date.today()`
# for all 110 URLs on every request, which tells Google the entire site changes
# daily. Google's response to a sitemap it cannot trust is to ignore the field —
# and then a genuine edit can no longer be signalled, which is exactly when you
# need it.
#
# So these are hand-maintained: when you change a section's COPY, bump its date.
# Chrome changes — nav, footer, a new tool pill — do not count. What a crawler is
# being told about is the page's own content.
#
# Guides are the exception and carry their own date (guides.py `updated`), since
# they are individually authored and individually revised.
CONTENT_UPDATED = {
    "passport": "2026-07-28",      # passport_data.py — country facts verified and corrected
    "use_case": "2026-07-28",      # USE_CASES long-form copy + per-case FAQs
    "deep": "2026-07-28",          # page_content.DEEP — tool and landing long-form copy
    "tool_landing": "2026-07-27",  # TOOL_LANDINGS data, untouched since
    "legal": "2026-07-14",         # privacy + terms prose (dd2e958); later edits were CSS only
    "default": "2026-07-20",       # anything with no content change more recent than this
}

# The legal pages print their own revision date, and the privacy policy states
# that the date "reflects the latest revision" — so it has to be the real one.
# It was `{% now %}`, which claimed a fresh revision every single day.
#
# Formatted here rather than in the template: these pages are English on /pt/
# too, and a template `date` filter localises the month name against the active
# locale, which produced "Julho 14, 2026" in otherwise-English prose.
LEGAL_UPDATED = f"{_date.fromisoformat(CONTENT_UPDATED['legal']):%B %-d, %Y}"


def _sitemap_lastmod(path):
    """The date this page's own content last changed (see CONTENT_UPDATED)."""
    if path.startswith("/guides/") and path != "/guides/":
        guide = GUIDES_BY_SLUG.get(path.strip("/").split("/")[-1])
        if guide is not None:
            return guide["updated_iso"]
    if path.startswith("/passport-photo/") and path != "/passport-photo/":
        return CONTENT_UPDATED["passport"]
    if path.startswith("/remove-background/"):
        return CONTENT_UPDATED["use_case"]
    if path in TOOL_LANDING_PATHS:
        return CONTENT_UPDATED["tool_landing"]
    if path in ("/privacy/", "/terms/"):
        return CONTENT_UPDATED["legal"]
    # A page carrying a long-form block changed when that block was written.
    # Derived from the content itself rather than a parallel list, so the two
    # cannot drift apart.
    try:
        match = resolve(path)
    except Resolver404:
        return CONTENT_UPDATED["default"]
    if deep_for(match.url_name, match.kwargs) is not None:
        return CONTENT_UPDATED["deep"]
    return CONTENT_UPDATED["default"]


def _sitemap_priority(path):
    """Relative importance hint for crawlers (home > tools > landing > info)."""
    if path == "/":
        return "1.0"
    if path in TOOL_PATHS:
        return "0.9"
    if path == "/guides/":
        return "0.8"  # the editorial hub, second only to the tools themselves
    if path in INFO_PATHS:
        return "0.4"
    return "0.7"  # keyword landing + country + guide pages


@require_safe
def index(request):
    """Render the main single-page application."""
    return render(request, "remover/index.html", {
        "faqs": INDEX_FAQS,
        "faq_jsonld": faq_jsonld(INDEX_FAQS),
        "background_groups": BACKGROUND_GROUPS,
    })


@require_safe
def use_case(request, slug):
    """Render a keyword-targeted landing page for a specific audience."""
    case = USE_CASES_BY_SLUG.get(slug)
    if case is None:
        raise Http404("Unknown use case")
    faqs = USE_CASE_FAQS.get(slug, [])
    return render(request, "remover/use_case.html", {
        "case": localize_use_case(case),
        "faqs": faqs,
        "faq_jsonld": faq_jsonld(faqs) if faqs else "",
    })


@require_safe
def privacy_page(request, slug):
    """Render a privacy-angle landing page (hub + 'without uploading' + offline)."""
    page = PRIVACY_PAGES_BY_SLUG.get(slug)
    if page is None:
        raise Http404("Unknown page")
    siblings = [
        {"nav": p["nav"], "url": reverse(f"remover:{p['url_name']}")}
        for p in PRIVACY_PAGES if p["slug"] != slug
    ]
    return render(request, "remover/landing.html", {
        "page": {**page, "benefits_title": "Why it stays private", "siblings_title": "More on privacy"},
        "siblings": siblings,
        "cta_url": reverse(f"remover:{page['cta']['url_name']}"),
        "faqs": page["faqs"],
        "faq_jsonld": faq_jsonld(page["faqs"]),
    })


@require_safe
def tool_landing(request, slug):
    """Render a tool intent-variant landing page (HEIC, OCR, …)."""
    page = TOOL_LANDINGS_BY_SLUG.get(slug)
    if page is None:
        raise Http404("Unknown page")
    siblings = [
        {"nav": p["nav"], "url": reverse(f"remover:{p['url_name']}")}
        for p in TOOL_LANDINGS if p["slug"] != slug
    ]
    return render(request, "remover/landing.html", {
        "page": {**page, "benefits_title": "Why use it", "siblings_title": "Related guides"},
        "siblings": siblings,
        "cta_url": reverse(f"remover:{page['cta']['url_name']}"),
        "faqs": page["faqs"],
        "faq_jsonld": faq_jsonld(page["faqs"]),
    })


@require_safe
def compress_page(request, slug):
    """Render a compress intent-variant landing page (by format / size / use case)."""
    page = COMPRESS_PAGES_BY_SLUG.get(slug)
    if page is None:
        raise Http404("Unknown page")
    siblings = [
        {"nav": p["nav"], "url": reverse(f"remover:{p['url_name']}")}
        for p in COMPRESS_PAGES if p["slug"] != slug
    ]
    return render(request, "remover/landing.html", {
        "page": {**page,
                 "benefits_title": "Why compress with ClearBG",
                 "siblings_title": "More ways to compress",
                 "tools_title": "Related free tools",
                 "tools_subtitle": "Convert, resize or strip metadata — all on your device.",
                 "tools": ["convert", "resize", "exif", "index"],
                 "cta": {"label": "Compress a video now" if page.get("cta_url_name") else "Compress an image now"},
                 "cta_icon": "fa-compress",
                 "cta_title": "Compress your images — free and private",
                 "cta_text": "No upload, no watermark, no sign-up — everything runs in your browser."},
        "siblings": siblings,
        # Most entries funnel to the image compressor; an entry may name another
        # tool (compress-video → the video converter).
        "cta_url": reverse(f"remover:{page.get('cta_url_name', 'compress')}"),
        "faqs": page["faqs"],
        "faq_jsonld": faq_jsonld(page["faqs"]),
    })


@require_safe
def convert(request):
    """Render the client-side image format converter."""
    return render(request, "remover/convert.html", {
        "formats": CONVERT_FORMATS,
        "faqs": CONVERT_FAQS,
        "faq_jsonld": faq_jsonld(CONVERT_FAQS),
    })


@require_safe
def instagram(request):
    """Render the client-side Instagram photo editor."""
    return render(request, "remover/instagram.html", {
        "formats": IG_FORMATS,
        "faqs": INSTAGRAM_FAQS,
        "faq_jsonld": faq_jsonld(INSTAGRAM_FAQS),
    })


@require_safe
def crop(request):
    """Render the standalone client-side crop tool (no background removal)."""
    return render(request, "remover/crop.html", {
        "faqs": CROP_FAQS,
        "faq_jsonld": faq_jsonld(CROP_FAQS),
    })


@require_safe
def favicon_generator(request):
    """Render the client-side favicon / app-icon generator."""
    return render(request, "remover/favicon.html", {
        "faqs": FAVICON_FAQS,
        "faq_jsonld": faq_jsonld(FAVICON_FAQS),
    })


@require_safe
def sticker(request):
    """Render the client-side WhatsApp sticker maker."""
    return render(request, "remover/sticker.html", {
        "faqs": STICKER_FAQS,
        "faq_jsonld": faq_jsonld(STICKER_FAQS),
    })


@require_safe
def compress(request):
    """Render the client-side image compressor."""
    return render(request, "remover/compress.html", {
        "faqs": COMPRESS_FAQS,
        "faq_jsonld": faq_jsonld(COMPRESS_FAQS),
    })


@require_safe
def meme(request):
    """Render the client-side meme generator."""
    return render(request, "remover/meme.html", {
        "faqs": MEME_FAQS,
        "faq_jsonld": faq_jsonld(MEME_FAQS),
    })


@require_safe
def passport(request):
    """Render the client-side passport / ID photo maker."""
    return render(request, "remover/passport.html", {
        "countries": COUNTRIES,
        "faqs": PASSPORT_FAQS,
        "faq_jsonld": faq_jsonld(PASSPORT_FAQS),
        "privacy": PASSPORT_PRIVACY,
    })


@require_safe
def passport_country(request, country):
    """Render a per-country passport-photo landing page (programmatic SEO)."""
    c = COUNTRIES_BY_SLUG.get(country)
    if c is None:
        # A retired near-duplicate page: 301 to the hub so its equity consolidates
        # instead of 404-ing (see passport_data.FOLDED_COUNTRY_SLUGS).
        if country in FOLDED_COUNTRY_SLUGS:
            return redirect(reverse("remover:passport"), permanent=True)
        raise Http404("Unknown country")
    faqs = country_faqs(c)
    # A few sibling countries for internal linking (keeps crawlers moving).
    others = [x for x in COUNTRIES if x["slug"] != country][:8]
    return render(request, "remover/passport_country.html", {
        "country": c,
        "others": others,
        "faqs": faqs,
        "faq_jsonld": faq_jsonld(faqs),
    })


def _guide_tool_links(names):
    """Resolve a guide's `tools` url_names into renderable links.

    Imported lazily: context_processors imports from this module at import time,
    so a module-level import here would be circular. By the time a request is
    served both modules are loaded, and the cost is a dict lookup.

    A name may be a tool (in TOOL_NAV) or one of the privacy landing pages, which
    have their own nav labels; anything else is a typo and `GuideContentTests`
    fails on it rather than silently dropping the link.
    """
    from .context_processors import FOOTER_LABELS, TOOL_NAV

    by_name = {t["name"]: t for t in TOOL_NAV}
    landings = {p["url_name"]: p for p in PRIVACY_PAGES}
    links = []
    for name in names:
        tool = by_name.get(name)
        if tool is not None:
            links.append({
                "url": reverse(f"remover:{name}"),
                "label": FOOTER_LABELS.get(name, tool["label"]),
                "icon": tool["icon"],
                "blurb": tool["blurb"],
            })
            continue
        page = landings.get(name)
        if page is not None:
            links.append({
                "url": reverse(f"remover:{name}"),
                "label": page["nav"],
                "icon": "fa-solid fa-shield-halved",
                "blurb": page["h1"],
            })
    return links


@require_safe
def guides_index(request):
    """Render the guides hub — the site's editorial index, grouped by topic."""
    return render(request, "remover/guides.html", {
        "groups": guides_by_category(),
        "guide_count": len(GUIDES),
    })


@require_safe
def guide_detail(request, slug):
    """Render one guide article."""
    guide = GUIDES_BY_SLUG.get(slug)
    if guide is None:
        raise Http404("Unknown guide")
    return render(request, "remover/guide.html", {
        "guide": guide,
        "guide_tools": _guide_tool_links(guide["tools"]),
        "related_guides": related_guides(slug),
        "faqs": guide["faqs"],
        "faq_jsonld": faq_jsonld(guide["faqs"]),
    })


@require_safe
def ecommerce(request):
    """Render the client-side marketplace (Amazon/Etsy/Shopify) product-photo maker."""
    return render(request, "remover/ecommerce.html", {
        "faqs": ECOMMERCE_FAQS,
        "faq_jsonld": faq_jsonld(ECOMMERCE_FAQS),
    })


@require_safe
def blur(request):
    """Render the client-side AI background-blur (portrait mode) tool."""
    return render(request, "remover/blur.html", {
        "faqs": BLUR_FAQS,
        "faq_jsonld": faq_jsonld(BLUR_FAQS),
    })


@require_safe
def text_behind(request):
    """Render the client-side text-behind-image effect tool."""
    return render(request, "remover/text_behind.html", {
        "faqs": TEXTBEHIND_FAQS,
        "faq_jsonld": faq_jsonld(TEXTBEHIND_FAQS),
    })


@require_safe
def qr(request):
    """Render the client-side QR code generator."""
    return render(request, "remover/qr.html", {
        "faqs": QR_FAQS,
        "faq_jsonld": faq_jsonld(QR_FAQS),
    })


@require_safe
def redact(request):
    """Render the client-side redact / blur (hide faces & info) tool."""
    return render(request, "remover/redact.html", {
        "faqs": REDACT_FAQS,
        "faq_jsonld": faq_jsonld(REDACT_FAQS),
        "privacy": REDACT_PRIVACY,
    })


@require_safe
def watermark(request):
    """Render the client-side watermark tool."""
    return render(request, "remover/watermark.html", {
        "faqs": WATERMARK_FAQS,
        "faq_jsonld": faq_jsonld(WATERMARK_FAQS),
    })


@require_safe
def gif(request):
    """Render the client-side animated GIF maker."""
    return render(request, "remover/gif.html", {
        "faqs": GIF_FAQS,
        "faq_jsonld": faq_jsonld(GIF_FAQS),
    })


@require_safe
def video_gif(request):
    """Render the client-side video → animated GIF converter."""
    return render(request, "remover/video_gif.html", {
        "faqs": VIDEO_GIF_FAQS,
        "faq_jsonld": faq_jsonld(VIDEO_GIF_FAQS),
    })


@require_safe
def video_converter(request):
    """Render the client-side video converter (trim / speed / mute / re-encode)."""
    return render(request, "remover/video_converter.html", {
        "faqs": VIDEO_CONVERTER_FAQS,
        "faq_jsonld": faq_jsonld(VIDEO_CONVERTER_FAQS),
    })


@require_safe
def resize(request):
    """Render the client-side image resizer."""
    return render(request, "remover/resize.html", {
        "faqs": RESIZE_FAQS,
        "faq_jsonld": faq_jsonld(RESIZE_FAQS),
    })


@require_safe
def image_to_pdf(request):
    """Render the client-side image → PDF builder."""
    return render(request, "remover/pdf.html", {
        "faqs": PDF_FAQS,
        "faq_jsonld": faq_jsonld(PDF_FAQS),
    })


@require_safe
def exif(request):
    """Render the client-side EXIF / metadata viewer & remover."""
    return render(request, "remover/exif.html", {
        "faqs": EXIF_FAQS,
        "faq_jsonld": faq_jsonld(EXIF_FAQS),
        "privacy": EXIF_PRIVACY,
    })


@require_safe
def base64_image(request):
    """Render the client-side image ⇄ Base64 data-URI converter."""
    return render(request, "remover/base64.html", {
        "faqs": BASE64_FAQS,
        "faq_jsonld": faq_jsonld(BASE64_FAQS),
    })


@require_safe
def palette(request):
    """Render the client-side colour palette extractor."""
    return render(request, "remover/palette.html", {
        "faqs": PALETTE_FAQS,
        "faq_jsonld": faq_jsonld(PALETTE_FAQS),
    })


@require_safe
def border(request):
    """Render the client-side border / Polaroid frame tool."""
    return render(request, "remover/border.html", {
        "faqs": BORDER_FAQS,
        "faq_jsonld": faq_jsonld(BORDER_FAQS),
    })


@require_safe
def screenshot(request):
    """Render the client-side screenshot beautifier (backdrop / frame / shadow)."""
    return render(request, "remover/screenshot.html", {
        "faqs": SCREENSHOT_FAQS,
        "faq_jsonld": faq_jsonld(SCREENSHOT_FAQS),
    })


@require_safe
def collage(request):
    """Render the client-side collage / photo grid maker."""
    return render(request, "remover/collage.html", {
        "faqs": COLLAGE_FAQS,
        "faq_jsonld": faq_jsonld(COLLAGE_FAQS),
    })


@require_safe
def remove_object(request):
    """Render the client-side object remover (brush + content-aware fill)."""
    return render(request, "remover/remove_object.html", {
        "faqs": localize_faqs(REMOVE_OBJECT_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(REMOVE_OBJECT_FAQS)),
    })


@require_safe
def upscale(request):
    """Render the client-side image upscaler (Lanczos resample + sharpen)."""
    return render(request, "remover/upscale.html", {
        "faqs": localize_faqs(UPSCALE_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(UPSCALE_FAQS)),
    })


@require_safe
def heic(request):
    """Render the client-side HEIC → JPG/PNG/WEBP converter."""
    return render(request, "remover/heic.html", {
        "faqs": localize_faqs(HEIC_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(HEIC_FAQS)),
    })


@require_safe
def pdf_to_image(request):
    """Render the client-side PDF → images extractor."""
    return render(request, "remover/pdf_to_image.html", {
        "faqs": localize_faqs(PDF_TO_IMAGE_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(PDF_TO_IMAGE_FAQS)),
    })


@require_safe
def ocr(request):
    """Render the client-side OCR (copy text from an image) tool."""
    return render(request, "remover/ocr.html", {
        "faqs": localize_faqs(OCR_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(OCR_FAQS)),
    })


@require_safe
def svg_to_png(request):
    """Render the client-side SVG → PNG rasteriser."""
    return render(request, "remover/svg_to_png.html", {
        "faqs": localize_faqs(SVG_TO_PNG_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(SVG_TO_PNG_FAQS)),
    })


@require_safe
def photo_filters(request):
    """Render the client-side photo filters / adjustments editor."""
    return render(request, "remover/photo_filters.html", {
        "faqs": localize_faqs(PHOTO_FILTERS_FAQS),
        "faq_jsonld": faq_jsonld(localize_faqs(PHOTO_FILTERS_FAQS)),
    })


@require_safe
def alternative(request):
    """SEO comparison landing page targeting 'free remove.bg alternative'."""
    # (feature, ClearBG, remove.bg) — based on each service's public free tier.
    rows = [
        ("Price", "Free & unlimited", "Free preview; paid credits for full use"),
        ("Your images", "Never uploaded — processed in-browser", "Uploaded to their servers"),
        ("Full-resolution download", "Free", "Requires paid credits / subscription"),
        ("Watermark", "None", "None"),
        ("Batch processing", "Free", "Paid plans / API"),
        ("Sign-up", "Not required", "Account needed for credits / API"),
        ("Refine / edge brush", "Built in", "Limited"),
        ("Other image tools", "12+ (convert, crop, stickers…)", "Background removal focused"),
    ]
    return render(request, "remover/alternative.html", {
        "rows": rows,
        "faqs": ALTERNATIVE_FAQS,
        "faq_jsonld": faq_jsonld(ALTERNATIVE_FAQS),
    })


@require_safe
def comparison(request, slug):
    """Render a 'ClearBG vs <competitor>' comparison landing page."""
    page = COMPARISONS_BY_SLUG.get(slug)
    if page is None:
        raise Http404("Unknown comparison")
    siblings = [
        {"nav": p["nav"], "url": reverse(f"remover:{p['url_name']}")}
        for p in COMPARISONS if p["slug"] != slug
    ]
    # Link the remove.bg comparison in too, so all five cross-reference.
    siblings.append({"nav": "vs remove.bg", "url": reverse("remover:alternative")})
    return render(request, "remover/comparison.html", {
        "page": page,
        "siblings": siblings,
        "cta_url": reverse(f"remover:{page['cta_url_name']}"),
        "faqs": page["faqs"],
        "faq_jsonld": faq_jsonld(page["faqs"]),
    })


@require_safe
def about(request):
    """Render the About / contact page."""
    return render(request, "remover/about.html")


@require_safe
def privacy(request):
    """Render the privacy policy."""
    return render(request, "remover/privacy.html", {"updated": LEGAL_UPDATED})


@require_safe
def terms(request):
    """Render the terms of use."""
    return render(request, "remover/terms.html", {"updated": LEGAL_UPDATED})


def _upstash(path):
    """Call the Upstash Redis REST API; return the ``result`` value or None."""
    base = settings.UPSTASH_REDIS_REST_URL.rstrip("/")
    token = settings.UPSTASH_REDIS_REST_TOKEN
    if not base or not token:
        return None
    req = urllib.request.Request(f"{base}/{path}", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode()).get("result")
    except Exception as exc:  # network / auth / parse — fail closed, never break the page
        logger.warning("Upstash request failed: %s", exc)
        return None


# Per-tool / per-action conversion counters. Tool + event are validated against
# these whitelists BEFORE they're used to build the Upstash REST key, so a
# malicious client can never inject arbitrary Redis keys/commands via the path.
STATS_EVENTS = {"processed", "downloaded"}
STATS_TOOLS = {
    "home", "blur", "ecommerce", "sticker", "passport",
    "instagram", "crop", "convert", "compress", "meme", "favicon",
    "redact", "exif", "resize", "watermark", "gif", "video_gif", "video_converter", "qr", "text_behind", "pdf",
    "base64", "palette", "border", "collage", "screenshot",
    "remove_object", "photo_filters", "upscale", "heic", "pdf_to_image", "ocr", "svg_to_png",
}


def _stats_ns():
    """Key namespace for the per-tool counters (derived from STATS_KEY)."""
    return (settings.STATS_KEY or "clearbg:processed").split(":", 1)[0]


# How long a weekly bucket lives after its last write. Only the current week is
# ever read, so this just stops old buckets accumulating in the store forever.
STATS_WEEK_TTL = 60 * 60 * 24 * 45


def _as_count(value):
    """A store value as a display integer; a missing key is a count of 0."""
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0


def _upstash_counts():
    """(all-time, this week) in ONE round trip — the badge always shows both."""
    raw = _upstash(f"mget/{settings.STATS_KEY}/{_stats_week_key()}") or [None, None]
    return (raw + [None, None])[:2]


def _stats_week_key():
    """Redis key for this week's counter, e.g. ``clearbg:processed:w:2026-W31``.

    ISO week in UTC (Monday-based), so the bucket rolls over at the same instant
    for everyone rather than following whoever happens to be looking at it.
    """
    year, week, _ = datetime.now(timezone.utc).isocalendar()
    return f"{settings.STATS_KEY}:w:{year}-W{week:02d}"


# Abuse guard for the only public, unauthenticated write endpoint. Without it a
# loop of POSTs could inflate the vanity counter and — the real cost — burn
# Upstash request quota, since every accepted POST is 1-2 REST calls. A
# fixed-window counter in the same store caps accepted writes per client IP.
STATS_POST_LIMIT = 60      # accepted POSTs per IP per window
STATS_POST_WINDOW = 60     # window length, seconds


def _client_ip(request):
    """Best-effort client IP, honouring the proxy's X-Forwarded-For (Vercel).

    Parsed through ``ipaddress`` before it is ever used to build a Redis key:
    X-Forwarded-For is attacker-controlled, so an unfiltered value like
    ``1.2.3.4/flushall`` would inject extra path segments into the Upstash REST
    call, and a varying junk suffix would also mint a fresh rate-limit bucket
    per request. Anything that is not a valid IP collapses to a single shared
    ``unknown`` bucket. (A spoofed *valid* IP per request can still evade the
    limit — inherent to trusting XFF — but this is a vanity-counter speed bump,
    not an auth boundary.)
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    candidate = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return "unknown"


def _stats_rate_limited(request):
    """True if this client IP is over the stats-POST budget for the window.

    Fixed-window counter: INCR a per-IP/per-window key and set its TTL on the
    first hit so it self-expires. Fails OPEN (returns False) whenever Upstash
    can't be reached or returns a non-integer, so a transient store outage
    never blocks the counter instead of merely failing to throttle.
    """
    bucket = int(time.time()) // STATS_POST_WINDOW
    key = f"{_stats_ns()}:rl:{bucket}:{_client_ip(request)}"
    count = _upstash(f"incr/{key}")
    try:
        count = int(count)
    except (ValueError, TypeError):
        return False
    if count == 1:
        _upstash(f"expire/{key}/{STATS_POST_WINDOW}")
    return count > STATS_POST_LIMIT


@csrf_exempt
def stats(request):
    """Global 'images processed' counter + per-tool conversion events (Upstash).

    GET reads the totals (``count`` all-time and ``week``, this ISO week);
    ``GET ?breakdown=1`` returns the per-tool/per-event counts; POST
    ``{"n": <int>, "tool": <str>, "event": <str>}`` increments the global and
    weekly counters (for ``processed`` events) and the validated per-tool
    counter. Returns ``{"enabled": bool, ...}`` — disabled (no number) when
    Upstash isn't configured, so the UI never shows a fabricated figure.
    """
    # `enabled` reflects whether the store is CONFIGURED — not whether the counter
    # has a value yet. A brand-new database has no key, so a read returns nothing;
    # that's a count of 0, not "disabled".
    configured = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)
    if not configured:
        response = JsonResponse({"enabled": False, "count": None})
        response["Cache-Control"] = "no-store"
        return response

    key = settings.STATS_KEY

    # Per-tool breakdown: one MGET over the whitelisted keys (safe, server-built).
    if request.method == "GET" and request.GET.get("breakdown"):
        ns = _stats_ns()
        keys = [f"{ns}:evt:{ev}:{t}" for ev in sorted(STATS_EVENTS) for t in sorted(STATS_TOOLS)]
        raw = _upstash("mget/" + "/".join(keys)) or []
        breakdown = {}
        for k, v in zip(keys, raw):
            name = k.split(":evt:", 1)[1]
            try:
                breakdown[name] = int(v) if v is not None else 0
            except (ValueError, TypeError):
                breakdown[name] = 0
        response = JsonResponse({"enabled": True, "breakdown": breakdown})
        response["Cache-Control"] = "no-store"
        return response

    if request.method == "POST":
        if _stats_rate_limited(request):
            response = JsonResponse(
                {"enabled": True, "count": None, "error": "rate_limited"}, status=429
            )
            response["Cache-Control"] = "no-store"
            return response
        try:
            payload = json.loads(request.body or b"{}")
        except (ValueError, TypeError, json.JSONDecodeError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        try:
            n = int(payload.get("n", 1))
        except (ValueError, TypeError):
            n = 1
        n = max(1, min(n, 50))  # cap: it's a public, unauthenticated vanity counter
        event = payload.get("event", "processed")
        tool = payload.get("tool")
        # The global 'images processed' badge only counts real cut-outs, so it's
        # incremented for 'processed' events (and legacy payloads with no event).
        if event == "processed":
            result = _upstash(f"incrby/{key}/{n}")
            # Same increment against this week's bucket, so the badge can say
            # what has happened recently as well as in total — an all-time number
            # alone says nothing about whether the site is still alive.
            week_key = _stats_week_key()
            week = _upstash(f"incrby/{week_key}/{n}")
            _upstash(f"expire/{week_key}/{STATS_WEEK_TTL}")
        else:
            result, week = _upstash_counts()
        # Per-tool / per-event counter (whitelisted → safe key).
        if event in STATS_EVENTS and tool in STATS_TOOLS:
            _upstash(f"incrby/{_stats_ns()}:evt:{event}:{tool}/{n}")
    else:
        result, week = _upstash_counts()
    response = JsonResponse({
        "enabled": True,
        "count": _as_count(result),
        "week": _as_count(week),
    })
    response["Cache-Control"] = "no-store"
    return response


@require_safe
def healthz(request):
    """Lightweight health check for load balancers and uptime monitors."""
    return HttpResponse("ok", content_type="text/plain")


@require_safe
def service_worker(request):
    """Serve the PWA service worker from the site root so its scope is '/'."""
    response = render(
        request,
        "sw.js",
        {
            "shell_pages": SHELL_PAGES,
            "shell_assets": SHELL_ASSETS,
            "shell_runtime_assets": SHELL_RUNTIME_ASSETS,
        },
        content_type="application/javascript",
    )
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


@require_safe
@cache_control(max_age=86400)
def manifest(request):
    """Serve the web app manifest with the correct content type."""
    return render(request, "manifest.webmanifest", content_type="application/manifest+json")


@require_safe
@cache_control(max_age=3600)
def robots_txt(request):
    """Serve robots.txt, pointing crawlers at the sitemap."""
    return render(
        request,
        "seo/robots.txt",
        {"site_url": settings.SITE_URL.rstrip("/")},
        content_type="text/plain",
    )


@require_safe
def yandex_verify(request):
    """Yandex Webmaster site-ownership verification file (served at the root)."""
    return HttpResponse(
        '<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
        "    </head>\n    <body>Verification: ee6a725348d1a333</body>\n</html>",
        content_type="text/html",
    )


@require_safe
@cache_control(max_age=3600)
def sitemap_xml(request):
    """Serve an XML sitemap for the static routes, with per-URL priority.

    A path is listed once in English plus once per language that really
    translates it, and *every* entry in that cluster carries the full alternate
    set — Google treats a page that names its siblings from only one side as
    unlinked, so the English entry must name the translations and each
    translation must name English and its siblings.

    A path that is merely *reachable* under a language prefix but still renders
    English (see ``TRANSLATED_PATHS``) is listed once, in English, with no
    alternates. Listing it twice submitted a near-duplicate for indexing and
    claimed a translation that does not exist.
    """
    site_url = settings.SITE_URL.rstrip("/")
    urls = []
    for path in SITEMAP_PATHS:
        alt_en = f"{site_url}{path}"
        langs = translated_languages(path)
        # The whole cluster shares one alternate set, so it is built once and
        # attached to each member — including x-default, which always points at
        # English as the version to serve a visitor we can't place.
        alternates = (
            [{"code": "en", "url": alt_en}]
            + [{"code": lang, "url": f"{site_url}/{lang}{path}"} for lang in langs]
            + [{"code": "x-default", "url": alt_en}]
        ) if langs else []
        priority = _sitemap_priority(path)
        lastmod = _sitemap_lastmod(path)
        for loc in [alt_en] + [f"{site_url}/{lang}{path}" for lang in langs]:
            urls.append({
                "loc": loc,
                "alternates": alternates,
                "priority": priority,
                "lastmod": lastmod,
            })
    return render(
        request,
        "seo/sitemap.xml",
        {"urls": urls},
        content_type="application/xml",
    )
