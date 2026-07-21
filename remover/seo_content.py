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

TEXTBEHIND_FAQS = [
    {"q": "How does the text-behind-image effect work?",
     "a": "The AI cuts your subject out of the photo, then your text is drawn on top of the original background but underneath the subject — so the subject appears to stand in front of the words, like a magazine cover."},
    {"q": "Is it free and private?",
     "a": "Yes. It's completely free with no watermark, and everything — the cut-out and the text layering — happens in your browser. Your photo is never uploaded."},
    {"q": "What photos work best?",
     "a": "Photos with a clear subject (a person, pet or product) that stands out from the background give the strongest depth, since the subject needs to overlap the text convincingly."},
    {"q": "Can I change the font, size, colour and position?",
     "a": "Yes — pick from several display fonts, set the size, colour and opacity, and drag the text anywhere on the image to place it behind your subject."},
]

QR_FAQS = [
    {"q": "Is this QR code generator free?",
     "a": "Yes — free, unlimited, no watermark and no sign-up. The codes are static, so they never expire."},
    {"q": "Do the QR codes expire or track scans?",
     "a": "No. These are static QR codes built entirely in your browser — no redirect, no tracking, nothing uploaded — so they work forever and stay private."},
    {"q": "What can I put in a QR code?",
     "a": "Any text: a website URL, Wi-Fi details, an email address, a phone number, or plain text. Just paste it in and the code updates instantly."},
    {"q": "Can I change the colours and download a vector file?",
     "a": "Yes — set the foreground and background colours and size, then download a crisp PNG or a scalable SVG that stays sharp at any print size."},
]

REDACT_FAQS = [
    {"q": "Is it safe to blur sensitive photos here?",
     "a": "Yes — the whole tool runs in your browser and nothing is uploaded, so faces, license plates, addresses and documents never leave your device."},
    {"q": "Does blurring really hide the information?",
     "a": "Use the Pixelate or Black-bar modes for anything that must stay unreadable — a heavy blur can sometimes be reversed, but a solid bar or coarse pixelation cannot."},
    {"q": "How do I blur a face or a plate?",
     "a": "Just drag a box over each area you want to hide. Add as many boxes as you like, then pick blur, pixelate or a black bar and download."},
    {"q": "Is it free and watermark-free?",
     "a": "Completely free, unlimited and with no watermark — export a full-resolution PNG or JPG."},
]

EXIF_FAQS = [
    {"q": "What is EXIF / photo metadata?",
     "a": "Hidden data your camera or phone saves inside a photo — GPS location, the exact date and time, and the device model. It travels with the file when you share it."},
    {"q": "Is removing it private?",
     "a": "Yes — the photo is read and cleaned entirely in your browser and never uploaded, so even geotagged private photos stay on your device."},
    {"q": "Does removing metadata reduce quality?",
     "a": "No. For JPEGs the metadata is stripped losslessly — the actual image data is untouched, so there's zero quality loss."},
    {"q": "Why remove location data before sharing?",
     "a": "Geotagged photos reveal exactly where they were taken — often your home. Stripping the GPS tag before you post protects your privacy."},
]

RESIZE_FAQS = [
    {"q": "Is this image resizer free?",
     "a": "Yes — free, unlimited, no watermark and no sign-up. Resize as many images as you like."},
    {"q": "Will resizing reduce quality?",
     "a": "Making an image smaller stays crisp. Enlarging past the original size can look soft, since there's no extra detail to add — best results come from scaling down."},
    {"q": "Can I keep the aspect ratio?",
     "a": "Yes. Lock the ratio and changing the width updates the height automatically so the image never looks stretched; unlock it to set exact dimensions."},
    {"q": "Is my image uploaded?",
     "a": "No — resizing happens entirely in your browser, so your images never leave your device."},
]

