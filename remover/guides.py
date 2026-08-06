"""
Editorial guides — the site's only non-utility content.

Every other page on ClearBG exists to run a tool. That made the site a toolbox
with landing pages rather than a publication, which is the distinction an ad
network or a search quality reviewer is drawing when it calls a site "thin":
the tool itself is not content, and wrapping it in 130 words of supporting copy
does not make it content.

These guides are the answer to that. Each one is a standalone article that is
useful to someone who never touches a tool on this site — real explanation, real
numbers, and an honest account of the trade-offs, including where our own tools
are the wrong choice. Articles link out to the relevant tools, not the reverse.

House rules, because they are what keep this from decaying into more landing
pages:

* No article may be a rewrite of a tool page. If the substance is "here is what
  our compressor does", it belongs on /compress/.
* Every article must contain something concrete a reader could not guess —
  a measurement, a threshold, a format's actual behaviour, a specific failure.
* Say when a tool is the wrong answer. The redaction guide tells you to retype
  text rather than trust any pixelation, ours included.
* ``GuideContentTests`` enforces the word floor, the uniqueness floor and the
  cross-link integrity, so a thin article cannot quietly ship.
"""
from datetime import date as _date

_WORDS_PER_MINUTE = 225

# Short labels for the footer column, where the full headline does not fit. Kept
# together rather than inline so the whole nav can be read at a glance and scanned
# for overlap. A guide with no entry here raises at import — better than shipping
# a footer link labelled with a 12-word headline.
_NAV_LABELS = {
    "image-formats-explained": "Image formats",
    "product-photography-for-marketplaces": "Product photography",
    "why-passport-photos-are-rejected": "Passport photo rules",
    "what-exif-data-reveals": "Photo metadata",
    "how-image-compression-works": "Image compression",
    "redacting-images-safely": "Safe redaction",
    "transparent-backgrounds-explained": "Transparency",
    "resize-images-without-losing-quality": "Resizing images",
    "image-sizes-for-social-media": "Social media sizes",
    "on-device-vs-cloud-image-tools": "On-device vs cloud",
    "shooting-for-clean-cutouts": "Shooting for cut-outs",
    "colour-profiles-explained": "Colour profiles",
    "heic-and-why-your-photos-will-not-open": "HEIC photos",
    "making-stickers-for-whatsapp-and-telegram": "Chat stickers",
    "qr-codes-that-actually-scan": "QR codes",
    "favicons-that-work-everywhere": "Favicons",
    "gif-versus-video-for-short-clips": "GIF vs video",
    "getting-text-out-of-images-with-ocr": "OCR & text",
}


def _guide(slug, title, h1, description, category, updated, intro, sections,
           takeaways, tools, faqs):
    """One article.

    intro      list of paragraphs, rendered above the contents box
    sections   list of {"h": heading, "p": [paragraphs], "list": [bullets]}
               — "list" optional; headings become the in-page contents links
    takeaways  the summary box; must be genuinely substantive, not a recap
    tools      url_names of tools the article legitimately points at
    """
    # `updated` is an ISO date so the sitemap can use it directly; the human label
    # is derived rather than stored twice, so the two can never disagree.
    updated_date = _date.fromisoformat(updated)
    body = " ".join(
        intro
        + [s["h"] for s in sections]
        + [p for s in sections for p in s.get("p", [])]
        + [b for s in sections for b in s.get("list", [])]
        + takeaways
        + [f["q"] + " " + f["a"] for f in faqs]
    )
    words = len(body.split())
    return {
        "slug": slug,
        "nav": _NAV_LABELS[slug],
        "title": title,
        "h1": h1,
        "description": description,
        "category": category,
        "updated": f"{updated_date:%B %Y}",
        "updated_iso": updated,
        "intro": intro,
        "sections": [{**s, "id": _anchor(s["h"])} for s in sections],
        "takeaways": takeaways,
        "tools": tools,
        "faqs": faqs,
        "words": words,
        "minutes": max(1, round(words / _WORDS_PER_MINUTE)),
    }


def _anchor(heading):
    """A stable in-page anchor id for a section heading."""
    keep = [ch.lower() if ch.isalnum() else "-" for ch in heading]
    slug = "".join(keep)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


