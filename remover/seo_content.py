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
    {"q": "What's the catch — how can it be free and unlimited?",
     "a": "Your device does the expensive part. Cloud tools rent GPUs by the second and bill per image, so they have to meter you; here the model runs in your browser, so an extra image costs nobody anything. The whole bill is a domain and some cheap hosting, covered by ads on the written guides (the tool pages stay ad-free) and the occasional coffee. There is no account, no trial and no upsell, because there is nothing to upsell."},
    {"q": "Which AI model does it use, and where does it run?",
     "a": "IS-Net, a segmentation model, running through ONNX Runtime Web inside your browser tab. Where WebGPU is available it runs on your graphics card and off the main thread; otherwise it uses WebAssembly with SIMD and threads on the CPU. Browsers that support cross-origin isolation get the full-precision weights, others a smaller quantised build. The model downloads once and is then cached, so later runs work offline."},
    {"q": "What does my device need, and why is the first image slow?",
     "a": "Any modern browser on a device with a bit of memory to spare. The first run downloads the model once — that is the wait you notice — and everything after it is fast because the model is cached. A recent laptop or phone takes a few seconds per image; an older device can take up to a minute and uses the smaller model. If your browser cannot run the model at all, the page tells you instead of hanging, and the tools that need no AI (crop, convert, compress, resize) keep working."},
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

VIDEO_GIF_FAQS = [
    {"q": "Is this video-to-GIF converter free?",
     "a": "Yes — free, unlimited, no sign-up and no watermark. Convert as many clips as you like and export a full-quality animated GIF."},
    {"q": "Is my video uploaded to a server?",
     "a": "No. Your browser decodes the video and encodes the GIF entirely on your device, so the file never leaves your computer. Nothing is uploaded — which matters for private recordings and screen captures."},
    {"q": "Which video formats can I convert?",
     "a": "Any format your browser can play — MP4 (H.264), WebM and most MOV files work everywhere. Because the decoding is done by the browser itself, a few older or unusual codecs may not open; re-saving as MP4 or WebM fixes that."},
    {"q": "Can I trim the video before converting?",
     "a": "Yes — drag the start and end handles to pick the exact section you want. A GIF stores every frame separately, so a shorter clip is the single biggest thing you can do to keep the file small."},
    {"q": "How do I make the GIF smaller?",
     "a": "Trim to a shorter clip, drop the frame rate (5–10 fps is plenty for most GIFs) and choose a smaller output size. GIF size grows with duration, frame rate and dimensions."},
    {"q": "Why doesn't it keep the sound?",
     "a": "GIF is an image format — it has no audio track at all. The converter takes the picture frames only, which is why animated GIFs are always silent."},
]

