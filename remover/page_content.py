"""
Long-form content for the pages that were too thin to stand on their own.

Background: the tool and use-case pages carried ~130 unique words apiece wrapped
around an interface, which is what a search or ad-network quality review calls
thin. The passport pages had the same problem and were fixed the same way — real,
page-specific prose in a data module, rendered by a shared partial.

One dict, one lookup, one partial (`partials/deep_dive.html`), so a page gains
substance by acquiring an entry here rather than by growing its own template.

Keys are url_names, except the use-case pages, which all share one url_name and
are therefore keyed ``use_case:<slug>``. `deep_for` resolves both.

The rule that keeps this from turning back into filler: every section must say
something specific to THAT page. Platform requirements, real numbers, the actual
failure mode. If a paragraph would read the same on a sibling page, it belongs in
the shared template instead — and `ThinPageTests` measures sibling similarity, so
a copy-paste job fails rather than ships.

Deliberately NOT duplicated here: the material in remover/guides.py. The guides
explain how something works; these sections cover doing one specific job. Where
they touch the same topic the page links to the guide instead of restating it.
"""

DEEP = {
    # --- Use-case pages (background removal, by subject) ---------------------
    "use_case:product-photos": {
        "title": "Getting product cut-outs right",
        "sections": [
            {
                "h": "What marketplaces actually require",
                "p": [
                    "Amazon is the strictest and therefore the useful target: the main image must sit on pure white (RGB 255,255,255), the product must fill about 85% of the frame, and no text, watermark, border, prop or additional item may appear. Meeting that automatically satisfies eBay and Etsy, which are looser.",
                    "The 85% rule is the one people miss. A cut-out composited onto a large white canvas with generous margins technically has a white background and still fails, because the product is too small in the frame. Crop tight after removing the background, not before.",
                ],
            },
            {
                "h": "Why the background looks grey before you remove it",
                "p": [
                    "Even shot on white card under good light, your background will land around RGB 240 rather than 255 — card reflects less light than a perfect white, so the camera records a light grey. Next to a competitor's true-white listing it reads as dingy.",
                    "Removing the background and compositing onto pure white closes that gap exactly, which is why this step is standard practice for marketplace sellers rather than a shortcut. What marketplaces prohibit is misrepresenting the product, not editing the backdrop.",
                ],
            },
            {
                "h": "Where cut-outs go wrong on products",
                "p": [
                    "Three failure modes account for almost everything, and all are visible only at full zoom — which is exactly the view a buyer gets:",
                ],
                "list": [
                    "A pale halo around the outline, left by background colour still sitting in the semi-transparent edge pixels. Most obvious on dark products shot on white.",
                    "Reflective and chrome surfaces, which show the background inside the product, so parts of the item get cut away with it.",
                    "Transparent packaging, glassware and mesh, where a pixel is genuinely both product and background at once. No automatic tool resolves these cleanly.",
                ],
            },
            {
                "h": "Batch work without a per-image cost",
                "p": [
                    "A catalogue is where this stops being a single edit and becomes a workflow. Because removal runs on your own device, there is no per-image charge and no rate limit — a few hundred shots is a matter of waiting rather than budgeting.",
                    "Apply one image's background and export settings across the batch, then download the set as a ZIP. Spot-check a handful at full zoom before you list: the settings that work for a dark product on white will not necessarily suit a pale one.",
                ],
            },
        ],
    },
    "use_case:profile-picture": {
        "title": "Headshots that work as avatars",
        "sections": [
            {
                "h": "Every platform crops you to a circle",
                "p": [
                    "LinkedIn, X, Slack, Discord, GitHub and Teams all display profile pictures as circles, but they accept square uploads. That mismatch is where most avatars go wrong: the corners of your square are cut off, and anything near them disappears.",
                    "Compose so your head and shoulders sit inside the inscribed circle, with real margin. A safe test is to imagine a circle touching all four edges of your square — anything outside it is decoration, not content.",
                ],
            },
            {
                "h": "Size for the smallest view, not the largest",
                "p": [
                    "Upload at 800×800 or larger so the image stays sharp on high-density screens and on the profile page itself. Then judge it at 40 pixels, because that is the size it appears at in a comment thread, a member list or a message header.",
                    "At that size, facial expression and tonal contrast are all that survive. Fine detail, background scenery and anything written on your shirt are simply gone, which is the argument for a plain background rather than an interesting one.",
                ],
            },
            {
                "h": "Choosing a background colour",
                "p": [
                    "Once the original background is removed you are picking a colour deliberately, and the choice matters more than it looks. Pick something that contrasts with your hair and clothing, since the avatar reads as a silhouette at small sizes.",
                    "A mid-tone solid works on most platforms because it holds up in both light and dark interface themes. Pure white vanishes into a light theme and pure black vanishes into a dark one, leaving a head floating with no outline.",
                    "For a consistent professional presence, use one brand or accent colour across every platform. Recognisability at 40 pixels comes mostly from colour, not from your face.",
                ],
            },
            {
                "h": "Hair is the hard part",
                "p": [
                    "A headshot is mostly a hair-matting problem. Individual strands are thinner than a pixel, so a wide band around your head is genuinely part subject and part background, and that band is where a cut-out looks convincing or looks pasted.",
                    "Use the refine brush on flyaway strands and check the result against a background very different from the original — a subject cut from a white wall looks flawless on white and shows every flaw on dark blue.",
                ],
            },
        ],
    },
    "use_case:logo": {
        "title": "Working with logo files",
        "sections": [
            {
                "h": "Raster is the fallback, not the goal",
                "p": [
                    "If the original vector file exists — .svg, .ai, .eps or .pdf — use it. Vectors scale to any size with no quality loss, which is what a logo needs when it has to work on a business card and a trade-show banner from the same source.",
                    "Removing the background from a raster logo is what you do when the vector is genuinely gone: an old JPEG from a supplier, a logo pulled off a website, a scan of printed stationery. The result is a fixed-resolution image, so export it larger than you think you need.",
                ],
            },
            {
                "h": "White background is not transparency",
                "p": [
                    "A logo on a white background looks transparent right up until you place it on a coloured header, a photo or a dark-mode interface — at which point it arrives inside a white box. This is the single most common logo problem there is.",
                    "The distinction is real: transparency is a fourth channel per pixel recording opacity, and a JPEG has no way to store it. Any logo saved as JPG has a background, whatever it looks like against your white page.",
                ],
            },
            {
                "h": "Getting clean edges on type and marks",
                "p": [
                    "Logos are the opposite of a photograph: hard edges, flat colour, and usually type. That makes them easy to cut out and unforgiving about how it is done, because a jagged edge on a letterform is immediately visible in a way it never is on hair.",
                    "Two things to check at full zoom. Enclosed shapes — the middle of an O, the gap in an A, the space inside a ring mark — must actually be transparent, not filled with leftover white. And the outline should be smooth rather than stepped, which means the semi-transparent edge band was preserved instead of collapsed to a hard mask.",
                ],
            },
            {
                "h": "Which file to keep",
                "p": [
                    "Export PNG as your master: lossless, universally supported, and safe to hand to a printer, a developer or a marketplace. Keep it larger than any current use.",
                    "For a website, export lossy WebP as well. It carries the same transparency at a fraction of the size, which matters for a logo that loads on every page. Never save the final logo as JPG — that discards the alpha channel and puts the white box back.",
                ],
            },
        ],
    },
    "use_case:signature": {
        "title": "Turning a signed page into a usable signature",
        "sections": [
            {
                "h": "Sign on unlined white paper",
                "p": [
                    "The quality of a digital signature is set before you photograph it. Use a black or dark blue pen with a reasonably thick stroke on plain, unlined white paper — ruled or squared paper leaves lines that have to be cleaned up individually.",
                    "Sign larger than usual. A big signature photographed and scaled down looks crisp; a small one photographed and enlarged looks soft and pixellated, and the thin parts of the stroke break up.",
                ],
            },
            {
                "h": "Photograph it flat and evenly lit",
                "p": [
                    "Shoot from directly above with the camera parallel to the paper. Photographing at an angle skews the signature into a trapezoid, and the correction never looks quite right.",
                    "Even light matters more here than anywhere else, because a shadow across the page becomes a grey wash across the cut-out. Daylight from a window with the paper away from your own shadow is ideal; overhead room lighting with you leaning over the page is the usual cause of a muddy result.",
                ],
            },
            {
                "h": "What a clean signature file looks like",
                "p": [
                    "The result should be the ink alone on transparency, with no paper tone and no grey box, so it can be placed over any document background — including the coloured or watermarked pages many contracts use.",
                    "Check the thin strokes at full zoom. The delicate parts of a signature, where the pen lifted, are exactly what an over-aggressive cut-out removes, and a signature missing its tapering strokes looks visibly altered.",
                ],
            },
            {
                "h": "Keep the file private",
                "p": [
                    "A signature is one of the few images where the file itself is a security concern: anyone holding a clean transparent PNG of your signature can place it on any document.",
                    "That is a direct argument for processing it on your own device rather than uploading it to a service, and for being deliberate about where the finished file is stored and who it is sent to. Strip metadata before sharing, and avoid emailing the transparent master when a flattened copy inside the finished document would do.",
                ],
            },
        ],
    },
    "use_case:car-photos": {
        "title": "Cutting out vehicles",
        "sections": [
            {
                "h": "Cars are mostly reflection",
                "p": [
                    "A car's paint, glass and chrome are all mirrors, which means large parts of the image are literally showing the background you are trying to remove. Sky reflects across the bonnet and roof, and the surroundings wrap around the doors.",
                    "This is why vehicles are harder than they look. A tool separating subject from background sees sky-coloured pixels in the middle of the car and has to decide they belong to the car, which is a genuinely ambiguous call.",
                ],
            },
            {
                "h": "Shoot for the cut-out",
                "p": [
                    "Where you park changes the result more than any setting afterwards:",
                ],
                "list": [
                    "An open, empty area — an unused car park, an industrial estate on a Sunday — so nothing intersects the outline.",
                    "Overcast light. Direct sun creates blown highlights on the bodywork and hard shadows that read as part of the car.",
                    "A three-quarter front angle, showing one side and the front, which is the view that sells and the easiest outline to separate.",
                    "Wheels turned slightly towards the camera, so the front wheel shows its face rather than a thin edge.",
                    "Shoot from around waist height rather than standing, which keeps the proportions natural.",
                ],
            },
            {
                "h": "The parts that need checking",
                "p": [
                    "Zoom in on three areas before you use the result. Wheel arches and the gap under the car, where the shadow often gets kept as if it were bodywork. Aerials, mirrors and spoilers, which are thin enough to be dropped entirely. And window glass, where you have to decide whether the interior stays or goes — keeping it usually looks more natural for a listing.",
                    "A car cut out and placed on plain white with its original ground shadow removed tends to look like it is floating. Adding a soft elliptical shadow underneath, or keeping a hint of the original contact shadow, is what makes it sit on the surface.",
                ],
            },
            {
                "h": "For listings and dealer stock",
                "p": [
                    "A consistent background across every vehicle is what makes a small dealer's stock page look professional, and it is achievable without a studio: photograph each car in the same spot under similar light, cut out, and composite onto one shared backdrop.",
                    "Buyers still expect honesty about condition. Cut out the car cleanly, but photograph the scratches, kerbed alloys and interior wear separately and leave them untouched — an unnaturally perfect gallery raises more doubt than a visible scuff does.",
                ],
            },
        ],
    },
    "use_case:clothing": {
        "title": "Apparel and fashion cut-outs",
        "sections": [
            {
                "h": "Flat lay, mannequin, or model",
                "p": [
                    "Each approach cuts out differently and suits a different purpose. Flat lay — the garment arranged on a plain surface, shot from above — is the easiest to cut out cleanly and the cheapest to produce, but it shows the garment's shape poorly.",
                    "A mannequin shot shows how a garment hangs, and cutting out the mannequin as well produces the 'ghost' or 'invisible mannequin' effect that most clothing marketplaces prefer. On a model, the cut-out has to separate garment, skin and hair at once, which is by far the hardest case and usually worth keeping the background for instead.",
                ],
            },
            {
                "h": "Fabric that fights the cut-out",
                "p": [
                    "Some materials are structurally hard, not just fiddly:",
                ],
                "list": [
                    "Lace, mesh, knitwear and anything open-weave, where the background shows through the garment itself and each hole is a separate edge.",
                    "Chiffon, organza and other sheer fabrics, which are genuinely semi-transparent — a pixel is part fabric and part background.",
                    "Fur, faux fur and mohair, which have the same fine-strand problem as hair.",
                    "Black garments on a dark background, where there is no brightness contrast for an edge to be found in.",
                    "White garments on white, for the same reason in reverse.",
                ],
            },
            {
                "h": "Colour accuracy matters more than the cut-out",
                "p": [
                    "Returns in apparel are driven by colour mismatch more than by anything a cut-out affects. A garment that arrives a different shade than the listing showed is the most common complaint in the category.",
                    "Lock your white balance and shoot every item under the same light rather than correcting each photo afterwards by eye. If a colour is hard to reproduce — deep reds and vivid blues are the usual culprits — say so in the description rather than editing until it looks right on your screen.",
                ],
            },
            {
                "h": "Consistency across the range",
                "p": [
                    "A clothing store's product grid is judged as a whole. Garments cut out and placed on the same background at the same scale look like a collection; a mix of backgrounds and crops looks like a car-boot sale.",
                    "Set your framing once and reuse it: same distance, same angle, same background colour, garment occupying the same proportion of the frame. Batch the removal in one pass so the whole range shares its settings.",
                ],
            },
        ],
    },
    "use_case:pet-photos": {
        "title": "Cutting out pets",
        "sections": [
            {
                "h": "Fur is the whole difficulty",
                "p": [
                    "A pet is a fur-matting problem in the same way a headshot is a hair-matting problem, only more so. The outline is not a line — it is a band of individual strands, each thinner than a pixel, every one of which is part animal and part background.",
                    "Long-haired and fluffy breeds have the widest band and are the hardest. Short-coated animals with a defined silhouette cut out far more easily, which is worth knowing before you judge the tool by your Samoyed.",
                ],
            },
            {
                "h": "Contrast beats everything",
                "p": [
                    "The most useful thing you can do is photograph the animal against something clearly lighter or darker than its coat. A black cat on a dark sofa is not a hard cut-out, it is an impossible one — the information needed to find the edge is not in the photo.",
                    "Brightness contrast matters more than colour contrast, because edges are found in luminance. A ginger cat against a mid-green cushion looks high-contrast to you and may be nearly identical in brightness.",
                ],
            },
            {
                "h": "Getting the shot at all",
                "p": [
                    "The practical problem with pets is not editing, it is capture:",
                ],
                "list": [
                    "Use burst mode and take far more frames than feels sensible — you are selecting, not shooting.",
                    "Get down to the animal's eye level; photographs taken from standing height read as snapshots.",
                    "Have someone else hold their attention just beside the lens, so the eyes point at the camera.",
                    "Use daylight rather than flash. Flash causes eyeshine, which is much harder to fix than red-eye in people.",
                    "Keep the shutter fast — motion blur widens the fur band across the whole moving edge and ruins the cut-out.",
                ],
            },
            {
                "h": "Checking the result",
                "p": [
                    "Whiskers are the giveaway. They are the finest structure in the image and the first thing an over-aggressive cut-out removes, and a cat missing its whiskers looks wrong even to someone who could not say why.",
                    "Preview against a background very different from the original, and use the refine brush to bring back fur detail at the outline rather than accepting a clean, hard edge — on an animal, a slightly soft outline is the correct one.",
                ],
            },
        ],
    },
    "use_case:youtube-thumbnail": {
        "title": "Thumbnails that work at actual size",
        "sections": [
            {
                "h": "You are designing for 210 pixels",
                "p": [
                    "YouTube's specification says 1280 × 720, and that is what you should upload. But in a sidebar, a mobile feed or a suggested-video strip, your thumbnail is displayed at roughly 210 pixels wide — about a sixth of the size you are designing at.",
                    "This one fact explains most thumbnail advice. Small text disappears. Detailed compositions turn to mush. Subtle facial expressions read as nothing. The test that matters is to shrink your finished thumbnail to 210 pixels and look at it — if you cannot tell what it is, neither can anyone scrolling.",
                ],
            },
            {
                "h": "Why cut-outs dominate the format",
                "p": [
                    "The standard thumbnail is a cut-out person on a high-contrast background, and that convention exists for a reason: separating the subject from its background is what makes a face readable at 210 pixels. A face photographed in a room competes with the room.",
                    "Cutting yourself out lets you place the subject against a flat, saturated colour or a simplified graphic, control exactly where the eye goes, and keep the composition legible when it is shrunk. It also lets you break the frame — a head slightly overlapping a text block reads as depth at any size.",
                ],
            },
            {
                "h": "Composition rules that survive shrinking",
                "p": [
                    "The things that still work at a sixth scale:",
                ],
                "list": [
                    "One subject, one idea. Two competing focal points become zero at small size.",
                    "Three to five words of text maximum, in a heavy weight, occupying a real portion of the frame.",
                    "Strong tonal contrast between subject and background, not just colour contrast.",
                    "Faces looking towards the camera or towards the text, with a clear expression.",
                    "Keep the bottom-right corner clear — the duration stamp is drawn over it.",
                    "Avoid pure red and white backgrounds, which blend into YouTube's own interface.",
                ],
            },
            {
                "h": "Edges and export",
                "p": [
                    "A thumbnail cut-out is usually placed on a background very different from the one it was shot against, which is exactly the situation where a pale halo around the subject becomes obvious. Check the outline at full zoom before compositing, particularly around hair.",
                    "Export at 1280 × 720 and keep the file under 2 MB. YouTube recompresses whatever you upload, so export at high quality rather than pre-compressing — their encoder does better work starting from a clean image.",
                ],
            },
        ],
    },
    "use_case:ebay": {
        "title": "Photos that sell on eBay",
        "sections": [
            {
                "h": "What eBay requires and what it rewards",
                "p": [
                    "eBay's rules are looser than Amazon's: photos must be at least 500 pixels on the longest side, and the main image may not carry added text, borders or watermarks. There is no pure-white requirement, only a preference for a plain background.",
                    "But 500 pixels is a floor, not a target. eBay's zoom feature activates around 800 pixels and works properly above 1600, and listings with zoom convert better. Upload the largest clean version you have.",
                ],
            },
            {
                "h": "Why a plain background matters more on eBay",
                "p": [
                    "eBay search results are a dense grid of small images from thousands of sellers, most of them photographed on a kitchen table. A listing whose product sits on clean white is visibly different in that grid before anyone reads the title.",
                    "This is the cheapest competitive advantage available to a small seller. It costs nothing but a cut-out, and it separates your listing from the identical item photographed on a carpet.",
                ],
            },
            {
                "h": "Used items need honest photography",
                "p": [
                    "Most eBay stock is used, and that changes the goal. A cut-out on white is right for the gallery image, but the supporting photos should show the item exactly as it is.",
                    "Photograph every flaw deliberately — the scratch, the chip, the worn corner, the missing accessory — and describe it. Sellers consistently find this reduces returns and 'not as described' disputes far more than it costs in bids, because the buyer who purchases anyway has already accepted the condition.",
                ],
            },
            {
                "h": "Using all twelve slots",
                "p": [
                    "eBay allows twelve photos free, and most listings use three. The unused ones are the cheapest improvement available:",
                ],
                "list": [
                    "Cut-out on white as the gallery image, since that is what appears in search.",
                    "The item from the back, the sides and underneath.",
                    "A scale reference — beside a common object or in hand.",
                    "Labels, model numbers and serial plates, sharp enough to read.",
                    "Every flaw, individually and close up.",
                    "What the buyer actually receives, including cables, cases and manuals.",
                ],
            },
        ],
    },
    "use_case:discord-pfp": {
        "title": "Avatars for Discord",
        "sections": [
            {
                "h": "Circular crop, tiny display",
                "p": [
                    "Discord crops every avatar to a circle and shows it at 32 to 40 pixels in a message list — smaller than almost any other platform. Upload at 512 × 512 so it stays sharp on the profile card, then judge it at 40.",
                    "Because the crop is circular, anything in the corners of your square is discarded. Compose inside the inscribed circle and leave margin, or your character's ears and your own shoulders will be the first casualties.",
                ],
            },
            {
                "h": "Designing for both themes",
                "p": [
                    "Discord runs in dark mode for most people but not all, and your avatar sits directly on the interface background in both. A cut-out with a transparent background will look completely different depending on which theme the viewer uses.",
                    "The reliable answer is to composite onto a solid colour rather than shipping transparency, so the avatar looks identical everywhere. Pick a mid-tone: near-black disappears into dark mode and near-white disappears into light mode, leaving a floating head with no outline.",
                ],
            },
            {
                "h": "Animated avatars and file limits",
                "p": [
                    "Nitro subscribers can use an animated GIF avatar, and the same rules apply harder — at 40 pixels, an animation with lots of movement reads as flicker. Slow, simple motion in one area works; a full animated scene does not.",
                    "Keep the file well under the limit and remember GIF supports only one fully transparent colour, with no partial transparency. A cut-out exported as GIF will have a hard, jagged outline, which is another reason to composite onto a solid background first.",
                ],
            },
            {
                "h": "Server identity",
                "p": [
                    "Discord lets you set a different avatar per server, which is worth using if you are in both professional and personal spaces. The same cut-out on two different background colours gives you two distinct identities from one photo.",
                    "For server icons rather than personal avatars, the same constraints apply with less room: icons show in the server rail at around 48 pixels, so a single bold shape or two letters beats any detailed artwork.",
                ],
            },
        ],
    },
    "use_case:twitch": {
        "title": "Stream graphics and overlays",
        "sections": [
            {
                "h": "Where transparency is doing the work",
                "p": [
                    "Streaming is one of the few places transparency is essential rather than convenient. Overlays, alerts, webcam frames, panel graphics and emotes all sit on top of live gameplay, and any of them shipped with a background arrives as a solid rectangle covering the thing viewers came to watch.",
                    "In OBS and Streamlabs, a PNG with a real alpha channel composites over your scene cleanly. A JPG cannot — it has no alpha channel at all, so a 'transparent' JPG is always a white or black box.",
                ],
            },
            {
                "h": "Chroma key versus cut-out",
                "p": [
                    "For live webcam removal, a physical green screen plus OBS's chroma key filter is still the best answer: it runs in real time with no per-frame cost and handles motion well. It needs even lighting on the screen itself, and separation between you and the fabric to avoid green spill on your hair and shoulders.",
                    "Cutting out a still image is the right tool for the assets around the stream rather than the stream itself — your panel headshots, offline banner, alert graphics, emotes and thumbnail art. Those are produced once and need to be clean rather than fast.",
                ],
            },
            {
                "h": "Sizes Twitch actually uses",
                "p": [
                    "Getting these right the first time saves rebuilding a whole overlay set:",
                ],
                "list": [
                    "Profile picture: 256 × 256, displayed as a circle at small sizes.",
                    "Profile banner: 1200 × 480, with the centre kept clear of critical content.",
                    "Video player banner (offline screen): 1920 × 1080.",
                    "Panel images: 320 pixels wide, any height, shown below the stream.",
                    "Emotes: 112 × 112, 56 × 56 and 28 × 28 — and the 28-pixel version is the one that matters, since that is chat size.",
                ],
            },
            {
                "h": "Emotes are the hardest thing here",
                "p": [
                    "An emote has to be legible at 28 pixels, which is smaller than a line of text. That rules out detail, thin lines, subtle shading and anything resembling a scene.",
                    "What survives is a single bold shape with a strong outline and high internal contrast. Design at 112 pixels, then check at 28 constantly rather than at the end — most emotes that fail do so because they were only ever judged at full size.",
                ],
            },
        ],
    },

    # --- Tool pages ----------------------------------------------------------
    "convert": {
        "title": "Choosing the right format",
        "sections": [
            {
                "h": "What conversion does and does not cost you",
                "p": [
                    "Converting to a lossless format — PNG, or WebP in lossless mode — preserves your pixels exactly. Converting to a lossy format (JPG, lossy WebP, AVIF) discards data permanently, in exchange for a much smaller file.",
                    "The case worth avoiding is converting between two lossy formats. A JPG turned into a lossy WebP has been through two rounds of quantisation, and the second round treats the first round's artefacts as real detail worth preserving. Always convert from the highest-quality copy you have, not from a file that has already been compressed.",
                ],
            },
            {
                "h": "Which target format to pick",
                "p": [
                    "The answer depends almost entirely on where the file is going:",
                ],
                "list": [
                    "For your own website: WebP. Typically 25–35% smaller than JPG at the same visual quality, supported by every current browser.",
                    "For sending to someone else: JPG. It is the most compatible image format in existence and never gets rejected.",
                    "For anything with a transparent background: PNG as a master, lossy WebP for the web. JPG cannot store transparency at all.",
                    "For screenshots and images containing text: PNG or lossless WebP — sharp edges are the worst case for lossy compression.",
                    "For large hero images where bandwidth matters: AVIF, which compresses hardest but encodes slowly.",
                ],
            },
            {
                "h": "The transparency trap",
                "p": [
                    "Converting a transparent PNG to JPG is the most common conversion mistake, because JPEG has no alpha channel and no way to represent one. The transparency has to be resolved against something, and the software picks — usually white, sometimes black.",
                    "Nothing is broken and nothing can be recovered afterwards; the alpha channel was discarded at export. If your cut-out came back with a white background, this is why. Re-export from the original as PNG or WebP.",
                ],
            },
            {
                "h": "Why this runs on your device",
                "p": [
                    "Conversion happens in your browser using the same canvas and codec support the browser already ships for displaying images. Nothing is uploaded, which means no file size ceiling imposed by a server, no queue, and no per-image cost — so batch conversion is just a matter of waiting.",
                    "It also means the tool works on files you would not want to hand to a service: scanned documents, identity paperwork, medical images, unreleased work.",
                ],
            },
        ],
    },
    "compress": {
        "title": "Compressing without visible damage",
        "sections": [
            {
                "h": "Resize before you compress",
                "p": [
                    "This is the single most useful thing to know about hitting a size limit, and most people do it in the wrong order. File size scales roughly with pixel count, so halving an image's width and height cuts it to about a quarter — before the quality slider is touched at all.",
                    "A 4000-pixel-wide photo dropped to 1600 pixels will usually clear an upload limit on its own, with no perceptible loss, because nothing displaying it needed 4000 pixels. A 1600-pixel image at quality 85 looks better and weighs less than a 4000-pixel image at quality 40.",
                ],
            },
            {
                "h": "Where the quality scale actually bites",
                "p": [
                    "The 0–100 quality number is badly non-linear, and knowing its shape saves a lot of guessing:",
                ],
                "list": [
                    "100 to 90: no visible difference on most photographs, but a large file. Wasteful for the web.",
                    "90 to 80: still visually indistinguishable, at roughly half the size. Where most images should sit.",
                    "80 to 70: slight softening in fine texture. Fine for thumbnails and secondary images.",
                    "70 to 60: artefacts appear in skies, skin tones and around sharp edges.",
                    "Below 60: obvious blockiness and haloing. Only when size dominates everything.",
                ],
            },
            {
                "h": "Content changes the answer",
                "p": [
                    "Those bands assume photographs. Busy texture — foliage, gravel, fabric — hides compression artefacts well and can go lower than you would expect.",
                    "Smooth gradients are the opposite. A clear sky or a studio backdrop has no texture to mask the boundaries between compression blocks, so banding appears early. Screenshots, illustrations and anything with text are the worst case and often should not be lossy at all; if they must be, start at 90 rather than 80.",
                ],
            },
            {
                "h": "Never compress twice",
                "p": [
                    "Each lossy save re-quantises data that already carries artefacts from the previous save, and the damage accumulates permanently. Ten saves at quality 90 produce a visibly worse image than one save at quality 60.",
                    "Keep a lossless master and export to a compressed format once, at the end. If you need to send an image to someone who will edit it further, send the master.",
                ],
            },
        ],
    },
    "crop": {
        "title": "Cropping with intent",
        "sections": [
            {
                "h": "Cropping is free, enlarging is not",
                "p": [
                    "Cropping discards pixels, which costs you nothing in quality — the pixels that remain are the original measured data. What it costs is resolution, and that only matters if the result ends up smaller than where it is going.",
                    "A 4000-pixel photo cropped to a quarter of its area is still 2000 pixels wide, which is more than enough for almost any screen use. Crop confidently; the mistake is enlarging afterwards to compensate, which invents detail that was never captured.",
                ],
            },
            {
                "h": "The ratios worth knowing",
                "p": [
                    "Most crops are made to fit a destination, and there are only a handful that matter:",
                ],
                "list": [
                    "1:1 square — profile pictures, and the universally safe social format.",
                    "4:5 vertical — the tallest ratio most feeds display uncropped, so it occupies the most screen space.",
                    "9:16 — stories, reels and TikTok, full phone screen.",
                    "16:9 — YouTube, link previews and most horizontal video.",
                    "3:2 and 4:3 — the native ratios of most cameras and phones, and the right choice for print.",
                ],
            },
            {
                "h": "Circles are a crop plus transparency",
                "p": [
                    "A circular crop is not really a crop — an image file is always rectangular. What it produces is a square image whose corners are transparent, which is why the export format matters.",
                    "Save a circular crop as PNG or WebP and the corners stay transparent over any background. Save it as JPG and the corners become solid white or black, giving you a circle in a box. This catches people out constantly with avatars.",
                ],
            },
            {
                "h": "Composition, briefly",
                "p": [
                    "Two habits improve most crops. Leave space in the direction a subject faces or moves, so the frame does not feel cramped against their gaze. And avoid cropping a person at a joint — the wrist, elbow, knee or ankle — because it reads as an amputation rather than a frame edge; crop mid-limb instead.",
                    "For anything going into a circular avatar slot, compose inside the inscribed circle. Everything in the corners of your square will be discarded by the platform.",
                ],
            },
        ],
    },
    "resize": {
        "title": "Resizing well",
        "sections": [
            {
                "h": "Down is safe, up is not",
                "p": [
                    "Making an image smaller derives every output pixel from real measured data, so it is the safe direction. It can even improve apparent quality, since averaging groups of pixels reduces noise — a high-ISO photo often looks cleaner at half size.",
                    "Enlarging is a different problem. The detail was never captured, so it has to be invented: classical resampling does it softly, producing a bigger but blurrier image. Around 2× is the practical ceiling for anything that must look natural.",
                ],
            },
            {
                "h": "Keep the aspect ratio",
                "p": [
                    "Changing width and height by different amounts stretches the image, and people are extremely good at spotting it — a face a few percent too wide looks wrong even to someone who cannot say why.",
                    "When a destination demands an exact ratio your original does not have, crop to that ratio first and then resize, rather than stretching to fit. You lose some framing and keep the proportions.",
                ],
            },
            {
                "h": "Resize before compressing, not after",
                "p": [
                    "File size is driven far more by pixel count than by the quality setting, so reducing dimensions to what will actually be displayed usually clears an upload limit on its own.",
                    "The common mistake is to keep full dimensions and push quality down until the file fits, which produces a large, artefact-ridden image where a smaller clean one would have looked better and weighed less.",
                ],
            },
            {
                "h": "Sharpening comes last",
                "p": [
                    "Downscaling softens an image slightly — that is inherent to averaging pixels together — so a light sharpen afterwards is normal and appropriate.",
                    "Doing it in the other order does not work: sharpening before you downscale amplifies noise and edge detail that the resize is about to average away, and can leave visible halos around high-contrast edges.",
                ],
            },
        ],
    },
    "instagram": {
        "title": "Sizing for Instagram",
        "sections": [
            {
                "h": "The three formats that matter",
                "p": [
                    "Instagram accepts a range of ratios but treats them differently in the feed:",
                ],
                "list": [
                    "1080 × 1350 (4:5) — the tallest the feed displays uncropped, so it takes the most screen space as people scroll. The default worth using for most posts.",
                    "1080 × 1080 (1:1) — square. Safe everywhere, and still what the profile grid crops to.",
                    "1080 × 1920 (9:16) — stories and reels, full screen.",
                    "1080 × 566 (1.91:1) — landscape. Occupies the least feed space of any option.",
                ],
            },
            {
                "h": "Your grid crops everything to square",
                "p": [
                    "This is the detail that catches people: a 4:5 post displays tall in the feed but is cropped to a square thumbnail on your profile grid, from the centre.",
                    "So a portrait post needs to work twice — as the tall version people see while scrolling, and as the centre square people see when they visit your profile. Keeping the subject centred rather than at the top or bottom edge is what makes both work.",
                ],
            },
            {
                "h": "Safe zones in stories and reels",
                "p": [
                    "Vertical formats have interface drawn over them. Keep anything important out of the top 250 pixels, where the profile row and progress bars sit, and the bottom 250 pixels, where the caption, reply field and action buttons appear.",
                    "For reels specifically, also avoid the right-hand strip where the like, comment and share column lives. Text placed there is readable in your editor and covered on the phone.",
                ],
            },
            {
                "h": "Why uploads look worse than your export",
                "p": [
                    "Instagram recompresses everything, which is a second lossy pass on top of yours. Three things genuinely reduce the damage: upload at exactly the target dimensions so their resize is a clean downscale, export at high quality (90+) rather than pre-compressing, and never upload an image that was already downloaded from another platform.",
                    "Fine detail, dense texture and thin lines are what a second compression pass destroys first, so a simpler composition survives the trip better than a busy one.",
                ],
            },
        ],
    },
    "favicon": {
        "title": "Favicons that actually work",
        "sections": [
            {
                "h": "16 pixels is the real constraint",
                "p": [
                    "A favicon appears in a browser tab at 16 × 16 pixels — roughly the size of a single character of text. Almost nothing survives at that size: no detail, no thin lines, no more than two letters, and certainly not a full logo.",
                    "What works is one bold shape with high contrast against both light and dark tab bars. Design at 512 and check at 16 constantly rather than at the end, because most favicons that fail were only ever judged large.",
                ],
            },
            {
                "h": "The sizes a site actually needs",
                "p": [
                    "Different platforms reach for different files, and missing one produces a blurry upscale of another:",
                ],
                "list": [
                    "16 × 16 and 32 × 32 — browser tabs and bookmarks.",
                    "180 × 180 — the Apple touch icon, used when someone adds your site to an iOS home screen.",
                    "192 × 192 and 512 × 512 — Android and the web app manifest, used for installed PWAs and splash screens.",
                    "favicon.ico containing 16 and 32 — still requested by older browsers and some crawlers at the site root.",
                ],
            },
            {
                "h": "Transparent or solid",
                "p": [
                    "A transparent background lets the icon sit on whatever colour the browser uses, which adapts well to light and dark themes but can leave a thin dark mark invisible against a dark tab bar.",
                    "A solid background — your brand colour with the mark reversed out — is more reliable, because it looks identical everywhere. For iOS specifically, transparency is a poor choice: the home-screen icon is composited onto a background you do not control, and transparent areas turn black.",
                ],
            },
            {
                "h": "Where the files go",
                "p": [
                    "Put favicon.ico at your site root, since browsers and crawlers request it there whether or not you link it. Everything else is declared in your HTML head with link tags, plus a web app manifest listing the 192 and 512 icons.",
                    "Browsers cache favicons aggressively and often ignore normal cache headers, so a changed icon may take a while to appear. That is usually caching rather than a broken file — check in a private window before debugging.",
                ],
            },
        ],
    },
    "sticker": {
        "title": "Making stickers that read well",
        "sections": [
            {
                "h": "The outline is what makes it a sticker",
                "p": [
                    "A die-cut white border around the subject is not decoration — it is what separates a sticker from a cut-out photo. Chat apps show stickers over wallpapers, photos and both light and dark themes, and a bare cut-out disappears against a background close to its own colours.",
                    "The outline provides contrast against anything. That is why the convention exists across every sticker format from physical vinyl to WhatsApp, and why a sticker without one looks unfinished.",
                ],
            },
            {
                "h": "Platform requirements",
                "p": [
                    "The main chat platforms differ enough to matter:",
                ],
                "list": [
                    "WhatsApp: 512 × 512 PNG with a transparent background, under 100 KB for static stickers, and a small margin of empty space around the subject.",
                    "Telegram: 512 pixels on the longest side, PNG or WebP, with the other dimension free.",
                    "Discord: 320 × 320, and animated stickers are Nitro-only.",
                    "Signal: 512 × 512 WebP, with a strict per-sticker file-size budget.",
                ],
            },
            {
                "h": "Choosing a subject",
                "p": [
                    "Stickers are viewed small and in a busy chat, so the same rule applies as for emotes and favicons: one clear subject, strong silhouette, high contrast.",
                    "Faces and expressive gestures work best because they carry meaning at a glance. Wide shots, scenes and anything with fine detail or small text do not — by the time the sticker is rendered in a conversation, that detail is gone.",
                ],
            },
            {
                "h": "Edges matter more here than usual",
                "p": [
                    "Because the outline traces the cut-out exactly, any error in the removal becomes a visible feature of the sticker. A missed strand of hair becomes a spike in the border; a chunk of leftover background becomes a lump.",
                    "Check the outline at full zoom before adding the border, and use the refine brush to tidy the silhouette. It is worth simplifying deliberately — a slightly smoothed outline usually makes a better sticker than a perfectly faithful one.",
                ],
            },
        ],
    },
    "meme": {
        "title": "The meme format, and why it looks like that",
        "sections": [
            {
                "h": "Impact, white, black outline",
                "p": [
                    "The classic top-and-bottom caption in heavy white Impact with a black stroke is not an aesthetic choice that stuck around by accident. It is the most legible possible combination over an unknown photograph.",
                    "A white fill works over dark areas, the black outline works over light areas, and the heavy condensed weight stays readable when the image is screenshotted, recompressed and reshared at half size. Any other combination fails over some part of some image.",
                ],
            },
            {
                "h": "Uppercase and line breaks",
                "p": [
                    "Captions are set in uppercase for the same reason: consistent letter height means no descenders dropping into the image and a solid, predictable block of text.",
                    "Keep lines short. Two lines of five or six words read instantly; four lines of long text is a paragraph sitting on a photo, and people scroll past it. If the joke needs more words than that, the image is doing none of the work.",
                ],
            },
            {
                "h": "Surviving the reshare",
                "p": [
                    "A meme's real life is being screenshotted, recompressed by three platforms and reshared at reduced size. That is a brutal path for image quality, and it is why the format favours extremes.",
                    "Practical consequences: use a large enough source image that a screenshot of it is still sharp, keep text large relative to the frame, and avoid subtle tonal detail that the second and third compression passes will destroy. Export at high quality — every platform downstream will compress it again anyway.",
                ],
            },
            {
                "h": "Cut-outs and the modern formats",
                "p": [
                    "Many current formats are not captioned photos at all but composites — a cut-out subject placed onto a different scene, or a face pasted into a template. That needs a clean transparent cut-out rather than a caption box.",
                    "Since the composite lands on a background very different from the original, edge quality shows: check the outline against the destination before exporting, since a pale halo that was invisible on the original background will be obvious on the new one.",
                ],
            },
        ],
    },
    "border": {
        "title": "Borders, frames and Polaroids",
        "sections": [
            {
                "h": "What a border is for",
                "p": [
                    "A border does two jobs. Practically, it separates the image from whatever surrounds it — a white photo on a white page has no edge, and a border gives it one. Aesthetically, it signals deliberateness: a framed image reads as presented rather than posted.",
                    "That is why borders work well on feeds and gallery grids, where images butt against each other and against the interface, and less well on a page you already control the layout of.",
                ],
            },
            {
                "h": "Picking a width and colour",
                "p": [
                    "Border width should scale with the image, not be a fixed pixel value. A 20-pixel border is prominent on a 400-pixel thumbnail and invisible on a 4000-pixel photo; expressing it as a percentage keeps a set consistent.",
                    "For colour, white is the default because it reads as matting and works on most backgrounds. Black suits high-contrast and monochrome work. A colour pulled from the photograph itself ties the frame to the image, and sampling one from the palette tool is a reliable way to pick something that does not fight the content.",
                ],
            },
            {
                "h": "The Polaroid proportions",
                "p": [
                    "A Polaroid frame is not a uniform border — that is what makes it recognisable. The image sits high in the frame with a thin, even margin on the top and sides and a much deeper margin at the bottom, historically the space for writing.",
                    "Getting that asymmetry right is most of the effect. An even border with a caption underneath reads as a bordered photo; the deep bottom margin reads as a Polaroid. The classic image area is close to square, so a panoramic photo in a Polaroid frame never quite convinces.",
                ],
            },
            {
                "h": "Fitting a ratio without cropping",
                "p": [
                    "A border is also a practical way to fit an awkward image into a fixed aspect ratio without losing any of it. Padding a landscape photo with white to make it square keeps the whole frame, where cropping to square would cut the sides off.",
                    "This is worth knowing for platforms that crop to a ratio you did not shoot for. Pad rather than crop when the edges of the image matter, and crop rather than pad when the composition can take it.",
                ],
            },
        ],
    },
    "palette": {
        "title": "Reading colour out of an image",
        "sections": [
            {
                "h": "How a palette gets extracted",
                "p": [
                    "Pulling colours from a photograph is a clustering problem. A photo contains tens of thousands of distinct colour values, and extraction groups them into a handful of representative clusters — usually with an algorithm like k-means — then returns each cluster's centre.",
                    "That is why an extracted palette is not simply the most common pixels. A large area of near-identical sky would dominate a naive count; clustering instead returns colours that represent the range of the image, which is what makes the result useful.",
                ],
            },
            {
                "h": "Dominant is not the same as useful",
                "p": [
                    "The most-present colour in an image is frequently the least interesting one — the wall, the sky, the tablecloth. A palette built only from area gives you five shades of beige.",
                    "In practice, a usable palette needs contrast and range: a dark, a light, a saturated accent and one or two mid-tones. When picking from an extracted set, choose for that spread rather than taking the top five by frequency.",
                ],
            },
            {
                "h": "Hex, RGB and HSL",
                "p": [
                    "The same colour has several notations, and which one you want depends on the job:",
                ],
                "list": [
                    "Hex (#4F46E5) — the web default, and what most design tools expect.",
                    "RGB (79, 70, 229) — identical information, easier to manipulate in code.",
                    "HSL (243°, 75%, 59%) — hue, saturation and lightness separately, which is what you want when building tints and shades of one colour.",
                ],
            },
            {
                "h": "Check contrast before you commit",
                "p": [
                    "A palette pulled from a photograph is chosen for how the colours look together, not for whether text is readable on them, and those are different questions.",
                    "If any of these colours will carry text, check the contrast ratio: 4.5:1 against its background for body text, 3:1 for large text, to meet WCAG AA. Mid-tone colours are the usual failure — they look pleasant and fail against both white and black.",
                ],
            },
        ],
    },
    # --- Landing pages (rendered by landing.html) ----------------------------
    "compress_under_500kb": {
        "title": "Hitting a 500 KB limit",
        "sections": [
            {
                "h": "Reduce dimensions first",
                "p": [
                    "500 KB is a common ceiling on job application portals, government forms, forum attachments and older content systems, and the instinct is to drag the quality slider down until the number fits. That produces a large, visibly damaged image.",
                    "File size scales with pixel count, so resizing is the more powerful lever. A 4000-pixel photo dropped to 1600 pixels is roughly a sixth of the data before quality is touched at all — usually enough on its own, with no perceptible loss, because nothing displaying it needed 4000 pixels.",
                ],
            },
            {
                "h": "A reliable order of operations",
                "p": [
                    "Work through these in order and stop as soon as you are under the limit:",
                ],
                "list": [
                    "Resize to the largest dimension the image will actually be shown at — often 1600 pixels or less.",
                    "Export at quality 80–85, which is visually indistinguishable from the original on most photographs.",
                    "Switch format if the destination allows it: WebP is typically 25–35% smaller than JPG at matched quality.",
                    "Only then lower quality further, and check the result at full size before accepting it.",
                ],
            },
            {
                "h": "When the file will not shrink",
                "p": [
                    "Some images resist compression for structural reasons. Screenshots and images containing text have sharp edges that lossy compression handles badly, so they stay large at any acceptable quality — convert those to PNG, which often ends up smaller than a high-quality JPG of the same content.",
                    "Photographs with large smooth gradients, like clear skies, band visibly before they get small. And a PNG of a photograph is the classic case: it is likely five to ten times larger than it needs to be purely because of the format, and converting to JPG or WebP will collapse it.",
                ],
            },
        ],
    },
    "compress_discord": {
        "title": "Discord's upload limits",
        "sections": [
            {
                "h": "What the limits actually are",
                "p": [
                    "Discord's free tier caps uploads at 10 MB per file, raised for Nitro subscribers, and individual servers can have their own boost-dependent ceilings. For images that limit is generous — most photos fit without any work.",
                    "The cases where it bites are screen recordings, long GIFs, uncompressed PNG screenshots of high-resolution displays, and phone photos from recent cameras, which can exceed 10 MB straight out of the camera.",
                ],
            },
            {
                "h": "Screenshots are the usual culprit",
                "p": [
                    "A full-screen PNG screenshot from a 4K or Retina display is genuinely enormous, because PNG is lossless and stores the whole thing faithfully.",
                    "If the screenshot contains readable text, keep it as PNG and reduce the dimensions instead — lossy compression puts haloing around text and makes it harder to read, which defeats the point of sharing it. If it is mostly a photograph or a game capture, convert to JPG or WebP and it will collapse in size with no visible change.",
                ],
            },
            {
                "h": "Discord recompresses anyway",
                "p": [
                    "Images posted to Discord are re-encoded and served through its own CDN, and thumbnails are generated at reduced size. That means very high quality exports are partly wasted effort — you are feeding an encoder that will compress again.",
                    "Export at quality 85 rather than 100 and the difference after Discord's own pass is not visible, while the upload is faster and comfortably inside the limit. What does survive is resolution, so keep dimensions rather than quality when you have to choose.",
                ],
            },
            {
                "h": "GIFs and short clips",
                "p": [
                    "GIF is the format that most often blows the limit, because it is a poor video codec: every frame is stored as an indexed-colour image with no compression between frames, so file size grows roughly linearly with length.",
                    "A ten-second GIF can easily exceed 10 MB where the same clip as MP4 is under 1 MB. If the destination accepts video, converting is dramatically more effective than any amount of compression. If it must stay a GIF, the levers that work are fewer frames, a lower frame rate, smaller dimensions and a reduced colour palette — in that order.",
                ],
            },
        ],
    },
    # --- Info pages ----------------------------------------------------------
    "about": {
        "title": "How ClearBG works, and why it is built this way",
        "sections": [
            {
                "h": "Everything runs in your browser",
                "p": [
                    "Most free online image tools upload your file to a server, process it there, and send the result back. ClearBG does not: the AI model and every edit run inside the page, on your own device, using WebAssembly and your GPU.",
                    "The model downloads once, is cached, and then does its work locally. There is no upload step in any tool on this site — not for background removal, not for conversion, not for compression, not for the passport photo maker.",
                ],
            },
            {
                "h": "You can verify that, rather than trusting it",
                "p": [
                    "Privacy claims are cheap and mostly unfalsifiable. This one is not, and checking takes about ten seconds.",
                    "Open your browser's developer tools, switch to the Network tab, and use any tool on the site. If your image were being uploaded, you would see the request carrying it. Alternatively, load the page and then disconnect from the internet — the tools keep working, because nothing needs a server.",
                ],
            },
            {
                "h": "Why it is free and has no limits",
                "p": [
                    "Because the processing happens on your hardware, there is no per-image cost to us. The economic reason that other services impose credits, watermarks, resolution caps and monthly quotas simply does not exist here.",
                    "So there are none: no account, no sign-up, no watermark, no export limit, no downscaling. Running a hundred product photos through costs the same as running one, which is nothing.",
                ],
            },
            {
                "h": "What this approach cannot do",
                "p": [
                    "It is worth being straight about the trade-offs. A server can run a model hundreds of times larger than anything that fits in a browser tab, so for the very hardest cut-outs — fine hair against a busy background, semi-transparent fabric, glass — a large cloud service can still produce a better result.",
                    "Performance also depends on your device rather than on our hardware, so an older phone will be slower than a recent laptop. And very large files can exceed what a browser tab can hold in memory. Where those limits matter more than privacy, a cloud tool is the honest recommendation.",
                ],
            },
        ],
    },
}


