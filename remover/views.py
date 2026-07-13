"""
Views for the background remover.

The heavy lifting (AI background removal) runs client-side, so these views only
render the single-page app and the SEO helper endpoints (robots.txt, sitemap).
"""
import logging

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


# Output formats offered by the converter (all encodable via <canvas>.toBlob).
CONVERT_FORMATS = [
    {"mime": "image/png", "label": "PNG", "ext": "png", "lossy": False, "desc": "Lossless, supports transparency"},
    {"mime": "image/jpeg", "label": "JPG", "ext": "jpg", "lossy": True, "desc": "Small size, no transparency"},
    {"mime": "image/webp", "label": "WEBP", "ext": "webp", "lossy": True, "desc": "Modern, small, supports transparency"},
    {"mime": "image/avif", "label": "AVIF", "ext": "avif", "lossy": True, "desc": "Next-gen, smallest files (Chromium)"},
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
            {"icon": "fa-palette", "title": "Any background color", "text": "Match a brand palette or a plain studio backdrop, then export PNG, JPG or WEBP."},
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
            {"icon": "fa-file-signature", "title": "Document-ready", "text": "Get transparent ink you can drop straight into PDFs, contracts and letters."},
            {"icon": "fa-shield-halved", "title": "Kept private", "text": "Your signature never leaves your device — nothing is sent anywhere."},
            {"icon": "fa-wand-magic-sparkles", "title": "Clean isolation", "text": "Separates ink from paper texture and shadows, with a brush to refine the result."},
        ],
    },
    {
        "slug": "car-photos",
        "nav": "Car photos",
        "title": "Remove Background from Car Photos — Free & Instant",
        "description": "Remove the background from car photos for dealer listings and marketplace ads. Put any vehicle on a clean white or transparent backdrop — free, private, in your browser.",
        "h1": "Remove Backgrounds from Car Photos",
        "tagline": "Give every vehicle a clean, consistent listing shot for your dealership or marketplace ad — free, unlimited, and processed on your device.",
        "intro": [
            "Car listings sell faster when every vehicle sits on a clean, consistent backdrop instead of a cluttered forecourt. This tool cuts the background from your car photos in seconds, so you can drop in pure white or keep a transparent PNG for your template.",
            "Because the AI runs locally in your browser, you can process a whole lot of stock without uploading a single photo, hitting an API limit, or paying per image.",
        ],
        "benefits": [
            {"icon": "fa-car", "title": "Showroom-clean", "text": "Swap a messy forecourt for a spotless studio-style backdrop that keeps the focus on the car."},
            {"icon": "fa-layer-group", "title": "Whole-lot batches", "text": "Drop in dozens of shots at once and download them together as a ZIP."},
            {"icon": "fa-bolt", "title": "Instant & free", "text": "No per-photo cost and no watermark — full-resolution output every time."},
        ],
    },
    {
        "slug": "clothing",
        "nav": "Clothing & fashion",
        "title": "Remove Background from Clothing Photos — Free for Resellers",
        "description": "Remove the background from clothing and fashion photos for Vinted, Depop, Poshmark or your own shop. Clean white or transparent PNGs — free, private, in your browser.",
        "h1": "Remove the Background from Clothing Photos",
        "tagline": "Turn phone snaps of clothes into clean, sellable product shots for Vinted, Depop, Poshmark or your own store — free and unlimited.",
        "intro": [
            "Second-hand and boutique fashion sells faster when every item looks consistent and professional. Upload a photo of a garment and the AI isolates it from your carpet, hanger or wall, so you can place it on clean white or a transparent background.",
            "It all runs in your browser at full resolution, so you can prep an entire wardrobe of listings privately — no uploads, no per-photo fees.",
        ],
        "benefits": [
            {"icon": "fa-shirt", "title": "Sellable in seconds", "text": "Clean cut-outs of tops, dresses and shoes that look at home in any shop grid."},
            {"icon": "fa-tags", "title": "Consistent listings", "text": "Give every item the same tidy backdrop so your storefront looks professional."},
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
            {"icon": "fa-paw", "title": "Great with fur", "text": "Trained to handle soft edges, fur and whiskers for a natural-looking cut-out."},
            {"icon": "fa-wand-magic-sparkles", "title": "Refine by hand", "text": "Tidy leftover background or restore fine detail with the built-in edge brush."},
            {"icon": "fa-heart", "title": "Print & sticker ready", "text": "Full-resolution transparent PNGs for mugs, stickers, prints and memes."},
        ],
    },
    {
        "slug": "youtube-thumbnail",
        "nav": "YouTube thumbnails",
        "title": "Remove Background for YouTube Thumbnails — Free",
        "description": "Cut yourself out of a photo for a click-worthy YouTube thumbnail. Free transparent PNGs to drop over any background — private, in your browser, nothing uploaded.",
        "h1": "Remove Backgrounds for YouTube Thumbnails",
        "tagline": "Cut yourself or your subject out cleanly and drop it over a bold background for thumbnails that get the click — free and unlimited.",
        "intro": [
            "The best-performing thumbnails put a crisp cut-out of a person or product over a punchy background. Upload your shot and the AI removes the background in seconds, giving you a transparent PNG to composite in your thumbnail editor.",
            "It runs entirely in your browser at full resolution, so creators can turn thumbnails around fast — no uploads, no subscriptions, and no watermark.",
        ],
        "benefits": [
            {"icon": "fa-clapperboard", "title": "Made for creators", "text": "Clean cut-outs of you or your subject to pop against any thumbnail background."},
            {"icon": "fa-bolt", "title": "Fast turnaround", "text": "Removes the background in seconds so you can ship the thumbnail and hit publish."},
            {"icon": "fa-crop-simple", "title": "Full quality", "text": "Full-resolution transparent PNGs with no watermark, ready for any editor."},
        ],
    },
]

