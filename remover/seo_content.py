"""
Shared SEO content: FAQ copy and a helper to emit valid FAQPage JSON-LD.

FAQ blocks add real, keyword-rich content to the tool pages and can win rich
results (an expanded FAQ listing) in Google. The visible accordion and the
structured data are rendered from the same source (see
``templates/remover/partials/faq.html``) so they never drift apart.
"""
import json

from django.utils.safestring import mark_safe


def faq_jsonld(faqs):
    """Return a FAQPage JSON-LD string (marked safe) for the given Q&A list."""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            }
            for f in faqs
        ],
    }
    # </script> can't appear in the payload (our answers are plain prose), so a
    # straight dump is safe to inline in a <script type="application/ld+json">.
    return mark_safe(json.dumps(data))


INDEX_FAQS = [
    {"q": "Is this background remover really free?",
     "a": "Yes — completely free and unlimited, with no sign-up, no watermark and no per-image cost. The AI runs in your browser, so there's nothing to pay for."},
    {"q": "Are my images uploaded to a server?",
     "a": "No. Background removal runs entirely on your device, so your images never leave your browser. Nothing is uploaded, stored or seen by anyone."},
    {"q": "What image formats can I use?",
     "a": "You can upload JPG, PNG or WEBP and export a transparent PNG, or a JPG or WEBP. Full resolution is preserved — there's no downscaling."},
    {"q": "Does it work on my phone?",
     "a": "Yes. It works in any modern mobile or desktop browser. On desktop you can also paste an image with Ctrl+V and process several at once."},
    {"q": "Can I remove the background from many images at once?",
     "a": "Yes. Drop in a batch of photos and download them together as a ZIP. You can also apply one image's background and export settings to the whole batch."},
    {"q": "Will I lose quality or get a watermark?",
     "a": "Neither. Exports are full-resolution and never watermarked. PNG output is lossless and keeps clean transparency around hair and soft edges."},
]

PASSPORT_FAQS = [
    {"q": "Is this an official passport photo service?",
     "a": "No — it's a free helper tool. It produces the correct size and a compliant background, but you should always check your government's exact requirements before submitting."},
    {"q": "Which passport photo sizes are supported?",
     "a": "US 2×2 in, EU/Schengen/UK 35×45 mm, Canada 50×70 mm, China 33×48 mm and many more, plus any custom size in millimetres — all exported at 300 DPI."},
    {"q": "Is my photo private?",
     "a": "Yes. The background removal and sizing happen entirely in your browser, so your photo — a sensitive personal document — is never uploaded anywhere."},
    {"q": "Can I print passport photos at home?",
     "a": "Yes. Use the 6×4 inch sheet option to tile several copies onto a single standard print, then order it at any pharmacy or photo kiosk."},
    {"q": "What background do I need?",
     "a": "Most countries require a plain white or light-grey background. The tool removes your original background and drops in a clean, even colour automatically."},
]

ECOMMERCE_FAQS = [
    {"q": "What size should an Amazon product photo be?",
     "a": "Amazon's main image must be on a pure white (RGB 255,255,255) background with the product filling about 85% of the frame. This tool exports 2000×2000 px, which is large enough for Amazon's zoom feature."},
    {"q": "Is this free and private?",
     "a": "Yes. It's completely free with no watermark, and the background removal runs in your browser, so your product photos are never uploaded."},
    {"q": "Can I use it for Etsy and Shopify too?",
     "a": "Yes. Pick Etsy (2000×2000) or Shopify (2048×2048) and the product is centred on white at the right size. You can also export a transparent PNG."},
    {"q": "Can I process a whole catalogue?",
     "a": "Yes — there are no per-image limits or fees. Process as many products as you like, one after another, entirely on your device."},
]

BLUR_FAQS = [
    {"q": "How does the background blur work?",
     "a": "The AI detects your subject and keeps it perfectly sharp while blurring everything behind it, recreating a camera's portrait-mode depth-of-field effect."},
    {"q": "Is it free and private?",
     "a": "Yes. It's free with no watermark, and the whole effect is computed in your browser — your photo is never uploaded."},
    {"q": "What photos work best?",
     "a": "Photos with a clear subject (a person, pet or product) separated from the background work best, just like phone portrait mode."},
    {"q": "Can I control how strong the blur is?",
     "a": "Yes — a slider takes you from a subtle, natural depth effect to a strong, dreamy background blur."},
]