# FAQs for the use-case pages, keyed by slug. Every other page type on the site
# had a FAQ block (visible accordion + FAQPage structured data) and these did not,
# so they were the only landing pages ineligible for an expanded FAQ rich result.
# Questions are the ones actually asked about that subject — a generic set repeated
# eleven times would be worse than none, since FAQPage markup is compared sitewide.
USE_CASE_FAQS = {
    "product-photos": [
        {"q": "Does Amazon allow digitally removed backgrounds?",
         "a": "Yes. Amazon requires an accurate representation of the product on a pure white background, not an unedited photograph. Removing the background and compositing onto white is standard practice. Altering the product's own colour or shape is not allowed."},
        {"q": "Why does my white background look grey in photos?",
         "a": "White card reflects less light than a perfect white, so a camera typically records it around RGB 240 rather than 255. Removing the background and compositing onto pure white closes that gap exactly."},
        {"q": "How large should marketplace product photos be?",
         "a": "At least 1600 pixels on the longest side, which is where Amazon's zoom activates; 2000 or more is better. Shoot at full resolution and downscale — never enlarge to reach a minimum."},
        {"q": "Can I process a whole catalogue at once?",
         "a": "Yes. Removal runs on your own device, so there is no per-image cost and no rate limit. Apply one image's settings across the batch and download the results as a ZIP."},
    ],
    "profile-picture": [
        {"q": "What size should a profile picture be?",
         "a": "Upload at 800×800 or larger so it stays sharp on the profile page and on high-density screens, but judge it at 40 pixels — the size it appears at in comment threads and member lists."},
        {"q": "Why is my profile picture cropped strangely?",
         "a": "Almost every platform crops avatars to a circle while accepting square uploads, so the corners of your image are discarded. Compose inside the circle that touches all four edges of your square."},
        {"q": "What background colour works best for an avatar?",
         "a": "A mid-tone that contrasts with your hair and clothing. Pure white disappears into light interface themes and pure black into dark ones, leaving a head with no outline."},
        {"q": "Will the cut-out handle my hair properly?",
         "a": "Hair is the hardest part of any portrait cut-out because individual strands are thinner than a pixel. Use the refine brush on flyaway strands, and check the result against a background very different from the original."},
    ],
    "logo": [
        {"q": "Can I get a transparent logo from a JPG?",
         "a": "Yes — removing the background produces a transparent PNG. But if the original vector file (.svg, .ai, .eps) exists anywhere, use that instead: vectors scale to any size with no quality loss."},
        {"q": "Why does my logo have a white box around it?",
         "a": "Because it was saved as JPG, which has no alpha channel and cannot store transparency at all. Re-export from the original as PNG or WebP."},
        {"q": "What resolution should I export a logo at?",
         "a": "Larger than any current use, since a raster logo cannot be enlarged later without softening. If the logo will ever appear in print, export at several times the size you need on screen."},
        {"q": "Will the inside of letters like O and A be transparent?",
         "a": "They should be, and it is worth checking at full zoom. Enclosed counters filled with leftover white are the most common flaw in a logo cut-out, and they only show once the logo is placed on a colour."},
    ],
    "signature": [
        {"q": "How do I get a clean digital signature?",
         "a": "Sign larger than usual with a dark, thick pen on plain unlined white paper, photograph it from directly above under even light, then remove the background. The result is the ink alone on transparency."},
        {"q": "Is it safe to make a signature image online?",
         "a": "It depends entirely on whether the file is uploaded. Here the processing runs in your browser and the image never leaves your device, which matters more for a signature than for almost any other image."},
        {"q": "What format should I save a signature in?",
         "a": "PNG, so the transparency is preserved and it can be placed over any document background. A JPG will arrive with a white box around it."},
        {"q": "Why do the thin parts of my signature disappear?",
         "a": "The delicate strokes where the pen lifted are the first thing an over-aggressive cut-out removes. Sign with a thicker pen, photograph at higher resolution, and check the fine strokes at full zoom."},
    ],
    "car-photos": [
        {"q": "Why are cars hard to cut out?",
         "a": "Paint, glass and chrome are all mirrors, so large parts of the image literally show the background you are removing. A tool has to decide that sky-coloured pixels in the middle of the bonnet belong to the car."},
        {"q": "What is the best place to photograph a car for a listing?",
         "a": "An open, empty area under overcast light, shot from a three-quarter front angle at around waist height. Direct sun creates blown highlights and hard shadows that get read as part of the vehicle."},
        {"q": "Why does my cut-out car look like it is floating?",
         "a": "Because the ground contact shadow was removed with the background. Adding a soft shadow beneath the car, or keeping a hint of the original contact shadow, is what makes it sit on the surface."},
        {"q": "Should I edit out scratches and damage?",
         "a": "No. Cut out the car cleanly for the gallery image, but photograph flaws honestly in the supporting shots. An unnaturally perfect gallery raises more buyer doubt than a visible scuff."},
    ],
    "clothing": [
        {"q": "What is a ghost mannequin photo?",
         "a": "A garment photographed on a mannequin which is then cut away, so the clothing keeps its three-dimensional shape with nothing visible inside it. Most clothing marketplaces prefer this over a flat lay."},
        {"q": "Why does lace or mesh cut out badly?",
         "a": "Because the background shows through the garment itself, so every hole is a separate edge and many pixels are genuinely part fabric and part background. Sheer fabrics like chiffon have the same problem."},
        {"q": "How do I keep colours accurate across a range?",
         "a": "Lock your white balance and shoot every item under the same light, rather than correcting each photo by eye afterwards. Colour mismatch drives more apparel returns than anything a cut-out affects."},
        {"q": "Can I photograph clothing on a model instead?",
         "a": "You can, but it is the hardest cut-out case — the tool has to separate garment, skin and hair at once. For model shots it is usually better to keep the background than to cut it out."},
    ],
    "pet-photos": [
        {"q": "Why is pet fur hard to cut out?",
         "a": "Fur is a matting problem rather than an edge problem: the outline is a wide band of strands each thinner than a pixel, every one part animal and part background. Long-haired breeds are hardest."},
        {"q": "What background should I photograph my pet against?",
         "a": "Something clearly lighter or darker than their coat. Brightness contrast matters more than colour — a black cat on a dark sofa has no findable edge at all."},
        {"q": "How do I get a pet to look at the camera?",
         "a": "Have someone hold their attention just beside the lens, shoot from the animal's eye level, and use burst mode. You are selecting a frame rather than taking one."},
        {"q": "Why did my cat's whiskers disappear?",
         "a": "Whiskers are the finest structure in the image and the first thing an aggressive cut-out removes. Use the refine brush to bring them back — a slightly soft outline is the correct one on an animal."},
    ],
    "youtube-thumbnail": [
        {"q": "What size should a YouTube thumbnail be?",
         "a": "1280 × 720 pixels, under 2 MB. More importantly, design it to work at around 210 pixels wide, which is the size most viewers actually see in feeds and sidebars."},
        {"q": "Why do so many thumbnails use cut-out people?",
         "a": "Because separating the subject from its background is what keeps a face readable at 210 pixels. A face photographed in a room competes with the room; a cut-out on flat colour does not."},
        {"q": "How much text should a thumbnail have?",
         "a": "Three to five words at most, in a heavy weight, occupying a real portion of the frame. Anything longer is unreadable at the size it is displayed."},
        {"q": "What should I avoid in a thumbnail?",
         "a": "Two competing focal points, fine detail, small text, and pure red or white backgrounds that blend into YouTube's own interface. Keep the bottom-right corner clear for the duration stamp."},
    ],
    "ebay": [
        {"q": "What are eBay's photo requirements?",
         "a": "At least 500 pixels on the longest side, with no added text, borders or watermarks on the main image. There is no pure-white requirement, only a preference for a plain background."},
        {"q": "Does a white background help eBay listings?",
         "a": "Yes, mainly by contrast. Search results are a dense grid of photos taken on kitchen tables, so a product on clean white stands out before anyone reads the title."},
        {"q": "How many photos should an eBay listing have?",
         "a": "eBay allows twelve free and most listings use three. Use the rest for other angles, a scale reference, labels and model numbers, every flaw, and everything included in the box."},
        {"q": "Should I photograph damage on used items?",
         "a": "Yes, deliberately and close up. Sellers consistently find it reduces returns and 'not as described' disputes far more than it costs in bids."},
    ],
    "discord-pfp": [
        {"q": "What size should a Discord avatar be?",
         "a": "Upload at 512 × 512. Discord crops it to a circle and displays it at 32 to 40 pixels in message lists, so judge it at that size rather than on the profile card."},
        {"q": "Should a Discord avatar have a transparent background?",
         "a": "Usually not. Discord runs in dark mode for most people but not all, so a transparent avatar looks different depending on the viewer's theme. Compositing onto a mid-tone colour looks identical everywhere."},
        {"q": "Can I use an animated avatar?",
         "a": "Animated GIF avatars require Nitro. Keep the motion slow and confined to one area — at 40 pixels, a busy animation reads as flicker."},
        {"q": "Why does my GIF avatar have jagged edges?",
         "a": "GIF supports only one fully transparent colour with no partial transparency, so cut-out edges cannot be smooth. Composite onto a solid background before exporting as GIF."},
    ],
    "twitch": [
        {"q": "Why do stream overlays need transparent PNGs?",
         "a": "Because they sit on top of live gameplay. A JPG has no alpha channel, so a 'transparent' JPG overlay arrives as a solid rectangle covering what viewers came to watch."},
        {"q": "Should I use a green screen or cut out images?",
         "a": "A green screen with OBS chroma key is right for the live webcam feed, since it runs in real time. Cutting out stills is for the assets around the stream — panels, alerts, banners and emotes."},
        {"q": "What size should Twitch emotes be?",
         "a": "112 × 112, 56 × 56 and 28 × 28. Design at 112 but check constantly at 28, which is chat size and smaller than a line of text."},
        {"q": "What are the Twitch panel and banner sizes?",
         "a": "Panels are 320 pixels wide with free height, the profile banner is 1200 × 480, the offline video player banner is 1920 × 1080, and the profile picture is 256 × 256."},
    ],
}


def deep_for(url_name, kwargs=None):
    """The long-form block for the current page, or None.

    Use-case pages all resolve to one url_name, so they are keyed by their slug
    as well; everything else is keyed by url_name alone.
    """
    kwargs = kwargs or {}
    if url_name == "use_case":
        return DEEP.get(f"use_case:{kwargs.get('slug')}")
    return DEEP.get(url_name)
