"""
Views for the background remover.

The heavy lifting (AI background removal) runs client-side, so these views only
render the single-page app and the SEO helper endpoints (robots.txt, sitemap).
"""
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


def faq_jsonld(faqs):
    """Build schema.org FAQPage JSON-LD from the FAQ list.

    Generating this from the same source that renders the visible FAQ keeps the
    structured data and the on-page content from drifting apart. The ``<`` is
    escaped so the payload can never break out of the surrounding <script> tag.
    """
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["q"],
                "acceptedAnswer": {"@type": "Answer", "text": faq["a"]},
            }
            for faq in faqs
        ],
    }
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")

# Static routes exposed in the sitemap. Extend as pages are added.
SITEMAP_PATHS = ["/", "/convert/"]

# Output formats offered by the converter (all encodable via <canvas>.toBlob).
CONVERT_FORMATS = [
    {"mime": "image/png", "label": "PNG", "ext": "png", "lossy": False, "desc": "Lossless, supports transparency"},
    {"mime": "image/jpeg", "label": "JPG", "ext": "jpg", "lossy": True, "desc": "Small size, no transparency"},
    {"mime": "image/webp", "label": "WEBP", "ext": "webp", "lossy": True, "desc": "Modern, small, supports transparency"},
]

# Landing-page content kept here so copy lives in one maintainable place.
FEATURES = [
    {"icon": "fa-bolt", "title": "Instant results", "text": "The AI runs locally and returns a clean cut-out in seconds — no queue, no wait."},
    {"icon": "fa-shield-halved", "title": "Totally private", "text": "Images are processed in your browser and never uploaded to any server."},
    {"icon": "fa-layer-group", "title": "Batch processing", "text": "Drop in many images at once and download them all together as a ZIP."},
    {"icon": "fa-palette", "title": "Custom backgrounds", "text": "Keep it transparent or drop in any solid color, then export PNG, JPG or WEBP."},
    {"icon": "fa-brush", "title": "Refine by hand", "text": "Erase leftover background or restore parts the AI trimmed too far with a soft brush."},
    {"icon": "fa-crop-simple", "title": "Full quality", "text": "Original resolution preserved. No downscaling, no watermark, ever."},
    {"icon": "fa-gift", "title": "Free forever", "text": "No sign-up, no credits, no limits. Open source and free for everyone."},
]

FAQS = [
    {"q": "Is the background remover really free?", "a": "Yes — 100% free with no sign-up, no watermarks, and no limits. Because the AI runs in your browser, there are no per-image costs."},
    {"q": "Are my images uploaded to a server?", "a": "No. All processing happens locally in your browser, so your images never leave your device."},
    {"q": "What image formats are supported?", "a": "Upload JPG, PNG or WEBP. Export a transparent PNG, or a JPG/WEBP with a custom background color."},
    {"q": "Does it reduce image quality?", "a": "No. The result keeps the original resolution with no downscaling and no watermark."},
    {"q": "Why is the first image a little slower?", "a": "The first run downloads the AI model (~40 MB) once. Your browser caches it, so every image after that is fast."},
]


@require_GET
def index(request):
    """Render the main single-page application."""
    return render(
        request,
        "remover/index.html",
        {"features": FEATURES, "faqs": FAQS, "faq_jsonld": faq_jsonld(FAQS)},
    )


@require_GET
def convert(request):
    """Render the client-side image format converter."""
    return render(request, "remover/convert.html", {"formats": CONVERT_FORMATS})


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
@cache_control(max_age=86400)
def robots_txt(request):
    """Serve robots.txt, pointing crawlers at the sitemap."""
    return render(
        request,
        "seo/robots.txt",
        {"site_url": settings.SITE_URL.rstrip("/")},
        content_type="text/plain",
    )


@require_GET
@cache_control(max_age=86400)
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