WATERMARK_FAQS = [
    {"q": "Is this watermark tool free?",
     "a": "Yes — free, unlimited, no sign-up and no watermark from us (only the one you add). Export a full-resolution copy."},
    {"q": "Is my photo uploaded?",
     "a": "No. The watermark is drawn onto your photo entirely in your browser, so nothing is ever uploaded — ideal for unreleased product shots and client work."},
    {"q": "What's the difference between single and tiled?",
     "a": "Single places one watermark where you choose (great for a subtle logo in a corner). Tiled repeats it diagonally across the whole image, which is much harder to crop out."},
    {"q": "Can I change the size, colour and opacity?",
     "a": "Yes — set the text, size, colour, opacity and rotation, and the preview updates live before you download."},
]

GIF_FAQS = [
    {"q": "Is this GIF maker free?",
     "a": "Yes — free, unlimited, no sign-up and no watermark. Add as many frames as you like and export a full-quality animated GIF."},
    {"q": "Are my photos uploaded?",
     "a": "No. The GIF is encoded entirely in your browser, so your photos never leave your device. Nothing is uploaded to a server."},
    {"q": "How many images do I need?",
     "a": "At least two, though three or more makes for a smoother animation. There's no upper limit — but very long GIFs get large, so a handful of frames usually works best."},
    {"q": "Can I change the speed and order?",
     "a": "Yes — set the frame delay to speed the animation up or slow it down, reorder frames, remove any you don't want, and preview the result before downloading."},
    {"q": "Why is my GIF file so big?",
     "a": "GIF is an old format that stores every frame separately, so size grows with frame count and dimensions. Lowering the output size is the most effective way to shrink it."},
    {"q": "Do the images need to be the same size?",
     "a": "No. Frames are fitted onto a canvas of the size you pick, so mixed dimensions and orientations work fine."},
]

PDF_FAQS = [
    {"q": "Is this image-to-PDF converter free?",
     "a": "Yes — free, unlimited, no sign-up and no watermark. Combine as many photos or scans as you like into one PDF."},
    {"q": "Are my images uploaded to make the PDF?",
     "a": "No. The PDF is built entirely in your browser, so your images never leave your device. That matters for the documents people usually convert — IDs, contracts, receipts and payslips."},
    {"q": "Can I combine several images into one PDF?",
     "a": "Yes. Add a batch of images, reorder them, and they become one multi-page PDF in that order — one image per page."},
    {"q": "What page size does it use?",
     "a": "Choose A4, US Letter, or a page that matches each image exactly. With A4 or Letter, each image is centred and scaled to fit inside the margin you set, keeping its aspect ratio."},
    {"q": "Does converting to PDF reduce the quality?",
     "a": "JPEG images are embedded as-is, with no re-encoding, so there's no extra quality loss. PNG images are embedded losslessly."},
    {"q": "Can I convert a scanned document to PDF?",
     "a": "Yes — photograph or scan each page, add them in order, and export a single PDF. Because nothing is uploaded, it's safe for sensitive paperwork."},
]

ALTERNATIVE_FAQS = [
    {"q": "Is ClearBG really a free remove.bg alternative?",
     "a": "Yes — background removal is free and unlimited with no credits, no sign-up and no watermark. You export full-resolution transparent PNGs at no cost."},
    {"q": "Do I have to upload my images like on remove.bg?",
     "a": "No. ClearBG runs the AI entirely in your browser, so your images never leave your device — nothing is uploaded to a server. That's the biggest difference for privacy-sensitive work."},
    {"q": "Is the quality as good?",
     "a": "It uses a modern in-browser segmentation model that handles hair and fine edges well, with a built-in refine brush to touch up any tricky areas — and there's no resolution cap on the free export."},
    {"q": "What else can ClearBG do that remove.bg can't?",
     "a": "Beyond background removal it includes a whole free toolkit — image converter and compressor, crop, Instagram editor, stickers, passport photos, product-photo maker, background blur, a text-behind-image effect, a QR generator and a blur/redact tool — all private and in your browser."},
]