GUIDES = [
    _guide(
        slug="image-formats-explained",
        title="PNG vs JPG vs WebP vs AVIF — Which Format to Use and When",
        h1="PNG vs JPG vs WebP vs AVIF: which format should you actually use?",
        description="PNG, JPG, WebP or AVIF? What each format is good at, what it costs you, real file-size numbers, and which to pick for photos, logos and transparency.",
        category="Formats",
        updated="2026-07-28",
        intro=[
            "Most advice about image formats is a decade out of date. It tells you PNG for graphics and JPG for photos, which was excellent guidance in 2010 and leaves a lot of bandwidth on the table now. WebP has been supported in every major browser since 2020, AVIF since 2024, and between them they have changed which answer is right for most images on the web.",
            "This guide covers the four formats worth considering, what each is actually doing to your pixels, and how to pick between them without guessing.",
        ],
        sections=[
            {
                "h": "The one distinction that matters: lossy vs lossless",
                "p": [
                    "Every format below is either lossy or lossless, and some are both. A lossless format reconstructs your original pixels exactly — save, reopen, and every value is identical. A lossy format throws information away permanently in exchange for a much smaller file, betting that you will not miss what it discarded.",
                    "The bet is usually a good one. Lossy compression targets the things human vision is bad at: fine colour detail (we see brightness far more precisely than hue), and high-frequency variation in busy areas. A photograph of a beach can lose 90% of its data and look untouched. A screenshot of text cannot lose 10% without visible damage, because text is nothing but high-frequency edges.",
                    "That single fact — that lossy compression fails on sharp edges and succeeds on organic texture — predicts nearly every format decision you will make.",
                ],
            },
            {
                "h": "JPG: still the safe default for photographs",
                "p": [
                    "JPEG is from 1992 and remains the most compatible image format in existence. Anything that can display an image can display a JPG, which is why it stays the right answer for email attachments, print shops, forms that specify a format, and any workflow where you do not control the other end.",
                    "It is lossy only, so it cannot store transparency and cannot survive repeated editing. Every time you open a JPG, change something and re-save, it re-compresses from the already-compressed data and loses a little more. Do that ten times and the damage is obvious — blocky patches around edges and colour banding in skies. Keep an original in a lossless format if you expect to edit repeatedly.",
                    "JPEG's other weakness is the one implied above: it is poor at sharp edges. Text and line art in a JPG pick up 'mosquito noise', a faint halo of speckle around each edge. If your image is mostly text, JPG is the wrong format regardless of file size.",
                ],
            },
            {
                "h": "PNG: for transparency and for pixels you cannot lose",
                "p": [
                    "PNG is lossless, supports full alpha transparency, and is the correct choice whenever an image has hard edges: logos, icons, diagrams, screenshots with text, and anything with a transparent background.",
                    "The cost is size. A lossless photograph in PNG is routinely five to ten times larger than a visually identical JPG — a 3 MB JPG might be 20 MB as a PNG with no perceptible gain. PNG compression works by finding repeated patterns, and photographs, being noisy, have very few. This is the single most common image mistake on the web: a photograph saved as PNG because someone read that PNG is 'higher quality'.",
                    "PNG is at its best where its compression has something to grip. A screenshot of a code editor, with large flat areas of one colour, compresses beautifully. A logo with six colours compresses to almost nothing.",
                ],
                "list": [
                    "Use PNG when the image needs a transparent background.",
                    "Use PNG for screenshots that contain readable text.",
                    "Use PNG for logos, icons and flat-colour illustrations.",
                    "Do not use PNG for photographs unless you need a lossless master.",
                ],
            },
            {
                "h": "WebP: the sensible modern default for the web",
                "p": [
                    "WebP does both lossy and lossless, supports transparency and animation, and is supported by every browser in current use. In lossy mode it typically produces files 25–35% smaller than a JPG of equivalent visual quality. In lossless mode it beats PNG by roughly 20–25%.",
                    "The important capability that neither of its predecessors has is lossy compression with an alpha channel. A cut-out product photo on a transparent background had to be PNG before WebP, and was therefore large. As lossy WebP it can be a fraction of the size while looking the same — which is why a cut-out destined for a web page is usually best exported as WebP.",
                    "The reason to hesitate is compatibility outside the browser. Older desktop software, some print workflows, and a surprising number of upload forms still reject WebP. It is the right default for images you serve on a site, and the wrong default for images you hand to someone else.",
                ],
            },
            {
                "h": "AVIF: the best compression, with real caveats",
                "p": [
                    "AVIF is derived from the AV1 video codec and compresses harder than anything else in mainstream use — commonly 50% smaller than JPG at matched quality, and noticeably better than WebP at low bitrates, where it degrades into soft blur rather than blocky artefacts.",
                    "It has two practical costs. Encoding is slow: an AVIF can take several seconds where a JPG takes milliseconds, which matters when you are converting hundreds of images or working in a browser tab. And support, while good in browsers, is thinner than WebP everywhere else.",
                    "AVIF is worth it for large hero images and photo galleries where the bandwidth saving is real and the encode happens once. For a thumbnail, the saving is a few kilobytes and not worth the encode time.",
                ],
            },
            {
                "h": "What to actually pick",
                "p": [
                    "Roughly, in order of how often each situation comes up:",
                ],
                "list": [
                    "Photograph on your own website → WebP, with a JPG fallback if you support very old clients.",
                    "Photograph you are sending to someone → JPG, because it always works.",
                    "Large hero image or photo gallery → AVIF, if you can afford the encode.",
                    "Anything with a transparent background, for the web → lossy WebP.",
                    "Anything with a transparent background, for someone else → PNG.",
                    "Screenshot with text → PNG, or lossless WebP if it stays on your site.",
                    "Logo or icon → SVG if you have the vector; PNG if you only have pixels.",
                    "Master copy you will edit again → PNG or the original camera file, never JPG.",
                ],
            },
            {
                "h": "A note on quality settings",
                "p": [
                    "Most tools express lossy compression as a 0–100 quality number, and the scale is badly non-linear. The range from 100 down to about 85 costs you almost nothing visible while removing a large fraction of the file size. Below about 60, artefacts become obvious on most images. Between 75 and 85 is where the great majority of web images should sit, and going above 90 is nearly always wasted bytes.",
                    "The exception is images with sharp edges or large flat colour areas, where artefacts show up much earlier. If you are compressing a screenshot or an illustration and it must stay lossy, start at 90 rather than 80.",
                ],
            },
        ],
        takeaways=[
            "Lossy compression fails on sharp edges and excels on organic texture — that one fact drives most format choices.",
            "Never save a photograph as PNG to preserve quality; you get a file five to ten times larger with no visible gain.",
            "WebP is the modern default for the web, including for transparency, where it replaces large PNGs with small lossy files.",
            "AVIF compresses best but encodes slowly — reserve it for large images where the bandwidth saving is worth it.",
            "Quality 75–85 is the right band for most lossy exports; above 90 is usually wasted bytes.",
        ],
        tools=["convert", "compress"],
        faqs=[
            {"q": "Is WebP worse quality than PNG?",
             "a": "Not inherently. WebP has a lossless mode that preserves pixels exactly, like PNG, and compresses about 20–25% better. The confusion comes from lossy WebP, which does discard data — but that is a mode you choose, not a property of the format."},
            {"q": "Why is my PNG so large?",
             "a": "Almost certainly because it is a photograph. PNG compresses by finding repeated patterns, and photographs have very few, so it stores something close to the raw pixel data. Convert it to JPG or WebP and expect it to shrink by 80–90%."},
            {"q": "Does converting between formats lose quality?",
             "a": "Converting to a lossless format (PNG, lossless WebP) does not. Converting to a lossy format (JPG, lossy WebP, AVIF) does, and converting between two lossy formats loses data twice — once when the original was made, again on re-encode. Always convert from the highest-quality copy you have."},
            {"q": "Should I still provide JPG fallbacks for WebP?",
             "a": "For browsers, no — WebP support has been universal since 2020. For anything outside a browser, yes: plenty of desktop software, print workflows and upload forms still reject WebP."},
        ],
    ),
    _guide(
        slug="product-photography-for-marketplaces",
        title="How to Photograph Products for Amazon, eBay and Etsy",
        h1="How to photograph products for Amazon, eBay and Etsy",
        description="What marketplace image rules require, how to light a product with two lamps and a sheet of paper, and the shot list that converts — no studio needed.",
        category="Photography",
        updated="2026-07-28",
        intro=[
            "Marketplace product photography is a constrained problem, which is good news: there is a right answer, and it does not require expensive equipment. The main image rules are strict and published, buyers respond to a predictable set of shots, and the difference between a listing that converts and one that does not is usually lighting rather than camera.",
            "This guide covers what the platforms require, how to build a workable setup at home, and the shot list worth photographing once you have one.",
        ],
        sections=[
            {
                "h": "What the platforms actually require",
                "p": [
                    "The rules differ in detail but converge on the same idea: the main image is a clean, honest representation of the product on a plain background, and everything else is up to you.",
                    "Amazon is the strictest. The main image must be on a pure white background (RGB 255,255,255), the product must fill about 85% of the frame, and there must be no text, watermarks, logos, borders, props or additional items that are not part of what you are selling. Images should be at least 1600 pixels on the longest side so zoom works, and it is worth exceeding that. Additional images are much more permissive — lifestyle shots, props and infographics are all fine there.",
                    "eBay requires a minimum of 500 pixels on the longest side, prohibits added text and borders on the main image, and prefers a plain background without mandating pure white. Etsy is the most relaxed, with no background requirement at all, and a marketplace culture that rewards styled lifestyle photography over clinical cut-outs.",
                    "The practical consequence: shoot once against white, and you can meet Amazon's rule and satisfy the others. Shoot styled-only and you cannot list on Amazon without reshooting.",
                ],
            },
            {
                "h": "Lighting is the whole game",
                "p": [
                    "If your product photos look amateurish, the cause is almost always lighting, not your camera. A modern phone has more than enough sensor for product work; what it cannot do is invent soft, even light that is not there.",
                    "The property you want is 'soft' light — light from a large source relative to the subject. A bare bulb is a small source and produces hard, black-edged shadows. The same bulb fired through a sheet of tracing paper becomes a large source and produces a gentle shadow gradient. This is the entire principle behind every softbox and light tent ever sold.",
                    "A setup that genuinely works, for very little money: two desk lamps with the same colour temperature bulbs, one on each side at roughly 45 degrees to the product, each shooting through a sheet of baking parchment or tracing paper clipped a few inches in front. A sheet of white card curved up behind the product gives you a seamless background with no visible corner. Turn off the room lights, so you are not mixing colour temperatures.",
                    "Mixing colour temperatures is the most common self-inflicted problem: daylight from a window is around 5500K and a warm domestic bulb is around 2700K, and a photo lit by both has an orange side and a blue side that no white balance setting can fix simultaneously. Pick one light source type and commit.",
                ],
            },
            {
                "h": "Camera settings that matter",
                "p": [
                    "Three things are worth controlling, and the rest can be left alone.",
                    "Shoot from a tripod or a stable surface. Product shots benefit from small apertures for depth of field, which means slower shutter speeds, which means camera shake. A phone propped against a stack of books is fine.",
                    "Lock your white balance rather than leaving it automatic, so a series of shots matches. If you are shooting on a phone, this may mean using a manual camera app — worth it if you are photographing a catalogue.",
                    "Do not shoot from too close. Wide-angle lenses at short distances distort — a mug photographed from 20 cm has a bulging front and a shrunken handle. Back up and zoom in slightly; perspective flattens and the product looks like itself.",
                ],
            },
            {
                "h": "The shot list that converts",
                "p": [
                    "Buyers are trying to answer specific questions, and each image should answer one. In rough order of value:",
                ],
                "list": [
                    "The main shot: product filling the frame on white, straight-on or at a slight three-quarter angle.",
                    "Scale: the product next to something universally recognisable, or held in a hand. This prevents the single most common return reason — 'smaller than I expected'.",
                    "Detail: a close crop of texture, stitching, material or finish. This is where quality is communicated.",
                    "In use: the product doing its job, in the context a buyer imagines it in.",
                    "What's in the box: everything the buyer receives, laid out flat.",
                    "The imperfections, if you are selling used. Photographing the flaw honestly reduces returns and disputes far more than it costs you in sales.",
                ],
            },
            {
                "h": "Getting a genuinely white background",
                "p": [
                    "Even with white card and good lighting, the background in your photo will not be pure white — it will be a light grey, somewhere around 240,240,240, because the card is reflecting less light than a perfect white. Amazon wants 255,255,255.",
                    "There are two ways to close that gap. The photographic way is to light the background separately and slightly brighter than the product, so it blows out to pure white in camera. This is what studios do and it produces the most natural result, because the product keeps its own soft shadow.",
                    "The practical way is to remove the background afterwards and composite the product onto pure white. This is faster, works with any photo, and is what most home sellers do. The thing to watch is edge quality: a cut-out with a hard, jagged edge or a faint halo of the old background reads as fake and is the main way an edited photo looks edited. Hair, fur, transparent materials and fine detail like wicker are where automatic tools struggle most, and where it is worth checking the result at full zoom before you list.",
                    "Our own tools for this are the background remover for the cut-out and the marketplace preset in the eCommerce tool, which composites onto pure white at the aspect ratios Amazon and eBay expect. Both run in your browser, so a full catalogue does not go through anyone's server.",
                ],
            },
            {
                "h": "Common mistakes",
                "p": [
                    "In rough order of how much damage they do:",
                ],
                "list": [
                    "Shooting under mixed lighting, giving the product two different colours.",
                    "A background that is visibly grey rather than white, which looks dingy next to competitors.",
                    "No scale reference anywhere in the listing.",
                    "Over-editing the colour, so the product arrives looking different and gets returned.",
                    "Cut-outs with hard or haloed edges from an unchecked automatic removal.",
                    "Uploading at the minimum resolution, so the zoom view is soft.",
                ],
            },
        ],
        takeaways=[
            "Amazon's main image rule — pure white, 85% frame fill, no text or props — is the strictest, so shooting for it satisfies every other marketplace too.",
            "Soft light comes from a large source: two lamps fired through baking parchment beats any camera upgrade.",
            "Never mix daylight and domestic bulbs in one shot; no white balance setting can correct both halves.",
            "Include a scale reference — 'smaller than expected' is the most common return reason in every category.",
            "Check cut-out edges at full zoom before listing; haloes and jagged edges are what make an edited photo look edited.",
        ],
        tools=["ecommerce", "index", "resize", "compress"],
        faqs=[
            {"q": "Do I need a DSLR for product photography?",
             "a": "No. A recent phone has ample resolution and dynamic range for marketplace listings. Lighting, background and framing account for nearly all of the visible difference between amateur and professional product shots."},
            {"q": "What size should marketplace product images be?",
             "a": "At least 1600 pixels on the longest side for Amazon, which is the threshold where zoom activates; 2000+ is better. eBay's minimum is 500 but that is far too small to be competitive. Shoot at full resolution and downscale, never the reverse."},
            {"q": "Can I use a lifestyle photo as my Amazon main image?",
             "a": "No. The main image must be the product alone on pure white with no props, text or additional items. Lifestyle shots are allowed and encouraged in the additional image slots."},
            {"q": "Is it against the rules to remove the background digitally?",
             "a": "No. Marketplaces require an accurate representation of the product, not an unedited photograph. Removing the background and compositing onto white is standard practice. Altering the product's colour or shape is not."},
        ],
    ),
    _guide(
        slug="why-passport-photos-are-rejected",
        title="Why Passport Photos Get Rejected — And How to Avoid It",
        h1="Why passport photos get rejected, and how to avoid it",
        description="The real reasons passport and visa photos come back — head size, shadows, glasses, expression — plus how to shoot a compliant one at home.",
        category="Documents",
        updated="2026-07-28",
        intro=[
            "A rejected passport photo costs weeks, and the reasons are more mechanical than most applicants expect. Modern passport photos are not judged by eye in the first instance; they are checked against a biometric standard by software, and the software cares about a specific and slightly unintuitive list of things.",
            "This guide covers what that standard is, the failures that actually happen, and how to shoot something compliant without a studio.",
        ],
        sections=[
            {
                "h": "The photo is a biometric template, not a portrait",
                "p": [
                    "Almost every country's passport photo requirements derive from ICAO Document 9303, the international standard for machine-readable travel documents. The photo on the page and in the chip is intended to work with automated face recognition at borders, which is why the rules are shaped the way they are.",
                    "Face recognition works by locating landmarks — the pupils, the nose, the corners of the mouth and jaw — and measuring the distances between them. Anything that obscures a landmark or distorts a distance breaks the template. A neutral expression is required because smiling moves the mouth corners and changes the jawline. Glasses are restricted because reflections hide the pupils. Head tilt matters because it changes the apparent distance between features.",
                    "Understanding this reframes the whole exercise. You are not trying to look good; you are trying to present a clean, undistorted, well-lit set of facial landmarks. Some of the rules that seem arbitrary — no smiling, hair off the face, both ears visible where possible — all follow from that one purpose.",
                ],
            },
            {
                "h": "Head size: the most common failure",
                "p": [
                    "More photos are rejected for head size than anything else, and it is the hardest requirement to judge by eye.",
                    "The measurement is from the bottom of the chin to the top of the head — the crown, including hair volume, not the top of the forehead. Most countries following the international standard want that distance to be 32–36 mm within a 35 × 45 mm frame, which is about 70–80% of the frame height. The UK is tighter at 29–34 mm. Canada wants 31–36 mm within its larger 50 × 70 mm frame. The United States measures differently again, wanting 25–35 mm within a 51 × 51 mm square, which leaves visibly more space around the head than the European convention.",
                    "The practical consequence is that photos cannot be moved between countries. A compliant UK photo cropped down to US dimensions has a head that is too large, and a US photo enlarged to European dimensions has one that is too small. If you are applying to two countries, frame each one separately.",
                    "The second consequence is that self-taken photos usually fail high rather than low: people fill the frame with their face the way they would for a profile picture, and end up 10 mm over. Shoot wider than feels right and crop precisely afterwards.",
                ],
            },
            {
                "h": "Shadows, and why the wall matters",
                "p": [
                    "The second most common failure is a shadow — either on the face, or cast onto the background behind the head. Both come from the same cause: standing too close to the wall with light coming from in front of you.",
                    "The fix is distance. Stand at least a metre away from the background, ideally more. Your shadow then falls on the floor behind you rather than onto the wall in the frame. This single change eliminates most background shadow problems.",
                    "For light on the face, the enemy is a single hard source, especially overhead. Ceiling lights produce dark eye sockets and a shadow under the nose and chin. The best free light source is an overcast day through a large window, with the subject facing the window. Overcast sky is an enormous, even, soft source and is very hard to beat. Direct sunlight is the opposite — small, hard and contrasty — and causes squinting.",
                ],
            },
            {
                "h": "Glasses, expression and headwear",
                "p": [
                    "The rules here vary more by country than any other category, and assuming your country follows the one you read about is a good way to be rejected.",
                    "The United States has banned glasses in passport photos since November 2016, with an exception only for documented medical reasons. China bans them for visa photos with no exception. Australia asks you to remove them. Canada, by contrast, permits them as long as the eyes are clearly visible with no glare and no tint. The UK discourages them but does not forbid them.",
                    "Given that spread, the safe move is simply to take them off, unless you are in one of the countries that allows them and you have a reason to keep them on.",
                    "Expression rules are more consistent: neutral, mouth closed, both eyes open, looking straight at the camera. The US is the notable outlier in explicitly allowing a natural, unforced smile. The UK is explicit that you must not smile at all. When in doubt, neutral is accepted everywhere.",
                    "Headwear is permitted essentially everywhere for religious or medical reasons, and essentially nowhere otherwise. Where it is worn, the full face from the bottom of the chin to the top of the forehead must be visible, and the covering must not cast a shadow across the face.",
                ],
            },
            {
                "h": "The rules for babies that surprise people",
                "p": [
                    "Infants get latitude on expression and gaze — most countries accept closed eyes for newborns and do not require a neutral expression from under-ones — but they get no latitude at all on one rule: nobody else may appear in the photograph.",
                    "That includes a hand supporting the head, an arm at the edge of the frame, the back of a car seat, or a patterned blanket. This is the single most common reason an infant photo is returned, and it catches almost everyone the first time.",
                    "The reliable technique is to lay the baby on their back on a plain white or light grey sheet and photograph from directly above, with the camera parallel to the sheet. Natural light from a window, no flash. Take many frames — you are waiting for one where the eyes are open and the head is straight, and that frame is a matter of luck rather than skill.",
                    "China is the notable exception to infant leniency: it applies essentially the same head-size specification to babies as to adults, which makes a compliant Chinese visa photo of a newborn genuinely difficult.",
                ],
            },
            {
                "h": "Countries where you do not supply a photo at all",
                "p": [
                    "Before you spend an afternoon on this, check whether your application even uses a supplied photo. Several countries capture it at the counter.",
                    "India's Passport Seva process photographs applicants at the Passport Seva Kendra during the appointment. Portugal captures the photo at the Loja do Cidadão or Conservatória for both the Cartão de Cidadão and the passport. Brazil's Polícia Federal takes the photo at the passport appointment. In all three, turning up with prints is a wasted trip.",
                    "Canada sits at the opposite extreme: not only must you supply photos, they must be taken by a commercial photographer, and the back of one print must carry the studio's name, address and the date. A photo produced entirely at home does not satisfy that rule no matter how compliant it is technically.",
                ],
            },
            {
                "h": "A workable home procedure",
                "p": [
                    "Putting it together, in order:",
                ],
                "list": [
                    "Find a plain, light, untextured wall and stand at least a metre in front of it.",
                    "Face a large window on an overcast day. Turn off all indoor lights.",
                    "Have someone else shoot from about two metres away at eye level, zoomed in slightly. Do not use a selfie at arm's length — it distorts the nose and cheeks.",
                    "Remove glasses. Neutral expression, mouth closed, head straight, hair off the face and eyebrows.",
                    "Shoot wider than you think you need, so you have room to crop to the exact head-height requirement.",
                    "Take thirty frames. Blinks and micro-expressions ruin more shots than you would expect.",
                    "Crop to your country's exact dimensions and check the chin-to-crown measurement against its specific window rather than assuming 32–36 mm.",
                ],
            },
        ],
        takeaways=[
            "Passport photos are biometric templates — the rules follow from face recognition needing undistorted, unobscured facial landmarks.",
            "Head size is the most common rejection, and the windows differ by country: 32–36 mm for most, 29–34 mm in the UK, 25–35 mm in the US square format.",
            "Stand a metre or more from the wall; that one change removes most background-shadow rejections.",
            "For babies, no hand, arm or car seat may appear in frame — the most common infant rejection by far.",
            "India, Portugal and Brazil photograph you at the counter; Canada requires a commercial photographer's annotation on the back.",
        ],
        tools=["passport", "index", "crop"],
        faqs=[
            {"q": "Can I take a passport photo with my phone?",
             "a": "Yes, in most countries. The camera is not the limiting factor — framing, lighting and head size are. The exception is Canada, which requires a photo taken by a commercial photographer with the studio's details written on the back."},
            {"q": "Why do passport photos ban smiling?",
             "a": "Because face recognition measures distances between facial landmarks, and smiling moves the corners of the mouth and alters the jawline, which degrades the match. The US is unusual in allowing a natural, unforced smile."},
            {"q": "How recent does a passport photo have to be?",
             "a": "Six months in most countries. The UK is stricter at one month. In all cases, if your appearance has changed significantly — a beard, a very different hairstyle — a technically valid photo may still be refused."},
            {"q": "Can I crop a passport photo from an existing picture?",
             "a": "Sometimes, but rarely successfully. The original needs to be front-facing at eye level, neutral, evenly lit, high enough resolution to crop into, and taken within the recency window. Most casual photos fail on lighting or angle."},
        ],
    ),
    _guide(
        slug="what-exif-data-reveals",
        title="What EXIF Data Reveals About You — And How to Remove It",
        h1="What EXIF data reveals about you, and how to remove it",
        description="Every photo carries hidden metadata: GPS coordinates, serial numbers, timestamps. What is in there, which platforms strip it, and how to remove it.",
        category="Privacy",
        updated="2026-07-28",
        intro=[
            "Every photograph your phone or camera takes carries a block of metadata alongside the pixels. Most of it is mundane — exposure settings, the lens used. Some of it is a precise record of where you were and when, attached to a file you may be about to send to a stranger.",
            "This guide covers what is actually stored, who can read it, which platforms remove it and which do not, and how to strip it yourself.",
        ],
        sections=[
            {
                "h": "What is actually in there",
                "p": [
                    "EXIF — Exchangeable Image File Format — is a metadata standard embedded in JPEG, TIFF and HEIC files. PNG uses different metadata containers but can carry similar information. A typical smartphone photo contains a few dozen fields, of which these are the ones that matter for privacy:",
                ],
                "list": [
                    "GPS coordinates: latitude and longitude, typically accurate to a few metres, plus altitude. This is the significant one.",
                    "Timestamp: the exact date and time the shutter fired, usually with timezone.",
                    "Device make and model: 'iPhone 16 Pro', 'Canon EOS R6'.",
                    "Camera serial number: on many dedicated cameras, a unique identifier that links every photo you have ever taken with that body.",
                    "Lens model and settings: aperture, shutter speed, ISO, focal length.",
                    "Software: the app or editor that last wrote the file, including version.",
                    "Orientation, colour profile and thumbnail: the embedded thumbnail is worth knowing about, because it is not always regenerated after an edit.",
                ],
            },
            {
                "h": "The stale thumbnail problem",
                "p": [
                    "That last item deserves its own paragraph, because it has caused real harm.",
                    "EXIF can embed a small thumbnail of the image. Some editing software updates the main image but leaves the original thumbnail in place. The result is a file that looks cropped or redacted at full size, but still contains a small copy of the unedited original inside its own metadata.",
                    "This has produced actual privacy failures — cropped photos where the uncropped version was recoverable from the thumbnail. Modern mainstream editors handle it correctly, but it is a good argument for stripping metadata after editing rather than trusting that the editor did the right thing.",
                ],
            },
            {
                "h": "Who strips metadata and who does not",
                "p": [
                    "The picture is better than it used to be, but it is inconsistent enough that you should not rely on it.",
                    "Most large social platforms strip EXIF on upload — Facebook, Instagram, X and LinkedIn all remove GPS data from images they serve publicly. This is not entirely altruistic: they parse the metadata first and keep it for themselves. The location is gone from the file other people download, not from the platform's records.",
                    "Messaging apps vary. WhatsApp and Signal strip metadata. Telegram strips it when sending as a photo, but not when sending as a file — which is exactly the option people choose when they want to preserve quality. iMessage and email attachments generally preserve everything.",
                    "The places metadata most reliably survives are the ones people think least about: files attached to emails, images uploaded to forums and small websites, listings on marketplace sites, cloud storage share links, and anything sent as a document rather than a photo.",
                    "The classifieds case is worth stating plainly. Photographing an item for sale inside your home, then posting it with GPS intact, publishes your home address to anyone who downloads the image. Some marketplace sites strip metadata; not all do.",
                ],
            },
            {
                "h": "How someone reads it",
                "p": [
                    "There is no technical barrier. On Windows, right-click a file, choose Properties, and open the Details tab. On macOS, open the image in Preview and press Command-I. Any of dozens of free web tools and command-line utilities will dump the full field list in a second.",
                    "This is worth internalising: metadata is not obscured or encoded. Anyone who receives your file can read every field in about five seconds, with no expertise and no special software.",
                ],
            },
            {
                "h": "When you want to keep it",
                "p": [
                    "Metadata is not purely a liability, and blanket stripping has costs.",
                    "For photographers, EXIF is how you learn: reviewing which aperture and shutter speed produced a result is most of the feedback loop. Copyright and authorship fields in IPTC metadata are how professional images assert ownership. Photo libraries use timestamps and GPS to build timelines and maps, and stripping them breaks that organisation.",
                    "The sensible policy is to keep metadata on your originals and strip it on the copies you share. Treat your library as private and the exported file as public.",
                ],
            },
            {
                "h": "How to remove it",
                "p": [
                    "The most reliable general-purpose approach is a dedicated tool that rewrites the file without the metadata blocks. Our EXIF remover does this in your browser — the photo is never uploaded, which matters more than usual here, since the whole point is that you are handling a file you consider sensitive.",
                    "Two things worth knowing. First, screenshots of images do strip metadata, because the screenshot is a new file — but they also lose resolution and quality, so this is a crude fallback rather than a technique. Second, some formats carry metadata in more than one container: a file can have EXIF, IPTC and XMP blocks holding overlapping information, and a tool that clears only EXIF may leave GPS coordinates in the XMP block. A tool that rewrites the image data wholesale avoids this class of problem.",
                    "On phones, both major platforms now let you strip location at share time — iOS through the Options menu in the share sheet, Android through a similar toggle in Google Photos. These handle the common case well.",
                ],
            },
        ],
        takeaways=[
            "The field that matters is GPS: metre-accurate coordinates attached to a file anyone can read in five seconds with no special tools.",
            "Large social platforms strip metadata on upload; email attachments, forums, marketplace listings and 'send as file' in Telegram generally do not.",
            "A stale embedded thumbnail can preserve the pre-crop version of an image inside a file that looks edited.",
            "Metadata may live in EXIF, IPTC and XMP blocks at once — clearing only EXIF can leave coordinates behind.",
            "Keep metadata on your originals and strip it on shared copies, rather than destroying it everywhere.",
        ],
        tools=["exif", "redact", "priv_hub"],
        faqs=[
            {"q": "Does taking a screenshot remove EXIF data?",
             "a": "Yes — a screenshot is a new file containing only the pixels displayed, with no inherited metadata. But you lose resolution and re-compress the image, so it is a crude workaround rather than a good method."},
            {"q": "Do social media platforms remove EXIF from my photos?",
             "a": "The large ones do for images they serve publicly, including Facebook, Instagram, X and LinkedIn. They read and retain the metadata for their own purposes first. Smaller sites, forums and email attachments frequently preserve it."},
            {"q": "Does removing EXIF data reduce image quality?",
             "a": "No. Metadata is stored separately from the pixel data, so stripping it removes a few kilobytes and leaves the image untouched — provided the tool rewrites the container rather than re-encoding the image."},
            {"q": "Can EXIF data be recovered after removal?",
             "a": "Not from the stripped file — the fields are gone. But copies elsewhere may still carry it: the original in your camera roll, a cloud backup, or a version you already sent to someone."},
        ],
    ),
    _guide(
        slug="how-image-compression-works",
        title="How Image Compression Works — And How to Use It Well",
        h1="How image compression actually works",
        description="What lossy compression does to your pixels, why quality 80 looks identical to 100, and how to hit a target file size without visible damage.",
        category="Formats",
        updated="2026-07-28",
        intro=[
            "Compression is the one image operation almost everyone performs and almost nobody understands. The quality slider goes from 0 to 100, the file gets smaller, and somewhere along the way it starts looking bad — but where, and why, is usually left as a mystery.",
            "It is worth understanding, because the relationship between the number and the result is deeply non-linear, and knowing the shape of that curve is the difference between files that are three times larger than they need to be and files that visibly fall apart.",
        ],
        sections=[
            {
                "h": "The insight compression is built on",
                "p": [
                    "Human vision is not a uniform sensor. We are far more sensitive to changes in brightness than to changes in colour, and far more sensitive to broad shapes than to fine detail within a busy texture. Lossy compression is, fundamentally, a systematic exploitation of those two weaknesses.",
                    "The first is exploited by chroma subsampling. A JPEG typically stores brightness at full resolution but colour at half resolution horizontally and vertically — so three quarters of the colour information is discarded before any other compression happens. On a photograph this is essentially invisible. On a sharp red line against white it is not, which is why coloured text in a JPEG looks smeared.",
                    "The second is exploited by the frequency transform, and that is where the quality slider actually lives.",
                ],
            },
            {
                "h": "What the quality slider does",
                "p": [
                    "JPEG divides the image into 8×8 pixel blocks and converts each block from pixel values into frequency coefficients — one describing the block's average brightness, the rest describing progressively finer variation within it.",
                    "This transform is reversible and lossless on its own. The loss happens next: each coefficient is divided by a value from a quantisation table and rounded to an integer. High-frequency coefficients get divided by large numbers, so most of them round to zero — and long runs of zeros compress to almost nothing.",
                    "The quality setting scales that table. At quality 100 the divisors are small and little is lost. At quality 50 they are large and most fine detail rounds away. This is why the scale is non-linear: you are not removing a fixed fraction of information per point, you are scaling a table whose effect compounds.",
                    "It also explains where artefacts come from. Because the transform operates on independent 8×8 blocks, heavy quantisation makes adjacent blocks resolve to slightly different averages — visible as blockiness in smooth gradients like skies. And because a sharp edge requires many high-frequency coefficients to reconstruct, discarding them produces ringing around the edge: the faint halo of speckle known as mosquito noise.",
                ],
            },
            {
                "h": "Where the useful range is",
                "p": [
                    "For typical photographic content, the practical map looks like this:",
                ],
                "list": [
                    "100 to 90: essentially no visible difference from the original, but a large file. Wasteful for anything web-facing.",
                    "90 to 80: still visually indistinguishable on most photographs, at roughly half the file size of 100. This is where most images should sit.",
                    "80 to 70: fine for most photographs; slight softening in fine texture. Good for thumbnails and secondary images.",
                    "70 to 60: artefacts become visible in skies, skin tones and around sharp edges.",
                    "Below 60: obvious blockiness and ringing. Only appropriate when file size dominates everything else.",
                ],
            },
            {
                "h": "Why content matters more than the number",
                "p": [
                    "The bands above assume photographic content. Different material behaves very differently at the same setting.",
                    "A photograph of foliage, gravel or fabric hides artefacts extremely well, because the noise introduced by compression is masked by the texture already present. These images can go lower than you would expect.",
                    "A photograph containing large smooth gradients — a clear sky, a studio backdrop, out-of-focus background — shows banding early, because there is no texture to hide the block boundaries. These need a higher setting than their apparent simplicity suggests.",
                    "Images with sharp edges — screenshots, text, illustrations, logos — are the worst case, and often should not be lossy at all. If a screenshot must be a JPEG, start at 90.",
                    "This is why automatic 'compress to target size' tools that apply one quality setting across a batch produce inconsistent results: the same number does very different things to a landscape and a screenshot.",
                ],
            },
            {
                "h": "The mistake that does the most damage",
                "p": [
                    "Recompression. Every time a lossy image is decoded, modified and re-encoded, it is quantised again — and the second pass is working on data that already has artefacts, which it then treats as real detail worth preserving while discarding something else.",
                    "The damage accumulates and is not recoverable. Saving a JPEG at quality 90 ten times in a row produces a visibly worse image than saving the original once at quality 60, despite the higher nominal setting each time.",
                    "The rule that follows: always edit from the highest-quality version you have, and export to lossy once, at the end. Never use a lossy file as your working master. If you need to send an image to someone who will edit it, send a lossless copy.",
                ],
            },
            {
                "h": "Hitting a target file size",
                "p": [
                    "Upload limits are the usual reason people compress at all — a form wants under 2 MB, or a forum caps attachments at 500 KB.",
                    "The order of operations matters and most people get it backwards. Reducing dimensions is far more powerful than reducing quality, because file size scales roughly with pixel count: halving both width and height cuts pixels to a quarter. Dropping a 4000-pixel-wide photo to 1600 pixels will usually get you under a limit on its own, at no perceptible cost, because nothing displaying it needed 4000 pixels.",
                    "So: resize first to the largest size the image will actually be displayed at, then compress, and only then start lowering quality below 80. A 1600-pixel image at quality 85 will look better and be smaller than a 4000-pixel image at quality 40.",
                    "Switching format is the other lever. The same image as WebP is typically 25–35% smaller than JPEG at matched quality, and AVIF smaller again — often enough on its own to clear a limit without touching quality.",
                ],
            },
        ],
        takeaways=[
            "Lossy compression exploits two facts about human vision: we see brightness better than colour, and shapes better than fine texture.",
            "The quality slider scales a quantisation table, which is why its effect is non-linear — 90 to 80 costs almost nothing, 70 to 60 costs a lot.",
            "Blockiness in skies and haloes around text are the two signature artefacts, and both follow from JPEG's 8×8 block transform.",
            "Recompression damage accumulates permanently: ten saves at quality 90 look worse than one save at quality 60.",
            "To hit a size limit, resize before you compress — pixel count dominates file size far more than the quality number does.",
        ],
        tools=["compress", "resize", "convert"],
        faqs=[
            {"q": "Does compressing an image twice make it worse?",
             "a": "Yes, and permanently. Each pass quantises data that already contains artefacts from the previous pass. Always work from the highest-quality original and export to a lossy format once."},
            {"q": "What quality setting should I use for web images?",
             "a": "Between 75 and 85 for photographs — visually indistinguishable from the original at roughly half the file size. Start at 90 for screenshots, illustrations or anything with sharp edges and flat colour."},
            {"q": "Why does my compressed sky look banded?",
             "a": "Smooth gradients have no texture to mask JPEG's 8×8 block boundaries, so adjacent blocks resolve to slightly different averages and the seams become visible. Raise the quality setting, or use WebP or AVIF, which handle gradients better."},
            {"q": "Is it better to resize or compress to reduce file size?",
             "a": "Resize first, almost always. File size scales with pixel count, so halving the dimensions cuts the file to roughly a quarter with no visible loss if the image was larger than it needed to be. Then compress the resized version."},
        ],
    ),
    _guide(
        slug="redacting-images-safely",
        title="How to Redact a Screenshot Safely — Blurring Is Not Enough",
        h1="How to redact a screenshot safely",
        description="Blur and pixelation have both been reversed in real cases. What actually works, why mosaic filters fail, and the one method that cannot be undone.",
        category="Privacy",
        updated="2026-07-28",
        intro=[
            "Redaction failures are one of the most reliably repeated mistakes in computing, and they keep happening because the intuitive methods look convincing while being reversible. A blurred password looks unreadable to you. It is not necessarily unreadable to someone who wants it.",
            "This guide covers what actually fails, why, and the small number of techniques that genuinely work.",
        ],
        sections=[
            {
                "h": "Why pixelation fails",
                "p": [
                    "Pixelation — the mosaic filter — replaces each block of pixels with their average colour. That average is not random: it is a deterministic function of what was underneath, which means it carries information about the original content.",
                    "If an attacker knows the font, size and rendering of the original text, they can reconstruct it by brute force. Render every candidate string, apply the identical mosaic filter, and compare the resulting blocks against the redacted image. The match that fits is the original text. This is not theoretical — it is a published, implemented technique, and tools that do it automatically have existed for years.",
                    "The attack is strongest exactly where redaction matters most. Content with a small, known character set and predictable formatting — account numbers, card numbers, dates, IP addresses, sums of money — has a small enough search space to exhaust quickly. Redacted digits in a screenshot of a familiar interface are close to the ideal case for the attacker.",
                ],
            },
            {
                "h": "Why blurring fails too",
                "p": [
                    "Gaussian blur is a convolution: each output pixel is a weighted average of its neighbours. Like pixelation, it is deterministic and information-preserving in the mathematical sense — the operation has an inverse, and deconvolution can recover a usable approximation of the original when the blur radius is modest.",
                    "Even where exact recovery is not possible, the same brute-force approach works: blur a candidate rendering with the same radius and compare. Blurred text with a known font is not much safer than pixelated text.",
                    "Heavy blur with a large radius genuinely does destroy information, and at some radius the content is unrecoverable. The problem is that you cannot tell from looking at it whether you crossed that line. 'It looks blurry enough to me' is not a security property.",
                ],
            },
            {
                "h": "The swirl and other reversible transforms",
                "p": [
                    "Worth a specific mention because it produced one of the best-known cases: geometric distortion filters, like the swirl effect, are fully reversible. They rearrange pixels rather than destroying them, so applying the inverse transform reconstructs the original exactly.",
                    "A person who obscured his face with a swirl filter in photographs was identified after investigators simply un-swirled the images. Nothing had been removed — only moved.",
                    "The general principle: if the operation is a rearrangement or a smooth averaging, assume it is reversible. Only operations that genuinely discard information are safe.",
                ],
            },
            {
                "h": "What actually works",
                "p": [
                    "There are three reliable methods, in increasing order of certainty.",
                    "Draw solid opaque shapes over the content. A filled black or white rectangle replaces the pixels entirely — there is no underlying data left to recover, because the original values are simply gone. This is the standard method and it works, with one critical condition covered in the next section.",
                    "Crop the sensitive region out of the image entirely. If the pixels are not in the file, nothing can recover them. Where the layout allows it, this is stronger than covering, because it removes any question about layering.",
                    "Retype rather than redact. For the highest-stakes cases, do not screenshot the real thing at all. Replace the sensitive values with plausible fake ones in the source — change the account number in the page, then screenshot — or rebuild the example with dummy data. This is the only approach with no failure mode, and it is what you should do for anything genuinely serious. It is worth saying plainly that this includes not trusting our own redaction tool: a tool can only cover pixels, and covering pixels is the second-best answer.",
                ],
            },
            {
                "h": "The layering trap",
                "p": [
                    "Solid shapes only work if they are actually merged into the image. This is where most modern redaction failures now happen, and they happen in documents more often than images.",
                    "Drawing a black rectangle in a PDF editor, a word processor or a design tool typically adds an object on top of a layer that still contains the original text. The text remains selectable, searchable and extractable — it is merely hidden behind an opaque shape. Copy the region and paste it elsewhere and the redacted content comes straight out. Government agencies, law firms and newspapers have all published documents with this exact flaw.",
                    "The defence is flattening. Export to a flat raster image, or use a redaction function that explicitly removes the underlying content rather than covering it. A useful verification: open the finished file, select all, copy, and paste into a text editor. If the redacted text appears, you have not redacted anything.",
                ],
            },
            {
                "h": "What people forget to redact",
                "p": [
                    "Even a correctly executed redaction fails if it misses something. The commonly overlooked items, in rough order of frequency:",
                ],
                "list": [
                    "Browser tabs and window titles, which often contain names, account identifiers or document titles.",
                    "The URL bar — query strings routinely carry session tokens, email addresses and record IDs.",
                    "Notification banners that appeared mid-screenshot.",
                    "Autocomplete dropdowns showing previous entries.",
                    "The taskbar or dock, showing which applications are open.",
                    "Reflections in glossy surfaces, screens and eyeglasses within the photo.",
                    "File metadata — the screenshot's own EXIF, and the filename itself.",
                    "The embedded thumbnail, which in some editors preserves the pre-edit image inside the file.",
                ],
            },
        ],
        takeaways=[
            "Pixelation is reversible by brute force when the font is known — account numbers and dates are close to the ideal case for the attack.",
            "Blur is a convolution and can be deconvolved; you cannot tell by eye whether your radius was large enough.",
            "Swirl and other geometric filters rearrange pixels rather than destroying them, and undo exactly.",
            "Solid opaque shapes work only once flattened — a rectangle over live text in a PDF hides nothing.",
            "For anything serious, retype the values or crop them out rather than covering them; that is the only method with no failure mode.",
        ],
        tools=["redact", "crop", "exif"],
        faqs=[
            {"q": "Is blurring enough to hide text in a screenshot?",
             "a": "No. Blur is a reversible mathematical operation, and even where exact inversion fails, an attacker who knows the font can brute-force the content by blurring candidate renderings and comparing. Use a solid opaque shape or crop the region out."},
            {"q": "Is pixelation safer than blurring?",
             "a": "No — if anything it is worse, because the block averages are a clean, deterministic function of the original. Recovering pixelated text with a known font is a published and implemented technique."},
            {"q": "Why did my black box in a PDF not work?",
             "a": "Because it was drawn as an object on top of the text rather than replacing it. The text is still in the file, selectable and copyable. Flatten the page to a raster image, or use a redaction function that removes the underlying content."},
            {"q": "What is the safest way to redact a screenshot?",
             "a": "Do not capture the sensitive content in the first place — substitute fake values in the source and then screenshot. Failing that, crop the region out entirely, or draw solid opaque shapes and flatten the image to a format that cannot carry layers."},
        ],
    ),
    _guide(
        slug="transparent-backgrounds-explained",
        title="How Transparent Backgrounds Work — Alpha Channels Explained",
        h1="How transparent backgrounds actually work",
        description="What an alpha channel is, why cut-outs get white or black fringes, straight vs premultiplied alpha, and which formats carry transparency at all.",
        category="Formats",
        updated="2026-07-28",
        intro=[
            "Transparency is the source of more confusion than any other image concept. A cut-out looks perfect in one program and has a white halo in another. A logo saved as JPG mysteriously gains a black background. A PNG with a transparent background prints as a solid white rectangle.",
            "All of these have the same underlying explanation, and it is worth understanding, because the fixes are simple once you know what is happening.",
        ],
        sections=[
            {
                "h": "The fourth channel",
                "p": [
                    "A normal colour image stores three numbers per pixel: red, green and blue. An image with transparency stores a fourth, the alpha channel, which records how opaque that pixel is — 0 for fully transparent, 255 for fully opaque, and everything between for partial.",
                    "Partial transparency is the important part and the part people forget. A cut-out is not a binary mask where each pixel is either subject or background. Around every edge there is a band of pixels that are genuinely part-subject and part-background, because a single sensor pixel covering the boundary captured light from both. Hair, fur, motion blur and out-of-focus edges can be dozens of pixels wide in this in-between state.",
                    "Quality in a cut-out is almost entirely a question of how well that transitional band is handled. A hard binary mask produces the jagged, cut-with-scissors look. A well-estimated alpha channel produces edges that composite convincingly onto any background.",
                ],
            },
            {
                "h": "Where fringes come from",
                "p": [
                    "The white or dark halo around a cut-out is the single most common transparency problem, and it comes from colour contamination in those semi-transparent edge pixels.",
                    "Consider a dark object photographed against a white background. A pixel exactly on the boundary captured some object and some background, so its stored colour is a blend — a light grey. When the alpha channel marks that pixel as 50% opaque and you composite onto a new dark background, you get 50% of a light grey pixel showing. Multiply that across the whole outline and you get a visible light fringe.",
                    "The fix is to estimate what the object's colour would have been without the background contribution and store that, rather than the observed blend. Good background removal does this — it is called colour decontamination, and it is why a well-processed cut-out composites cleanly onto black as well as white.",
                    "This is also why you should always check a cut-out against a background very different from the original. A subject cut from a white background will look flawless composited onto white, and reveal every flaw composited onto dark blue. If you are producing cut-outs for other people to use, check against both.",
                ],
            },
            {
                "h": "Straight vs premultiplied alpha",
                "p": [
                    "There are two conventions for storing the colour of a semi-transparent pixel, and mixing them up produces predictable, recognisable errors.",
                    "Straight (or unassociated) alpha stores the colour as if the pixel were fully opaque, with transparency recorded separately. Premultiplied (or associated) alpha stores the colour already multiplied by the alpha value, so a 50%-opaque red pixel is stored as a darker red.",
                    "Premultiplied is faster to composite and avoids some interpolation artefacts, which is why video and compositing software often prefers it. PNG uses straight alpha. When software assumes the wrong convention, you get a distinctive result: an image interpreted as premultiplied when it is actually straight develops dark fringes; the reverse produces bright, washed-out edges.",
                    "If you have ever seen a logo that looks fine in one application and has a grey outline in another, this is usually the cause, and it is a software mismatch rather than anything wrong with your file.",
                ],
            },
            {
                "h": "Which formats can carry transparency",
                "p": [
                    "Not many, and this trips people up constantly.",
                ],
                "list": [
                    "PNG: full 8-bit alpha, lossless. The universal safe choice.",
                    "WebP: full alpha in both lossy and lossless modes. The best option for the web, because lossy-with-alpha did not exist before it.",
                    "AVIF: full alpha, best compression, slower to encode.",
                    "GIF: one single colour marked fully transparent — no partial transparency at all, which is why GIF cut-outs have hard, jagged edges.",
                    "TIFF and PSD: full alpha, for print and editing workflows.",
                    "SVG: transparency is native, since it is vector rather than pixels.",
                    "JPG: none whatsoever. This is the one that catches people.",
                ],
            },
            {
                "h": "Why your transparent image turned black or white",
                "p": [
                    "JPEG has no alpha channel and no way to represent one. When you export a transparent image to JPG, the transparency has to be resolved against something, and different software picks differently — most commonly white, sometimes black.",
                    "That is the whole explanation for the most-reported transparency bug there is: a cut-out saved as JPG and reopened with a solid background. Nothing is broken and nothing can be recovered; the alpha channel was discarded at export. Re-export from the original as PNG or WebP.",
                    "The related case is printing. Print is a physical process with no concept of transparency — ink either goes on the paper or it does not, and where it does not, you get paper. A transparent PNG sent to a printer produces whatever colour the paper is. If you need a specific background in print, composite it explicitly before sending.",
                ],
            },
            {
                "h": "Practical rules",
                "p": [
                    "Condensed to the decisions you actually make:",
                ],
                "list": [
                    "Keep your master cut-out as PNG, which is lossless and universally supported.",
                    "Export lossy WebP for the web — same transparency, a fraction of the size.",
                    "Never save a cut-out as JPG unless you have deliberately composited a background first.",
                    "Always preview a cut-out against a background very different from the original before you ship it.",
                    "For print, composite the background yourself rather than relying on the printer.",
                    "If edges look wrong in one program only, suspect a straight/premultiplied mismatch rather than a bad file.",
                ],
            },
        ],
        takeaways=[
            "Transparency is a fourth channel per pixel, and the semi-transparent band around edges is where cut-out quality lives or dies.",
            "White and dark fringes come from background colour contaminating edge pixels; good removal decontaminates rather than just masking.",
            "Always check a cut-out against a background unlike the original — errors are invisible against the colour they came from.",
            "JPG cannot store transparency at all, which is why cut-outs saved as JPG come back with white or black backgrounds.",
            "GIF supports only one fully transparent colour, so GIF cut-outs always have hard, jagged edges.",
        ],
        tools=["index", "convert", "sticker"],
        faqs=[
            {"q": "Why does my transparent PNG have a white background when I open it?",
             "a": "Either it was converted to JPG at some point, which discards the alpha channel entirely, or the program you are viewing it in composites transparency onto white for display. Check the file format first."},
            {"q": "Can a JPG have a transparent background?",
             "a": "No. JPEG has no alpha channel and no mechanism to add one. Any transparency is resolved to a solid colour — usually white — when the file is written. Use PNG or WebP instead."},
            {"q": "Why does my cut-out have a white outline?",
             "a": "The semi-transparent pixels around the edge still contain colour from the original background. Removal that only builds a mask leaves this contamination; removal that also decontaminates the edge colour composites cleanly onto any background."},
            {"q": "What is the best format for a transparent image on a website?",
             "a": "Lossy WebP. It carries a full alpha channel at a fraction of PNG's size, and is supported by every current browser. Keep a PNG master for anything you will edit or hand to someone else."},
        ],
    ),
    _guide(
        slug="resize-images-without-losing-quality",
        title="How to Resize Images Without Losing Quality",
        h1="How to resize images without losing quality",
        description="What resampling actually does, why downscaling is safe and upscaling is not, which algorithm to pick, and the honest limits of AI upscalers.",
        category="Editing",
        updated="2026-07-28",
        intro=[
            "Resizing looks like the simplest possible image operation and is in fact one of the easiest to do badly. The reason is that changing an image's dimensions requires inventing information that was not measured — and how a program invents it determines whether the result looks sharp, soft or wrong.",
            "This guide covers what is really happening, why one direction is safe and the other is not, and how far modern upscaling can actually take you.",
        ],
        sections=[
            {
                "h": "Resampling: making up pixels",
                "p": [
                    "An image is a grid of measurements. Resizing produces a different grid, and the new sample points almost never line up with the old ones — a pixel in the output may sit between four pixels in the input. The algorithm has to decide what colour belongs there. That decision is called resampling.",
                    "Nearest neighbour takes the value of the closest original pixel. It is fast, preserves hard edges exactly, and produces visibly blocky results on photographs. It is the right choice for pixel art and for anything where you want to preserve exact pixel values, and wrong for essentially everything else.",
                    "Bilinear interpolation averages the four surrounding pixels. Smooth, fast, and slightly soft.",
                    "Bicubic considers sixteen surrounding pixels with a weighting curve that slightly overshoots at edges, which reads as sharpness. It is the default in most editing software and a good general answer.",
                    "Lanczos uses a windowed sinc function over a larger neighbourhood and generally produces the sharpest result for photographic downscaling. Its overshoot can produce faint ringing next to very high-contrast edges, which is occasionally visible on text.",
                    "For most photographic work the practical ranking is Lanczos or bicubic for photographs, nearest neighbour for pixel art, and bilinear when speed matters more than quality.",
                ],
            },
            {
                "h": "Why downscaling is safe",
                "p": [
                    "Making an image smaller discards information, which sounds bad and is in fact the easy direction. Every output pixel is derived from real measured data — several input pixels averaged together — so nothing has to be invented.",
                    "Downscaling can even improve apparent quality. Averaging groups of pixels reduces noise, which is why a high-ISO photo often looks cleaner at half size. It is also why a slightly soft photo can look acceptably sharp when displayed small.",
                    "The one genuine pitfall is aliasing. Reducing dimensions dramatically in a single step can undersample fine repeating detail — a striped shirt, a brick wall, a fine grid — producing moiré patterns that were not in the original. Good resizing filters low-pass the image before sampling to prevent this. If a tool produces moiré on downscale, resizing in two stages usually avoids it.",
                ],
            },
            {
                "h": "Why upscaling is not",
                "p": [
                    "Enlarging is fundamentally different: the information you need was never captured. A 500-pixel-wide photo does not contain 1000 pixels of detail that a clever algorithm can extract. It contains 500, and the other 500 have to be fabricated.",
                    "Classical interpolation fabricates conservatively, by smoothly blending neighbours. The result is never wrong, exactly, but it is soft — an enlarged image with no more real detail than the original, spread over more pixels. Sharpening afterwards increases local contrast at edges, which reads as sharper without adding detail, and overdone produces halos.",
                    "This is why the honest answer to 'can you enhance this?' is usually no. The information is not there.",
                ],
            },
            {
                "h": "What AI upscalers really do",
                "p": [
                    "Machine-learning upscalers work differently, and the distinction matters. Rather than interpolating, they have been trained on millions of image pairs and have learned what kinds of detail tend to accompany what kinds of low-resolution patterns. Given a blurry region that looks like it was probably brickwork, the model generates plausible brickwork.",
                    "On many images the result is genuinely impressive and far better than interpolation. On others it is confidently wrong, and this is the important caveat: the model is generating detail that is statistically plausible, not detail that was there. Faces gain features that are not the person's. Text becomes crisp, legible, and says something slightly different. Textures gain a characteristic over-regular quality.",
                    "The practical rule: AI upscaling is excellent for making an image look good, and inappropriate where the image is evidence. Never use it on anything where the detail itself is the point — a document, a licence plate, a medical image, a screenshot being cited. Anything it adds is invention.",
                    "It is also worth knowing that these models are computationally heavy. Running one on a large image in a browser tab can lock the page for a long time, which is why our own upscaler uses high-quality Lanczos resampling rather than a generative model: it will not invent detail, and it will not freeze your tab.",
                ],
            },
            {
                "h": "Practical rules",
                "p": [
                    "The decisions that matter, in order:",
                ],
                "list": [
                    "Always resize from the largest original you have, never from an already-resized copy.",
                    "Downscale freely — it is safe and often improves apparent quality.",
                    "Treat 2× as the sensible ceiling for upscaling anything that must look natural.",
                    "Resize before compressing, not after: pixel count drives file size far more than the quality setting does.",
                    "Preserve the aspect ratio unless you have a specific reason not to; stretched photos are immediately obvious.",
                    "Sharpen after downscaling, not before — downscaling softens, and sharpening first amplifies noise you are about to average anyway.",
                    "Never upscale anything where the fine detail is evidence.",
                ],
            },
        ],
        takeaways=[
            "Resampling has to invent values for output pixels that fall between input pixels — the algorithm choice is what determines sharpness.",
            "Downscaling derives every output pixel from real data, so it is safe and can even reduce noise.",
            "Upscaling fabricates information that was never captured; classical methods do it softly, generative models do it convincingly.",
            "AI upscalers generate plausible detail, not true detail — never use them where the detail is evidence.",
            "Resize before you compress; pixel count dominates file size far more than the quality slider.",
        ],
        tools=["resize", "upscale", "compress"],
        faqs=[
            {"q": "Can I enlarge an image without losing quality?",
             "a": "Not really. The detail was never captured, so enlargement either softens the image (classical interpolation) or invents plausible detail (AI upscaling). Around 2× is the practical ceiling for a natural-looking result."},
            {"q": "Which resampling algorithm is best?",
             "a": "Lanczos or bicubic for photographs, nearest neighbour for pixel art where hard edges must be preserved exactly, and bilinear when speed matters more than quality."},
            {"q": "Should I resize or compress first?",
             "a": "Resize first. File size scales with pixel count, so reducing dimensions to what will actually be displayed usually gets you under a size limit without touching the quality setting at all."},
            {"q": "Why does my resized image look blurry?",
             "a": "Either you enlarged it, in which case the detail is genuinely absent, or you downscaled with a soft filter such as bilinear. Downscaling also naturally softens, so a light sharpen afterwards is normal and appropriate."},
        ],
    ),
    _guide(
        slug="image-sizes-for-social-media",
        title="The Right Image Size for Every Social Platform",
        h1="The right image size for every social platform",
        description="Current dimensions and aspect ratios for Instagram, X, LinkedIn, Facebook, YouTube, TikTok and Pinterest — plus how to lose the least quality.",
        category="Editing",
        updated="2026-07-28",
        intro=[
            "Every platform resizes and recompresses what you upload, and each one does it differently. Upload something at the wrong dimensions and it gets cropped in a way you did not choose; upload it at the wrong quality and the platform's own compression makes it worse than it needed to be.",
            "This guide covers the sizes that matter, the aspect ratios behind them, and — more usefully — the general rules that stay true when the numbers change.",
        ],
        sections=[
            {
                "h": "Think in aspect ratios, not pixels",
                "p": [
                    "Platforms revise their pixel dimensions constantly, but the aspect ratios have been remarkably stable for years, because they are tied to how phones are held rather than to any platform decision.",
                    "There are really only five that matter. 1:1 square, the old Instagram default, still the safest universal format. 4:5 vertical, which is the tallest ratio most feeds will display without cropping and therefore occupies the most screen space in a scroll. 9:16 full vertical, for stories, reels and TikTok. 16:9 horizontal, for YouTube, X and most link previews. And 2:3 tall, which is Pinterest's preference.",
                    "If you compose with the ratio in mind and export at a sensible resolution, the specific pixel count almost never matters — every platform downscales to its own targets anyway.",
                ],
            },
            {
                "h": "Current dimensions worth knowing",
                "p": [
                    "As of mid-2026, these are the sizes that give the best results:",
                ],
                "list": [
                    "Instagram feed: 1080 × 1350 (4:5) for maximum feed space, or 1080 × 1080 (1:1) for the safe square.",
                    "Instagram stories and reels: 1080 × 1920 (9:16), keeping text away from the top and bottom 250 pixels where the interface sits.",
                    "TikTok: 1080 × 1920 (9:16), same interface caveat.",
                    "X (Twitter) in-feed image: 1600 × 900 (16:9). The feed preview crops toward the centre, so keep the subject there.",
                    "LinkedIn post image: 1200 × 627 (roughly 1.91:1) for link previews, 1080 × 1080 for standalone images.",
                    "Facebook feed: 1200 × 630 (1.91:1) for links, 1080 × 1350 for photos.",
                    "YouTube thumbnail: 1280 × 720 (16:9), under 2 MB. Legible at roughly 210 pixels wide, which is how most people see it.",
                    "Pinterest: 1000 × 1500 (2:3). Taller pins are shown but get truncated in the grid.",
                ],
            },
            {
                "h": "The YouTube thumbnail rule everyone ignores",
                "p": [
                    "The specification says 1280 × 720. The actual display size in a sidebar or a mobile feed is around 210 pixels wide — about a sixth of that.",
                    "This means a thumbnail designed at full size and judged at full size is being judged at six times the size anyone will see it. Detailed compositions, small text and subtle expressions all disappear. The thumbnails that work are the ones that survive being shrunk: one clear subject, very large text if any, and strong tonal contrast between the subject and the background.",
                    "The practical test is to shrink your thumbnail to 210 pixels wide and look at it. If you cannot tell what it is, neither can anyone else, regardless of how good it looks at full size."],
            },
            {
                "h": "Why your uploads look worse than the file you made",
                "p": [
                    "Every platform recompresses. They are serving billions of images and bandwidth is a real cost, so your carefully exported file is decoded, resized to their targets, and re-encoded with their settings.",
                    "This is a second lossy pass on top of yours, which is the mechanism behind most 'why does my image look bad on Instagram' complaints. There are a few things that genuinely reduce the damage:",
                ],
                "list": [
                    "Upload at the platform's target dimensions or a clean multiple of them, so their resize is a simple downscale rather than an awkward resample.",
                    "Export at high quality (90+) rather than pre-compressing. Their encoder does better starting from a clean image than from one that already has artefacts.",
                    "Avoid fine detail, dense texture and thin lines, which are exactly what a second compression pass destroys.",
                    "Prefer PNG for text-heavy graphics where the platform accepts it, since text is the worst case for lossy compression.",
                    "Do not upload an image that has already been downloaded from another platform — that is a third compression generation and it shows.",
                ],
            },
            {
                "h": "Safe zones",
                "p": [
                    "Vertical formats overlay interface elements on your image, and the areas they cover are not obvious when you are designing.",
                    "For stories and reels, keep anything important out of the top 250 pixels, where the profile row and progress bars sit, and the bottom 250 pixels, where captions, the reply field and the action buttons appear. On TikTok, also avoid the right-hand strip where the action column lives.",
                    "For profile pictures, remember they are cropped to a circle on essentially every platform now. Design in a square and check that nothing important falls into the corners.",
                    "For link previews, the crop is horizontal and centre-weighted almost everywhere, so a subject at the edge of a tall image will simply be cut off.",
                ],
            },
        ],
        takeaways=[
            "Aspect ratios are stable even when pixel dimensions change — 1:1, 4:5, 9:16, 16:9 and 2:3 cover essentially everything.",
            "4:5 occupies the most feed space of any ratio most platforms will display uncropped.",
            "YouTube thumbnails are seen at around 210 pixels wide; design for that, not for 1280.",
            "Platforms always recompress, so upload at high quality and at their target dimensions rather than pre-compressing.",
            "Keep content out of the top and bottom 250 pixels of any 9:16 vertical, where the interface sits.",
        ],
        tools=["instagram", "resize", "crop", "compress"],
        faqs=[
            {"q": "What is the best image size for Instagram?",
             "a": "1080 × 1350 (4:5) for feed posts — the tallest ratio Instagram displays without cropping, so it takes up the most screen space as people scroll. Use 1080 × 1920 (9:16) for stories and reels."},
            {"q": "Why does Instagram make my photos look bad?",
             "a": "It recompresses everything you upload. Uploading at the target dimensions and at high quality (90+) reduces the damage, because their encoder produces a better result starting from a clean image than from one that is already compressed."},
            {"q": "What size should a YouTube thumbnail be?",
             "a": "1280 × 720 pixels, under 2 MB. More importantly, design it to be legible at around 210 pixels wide, which is the size most viewers actually see in feeds and sidebars."},
            {"q": "Should I upload PNG or JPG to social media?",
             "a": "JPG or WebP for photographs — the platform will recompress anyway. PNG is worth it for graphics with text or flat colour, where lossy artefacts are most visible, if the platform accepts it."},
        ],
    ),
    _guide(
        slug="on-device-vs-cloud-image-tools",
        title="On-Device vs Cloud Image Tools — What Happens to Your Photo",
        h1="On-device vs cloud image tools: what happens to your photo",
        description="What 'free online image tool' usually means for your file, what browser-based processing changes, and an honest account of where each approach wins and loses.",
        category="Privacy",
        updated="2026-07-28",
        intro=[
            "Most free online image tools work the same way: you upload a file to a server, it is processed there, and you download the result. That model is so standard that people rarely think about what it implies — which is that a copy of your photo now exists on a computer you do not control.",
            "Browser-based processing is a genuine alternative, not a marketing claim, but it comes with real limitations. This guide covers how each actually works and when each is the right choice. We build on-device tools, so read the trade-offs section with that in mind — it is the part where we say what we are worse at.",
        ],
        sections=[
            {
                "h": "What happens when you upload",
                "p": [
                    "Your file leaves your device, crosses the network, and is written to storage on a server. It is processed there and the result is sent back. Several things follow from this that are not obvious:",
                    "The file exists in at least two places on the server side — the upload and the output — and often more, including temporary files and cache layers. Deletion policies vary from immediate to indefinite, and are stated in a privacy policy that most people do not read.",
                    "It may pass through a CDN, an object store and a queue on its way, each of which may retain a copy for some period. It may be backed up as part of routine infrastructure backups, which can extend retention well past the stated policy.",
                    "Staff may have access. Content may be scanned, for legitimate reasons like abuse detection and less legitimate ones. And a company's privacy policy binds only that company: if it is acquired or fails, the data is an asset that goes somewhere.",
                    "None of this means uploading is reckless. It means it is a decision with consequences, and the consequences scale with what is in the photo.",
                ],
            },
            {
                "h": "How browser processing works",
                "p": [
                    "Modern browsers can run real computation. Three capabilities make this practical for image work: WebAssembly compiles near-native code to run in the page, WebGL and WebGPU give access to the graphics hardware, and Canvas provides direct pixel manipulation.",
                    "A background remover built this way downloads the neural network model into the page — a few megabytes, once, then cached — and runs inference on your device using your GPU. The image is read from a local file input, processed in memory, and written back out as a download. There is no upload step because there is no server involved in the processing at all.",
                    "You can verify this rather than trusting it, which is the part worth knowing: open your browser's developer tools, go to the Network tab, and use the tool. If your image were being uploaded you would see the request. This is a claim that is checkable from outside, unlike a privacy policy.",
                    "Two more properties follow. There are no per-image costs, so limits and paywalls are unnecessary. And once the model is cached the tool works offline, because nothing needs the network.",
                ],
            },
            {
                "h": "Where the cloud genuinely wins",
                "p": [
                    "This is the honest part, and it is not close on some axes.",
                    "Raw capability is the big one. A server can run a model that is tens of gigabytes and needs a dedicated accelerator. A browser realistically works with models of a few tens of megabytes. For the very best quality on the hardest cases — complex hair against a busy background, fine transparency, semi-transparent fabric — a large server-side model still produces better results than anything that fits in a page.",
                    "Consistency is another. A server has known, fixed hardware. Browser performance depends on the visitor's device, which spans a decade of phones and laptops. The same tool can be instant on a recent machine and slow on an old one, and there is no way to fix that from our side.",
                    "Very large files are a real constraint. Browser tabs have memory limits, and a 100-megapixel image or a long video can exceed what a tab can hold. Servers do not have this problem.",
                    "Integration is the last one. If you need image processing inside an automated pipeline, an API on a server is the right architecture and a browser tool is not an option at all.",
                ],
            },
            {
                "h": "How to decide",
                "p": [
                    "The question worth asking is not which is better in the abstract but what is in the image.",
                    "For anything sensitive — identity documents, medical images, financial statements, photographs of children, unreleased work, anything under a confidentiality obligation — on-device processing removes an entire category of risk. There is no server-side copy to leak, subpoena, retain past its policy, or inherit in an acquisition. That is a structural difference, not a promise.",
                    "For ordinary images where you need the best possible result and the content is not sensitive, a good cloud service is a perfectly reasonable choice, and on the hardest cut-outs it will still beat a browser.",
                    "For bulk work, on-device usually wins on economics rather than privacy: no per-image cost and no rate limit means processing a few hundred product photos is just a matter of waiting.",
                ],
            },
            {
                "h": "Reading the claims",
                "p": [
                    "'Secure', 'private' and 'encrypted' are used loosely enough to be nearly meaningless in this space. Some specific things to look for:",
                ],
                "list": [
                    "'Encrypted in transit' means HTTPS, which every site has. It says nothing about what happens after arrival.",
                    "'We delete your files after an hour' is a policy, not a mechanism, and it depends entirely on the operator honouring it.",
                    "'Your files are never shared with third parties' does not mean they are not retained, scanned, or used for training.",
                    "'Processed locally' is checkable — open the Network tab and watch. If a request goes out with your file in it, the claim is false.",
                    "A tool that works with your network connection off is not uploading anything, which is the most direct test available.",
                ],
            },
        ],
        takeaways=[
            "Uploading creates copies you do not control, in more places than the obvious one, with retention that depends on a policy rather than a mechanism.",
            "WebAssembly and WebGPU make real image processing possible in a page, with no upload step at all.",
            "The claim is verifiable: open the Network tab, or disconnect from the internet, and see whether the tool still works.",
            "Cloud services genuinely win on model size, hardware consistency, very large files and API integration.",
            "Match the method to the content — on-device for anything sensitive, cloud when you need maximum quality on an ordinary image.",
        ],
        tools=["priv_hub", "index", "exif"],
        faqs=[
            {"q": "How can I tell if an online tool uploads my image?",
             "a": "Open your browser's developer tools, switch to the Network tab, and use the tool. An upload appears as a request carrying your file. Alternatively, disconnect from the internet after the page loads — a tool that still works is not uploading anything."},
            {"q": "Is browser-based processing as good as server-based?",
             "a": "For most images, yes. For the hardest cases — fine hair against a busy background, semi-transparent materials — a large server-side model still produces better results, because it can be hundreds of times larger than anything that fits in a browser tab."},
            {"q": "Why are on-device tools free and unlimited?",
             "a": "Because the processing happens on your hardware, there is no per-image cost to the operator. The economic reason to impose limits and paywalls does not exist."},
            {"q": "Do browser-based tools work offline?",
             "a": "Usually, once the page and any models have been cached. That is a direct consequence of nothing needing to be sent anywhere."},
        ],
    ),
    _guide(
        slug="shooting-for-clean-cutouts",
        title="How to Photograph Anything for a Clean Cut-Out",
        h1="How to photograph anything for a clean cut-out",
        description="Background removal quality is decided when you take the photo. What separates edges cleanly, why hair and glass are hard, and how to shoot for it.",
        category="Photography",
        updated="2026-07-28",
        intro=[
            "Background removal is treated as a post-processing problem, and it mostly is not. Whether a cut-out looks clean or looks cut out is largely determined at the moment of capture, by decisions that cost nothing at the time and are impossible to fix afterwards.",
            "This guide covers what makes a subject separable, why certain materials are genuinely hard for every tool, and how to shoot so that the removal step becomes trivial.",
        ],
        sections=[
            {
                "h": "What removal is actually solving",
                "p": [
                    "For every pixel, a removal tool decides how much of it belongs to the subject. For most pixels this is easy — deep inside the subject or well outside it. The difficulty lives entirely in the transition band at the edge, which is rarely a clean line.",
                    "A single pixel at the boundary captured light from both the subject and the background, so its value is a mixture. Estimating the true mixing proportion, and the subject's underlying colour without background contamination, is the hard part of the problem. It is called matting, and it is much harder than segmentation.",
                    "Everything below follows from one principle: make the transition band as short and as unambiguous as possible.",
                ],
            },
            {
                "h": "Contrast is the whole thing",
                "p": [
                    "The single highest-leverage decision is the difference between subject and background — in brightness first, then in colour.",
                    "A dark subject against a light background separates trivially. A dark grey subject against a mid-grey background does not, and no tool will do it well, because the information required is genuinely not in the image. If you photograph a black jacket against a black sofa, you have not made a hard problem for the software; you have made an unsolvable one.",
                    "Brightness contrast matters more than hue contrast, because edge detection operates primarily on luminance. Two colours that look very different but have similar brightness — a mid red against a mid green — separate worse than you would expect.",
                    "The practical move is simply to look at the background before shooting and ask whether the subject's edges are visible against it. If you have to look hard, so will the algorithm.",
                ],
            },
            {
                "h": "Lighting the edges",
                "p": [
                    "The second lever is where the light is, and the goal is to keep the subject's outline bright and distinct rather than falling into shadow.",
                    "Front-lit subjects separate best. Light coming from behind the camera means the edges facing you are lit, so the outline is well defined against the background.",
                    "Backlighting is the hardest case: the subject becomes a silhouette with a rim of flare, edges lose definition, and the transition band grows wide and ambiguous. Backlit photos look dramatic and cut out badly.",
                    "A rim light — a light behind and to one side, catching the subject's outline — is the professional trick for exactly this problem, and it is why studio cut-outs look effortless. It draws a bright line around the subject that separates it from the background regardless of tone.",
                    "Also, keep the subject away from the background so the background falls out of focus slightly. Blur at the boundary is a real cue: the sharp subject and the soft background are easy to distinguish, and shadows cast onto a distant background do not appear in the frame.",
                ],
            },
            {
                "h": "The materials that are genuinely hard",
                "p": [
                    "Some subjects are difficult for every tool, and knowing which lets you plan around them.",
                    "Hair and fur are the classic case. Individual strands are thinner than a pixel, so a large fraction of the outline is semi-transparent — the transition band is not a thin line but a wide, fuzzy region. This is why hair is the benchmark everyone uses. Shooting hair against a strongly contrasting, evenly lit background is the only real answer.",
                    "Transparent and translucent materials — glass, bottles, plastic, sheer fabric, ice — break the underlying assumption that each pixel is either subject or background. A glass is both: you see it and you see through it. No automatic tool handles this well, and the practical approach is to photograph glassware on the background you actually want, or to accept manual work.",
                    "Motion blur widens the transition band across the whole moving region rather than just the edge. Reflective surfaces such as chrome show the background in the subject, which confuses tools in a way that is hard to correct. Fine repeating structures like wicker, mesh, lace and chain link have enormous edge length relative to their area, so small per-edge errors accumulate visibly.",
                ],
            },
            {
                "h": "A shooting checklist",
                "p": [
                    "In order of impact:",
                ],
                "list": [
                    "Pick a background that contrasts strongly in brightness with the subject.",
                    "Use a plain, untextured background — a wall, a sheet, a roll of paper.",
                    "Avoid backgrounds containing colours that appear in the subject.",
                    "Light from the front, not from behind. Add a rim light if you can.",
                    "Move the subject well away from the background to soften it and to move shadows out of frame.",
                    "Use even, soft lighting so no part of the outline falls into deep shadow.",
                    "Shoot at the highest resolution you have — more pixels across the transition band means a better matte.",
                    "Keep the subject in focus throughout; a soft edge is an ambiguous edge.",
                    "For hair, avoid backgrounds close in tone to the hair colour, which is the single most common cause of a poor cut-out.",
                ],
            },
            {
                "h": "Checking the result properly",
                "p": [
                    "Most cut-out flaws are invisible in the one view people check them in.",
                    "A subject cut from a white background, previewed on white, will look perfect even when it has a significant white fringe — the fringe is the same colour as what you are viewing it against. Always preview against a background very different from the original, and ideally against both black and white.",
                    "Zoom to 100% and inspect the edges, particularly around hair, shoulders and any fine detail. At fit-to-screen the errors that matter are all sub-pixel.",
                    "Look specifically for three things: a halo of the original background colour, a hard jagged edge where the transition band was collapsed to binary, and detached fragments where the tool lost a thin element like a strap or an antenna. All three are fixable with a refine brush if you catch them; none are fixable after you have published.",
                ],
            },
        ],
        takeaways=[
            "Cut-out quality is decided at capture — the removal step can only work with the contrast that exists in the photo.",
            "Brightness contrast between subject and background matters more than colour contrast, because edge detection works on luminance.",
            "Front lighting separates edges; backlighting produces silhouettes with wide, ambiguous transition bands.",
            "Hair, glass, motion blur, chrome and fine mesh are hard for every tool, for structural reasons rather than quality reasons.",
            "Always check a cut-out against a background unlike the original — a white fringe is invisible against white.",
        ],
        tools=["index", "ecommerce", "blur"],
        faqs=[
            {"q": "What background is best for background removal?",
             "a": "A plain, untextured one that contrasts strongly in brightness with your subject, and that does not share colours with it. Green screens work not because of the colour itself but because green rarely appears in skin, hair or clothing."},
            {"q": "Why does background removal struggle with hair?",
             "a": "Individual strands are thinner than a pixel, so much of the outline is semi-transparent rather than a clean boundary. Estimating those partial values across a wide, fuzzy region is a far harder problem than finding an edge."},
            {"q": "Can you remove the background from a photo of glass?",
             "a": "Not cleanly with any automatic tool. Transparent materials break the assumption that a pixel belongs to either the subject or the background — glass is both at once. Photograph glassware on the background you actually want."},
            {"q": "Does a higher resolution photo cut out better?",
             "a": "Yes. More pixels across the transition band at the subject's edge gives the tool more information to estimate partial coverage from, which is exactly where cut-out quality is decided."},
        ],
    ),
    _guide(
        slug="colour-profiles-explained",
        title="Colour Profiles: Why Photos Look Different on Every Screen",
        h1="Why your photo looks different on every screen",
        description="sRGB, Display P3 and Adobe RGB, what an embedded colour profile does, why exported images sometimes look washed out or oversaturated, and what to use where.",
        category="Formats",
        updated="2026-07-28",
        intro=[
            "You edit a photo until the colours are right, export it, and it looks wrong — flat and washed out on one screen, garish on another. Nothing is broken. What has happened is that the numbers in your file were interpreted against a different definition of what those numbers mean.",
            "Colour management is genuinely confusing, but the practical part is small, and understanding it fixes an entire category of frustrating problems.",
        ],
        sections=[
            {
                "h": "The numbers do not mean anything on their own",
                "p": [
                    "A pixel stored as (255, 0, 0) is 'as much red as this format can express'. It is not any particular red. How red it actually looks depends entirely on the display, and displays vary enormously in how saturated a red they can physically produce.",
                    "A colour space is the missing definition: it maps those numbers onto actual, measurable colours. Give the same file two different colour space definitions and it will display as two different images, without a single pixel value changing.",
                    "This is the whole problem in one sentence. Colour management exists to make sure that the definition travels with the file, so that everything downstream interprets the numbers the same way.",
                ],
            },
            {
                "h": "The three colour spaces you will meet",
                "p": [
                    "sRGB is the oldest and by far the most important. It dates to 1996, describes a relatively modest range of colours, and is the assumed default across the entire web. Anything that does not specify a colour space is treated as sRGB by essentially every browser and viewer.",
                    "Display P3 is Apple's adopted wide-gamut space, and it is now what most recent phones, tablets and laptops actually display. It covers roughly 25% more colours than sRGB, with noticeably more saturated reds and greens. Photos taken on a modern iPhone are captured in P3.",
                    "Adobe RGB is older and aimed at print, with a wider range of cyans and greens than sRGB but less reach in the reds than P3. It remains common in professional print workflows and is rarely the right choice for anything web-facing.",
                    "There is also ProPhoto RGB, which is enormous and used as an editing space in raw workflows. It should never leave your editor — exporting ProPhoto to the web produces the most dramatic version of the washed-out problem described below.",
                ],
            },
            {
                "h": "Why images look washed out",
                "p": [
                    "This is the most common symptom and it has one dominant cause: an image in a wide-gamut space displayed by something that assumes sRGB.",
                    "Say a photo is in Display P3 and its most saturated red is stored as (255, 0, 0). Viewed correctly, that is P3's red, which is very saturated. Viewed by software that assumes sRGB, the same numbers are interpreted as sRGB's red, which is less saturated. Every colour in the image is mapped to something duller than intended, and the whole photo looks flat and lifeless.",
                    "The reverse produces the opposite: an sRGB image interpreted as P3 renders every colour more saturated than intended. Skin tones go orange and reds glow.",
                    "Both are interpretation errors, not damage. The pixel values are fine; the wrong definition was applied.",
                ],
            },
            {
                "h": "Embedded profiles, and what strips them",
                "p": [
                    "The mechanism that prevents all this is the ICC profile — a block of metadata embedded in the file that states which colour space the numbers belong to. Software that reads it can convert correctly for whatever display is attached.",
                    "The problem is that profiles get lost. Some export settings omit them to save a few kilobytes. Some aggressive optimisation tools strip all metadata, profiles included. Some platforms discard them during their own recompression. Screenshots may or may not carry the profile of the content they captured.",
                    "And once the profile is gone, a wide-gamut image is indistinguishable from an sRGB image with unusual pixel values. Nothing downstream can recover the intent, which is why an image can look correct on your machine and wrong everywhere else — your editor remembered the colour space out of band, and the file did not carry it.",
                    "This is also the one case where blanket metadata stripping has a real cost. Removing EXIF and GPS from a shared image is good practice; removing the ICC profile along with it can visibly change how the image looks.",
                ],
            },
            {
                "h": "What to actually do",
                "p": [
                    "The rules are short:",
                ],
                "list": [
                    "Export to sRGB for anything going on the web, into a document, or to someone whose setup you do not know. It is the universal default and cannot be misinterpreted.",
                    "Always embed the profile. It is a couple of kilobytes and it removes the entire class of problem.",
                    "Convert, do not assign. Converting remaps the pixel values so the colours stay visually the same in the new space; assigning changes the label and leaves the values alone, which changes the appearance. Almost always you want convert.",
                    "Edit in a wide space if you like, but export narrow. Keeping P3 or ProPhoto in your editor preserves headroom; sending it out invites misinterpretation.",
                    "Use Display P3 deliberately, not accidentally — for a photo gallery where the extra saturation matters and you can serve sRGB as a fallback.",
                    "If an image looks flat everywhere but your editor, suspect a missing or wrong profile before you suspect the image.",
                ],
            },
            {
                "h": "Print is a different problem",
                "p": [
                    "Screens emit light and mix colours additively; ink absorbs light and mixes subtractively. The two have genuinely different achievable ranges, and some colours simply cannot be printed.",
                    "The saturated blues and greens that a screen produces easily are the usual casualties — they come out noticeably duller on paper, and no amount of profile correctness changes that. What colour management can do is choose intelligently how out-of-range colours are mapped into what the printer can reach, which is the job of the rendering intent setting.",
                    "For photographs, perceptual rendering compresses the whole range smoothly, preserving the relationships between colours at the cost of shifting all of them slightly. For logos and brand colours, relative colorimetric keeps in-range colours exact and clips the rest, which matters when a specific colour must be right. If you are sending work to print, ask the printer for their profile and soft-proof against it rather than guessing.",
                ],
            },
        ],
        takeaways=[
            "Pixel values are meaningless without a colour space — the same numbers describe different colours in sRGB and Display P3.",
            "Washed-out exports are almost always a wide-gamut image being interpreted as sRGB.",
            "Embed the ICC profile; it costs a couple of kilobytes and prevents the entire problem.",
            "Convert rather than assign — converting preserves appearance, assigning changes it.",
            "Stripping all metadata can remove the colour profile too, which is the one case where blanket stripping visibly hurts.",
        ],
        tools=["convert", "palette", "photo_filters"],
        faqs=[
            {"q": "Why does my photo look washed out after exporting?",
             "a": "Almost always because it is in a wide-gamut space like Display P3 or Adobe RGB and is being displayed by something that assumes sRGB. Export to sRGB with the profile embedded and it will look the same everywhere."},
            {"q": "Should I use sRGB or Display P3 for the web?",
             "a": "sRGB unless you have a specific reason and a fallback. It is the assumed default everywhere, so it cannot be misinterpreted. Display P3 is worth it for photo galleries where the extra saturation is the point."},
            {"q": "What is an ICC profile?",
             "a": "A block of metadata embedded in an image that states which colour space its pixel values belong to, so software can convert them correctly for whatever display is attached. Without it, viewers guess — and they guess sRGB."},
            {"q": "Does removing metadata affect image colour?",
             "a": "It can. If a tool strips all metadata including the ICC profile, a wide-gamut image loses its definition and will be interpreted as sRGB, which usually makes it look flat. Tools aimed at privacy should remove EXIF and GPS while keeping the colour profile."},
        ],
    ),
    _guide(
        slug="heic-and-why-your-photos-will-not-open",
        title="HEIC Explained — Why iPhone Photos Won't Open, and What to Convert To",
        h1="HEIC: why your iPhone photos will not open anywhere else",
        description="Why iPhones save photos as HEIC, what the format actually does, which devices refuse it, and how to convert to JPG without throwing away quality.",
        category="Formats",
        updated="2026-08-06",
        intro=[
            "You send a photo from your iPhone to a colleague and it arrives as a file nothing will open. You upload one to a web form and it is rejected. The photo looks perfectly fine on the phone that took it, which makes the failure feel arbitrary. It is not — the file is HEIC, and most of the computing world still cannot read it.",
            "This guide explains what HEIC is, why Apple switched to it, exactly where it breaks, and how to get out of it without losing what you paid for in quality.",
        ],
        sections=[
            {
                "h": "What HEIC actually is",
                "p": [
                    "HEIC stands for High Efficiency Image Container. The container is HEIF; the image data inside it is normally encoded with HEVC, also called H.265 — a video codec. That is the whole trick: still photos are compressed with a modern video codec rather than with a 1992 still-image codec, and video codecs have had thirty more years of research poured into them.",
                    "The result is roughly half the file size of a JPEG at the same visual quality. On a 128 GB phone that shoots 12-megapixel photos, halving the size of every image is not a rounding error — it is thousands of extra photos.",
                    "HEIC also carries things JPEG structurally cannot: 10-bit colour instead of 8-bit (so skies band less), transparency, image sequences such as Live Photos, and non-destructive edit data. When you crop a photo on an iPhone and can later press Revert, that is the container holding both the edit and the original.",
                ],
            },
            {
                "h": "Why it fails everywhere else",
                "p": [
                    "Apple made HEIC the default in iOS 11 in 2017. Support elsewhere has been slow, and the reason is licensing rather than difficulty. HEVC is covered by a large, fragmented set of patents administered by several separate licensing pools. Shipping a decoder can mean paying more than one of them, which is a straightforward business decision for Apple and an unattractive one for a free operating system, a browser vendor, or a small web service.",
                    "So the pattern you see is not random. Windows can open HEIC only if you install a codec from the Microsoft Store, which for a period was a paid item. Android added support in version 10, but individual apps still refuse it. Most websites reject it at upload because their server-side image library was built before it existed. Older photo software and print kiosks frequently do not know what it is at all.",
                    "The confusing part for most people is that the photo works flawlessly on the device that took it and on iMessage, so it does not feel like a broken file. It is a perfectly valid file that most software has chosen not to read.",
                ],
                "list": [
                    "iPhone and Mac: opens natively.",
                    "Windows 10/11: needs the HEIF and HEVC extensions installed.",
                    "Android 10 and later: system support, but app support varies.",
                    "Web upload forms: usually rejected outright.",
                    "Print shops and older editors: frequently unsupported.",
                ],
            },
            {
                "h": "The setting that prevents the problem",
                "p": [
                    "If you would rather not deal with this again, the iPhone has a switch. Under Settings → Camera → Formats, 'High Efficiency' shoots HEIC and 'Most Compatible' shoots JPEG. Choosing the second one costs you roughly double the storage per photo and the 10-bit colour depth, and buys you files that open anywhere.",
                    "There is a second, subtler setting worth knowing. Under Settings → Photos, at the very bottom, 'Transfer to Mac or PC' can be set to 'Automatic' or 'Keep Originals'. On Automatic, the phone converts HEIC to JPEG as it transfers over a cable. On Keep Originals, it hands over the raw HEIC and you get the problem back. Many people have this set to Keep Originals without knowing.",
                    "Neither setting changes photos you have already taken, which is the situation most people are actually in.",
                ],
            },
            {
                "h": "Converting without wasting the quality you paid for",
                "p": [
                    "Converting HEIC to JPEG means decoding the HEVC data and re-encoding it as JPEG. Because JPEG is lossy, this is a generational loss — you are compressing already-compressed data. In practice the loss is invisible at a sensible quality setting, but it is real, and it means you should convert from the original once rather than repeatedly converting the converted file.",
                    "Two things are genuinely lost and cannot be recovered by any converter. The first is colour depth: HEIC's 10-bit channel becomes JPEG's 8-bit, which can introduce faint banding in large smooth gradients such as a clear sky at sunset. The second is anything that depended on the container — Live Photo motion, depth maps used for portrait blur, and the ability to revert edits. A converted file is a flat, final picture.",
                    "If you want none of that loss, convert to PNG instead. It is lossless, so the pixels survive exactly, at the cost of a file several times larger than the HEIC you started with. That is the right choice for a photo you intend to edit further, and the wrong one for an email attachment.",
                ],
                "list": [
                    "Converting for a web form or email → JPEG at high quality.",
                    "Converting because you will edit it further → PNG, or keep the HEIC as your master.",
                    "Converting a large batch for storage → JPEG; the size saving is the point.",
                    "Never convert a file that was already converted — go back to the original.",
                ],
            },
            {
                "h": "Where the conversion happens matters",
                "p": [
                    "Most 'HEIC to JPG' results are upload-based services. Your photo travels to a server, is converted there, and comes back. That is a meaningful thing to agree to for a camera roll, which is typically the most personal set of files a person owns, and the photos usually still carry the GPS coordinates of where each was taken.",
                    "A browser can do this work itself. Decoding HEIC in a page requires a WebAssembly build of libheif, which is a few megabytes and then cached — after that the conversion is local, and the file never leaves the machine. Our HEIC converter works this way, which is also why it keeps working with the network switched off.",
                    "The practical tell for any converter you are considering: if it can convert with the connection dropped, the work was local. If it cannot, your photos went somewhere.",
                ],
            },
            {
                "h": "Batch converting a camera roll",
                "p": [
                    "The common real task is not one photo, it is four hundred from a holiday. A few things make that go smoothly.",
                    "Convert from the originals in one pass rather than in several rounds, so you take the generational loss once. Keep the HEIC files until you have confirmed the JPEGs are what you wanted — deleting the masters first is the one irreversible step in the process. And if the destination is a web upload with a size cap, convert first and compress second, as separate decisions; a converter that silently shrinks your images to hit a size target has made a quality choice on your behalf.",
                    "If the photos are going somewhere public, this is also the natural moment to strip metadata, since you are rewriting every file anyway.",
                ],
            },
        ],
        takeaways=[
            "HEIC is a video codec (HEVC) applied to still photos, which is why it halves file size against JPEG.",
            "It fails outside Apple's ecosystem for patent-licensing reasons, not technical ones — the files are not corrupt.",
            "Settings → Camera → Formats → 'Most Compatible' stops the problem for future photos, at double the storage.",
            "Converting to JPEG permanently loses 10-bit colour, Live Photo motion, depth data and the ability to revert edits.",
            "Convert once from the original, and keep the HEIC masters until you have checked the output.",
        ],
        tools=["heic", "convert", "compress", "exif"],
        faqs=[
            {"q": "Does converting HEIC to JPG lose quality?",
             "a": "Slightly, and unavoidably — JPEG is lossy, so re-encoding already-compressed data is a generational loss. At a high quality setting it is not visible. What is genuinely lost is 10-bit colour depth, Live Photo motion and depth data, none of which JPEG can store. Convert to PNG if you need the pixels preserved exactly."},
            {"q": "Why does my HEIC photo open on my phone but not my laptop?",
             "a": "Because the file is fine and your laptop lacks a decoder. HEIC uses the HEVC codec, which carries patent licensing costs, so Windows requires an extension from the Microsoft Store and many applications simply never added support."},
            {"q": "Can I stop my iPhone saving photos as HEIC?",
             "a": "Yes — Settings → Camera → Formats → Most Compatible. New photos will be JPEG. Existing HEIC photos are unaffected and still need converting."},
            {"q": "Is it safe to convert HEIC photos online?",
             "a": "It depends entirely on whether the conversion runs on a server or in your browser. Server-based converters receive your photos, which for a camera roll carrying GPS data is worth thinking about. A browser-based converter decodes locally and uploads nothing — you can verify this by turning off your network and watching it still work."},
        ],
    ),
    _guide(
        slug="making-stickers-for-whatsapp-and-telegram",
        title="How to Make WhatsApp and Telegram Stickers That Actually Work",
        h1="How to make stickers that actually work in WhatsApp and Telegram",
        description="The real technical rules for WhatsApp and Telegram stickers — 512x512, the 100 KB cap, why transparency matters, and how to make one from a photo.",
        category="Editing",
        updated="2026-08-06",
        intro=[
            "Sticker packs look like a casual thing, and then you try to make one and discover both apps enforce a surprisingly strict set of rules. Wrong dimensions, wrong format, one kilobyte over the limit, and the app refuses the file with an error that rarely says which rule you broke.",
            "This guide lists the rules that are actually enforced, explains why each exists, and covers the part most guides skip — how to get a clean cut-out of your subject, which is what separates a sticker from a photo with a white box around it.",
        ],
        sections=[
            {
                "h": "The rules WhatsApp actually enforces",
                "p": [
                    "WhatsApp's requirements are specific and unforgiving. A static sticker must be exactly 512 by 512 pixels, in WebP format, and no larger than 100 kilobytes. Animated stickers get 500 KB and must run no longer than 10 seconds. Each sticker also needs a small margin of transparent padding at the edges, and a pack needs a 96 by 96 pixel tray icon.",
                    "The 100 KB cap is the one that catches people. It is not a guideline — the file is rejected. It exists because stickers are sent constantly, cached aggressively on device, and often delivered over slow mobile connections in markets where WhatsApp is the primary messaging app. A 2 MB sticker sent to a group of fifty people is a real cost to someone.",
                    "Hitting 512x512 in WebP under 100 KB is comfortable for illustrations and flat art. It gets tight for photographs, which is why quality often has to be stepped down until the file fits.",
                ],
                "list": [
                    "Static: exactly 512x512 px, WebP, under 100 KB.",
                    "Animated: 512x512 px, WebP, under 500 KB, max 10 seconds.",
                    "Tray icon: 96x96 px, PNG, under 50 KB.",
                    "A pack needs at least 3 and at most 30 stickers.",
                    "Leave roughly 8-16 px of transparent padding around the subject.",
                ],
            },
            {
                "h": "Telegram's rules are different",
                "p": [
                    "Telegram is looser but not identical, and assuming the two are the same is a common way to waste an afternoon. Telegram stickers must have one side exactly 512 pixels, with the other side 512 or smaller — so 512x384 is legal on Telegram and rejected by WhatsApp.",
                    "Telegram accepts PNG as well as WebP, which removes the 100 KB squeeze entirely for static stickers, and its file limits are far more generous. Packs are created by messaging @Stickers rather than through a third-party app.",
                    "The practical consequence: if you want one sticker to work on both platforms, build to WhatsApp's rules. A 512x512 WebP under 100 KB is legal on Telegram too. The reverse is not true.",
                ],
            },
            {
                "h": "Why transparency is the whole point",
                "p": [
                    "A sticker is pasted over a conversation, and chat backgrounds are not white — they are patterned, coloured, dark in dark mode, and set to a photo by a large minority of users. A sticker with a solid background renders as a rectangle sitting on top of the chat, which reads as a mistake even when the image inside it is good.",
                    "This is why WebP matters beyond file size. WebP supports lossy compression with an alpha channel, a combination PNG cannot offer — PNG transparency is always lossless and therefore large. A photographic cut-out with soft edges can be lossy WebP at 40 KB where the PNG equivalent is 400 KB.",
                    "The transparent padding around the edge exists for a related reason: both apps draw a subtle outline or shadow behind stickers, and a subject touching the edge of the canvas gets visibly clipped.",
                ],
            },
            {
                "h": "Getting a clean cut-out from a photo",
                "p": [
                    "The hard part of making a sticker from a photo is separating the subject from its background convincingly. Hard edges are easy; the problems are always hair, fur, motion blur and anything semi-transparent such as a glass or a wisp of smoke.",
                    "Two things improve results more than any amount of tool choice. First, contrast between subject and background — a dark jacket against a dark sofa has no edge to find, and no software will invent one. Second, focus: a subject that is slightly out of focus has no crisp boundary, so the cut-out inherits the mush.",
                    "For fur and flyaway hair, expect to touch up by hand. A refine brush that lets you paint background back in or restore detail is worth more than a marginally better automatic mask, because the automatic mask is right about 95% of the pixels and the remaining 5% are all in the same visually obvious place — around the head.",
                    "Our sticker maker runs the cut-out in your browser and exports straight to 512x512 WebP, stepping the quality down until it clears 100 KB.",
                ],
            },
            {
                "h": "Making it read at thumbnail size",
                "p": [
                    "Stickers are viewed small — often around 128 pixels on screen despite the 512 pixel file. Designs that look great at full size regularly turn to mush in the chat, and it is nearly always for one of three reasons.",
                    "Too much detail: a full-body photo becomes an unrecognisable smudge. Crop tight to the face or the single element that carries the joke. Text too small: caption text needs to be far larger than feels reasonable, typically 10-15% of the canvas height, in a heavy weight. And insufficient edge contrast: a dark subject on a dark chat background disappears, which is why a white or light outline around the cut-out is near-universal in sticker design. It is not decoration — it guarantees the silhouette reads against any background.",
                ],
                "list": [
                    "Crop tight — one subject, filling most of the frame.",
                    "Add a thick outline so the shape reads on dark and light backgrounds.",
                    "Caption text at 10-15% of canvas height, heavy weight, short words.",
                    "Check it at 128 px before committing; that is how it will be seen.",
                ],
            },
            {
                "h": "Where sticker tools tend to go wrong",
                "p": [
                    "Most sticker makers are phone apps that upload your photo, add a watermark, or require an account. The watermark is the most damaging of the three: a sticker is a thing you send to other people repeatedly, so a watermarked sticker is an advertisement you have agreed to distribute to your friends on the app's behalf, forever.",
                    "The upload question also deserves more weight here than usual. Stickers are usually made from photos of family, friends and pets — exactly the images people are most careless about handing over and would most object to losing.",
                    "The honest limitation of a browser-based approach: it can build the sticker file, but it cannot install a pack into WhatsApp, because pack installation goes through the app's own API from a native app. You export the image and add it through a pack app, or send it directly into a chat.",
                ],
            },
        ],
        takeaways=[
            "WhatsApp: exactly 512x512, WebP, under 100 KB — the size cap is enforced, not advisory.",
            "Telegram is looser (one side 512, PNG allowed), so build to WhatsApp's rules and it works on both.",
            "Lossy WebP with alpha is why stickers can be transparent and still tiny; PNG transparency is always large.",
            "Design for roughly 128 px on screen: crop tight, add an outline, oversize any text.",
            "Never accept a watermark on a sticker — you would be distributing it to your friends every time you send it.",
        ],
        tools=["sticker", "index", "crop", "convert"],
        faqs=[
            {"q": "Why does WhatsApp reject my sticker?",
             "a": "Almost always dimensions or size. It must be exactly 512x512 pixels, in WebP, and under 100 KB. Photographs frequently exceed the size cap, so the quality has to be stepped down until it fits."},
            {"q": "Do stickers need a transparent background?",
             "a": "Technically no, practically yes. Chat backgrounds are patterned, dark or user-set photos, so a sticker with a solid background renders as an obvious rectangle pasted over the conversation."},
            {"q": "Can I use the same sticker on WhatsApp and Telegram?",
             "a": "Yes, if you build it to WhatsApp's stricter rules. A 512x512 WebP under 100 KB is valid on both. A Telegram sticker with unequal sides will be rejected by WhatsApp."},
            {"q": "Can a website install a sticker pack for me?",
             "a": "No. Pack installation goes through each app's own API and requires a native app. A web tool can produce a correctly formatted sticker image, which you then add via a pack app or send straight into a chat."},
        ],
    ),
    _guide(
        slug="qr-codes-that-actually-scan",
        title="QR Codes That Actually Scan — Size, Contrast and Error Correction",
        h1="Why QR codes fail to scan, and how to make ones that always do",
        description="How QR codes really work, the minimum size for a given distance, why low contrast and inverted colours break scanning, and what error correction buys you.",
        category="Formats",
        updated="2026-08-06",
        intro=[
            "A QR code either scans instantly or it does not scan at all, and the failures are rarely random. They come from a small set of causes: the code is too small for the distance, the contrast is too low, the colours are inverted, or a logo has been dropped in the middle without the error correction to survive it.",
            "This guide covers what the black squares are actually doing, and the specific numbers that decide whether a code works on a poster, a business card or a table tent.",
        ],
        sections=[
            {
                "h": "What is inside a QR code",
                "p": [
                    "A QR code is not an image of a link. It is a two-dimensional data structure with defined regions, and knowing them explains every failure mode.",
                    "The three large squares in the corners are finder patterns; they let a scanner locate the code and work out its rotation, which is why a QR code scans upside down. The smaller square near the fourth corner is the alignment pattern, correcting for the code being photographed at an angle. The dotted lines running between the finder patterns are timing patterns, establishing the grid size. Everything else is data and error correction.",
                    "Around all of it is the quiet zone — a margin of blank space, four modules wide, where a module is one of the small squares. The quiet zone is part of the specification, not decoration. A code printed flush against text or a coloured background frequently fails for this reason alone, and it is the single most common design mistake.",
                ],
            },
            {
                "h": "Error correction: how much damage it survives",
                "p": [
                    "QR codes use Reed-Solomon error correction, the same family of algorithm that lets a scratched CD play. There are four levels, and choosing one is a trade between resilience and capacity.",
                    "Level L recovers about 7% of the data, M about 15%, Q about 25% and H about 30%. Higher levels mean more of the code is redundancy, so for a given amount of data the code needs more modules — a longer URL at level H produces a visibly denser code than the same URL at level L.",
                    "This is what makes centre logos possible. A logo covering 20% of the code is simply damage, and at level H the code still decodes. At level L the same logo destroys it. If you are placing a logo, use H and keep the coverage under about 25%; there is no way to place a logo 'correctly' other than leaving enough redundancy to absorb it.",
                    "The other reason to raise the level is the physical environment. A code on a table in a restaurant, a sticker on a lamppost, a label on a machine — these accumulate scratches, grease and fading. Level Q or H is a maintenance decision.",
                ],
                "list": [
                    "L (~7%): screens and digital use where nothing will damage it.",
                    "M (~15%): the usual default; fine for clean print.",
                    "Q (~25%): print that will be handled, or a small logo.",
                    "H (~30%): outdoor, industrial, or a centre logo.",
                ],
            },
            {
                "h": "How big does it need to be?",
                "p": [
                    "There is a widely used rule of thumb: the code's width should be at least one tenth of the scanning distance. Scanned from one metre, the code should be at least 10 cm across. From five metres — a poster across a room — it needs to be 50 cm, which is far larger than most people expect and is why poster QR codes so often fail.",
                    "The rule is conservative and modern phone cameras often beat it, but designing to it means the code works for the person with an older phone in poor light, which is the case that matters.",
                    "There is also an absolute floor. Below roughly 2 cm, a printed code becomes unreliable regardless of distance, because the individual modules approach the resolution of the printing process and the camera. If your code carries a long URL it has more modules in the same physical space, each one smaller — so shortening the URL genuinely improves scannability. A link shortener is a legitimate technical fix here, not just tidiness.",
                ],
            },
            {
                "h": "Contrast, colour and the inversion trap",
                "p": [
                    "Scanners look for a luminance difference between modules and background. The specification effectively wants a contrast ratio of at least 3:1, and in practice you want considerably more.",
                    "Two rules break codes constantly. The first: the code must be darker than its background. Scanners expect dark modules on a light field, and while many modern decoders handle inversion, a meaningful number do not. A white code on a black poster is a coin flip across the installed base of scanning apps.",
                    "The second: colour contrast is not luminance contrast. Red modules on a green background look strongly contrasting to a human eye and can be nearly identical in brightness, which is what the camera is measuring. If you are colouring a code, check it in greyscale — if the modules and the background look similar there, the code will struggle.",
                    "Gradients are usable if the light end stays clearly darker than the background, but every increase in styling is a decrease in margin. A code is a functional object first.",
                ],
                "list": [
                    "Dark modules on a light background, not the reverse.",
                    "Check the design in greyscale before printing.",
                    "Keep the four-module quiet zone completely clear.",
                    "Avoid placing a code over a photograph or texture.",
                ],
            },
            {
                "h": "Static versus dynamic codes",
                "p": [
                    "A static QR code contains the destination directly. Anyone scanning it goes straight there, it never expires, it works with no third party involved — and it cannot be changed. Fixing a typo means reprinting.",
                    "A dynamic QR code contains a short URL owned by a service, which redirects. That gives you editable destinations and scan analytics, and it introduces a dependency: the code works only as long as that company exists, keeps the link active, and does not start charging. There is a well-established pattern of free dynamic QR services expiring links after a trial and turning printed materials into dead ends.",
                    "For anything printed at volume or intended to last, static is the safer engineering choice. Use dynamic when the ability to change the destination is genuinely worth the dependency — a campaign you expect to redirect, for instance. Our QR generator produces static codes only, which is a deliberate limitation rather than a missing feature.",
                ],
            },
            {
                "h": "Test before you print a thousand",
                "p": [
                    "Test at the real size, on the real material, in the light where it will live. A code that scans on your monitor tells you very little about a matte-laminated card under a restaurant's dim lighting.",
                    "Test with more than one phone, including an older one, and with the default camera app rather than a dedicated scanner app — most people scan with the camera. Test at the distance people will actually stand. And print one physical proof before the run: paper absorbs ink and slightly thickens the modules, which reduces the effective quiet zone and can push a marginal code over the edge.",
                ],
            },
        ],
        takeaways=[
            "The quiet zone — four modules of blank space — is part of the spec, and omitting it is the most common failure.",
            "Code width should be at least 1/10th of the scanning distance; posters need far bigger codes than people expect.",
            "Error correction level H absorbs a centre logo up to about 25% coverage; level L will not.",
            "Colour contrast is not luminance contrast — check the design in greyscale.",
            "Static codes never expire; dynamic codes depend on a company continuing to honour the redirect.",
        ],
        tools=["qr", "convert", "palette"],
        faqs=[
            {"q": "Why won't my QR code scan?",
             "a": "In order of likelihood: no quiet zone around it, too small for the distance, insufficient luminance contrast, inverted colours (light code on dark background), or a logo placed without enough error correction to absorb it."},
            {"q": "Can I put a logo in the middle of a QR code?",
             "a": "Yes, if you generate at error correction level H and keep the logo under about 25% of the area. The logo is treated as damage, and level H recovers roughly 30% of the data."},
            {"q": "Do QR codes expire?",
             "a": "Static codes never expire — the destination is encoded in the code itself. Dynamic codes point at a redirect owned by a service, and stop working if that service ends the link or the company disappears."},
            {"q": "What size should a QR code be on a poster?",
             "a": "At least one tenth of the viewing distance. Read from three metres, the code needs to be about 30 cm wide. Below roughly 2 cm nothing scans reliably regardless of distance."},
        ],
    ),
    _guide(
        slug="favicons-that-work-everywhere",
        title="Favicons Explained — Every Size, Format and File You Actually Need",
        h1="Favicons: which sizes and files you actually need in 2026",
        description="What a favicon set really requires — ICO versus PNG versus SVG, Apple touch icons, maskable PWA icons, dark mode, and the HTML that ties them together.",
        category="Formats",
        updated="2026-08-06",
        intro=[
            "Favicon advice has accumulated for twenty-five years, and most of what you find recommends a list of thirty files for devices that no longer exist. The real requirement in 2026 is much shorter, but it is not one file either, and the parts that are still genuinely needed are the ones people skip.",
            "This guide covers what each file is for, which ones you can safely drop, and the specific case — maskable icons — that silently makes installed web apps look broken.",
        ],
        sections=[
            {
                "h": "Why one file was never enough",
                "p": [
                    "The favicon began as favicon.ico in Internet Explorer 5, in a Windows icon container format that can hold several resolutions in one file. That was a sensible design, and it is why ICO persists despite being unusual in every other respect.",
                    "The requirement expanded because the contexts multiplied. A browser tab needs about 16 pixels. A bookmark bar and a pinned tab want more. iOS wants a 180-pixel icon for the home screen. Android and installed web apps want 192 and 512 pixel icons, and want to crop them into whatever shape the launcher uses. A search result may show your icon at 48 pixels.",
                    "These are not the same image scaled. A logo that reads at 512 pixels frequently turns to porridge at 16, which is why serious favicon sets contain a simplified mark for the small sizes and the full logo for the large ones.",
                ],
            },
            {
                "h": "The set that actually matters now",
                "p": [
                    "For a site starting today, the following covers effectively all real traffic. Everything else on the traditional thirty-file list is for browsers and devices with negligible share.",
                    "An ICO at the site root remains worth including even though PNG is universally supported, because a surprising amount of software — feed readers, link previewers, older enterprise browsers — still requests /favicon.ico by path without reading your HTML at all. It is 15 KB of insurance.",
                    "An SVG favicon is the modern addition and the most useful one, because it is resolution-independent and can respond to dark mode. Browsers that support it prefer it; those that do not fall back to the PNGs.",
                ],
                "list": [
                    "favicon.ico — 16 and 32 px inside one file, at the site root.",
                    "favicon.svg — scalable, and can adapt to dark mode.",
                    "favicon-96x96.png — search results and general fallback.",
                    "apple-touch-icon.png — 180x180, for iOS home screens.",
                    "icon-192.png and icon-512.png — referenced from the web manifest.",
                    "A 512x512 maskable icon — see below; this is the one everyone misses.",
                ],
            },
            {
                "h": "Maskable icons, and why installed apps look wrong without them",
                "p": [
                    "Android launchers crop app icons into a shape of the device's choosing — a circle, a squircle, a rounded square. If your icon is a normal square PNG, the launcher crops it, and the corners of your logo are cut off. If the logo fills the square, the crop removes a visible slice of it.",
                    "The fix is a separate icon declared with `\"purpose\": \"maskable\"` in the manifest. A maskable icon is designed with a safe zone: all essential content must sit inside a circle covering the central 80% of the canvas, with the outer 10% on each side treated as expendable bleed that the crop may remove. The background must extend to the full canvas, so no shape of crop ever exposes an empty corner.",
                    "This means a maskable icon is not the same file as your normal icon with a different label. It is the same logo, smaller within its canvas, on a filled background. Declaring a normal icon as maskable produces exactly the clipped result the mechanism exists to prevent.",
                ],
            },
            {
                "h": "Dark mode, and the disappearing black logo",
                "p": [
                    "Browser tabs are dark in dark mode, and a favicon that is black line art on transparency becomes invisible against them. This is common and easy to miss, because developers who work in dark mode look at their own favicon all day and stop seeing that it is a faint smudge.",
                    "An SVG favicon can solve this directly, because SVG can carry a media query. A `prefers-color-scheme` rule inside the SVG lets the same file draw dark strokes on light backgrounds and light strokes on dark ones. No other favicon format can do this.",
                    "If you cannot use SVG, the robust alternative is to give the icon its own background rather than relying on transparency — a coloured rounded square with the mark reversed out of it reads on any tab colour. Most well-known sites do exactly this, which is why so many favicons are a letter on a solid block.",
                ],
            },
            {
                "h": "The HTML, and the parts that are optional",
                "p": [
                    "The declarations are short. A link for the SVG, one for the ICO as fallback, one for the Apple touch icon, and one for the manifest — the manifest then carries the PWA icons rather than the HTML doing it.",
                    "Two long-standing recommendations can now be dropped. The `msapplication-*` meta tags for Windows tiles refer to a Start menu feature that no longer exists. And the long ladder of `apple-touch-icon-76x76`, `-120x120` and so on is unnecessary: iOS has scaled a single 180-pixel icon down for years.",
                    "One detail that still bites: browsers cache favicons aggressively and often ignore normal cache headers, so a changed favicon can appear stale for a long time. Changing the filename is more reliable than waiting.",
                ],
                "list": [
                    "<link rel=\"icon\" href=\"/favicon.svg\" type=\"image/svg+xml\">",
                    "<link rel=\"icon\" href=\"/favicon.ico\" sizes=\"32x32\">",
                    "<link rel=\"apple-touch-icon\" href=\"/apple-touch-icon.png\">",
                    "<link rel=\"manifest\" href=\"/site.webmanifest\">",
                ],
            },
            {
                "h": "Designing a mark that survives 16 pixels",
                "p": [
                    "At 16 pixels you have 256 pixels in total to work with, and after antialiasing perhaps a dozen meaningful shapes. Almost nothing survives that intact.",
                    "Words never do — a company name in a favicon is a grey smear. Use one letter, or a symbol. Thin strokes disappear, so weight lines far more heavily than looks right at full size. Detail must be removed rather than shrunk: the small favicon should be a deliberately simplified drawing, not the logo scaled down. And test on both a white and a dark tab strip, at actual size, on a real screen rather than zoomed in your editor.",
                    "Our favicon generator produces the full set from a single source image, including the maskable variant and the manifest.",
                ],
            },
        ],
        takeaways=[
            "Six files cover essentially all real traffic; the thirty-file lists online are maintaining support for dead devices.",
            "Keep favicon.ico at the site root — plenty of software requests that path without reading your HTML.",
            "A maskable icon is a genuinely different file: logo inside the central 80%, background filling the whole canvas.",
            "Only SVG favicons can respond to dark mode; otherwise give the icon its own solid background.",
            "Design the 16 px mark by removing detail, not by scaling the logo down.",
        ],
        tools=["favicon", "convert", "resize", "crop"],
        faqs=[
            {"q": "Do I still need favicon.ico?",
             "a": "Yes, as a fallback. Modern browsers prefer PNG and SVG, but a lot of other software — feed readers, link preview generators, older enterprise browsers — requests /favicon.ico by path without parsing your HTML."},
            {"q": "What is a maskable icon?",
             "a": "An icon designed to survive being cropped into a circle or squircle by an Android launcher. All important content sits within the central 80% and the background fills the entire canvas, so no crop shape exposes an empty corner or clips the logo."},
            {"q": "Why does my favicon disappear in dark mode?",
             "a": "Because it is dark artwork on a transparent background, and the tab strip is dark. Either use an SVG favicon with a prefers-color-scheme rule, or give the icon its own solid background colour."},
            {"q": "Why won't my new favicon show up?",
             "a": "Browsers cache favicons very aggressively and frequently ignore cache headers for them. Changing the filename is far more reliable than waiting for the cache to expire."},
        ],
    ),
    _guide(
        slug="gif-versus-video-for-short-clips",
        title="GIF vs Video — Why GIFs Are Enormous and When to Use One Anyway",
        h1="GIF vs video: why GIFs are so big, and when one is still the right answer",
        description="Why a three-second GIF can be larger than a minute of video, what GIF's 256-colour limit really costs, and how to decide between GIF, MP4 and WebP.",
        category="Formats",
        updated="2026-08-06",
        intro=[
            "A three-second GIF can easily be 8 megabytes. The same clip as an MP4 is often under 400 kilobytes and looks better. That is a twenty-fold difference, and it surprises people because GIFs feel like small, casual things.",
            "The reason is that GIF is from 1987 and was never designed for video. Understanding what it does explains both why it is so inefficient and why it nonetheless remains the right choice in a few specific places.",
        ],
        sections=[
            {
                "h": "What GIF is doing to each frame",
                "p": [
                    "GIF stores an animation as a sequence of images compressed with LZW, a general-purpose lossless algorithm that looks for repeated byte patterns. Critically, its compression works within each frame and, in the best case, stores only the rectangle that changed between frames. It has no concept of motion.",
                    "This is the central inefficiency. Modern video codecs achieve their size by predicting: they encode a keyframe, then describe subsequent frames as motion vectors — 'this block of pixels moved eleven pixels left' — plus a small correction. A panning shot is nearly free to a video codec, because almost everything simply moved. To GIF, a panning shot means every pixel in every frame changed, so nothing can be skipped and every frame is stored close to whole.",
                    "That is why camera movement destroys GIF file size while a static shot with a small moving element stays reasonable. It is also why the advice 'crop the GIF' works so well: you are removing pixels that were being stored repeatedly.",
                ],
            },
            {
                "h": "The 256-colour limit",
                "p": [
                    "A GIF frame can contain at most 256 distinct colours, drawn from a palette stored in the file. A photograph or a video frame typically contains tens of thousands. Reducing that to 256 is where most of the visible quality loss comes from — not from the compression, which is lossless, but from the palette.",
                    "Two techniques manage the reduction. Palette selection picks the 256 colours that best represent the frame, which is why a clip with a narrow colour range survives well and a colourful one does not. Dithering scatters pixels of available colours to simulate missing ones, trading banding for a fine noise texture.",
                    "Dithering has a cruel interaction with the compression. LZW compresses repeated patterns, and dithering deliberately introduces high-frequency noise, which has no repeated patterns. So turning dithering up to fix banding can substantially increase the file size. Gradients — skies, shadows, fades — are the worst case for GIF: they band badly without dithering and inflate badly with it.",
                ],
                "list": [
                    "Narrow palettes (cartoons, screencasts, line art) compress well.",
                    "Gradients and skies band or bloat, with no good setting.",
                    "Dithering trades banding for noise, and noise costs file size.",
                    "Reducing to 64 or 128 colours often saves more than reducing frames.",
                ],
            },
            {
                "h": "So why does anyone still use GIF?",
                "p": [
                    "Because of where it is allowed. GIF plays as an image, which means it works in contexts that forbid or awkwardly handle video: email clients, many chat and forum inputs, documentation platforms, some CMS fields, and older wiki software. An MP4 in an email will not play; a GIF will.",
                    "It also autoplays silently and loops without any player controls, with no user gesture required. On mobile browsers, video autoplay is restricted by policy — video needs to be muted, inline and often explicitly permitted — while a GIF simply animates. For a small looping demonstration, that reliability is worth real bytes.",
                    "And it degrades to a still image everywhere, which no video format does.",
                ],
            },
            {
                "h": "The alternatives, and what each costs",
                "p": [
                    "Animated WebP is the closest replacement: it supports full colour, real transparency, and both lossy and lossless modes, at file sizes commonly 30-50% below an equivalent GIF. It is supported by every current browser. It is not accepted by many of the platforms that accept GIF, which is exactly the problem it fails to solve.",
                    "MP4 with H.264 is the size winner by a wide margin for anything photographic, and plays everywhere video is allowed. For a web page, a muted autoplaying looping MP4 is almost always the correct implementation of what people mean by 'a GIF' — same visual result, a fraction of the bandwidth. The cost is that it is a video element with the policies that come with it.",
                    "APNG deserves a mention as the honest answer for animations that need lossless quality and true alpha, such as UI animations on a transparent background. It is larger than WebP and supported in current browsers.",
                ],
            },
            {
                "h": "Making a GIF that is not enormous",
                "p": [
                    "If GIF is the requirement, the size levers in order of effectiveness are dimensions, duration, frame rate and palette — in that order, and it is not close.",
                    "Dimensions dominate because cost scales with area: halving the width and height quarters the pixel count. A 480-pixel-wide GIF is usually plenty, and 320 is fine for a UI demonstration. Duration is linear, and ruthless trimming to the two seconds that matter is the second-biggest win. Frame rate can usually drop to 10-15 fps before motion looks wrong, against 30 in the source. Palette reduction to 128 or 64 colours is the last lever and often costs less quality than expected.",
                    "One structural trick: a static background with a small animated region compresses far better than a moving camera, so stabilising or cropping to the moving part pays twice.",
                ],
                "list": [
                    "Resize first — width 320-480 px is usually enough.",
                    "Trim to only the seconds that matter.",
                    "Drop to 10-15 fps.",
                    "Reduce the palette to 128 or 64 colours.",
                    "Crop to the moving region if the camera is static.",
                ],
            },
            {
                "h": "A short decision rule",
                "p": [
                    "If it is going on a web page you control, use a muted looping MP4 and stop thinking about it. If it is going into an email, a chat box, a forum post or a documentation platform that only takes images, use a GIF and optimise it hard. If it needs transparency and quality, use APNG or animated WebP and check the target accepts it.",
                    "The one combination to avoid is a long, full-screen, camera-moving GIF. That is the case where the format is at its absolute worst and something else is always available.",
                ],
            },
        ],
        takeaways=[
            "GIF has no motion prediction, so camera movement forces near-whole frames to be stored — the main size driver.",
            "The 256-colour palette, not the compression, causes most visible GIF quality loss.",
            "Dithering fixes banding by adding noise, and noise defeats LZW — so it can inflate the file substantially.",
            "GIF survives because it is allowed where video is not, and autoplays with no policy restrictions.",
            "To shrink one: dimensions first, then duration, then frame rate, then palette.",
        ],
        tools=["gif", "video_gif", "video_converter", "compress", "crop"],
        faqs=[
            {"q": "Why is my GIF bigger than the video it came from?",
             "a": "Because video codecs describe motion between frames while GIF stores each frame almost whole, and GIF's LZW compression is defeated by the noise in photographic content. A twenty-fold difference against an MP4 is normal."},
            {"q": "How do I make a GIF smaller?",
             "a": "In order of impact: reduce the dimensions (cost scales with area), trim the duration, drop the frame rate to 10-15 fps, and only then reduce the colour palette."},
            {"q": "Should I use WebP instead of GIF?",
             "a": "For your own web pages, yes — animated WebP is typically 30-50% smaller with full colour. But the platforms that force you into GIF in the first place, like email and many chat inputs, usually do not accept WebP either."},
            {"q": "Why does my GIF look grainy or banded?",
             "a": "The 256-colour palette. Gradients cannot be represented, so they either band into visible steps or get dithered into noise — and the dithering noise increases the file size."},
        ],
    ),
    _guide(
        slug="getting-text-out-of-images-with-ocr",
        title="OCR Explained — How to Get Accurate Text Out of Images and Screenshots",
        h1="How OCR really works, and what wrecks its accuracy",
        description="What optical character recognition does to your image, why screenshots read almost perfectly and photos do not, and the specific things that destroy accuracy.",
        category="Documents",
        updated="2026-08-06",
        intro=[
            "OCR feels like it should either work or not work, and instead it produces text that is 99% right on one image and unusable on another that looks similar. The difference is rarely luck — it comes from a short list of image properties that the recognition pipeline is extremely sensitive to.",
            "This guide explains what happens between your image and the text, which conditions matter most, and how to fix the inputs rather than fight the output.",
        ],
        sections=[
            {
                "h": "What happens between the image and the text",
                "p": [
                    "Classical OCR — including Tesseract, the open-source engine behind a large share of the world's scanning software — runs a pipeline, and each stage can fail in ways that show up much later.",
                    "First the image is binarised: every pixel is decided to be either ink or background. This single step causes most catastrophic failures, because it is where uneven lighting does its damage. A photograph with a shadow across one half will threshold that half to solid black, and no amount of cleverness downstream recovers text from a black rectangle.",
                    "Then the page is deskewed and analysed for layout — finding blocks, columns, lines and finally individual character shapes. Each shape is classified, and the results are checked against a language model that knows which letter sequences are plausible. That final stage is why OCR output often contains real words that are the wrong words: the model confidently repaired an ambiguous shape into something that fits the language.",
                ],
            },
            {
                "h": "Why screenshots are easy and photographs are hard",
                "p": [
                    "A screenshot is the ideal input. The text is perfectly sharp, perfectly aligned, evenly lit, high contrast, and rendered rather than captured. Accuracy on clean screenshots is routinely near-perfect, and if you have a choice between screenshotting something and photographing it, that choice matters more than any setting.",
                    "A photograph of a page introduces every problem at once: perspective distortion from not being exactly parallel, uneven lighting from the room, a shadow from your own head or phone, focus that is slightly off, motion blur, and page curvature if the document is a book. Each is individually survivable and they compound.",
                    "Resolution is the most commonly misunderstood factor. OCR wants roughly 300 DPI for body text, meaning a lowercase letter should be around 20-30 pixels tall. Below about 10 pixels tall, accuracy collapses no matter how clean the image is — there is simply not enough information to distinguish an 'e' from a 'c'. This is why zooming in before screenshotting small text beats any post-processing.",
                ],
                "list": [
                    "Lowercase letters should be at least 20 px tall; below 10 px is hopeless.",
                    "Even lighting matters more than bright lighting.",
                    "Shoot parallel to the page, not at an angle.",
                    "Sharp focus beats high megapixels.",
                ],
            },
            {
                "h": "The things that destroy accuracy",
                "p": [
                    "Some inputs are simply outside what classical OCR does well, and knowing them saves time spent assuming you configured something wrong.",
                    "Handwriting is the big one. Tesseract and its relatives are trained on printed type; cursive handwriting is a fundamentally different recognition problem that needs models built for it. Expect poor results and do not conclude the tool is broken.",
                    "Text over images or textured backgrounds breaks binarisation, because there is no clean ink-versus-background split to find. Decorative and script fonts are frequently misread. Very low contrast — grey text on a slightly lighter grey, common in modern UI design — thresholds unpredictably. Tables and multi-column layouts often produce correct words in the wrong reading order, because layout analysis decided the structure incorrectly. And rotation past a few degrees defeats line detection, though deskewing handles small angles automatically.",
                ],
            },
            {
                "h": "Choosing the language, and why it matters more than expected",
                "p": [
                    "OCR engines use a language model to resolve ambiguous shapes, so telling the engine the wrong language actively harms accuracy rather than merely failing to help. Running Portuguese text through an English model produces English-looking words that were never on the page, because every ambiguous character is repaired towards English.",
                    "This is also why accented characters are frequently dropped when the language is set wrong: the model has no expectation of them and treats the accent as noise.",
                    "For documents mixing languages, most engines accept several language packs at once, at some cost to accuracy in each. If one language dominates, choosing that single language usually beats a combined model.",
                ],
            },
            {
                "h": "Preparing an image so OCR can succeed",
                "p": [
                    "The fixes are almost all upstream. In rough order of effect: get more resolution, get the lighting even, get the page square to the camera, and raise contrast to a genuine black-on-white.",
                    "Cropping to just the text region helps twice — it removes background that could confuse layout analysis, and it removes anything that would drag automatic thresholding in the wrong direction. Converting to greyscale before OCR is essentially free and occasionally helps. Straightening a photographed page matters more than people expect, because line detection assumes horizontal text.",
                    "One counterintuitive point: do not sharpen aggressively. Sharpening creates haloes around strokes, and binarisation reads haloes as ink, which thickens characters and merges adjacent ones. Mild is fine; heavy sharpening makes things worse.",
                ],
                "list": [
                    "Crop tightly to the text before recognising.",
                    "Straighten the page; small skew is handled, large skew is not.",
                    "Increase contrast towards true black on true white.",
                    "Avoid heavy sharpening — it merges characters.",
                ],
            },
            {
                "h": "Where the recognition runs",
                "p": [
                    "OCR is applied disproportionately to documents people would not want to hand over: contracts, payslips, medical letters, ID documents, and screenshots of private conversations. That makes the location of the processing a real question rather than a technicality.",
                    "Tesseract compiles to WebAssembly and runs entirely in a browser tab, downloading the language pack once and caching it. That is how our image-to-text tool works, which is why it functions offline after first use — and why the documents never leave the device.",
                    "The honest trade-off: cloud OCR services, particularly the ones using modern transformer-based models, are meaningfully more accurate on hard inputs like handwriting and photographed receipts. If you have a difficult image and it contains nothing sensitive, they will do better. For anything private, local recognition on a well-prepared image is usually more than good enough, and the preparation matters more than the engine.",
                ],
            },
        ],
        takeaways=[
            "Binarisation — deciding each pixel is ink or background — is where uneven lighting causes catastrophic failure.",
            "Body text wants roughly 300 DPI; below 10 pixels of letter height, accuracy collapses regardless of processing.",
            "Setting the wrong language actively harms results, because the language model repairs characters towards it.",
            "Handwriting, textured backgrounds and low-contrast grey-on-grey are outside classical OCR's competence.",
            "Fix the input rather than the output — but avoid heavy sharpening, which merges characters.",
        ],
        tools=["ocr", "crop", "photo_filters", "pdf_to_image"],
        faqs=[
            {"q": "Why is my OCR result full of mistakes?",
             "a": "Usually resolution or lighting. Letters need to be at least 20 pixels tall, and uneven lighting breaks the binarisation step that decides which pixels are ink. A shadow across the page can black out a whole region before recognition even starts."},
            {"q": "Can OCR read handwriting?",
             "a": "Classical engines like Tesseract are trained on printed type and do poorly on cursive handwriting. Handwriting recognition is a different problem needing purpose-built models."},
            {"q": "Does choosing the wrong language matter?",
             "a": "Yes, and it makes things actively worse. The engine uses a language model to resolve ambiguous characters, so the wrong language repairs uncertain shapes into words from that language and tends to drop accented characters."},
            {"q": "Is browser-based OCR as good as a cloud service?",
             "a": "On clean screenshots and printed documents, close enough that the difference rarely matters. On hard inputs — handwriting, photographed receipts, poor lighting — cloud services using modern models are better. The trade is that they receive your document, which for contracts, IDs and medical letters is the whole question."},
        ],
    ),
]

GUIDES_BY_SLUG = {g["slug"]: g for g in GUIDES}

# Newest-first is wrong for evergreen reference material — the hub groups by
# category instead, so a reader scanning for "the format one" finds it by topic.
CATEGORIES = ["Formats", "Editing", "Photography", "Privacy", "Documents"]


def guides_by_category():
    """The hub's grouping: [(category, [guides…])], skipping empty categories."""
    return [
        (cat, [g for g in GUIDES if g["category"] == cat])
        for cat in CATEGORIES
        if any(g["category"] == cat for g in GUIDES)
    ]


def related_guides(slug, limit=3):
    """Other guides to link from `slug` — same category first, then the rest."""
    current = GUIDES_BY_SLUG[slug]
    same = [g for g in GUIDES if g["category"] == current["category"] and g["slug"] != slug]
    rest = [g for g in GUIDES if g["category"] != current["category"]]
    return (same + rest)[:limit]
