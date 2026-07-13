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

UPSCALER_FAQS = [
    {"q": "How does AI upscaling work?",
     "a": "A neural super-resolution model reconstructs realistic detail as it enlarges the image, giving cleaner edges and textures than a plain resize that just stretches pixels."},
    {"q": "Is the image upscaler free?",
     "a": "Yes — free and unlimited, with no watermark. The model runs on your device's GPU, so there are no per-image limits or costs."},
    {"q": "Are my images uploaded?",
     "a": "No. Upscaling runs locally in your browser using WebGL, so your images never leave your device."},
    {"q": "Should I choose 2× or 4×?",
     "a": "Use 2× for a quick, high-quality bump. 4× enlarges further (it runs two passes) and is best for smaller source images; very large inputs are processed in tiles."},
    {"q": "What's the best input for upscaling?",
     "a": "Smaller, reasonably sharp images upscale fastest and look best. Extremely blurry or heavily compressed images have less detail for the model to recover."},
]