VIDEO_CONVERTER_FAQS = [
    {"q": "Is this video converter free?",
     "a": "Yes — free, unlimited, no sign-up and no watermark. Trim, change speed, mute and re-encode as many videos as you like."},
    {"q": "Is my video uploaded to a server?",
     "a": "No. Your browser decodes and re-encodes the video entirely on your device, so the file never leaves your computer — nothing is uploaded. That's ideal for private clips and screen recordings."},
    {"q": "Can I convert MOV to MP4?",
     "a": "Yes, as long as your browser can play the source and record MP4 — recent Chrome, Edge and Safari can. Where MP4 recording isn't available the tool falls back to WebM, which plays on every modern browser and website."},
    {"q": "Can I speed up or slow down the video?",
     "a": "Yes — pick from 0.5× up to 2×. Unlike the GIF speed trick, this changes the actual video timing, so the exported file really plays faster or slower (the audio speeds up with it)."},
    {"q": "How can I make the file smaller?",
     "a": "Trim to just the part you need, drop the size to Max 720 or Max 480, and remove the audio if you don't need it. Each of those cuts the file size."},
    {"q": "Why does converting take about as long as the video?",
     "a": "The video is re-encoded by playing it through your browser in real time — that's what lets it work with no upload and no server. A shorter clip, or a faster speed setting, finishes sooner."},
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


BASE64_FAQS = [
    {"q": "Is this Base64 converter free?",
     "a": "Yes — free, unlimited and no sign-up. Encode and decode as many images as you like."},
    {"q": "Are my images uploaded?",
     "a": "No. Both the encode and the decode run entirely in your browser, so the file never leaves your device — safe for private assets."},
    {"q": "When should I use a Base64 data URI?",
     "a": "Inline a small image straight into CSS, HTML or an SVG, embed one inside a JSON payload, or avoid an extra network request for a tiny icon. For large photos a normal file is usually better, since Base64 adds about 33% to the size."},
    {"q": "Can I decode a data URI back to a file?",
     "a": "Yes — switch to Base64 → Image, paste a full data: URI or raw Base64, preview it, and download the original image."},
]

PALETTE_FAQS = [
    {"q": "Is this colour palette tool free?",
     "a": "Yes — free, unlimited and no sign-up. Extract a palette from as many photos as you like."},
    {"q": "Is my photo uploaded?",
     "a": "No. The image is read into a canvas in your browser and the colours are counted locally, so nothing is ever uploaded."},
    {"q": "How are the colours chosen?",
     "a": "The tool counts the most common colours in the image and merges near-duplicates, so the swatches read as a real palette rather than several shades of the same tone. Pick 4 to 12 colours."},
    {"q": "Can I copy an exact pixel colour?",
     "a": "Yes — hover the photo to eyedrop any pixel and click to copy its HEX or RGB value. You can also copy the whole palette as CSS variables."},
]

BORDER_FAQS = [
    {"q": "Is this border and frame tool free?",
     "a": "Yes — free, unlimited, no watermark and no sign-up. Frame as many photos as you like at full quality."},
    {"q": "Is my photo uploaded?",
     "a": "No. The border is drawn onto your photo entirely in your browser, so nothing is ever uploaded."},
    {"q": "What's the Polaroid style?",
     "a": "It wraps the photo in a white frame with a deep captioned bottom edge, like an instant photo. Type a caption and it's centred along the base."},
    {"q": "Can I get rounded corners or a gradient border?",
     "a": "Yes — set any border width and colour, round the corners, or switch on a two-colour gradient with an adjustable angle. Export PNG to keep transparent rounded corners, or JPG on white."},
]

COLLAGE_FAQS = [
    {"q": "Is this collage maker free?",
     "a": "Yes — free, unlimited, no watermark and no sign-up. Combine as many photos as you like."},
    {"q": "Are my photos uploaded?",
     "a": "No. The collage is composited entirely in your browser, so your photos never leave your device."},
    {"q": "Can I choose the layout?",
     "a": "Yes — pick 2 to 5 columns, adjust the gap and corner radius, set a background colour, and choose a square, 4:5, 3:2 or 16:9 output. Each photo is cover-fit so nothing is stretched."},
    {"q": "Can I add or remove photos after starting?",
     "a": "Yes — add more at any time, and remove any tile with the × on its thumbnail. The grid re-flows automatically."},
]

CONVERT_FAQS = [
    {"q": "Which image formats can I convert between?",
     "a": "You can convert between PNG, JPG, WEBP and AVIF in any direction — for example PNG to JPG, JPG to WEBP, or WEBP to PNG. Upload one of those formats and export any of the others."},
    {"q": "What's the difference between PNG, JPG, WEBP and AVIF?",
     "a": "PNG is lossless and supports transparency, which makes it ideal for logos, icons and screenshots. JPG is a small, lossy format best for photographs, but it has no transparency. WEBP and AVIF are modern formats that combine small file sizes with transparency support — AVIF is usually the smallest, WEBP has the widest browser support."},
    {"q": "Will converting reduce my image quality?",
     "a": "Converting to a lossless format like PNG keeps every pixel intact. Converting to a lossy format (JPG, WEBP or AVIF) re-encodes the image, so there can be a small quality change, but you keep the full original resolution — nothing is downscaled."},
    {"q": "Does converting to PNG add transparency to a JPG?",
     "a": "No. Converting a JPG to PNG changes the container, but it can't invent transparency that wasn't in the original — a JPG has a solid background. To make a background transparent you need our background remover, which cuts out the subject first."},
    {"q": "Are my images uploaded to a server?",
     "a": "No. The conversion runs entirely in your browser using the canvas API, so your images never leave your device. There are no upload limits and no per-file cost."},
    {"q": "Can I convert several images at once?",
     "a": "Yes. Drop in a batch of images, pick the output format, and download them together — all processed locally, one after another."},
]

COMPRESS_FAQS = [
    {"q": "How does image compression reduce file size?",
     "a": "Compression re-encodes the image at a lower quality setting and, for photos, discards fine detail the eye barely notices. This tool lets you trade a little quality for a much smaller file, and shows the before/after size so you can pick the sweet spot for your target."},
    {"q": "Will compressing make my image look bad?",
     "a": "Not if you pick a sensible quality level. At 70–85% quality most photos look identical to the original while the file shrinks by 60–80%. You can preview the result and adjust the slider before downloading, so you stay in control."},
    {"q": "What's the best format to compress to?",
     "a": "For photographs, WEBP or AVIF usually give the smallest file at the same visual quality, followed by JPG. For graphics with flat colour or transparency, PNG or WEBP are better. The tool lets you compare formats so you can choose the smallest acceptable file."},
    {"q": "Can I compress an image to a specific size, like under 1MB?",
     "a": "Yes — lower the quality slider until the estimated size drops below your target (for example 1MB, 500KB or 100KB for an email or upload limit). The live size readout updates as you adjust, so you can hit an exact budget."},
    {"q": "Are my images uploaded when I compress them?",
     "a": "No. All compression happens locally in your browser, so your images are never uploaded, stored or seen by anyone. It works offline once the page has loaded."},
    {"q": "Does compressing remove EXIF and location data?",
     "a": "Re-encoding an image typically strips most embedded metadata, including camera info and GPS coordinates. If you specifically want to remove metadata while keeping full quality, use our EXIF remover instead."},
]

CROP_FAQS = [
    {"q": "Is this image cropper free and private?",
     "a": "Yes — it's completely free with no watermark or sign-up, and the crop happens entirely in your browser, so your photo is never uploaded."},
    {"q": "How do I crop an image to a circle?",
     "a": "Choose the circle shape, and the tool masks your photo into a perfect circle with transparent corners. Export it as a PNG to keep the transparency — ideal for profile pictures and avatars."},
    {"q": "Can I crop to a specific aspect ratio?",
     "a": "Yes. Pick a preset ratio like 1:1, 4:5, 16:9 or 9:16, or enter your own custom width:height. The crop box locks to that ratio while you drag and zoom to frame the shot."},
    {"q": "Does cropping reduce the image resolution?",
     "a": "No upscaling ever happens. The download is exported at the native resolution of the cropped region, so you keep every pixel inside the crop at full quality."},
    {"q": "Can I rotate or flip while cropping?",
     "a": "Yes — rotate in 90° steps and flip horizontally or vertically before you export, so a sideways phone photo comes out the right way up."},
    {"q": "What format should I export a cropped image as?",
     "a": "Use PNG for circle or rounded crops so the transparent corners are preserved. Use JPG for a smaller file when you don't need transparency, or AVIF for the smallest file on modern browsers."},
]

INSTAGRAM_FAQS = [
    {"q": "What are the correct Instagram image sizes?",
     "a": "A feed post is 1080×1080 (square) or 1080×1350 (4:5 portrait), a story or reel is 1080×1920 (9:16), and a profile picture is displayed as a circle. This tool fits your photo to whichever size you pick without stretching it."},
    {"q": "Why does Instagram crop my photos?",
     "a": "Instagram fits every image into a fixed aspect ratio and crops whatever doesn't fit. By resizing to the exact ratio first — with the subject framed the way you want — you decide what stays in frame instead of leaving it to Instagram."},
    {"q": "Can I fit a whole photo without cropping it?",
     "a": "Yes. Choose a padded fit and the tool adds a background so the entire photo fits inside the square or portrait frame, with no important edges cut off."},
    {"q": "Is this Instagram resizer free and private?",
     "a": "Yes — free, unlimited and watermark-free, and the resizing runs in your browser, so your photos are never uploaded to a server."},
    {"q": "Does resizing for Instagram lower the quality?",
     "a": "The tool exports at Instagram's recommended pixel dimensions, which keeps images crisp in the feed. Because everything is processed locally at full quality, there's no extra compression beyond what you choose."},
]

FAVICON_FAQS = [
    {"q": "What sizes do I need for a favicon?",
     "a": "A complete set covers 16×16 and 32×32 for browser tabs, 180×180 for the Apple touch icon, and 192×192 and 512×512 for Android and PWA home-screen icons. This generator produces all of them from a single image at once."},
    {"q": "What image should I use to make a favicon?",
     "a": "Use a square image with a bold, simple mark that stays recognisable at 16×16 pixels. A transparent PNG works best so the icon blends into any tab colour, but you can also use a JPG or a logo on a solid background."},
    {"q": "How do I add the favicon to my website?",
     "a": "Download the generated icons, drop them in your site's root or assets folder, and add the accompanying link tags to your HTML head. The tool gives you the exact tags to paste, including the Apple touch icon and web manifest references."},
    {"q": "Is the favicon generator free and private?",
     "a": "Yes — completely free with no sign-up, and every icon size is rendered in your browser, so your source image is never uploaded."},
    {"q": "Can I make an icon for a PWA or app home screen?",
     "a": "Yes. The 192×192 and 512×512 outputs are exactly what a web app manifest needs for the Android and PWA home-screen icons, including a maskable-safe version."},
]

STICKER_FAQS = [
    {"q": "How do I make a WhatsApp or Telegram sticker?",
     "a": "Upload a photo, let the tool cut out the subject and add a white die-cut outline, then export a transparent PNG. WhatsApp stickers should be 512×512 with transparency, which is exactly what this tool produces."},
    {"q": "Do stickers need a transparent background?",
     "a": "Yes. A sticker is the subject only, with everything around it transparent, so it sits cleanly on any chat bubble. The tool removes the background automatically and adds the classic sticker outline."},
    {"q": "Is the sticker maker free and private?",
     "a": "Yes — free, unlimited and watermark-free. The cut-out and outline are generated in your browser, so your photos are never uploaded to a server."},
    {"q": "Can I change the outline thickness or colour?",
     "a": "Yes — adjust the outline width and colour to get the die-cut look you want, from a thin edge to a bold white border."},
    {"q": "What size are the exported stickers?",
     "a": "Stickers export as a square transparent PNG suitable for WhatsApp, Telegram and Signal sticker packs, at full quality with no watermark."},
]

SCREENSHOT_FAQS = [
    {"q": "What does the screenshot beautifier do?",
     "a": "It turns a plain screenshot into a share-ready image: your capture is centred on a colour or gradient backdrop with padding, rounded corners, a soft drop shadow and an optional browser-style window frame — the look you see in product launches, tweets and documentation."},
    {"q": "Is my screenshot uploaded anywhere?",
     "a": "No. The framing is drawn on a canvas in your browser, so the screenshot never leaves your device. That matters for screenshots especially — they often show private dashboards, names or messages."},
    {"q": "Can I add a macOS-style browser window around my screenshot?",
     "a": "Yes — toggle the window frame to add a title bar with the classic three traffic-light dots, in a light or dark style. It's drawn around your image, so nothing in the screenshot is covered."},
    {"q": "What sizes can I export?",
     "a": "Auto keeps the canvas hugging your screenshot plus its padding, or you can pick a fixed 16:9, 4:3 or square canvas — handy for Open Graph images, X/Twitter cards and slide decks. Exports are PNG or JPG at full quality."},
    {"q": "Is it free, and is there a watermark?",
     "a": "Completely free, unlimited and watermark-free — like every ClearBG tool. No account, no credits, no upsell on the export button."},
]

MEME_FAQS = [
    {"q": "Is this meme generator free?",
     "a": "Yes — completely free with no watermark, no sign-up and no limits. Make as many memes as you like."},
    {"q": "Can I add top and bottom text like a classic meme?",
     "a": "Yes. Add the classic bold white top and bottom captions in the traditional Impact style, with an automatic black outline so the text stays readable over any image."},
    {"q": "Are my images uploaded when I make a meme?",
     "a": "No. The meme is drawn entirely in your browser on a canvas, so your image and captions never leave your device."},
    {"q": "Can I use my own photo as a meme template?",
     "a": "Yes — upload any photo or screenshot and add captions to it. You're not limited to preset templates."},
    {"q": "What size does the meme export at?",
     "a": "The meme is exported at the resolution of your source image, so it stays sharp when you share it or post it online."},
]

REMOVE_OBJECT_FAQS = [
    {"q": "How do I remove an object from a photo?",
     "a": "Drop in a photo, brush over the object you want gone, and click Erase. The tool fills the brushed area from the surrounding pixels — all in your browser, in seconds."},
    {"q": "Does it use AI? How good is the result?",
     "a": "It uses a fast content-aware fill that blends the surrounding colours and texture into the erased area. It shines on skies, walls, grass, sand and other even backgrounds; very detailed or patterned backgrounds may need a second, smaller pass."},
    {"q": "Is my photo uploaded anywhere?",
     "a": "No. The whole fill runs on your device — the photo never leaves your browser, which is exactly what you want when editing personal pictures."},
    {"q": "Can I remove people from photos?",
     "a": "Yes — brush over the person and erase. Results are best when the person stands against a relatively even background such as sky, sea, grass or a wall."},
    {"q": "Is it free, and is there a watermark?",
     "a": "Completely free and unlimited, with no watermark and no sign-up — like every ClearBG tool."},
]

UPSCALE_FAQS = [
    {"q": "How does the upscaler enlarge my image?",
     "a": "It resamples the image at 2× or 4× using a high-quality Lanczos filter, then applies a gentle detail-sharpening pass — the same approach professional photo software uses for resizing. It runs instantly in your browser."},
    {"q": "Is this AI super-resolution?",
     "a": "No — and that's deliberate. In-browser AI upscaling models are slow and can freeze the tab on large photos. This tool trades a little of that magic for instant, dependable results at any size, with nothing uploaded."},
    {"q": "What sizes can I upscale to?",
     "a": "Double or quadruple the original, up to a safety cap of 8000 pixels on the longest side so the browser never runs out of memory. Exports are PNG (lossless) or JPG."},
    {"q": "Will an upscaled photo look better than the original?",
     "a": "Upscaling can't invent detail that was never captured, but a well-resampled, lightly sharpened enlargement looks dramatically better than a browser or editor doing a plain stretch — edges stay clean instead of going soft or blocky."},
    {"q": "Is it private and free?",
     "a": "Yes. The resampling runs entirely on your device — nothing is uploaded — and it's free, unlimited and watermark-free."},
]

HEIC_FAQS = [
    {"q": "Why can't I open my iPhone's HEIC photos?",
     "a": "iPhones save photos in HEIC (High Efficiency Image Container) by default. It halves file sizes, but Windows, Android and most websites can't open it — which is why the photo works on your phone and nowhere else. Converting to JPG fixes that instantly."},
    {"q": "How do I convert HEIC to JPG for free?",
     "a": "Drop your .heic files here and download them as JPG (or PNG / WEBP). The conversion happens in your browser — no software to install, no upload, no watermark, no limit."},
    {"q": "Are my photos uploaded to a server?",
     "a": "No. The HEIC decoder runs on your device, so your photos never leave your browser. That matters — personal photos shouldn't have to pass through someone's server just to change format."},
    {"q": "Does converting HEIC lose quality?",
     "a": "The photo is decoded at full resolution and re-encoded at high quality. JPG is slightly lossy by nature, but at this setting the difference is not visible; choose PNG for a lossless export."},
    {"q": "Can I convert many HEIC photos at once?",
     "a": "Yes — drop in a whole batch and download them individually or together as a ZIP."},
]

PDF_TO_IMAGE_FAQS = [
    {"q": "How do I turn a PDF into images?",
     "a": "Drop a PDF here and every page is rendered as a high-resolution image right in your browser. Download single pages as PNG or JPG, or grab all pages at once as a ZIP."},
    {"q": "Is my PDF uploaded anywhere?",
     "a": "No. The PDF is parsed and rendered entirely on your device — important, since PDFs are often contracts, IDs, statements and other private documents."},
    {"q": "What resolution are the exported images?",
     "a": "Pages render at twice their nominal size (roughly 150 DPI) by default, and you can raise it for print-quality output. Text stays sharp because the page is rendered from the vector source, not stretched from a preview."},
    {"q": "Can I extract just one page?",
     "a": "Yes — every page gets its own download button, so you can save exactly the pages you need, or all of them as a ZIP."},
    {"q": "Is it free, with no watermark?",
     "a": "Completely free, unlimited and watermark-free — no sign-up, no page limits, no trial."},
]

OCR_FAQS = [
    {"q": "How do I copy text out of an image?",
     "a": "Drop in a photo or screenshot and the text recogniser reads it right in your browser. The recognised text appears in an editable box — copy it all with one click."},
    {"q": "Is my image uploaded for the text recognition?",
     "a": "No. The OCR engine (Tesseract, the same open-source engine many scanners use) runs on your device via WebAssembly. Screenshots often contain private conversations and documents — they never leave your browser here."},
    {"q": "Which languages does it recognise?",
     "a": "English, Portuguese, Spanish, French and German are offered, and the engine downloads the selected language pack on first use — after that it's cached and works offline."},
    {"q": "How accurate is it?",
     "a": "Very good on clean screenshots and printed documents; harder photos (angles, handwriting, low light) reduce accuracy. Sharp, straight-on images with good contrast recognise best."},
    {"q": "Is it free and unlimited?",
     "a": "Yes — free, unlimited, no watermark, no sign-up. Recognise as many images as you like."},
]

SVG_TO_PNG_FAQS = [
    {"q": "How do I convert an SVG to PNG?",
     "a": "Drop an .svg file here, pick a size (1×, 2×, 4× or an exact pixel width) and download a crisp PNG. The browser rasterises the vector directly, so edges stay perfectly sharp at any scale."},
    {"q": "Why does my SVG export blurry from other tools?",
     "a": "Because they rasterise at the SVG's nominal size and then stretch the bitmap. This tool renders the vector at the exact output size you choose, so a 4× export has 4× the real detail."},
    {"q": "Does it keep transparency?",
     "a": "Yes — PNG exports keep a fully transparent background by default, or you can fill it with any colour. JPG export fills with white automatically."},
    {"q": "Is my SVG uploaded?",
     "a": "No. The file is read and rendered entirely in your browser — nothing is sent to a server."},
    {"q": "What about fonts and embedded images inside the SVG?",
     "a": "SVGs that embed their images and use standard system fonts render exactly. An SVG that references external files or webfonts may render with fallback fonts, since the browser rasterises it in isolation."},
]

PHOTO_FILTERS_FAQS = [
    {"q": "What can I adjust in this photo editor?",
     "a": "One-tap looks (vivid, warm, moody, film, black & white and more) plus manual sliders for brightness, contrast, saturation, warmth, vignette and grain. Hold the compare button any time to check against the original."},
    {"q": "Are the filters applied to the full-quality photo?",
     "a": "Yes. The preview is scaled for speed, but the export re-applies your exact settings to the original at full resolution — no quality loss beyond your chosen format."},
    {"q": "Is my photo uploaded to apply filters?",
     "a": "No. Every adjustment is drawn on a canvas on your device — the photo never leaves your browser."},
    {"q": "Can I fine-tune a preset look?",
     "a": "Yes — tap a look, then adjust any slider on top of it. The look sets a starting point; the sliders always stay in your control."},
    {"q": "Is it free, with no watermark?",
     "a": "Completely free and unlimited with no watermark or sign-up — export as PNG, JPG or WEBP."},
]


# --- "Why this one runs on your device" blocks -------------------------------
# Rendered by remover/partials/privacy_note.html on the three tools where the
# visitor's reason for searching IS the privacy question — stripping GPS from a
# photo, blacking out a document, or making an ID photo. On those pages "nothing
# is uploaded" is the product, not a footnote, so it gets stated in the terms the
# visitor is already worried about rather than left to a badge in the hero.
#
# Keyed by nothing: each view passes its own block, so a page that stops being a
# privacy-first page simply stops including it.
EXIF_PRIVACY = {
    "risk": (
        "A photo straight off a phone usually carries the exact GPS coordinates where it was "
        "taken, the time down to the second, and the device that took it. Uploading it to a "
        "site that strips metadata means handing over all of it first — to the one party you "
        "were trying to hide it from."
    ),
    "answer": (
        "This tool reads and strips that data in the page itself, so the file never leaves "
        "your device."
    ),
    "points": [
        {"icon": "fa-compass", "title": "GPS stays yours",
         "text": "See the coordinates before you remove them — including the home address a holiday photo quietly carries."},
        {"icon": "fa-scissors", "title": "Lossless for JPEG",
         "text": "Metadata segments are dropped and the pixel data is untouched, so stripping costs no quality."},
        {"icon": "fa-globe", "title": "Works offline",
         "text": "Load the page once and it keeps working with the network off — the clearest proof nothing is sent."},
    ],
}

REDACT_PRIVACY = {
    "risk": (
        "The images people redact are the sensitive ones: passports, bank statements, medical "
        "letters, screenshots of private chats. Uploading one to a redaction site means the "
        "un-redacted original sits on someone else's server — the exact version you were "
        "trying to make sure nobody sees."
    ),
    "answer": (
        "Every box, blur and pixelation here is drawn on a canvas in your own browser, and the "
        "original is never transmitted anywhere."
    ),
    "points": [
        {"icon": "fa-eraser", "title": "Really destroyed, not covered",
         "text": "The export is flattened pixels — there is no layer underneath for anyone to peel back later."},
        {"icon": "fa-lock", "title": "Documents never travel",
         "text": "The un-redacted original stays on your device, so there is no copy of it to leak or subpoena."},
        {"icon": "fa-eye", "title": "Check your work",
         "text": "Toggle back to the original before exporting to confirm every sensitive area is actually covered."},
    ],
}

PASSPORT_PRIVACY = {
    "risk": (
        "A passport or visa photo is a biometric portrait tied to your identity documents — the "
        "single image you should be most careful about uploading. Most online ID-photo services "
        "process it on their servers, and many keep it long enough to sell you a print."
    ),
    "answer": (
        "The cut-out, the white backdrop and the exact biometric sizing all happen in your "
        "browser, so your face is never sent to us or to anyone else."
    ),
    "points": [
        {"icon": "fa-ruler-combined", "title": "Exact official sizes",
         "text": "Compliant dimensions at 300 DPI for a long list of countries, measured to each one's own spec."},
        {"icon": "fa-shield-halved", "title": "No face on a server",
         "text": "No account, no upload and no retention — there is no copy of your portrait to store."},
        {"icon": "fa-print", "title": "Print at home or a shop",
         "text": "Export a 6x4 sheet and print it anywhere, instead of paying per photo for the same result."},
    ],
}