USE_CASES_BY_SLUG = {case["slug"]: case for case in USE_CASES}

# Affiliate / partner placements per landing page. The URLs are PLACEHOLDERS —
# swap the `?ref=YOURID` links for your real affiliate URLs. Rendered as a
# tasteful "Related services" block on the matching landing page; pages without
# an entry show nothing. Links are marked rel="sponsored" in the template.
PARTNERS = {
    "pet-photos": [
        {"label": "Print on canvas, mugs & stickers", "url": "https://example-print.com/?ref=YOURID", "note": "Turn your cut-out pet into a canvas, mug or sticker sheet.", "icon": "fa-mug-hot"},
    ],
    "product-photos": [
        {"label": "Launch a hosted store", "url": "https://example-store.com/?ref=YOURID", "note": "Open an online shop for your products in minutes.", "icon": "fa-store"},
    ],
    "clothing": [
        {"label": "Print-on-demand apparel", "url": "https://example-print.com/?ref=YOURID", "note": "Turn designs into shirts and hoodies with no inventory.", "icon": "fa-shirt"},
    ],
    "logo": [
        {"label": "Get fast web hosting", "url": "https://example-host.com/?ref=YOURID", "note": "Put your logo on a real website with cheap, fast hosting.", "icon": "fa-server"},
    ],
    "youtube-thumbnail": [
        {"label": "Creator analytics tools", "url": "https://example-tools.com/?ref=YOURID", "note": "Test thumbnails and track what earns the click.", "icon": "fa-chart-line"},
    ],
}

for _case in USE_CASES:
    _case["partners"] = PARTNERS.get(_case["slug"], [])

# Static routes exposed in the sitemap, generated from the same source that
# defines the pages so a new landing page is indexed automatically.
SITEMAP_PATHS = ["/", "/convert/", "/compress/", "/instagram/", "/crop/", "/favicon-generator/", "/sticker-maker/", "/meme-maker/", "/passport-photo/", "/upscale/"] + [f"/remove-background/{c['slug']}/" for c in USE_CASES]


@require_GET
def index(request):
    """Render the main single-page application."""
    return render(request, "remover/index.html")


@require_GET
def use_case(request, slug):
    """Render a keyword-targeted landing page for a specific audience."""
    case = USE_CASES_BY_SLUG.get(slug)
    if case is None:
        raise Http404("Unknown use case")
    return render(request, "remover/use_case.html", {"case": case})


@require_GET
def convert(request):
    """Render the client-side image format converter."""
    return render(request, "remover/convert.html", {"formats": CONVERT_FORMATS})


@require_GET
def instagram(request):
    """Render the client-side Instagram photo editor."""
    return render(request, "remover/instagram.html", {"formats": IG_FORMATS})


@require_GET
def crop(request):
    """Render the standalone client-side crop tool (no background removal)."""
    return render(request, "remover/crop.html")


@require_GET
def favicon_generator(request):
    """Render the client-side favicon / app-icon generator."""
    return render(request, "remover/favicon.html")


@require_GET
def sticker(request):
    """Render the client-side WhatsApp sticker maker."""
    return render(request, "remover/sticker.html")


@require_GET
def compress(request):
    """Render the client-side image compressor."""
    return render(request, "remover/compress.html")


@require_GET
def meme(request):
    """Render the client-side meme generator."""
    return render(request, "remover/meme.html")


@require_GET
def passport(request):
    """Render the client-side passport / ID photo maker."""
    return render(request, "remover/passport.html")


@require_GET
def upscaler(request):
    """Render the client-side AI image upscaler."""
    return render(request, "remover/upscaler.html")


@require_GET
def healthz(request):
    """Lightweight health check for load balancers and uptime monitors."""
    return HttpResponse("ok", content_type="text/plain")


@require_GET
def service_worker(request):
    """Serve the PWA service worker from the site root so its scope is '/'."""
    response = render(request, "sw.js", content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


@require_GET
@cache_control(max_age=86400)
def manifest(request):
    """Serve the web app manifest with the correct content type."""
    return render(request, "manifest.webmanifest", content_type="application/manifest+json")


@require_GET
@cache_control(max_age=3600)
def robots_txt(request):
    """Serve robots.txt, pointing crawlers at the sitemap."""
    return render(
        request,
        "seo/robots.txt",
        {"site_url": settings.SITE_URL.rstrip("/")},
        content_type="text/plain",
    )


@require_GET
@cache_control(max_age=3600)
def sitemap_xml(request):
    """Serve a minimal XML sitemap for the static routes."""
    site_url = settings.SITE_URL.rstrip("/")
    urls = [f"{site_url}{path}" for path in SITEMAP_PATHS]
    return render(
        request,
        "seo/sitemap.xml",
        {"urls": urls},
        content_type="application/xml",
    )
