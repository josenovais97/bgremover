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
    "blur": {
        "title": "How background blur actually works",
        "sections": [
            {
                "h": "Depth of field, and why phones fake it",
                "p": [
                    "Optical background blur — bokeh — comes from a wide aperture and a large sensor. Only one plane is truly in focus, and everything in front of or behind it falls off progressively. A full-frame camera at f/1.8 produces it naturally.",
                    "Phone sensors are tiny and their lenses have deep depth of field, so almost everything is sharp whether you want it or not. Portrait mode fakes the effect: the phone estimates a depth map, then blurs by an amount that varies with estimated distance. This tool does the same thing on any photo, after the fact.",
                ],
            },
            {
                "h": "Why the edges are the hard part",
                "p": [
                    "Simulated blur lives or dies on the boundary between subject and background. Real optical blur transitions gradually because the falloff follows actual distance; a naive mask blurs everything outside a hard outline by the same amount, which produces the cut-out look that gives portrait mode away.",
                    "The specific artefacts to check for: a halo of sharp background hugging the subject's outline, hair that has been blurred away with the background, and a foreground object at the same distance as the subject that got blurred anyway because it was outside the mask.",
                ],
            },
            {
                "h": "How much blur to apply",
                "p": [
                    "Less than feels right. The instinct is to push the slider until the background is unrecognisable, which reads as artificial immediately — real lenses rarely obliterate a background that completely at portrait distances.",
                    "A useful target is enough blur that background detail stops competing for attention but the setting is still legible. Somewhere around the point where you can tell it is a kitchen, but cannot read the labels.",
                ],
            },
            {
                "h": "What blur is good for",
                "p": [
                    "Beyond aesthetics, it solves practical problems: a cluttered room behind a video-call headshot, a distracting sign behind a portrait, or a busy street behind a product.",
                    "It is also a softer alternative to redaction when the background merely needs de-emphasising rather than hiding. If the background contains something that genuinely must not be readable — a screen, a document, a face — blur is the wrong tool, because it is reversible. Cover or crop those instead.",
                ],
            },
        ],
    },
    "collage": {
        "title": "Arranging photos into a grid",
        "sections": [
            {
                "h": "Pick a layout for the number of photos",
                "p": [
                    "Some counts arrange more comfortably than others. Two, three, four, six and nine sit naturally in regular grids; five and seven do not, and usually need one cell given more weight than the rest.",
                    "The reliable approach for an awkward count is a feature layout — one large image with the others in a column or strip beside it. That reads as deliberate, where a grid with one empty cell reads as a mistake.",
                ],
            },
            {
                "h": "Gutters and consistency",
                "p": [
                    "The space between images does more work than people expect. Zero gap makes a collage read as a single composite image, which suits a panorama or a sequence. A visible, even gutter separates the photos into distinct frames, which suits a set of unrelated shots.",
                    "What matters most is that the gutter is even. Uneven spacing is one of those things nobody consciously notices and everybody registers as amateurish. The same applies to the outer margin: it should match the internal gutters, or be deliberately larger, but never slightly different.",
                ],
            },
            {
                "h": "Cropping inside cells",
                "p": [
                    "Photos in a grid must fill their cells, and unless your source images happen to match the cell ratio, something has to give. Filling the cell and cropping the overflow keeps the grid clean but can cut heads off; fitting the whole image inside leaves letterbox bars.",
                    "Fill-and-crop is almost always the better choice, but it needs checking per cell. The common failure is a portrait photo dropped into a landscape cell, where a centre crop removes the top of someone's head.",
                ],
            },
            {
                "h": "Sizing the export",
                "p": [
                    "A collage's output resolution multiplies: a 3 × 3 grid at 1000 pixels per cell is a 3000-pixel image before gutters. That is often larger than needed and slow to upload.",
                    "Decide the final display size first and work back. For a social post, 1080 pixels on the longest side is plenty regardless of how many photos are in it — each cell only needs a few hundred pixels. For print, work from the physical size at 300 DPI instead.",
                ],
            },
        ],
    },
    "watermark": {
        "title": "Watermarking that is worth doing",
        "sections": [
            {
                "h": "Be honest about what it prevents",
                "p": [
                    "A watermark does not stop theft. Anyone determined can crop it, clone it out, or run an inpainting model over it in seconds, and the tools to do that are as free as this one.",
                    "What a watermark actually does is raise the effort above casual, and attach attribution to an image that travels. Someone who would have right-clicked and reposted may not bother; someone who reposts anyway carries your name with them. Those are real benefits, and they are the honest reason to do it.",
                ],
            },
            {
                "h": "Placement and the trade-off",
                "p": [
                    "There is a straight trade between removability and intrusiveness, and where you sit on it depends on what the image is for:",
                ],
                "list": [
                    "A corner mark is unobtrusive and trivially cropped out — fine for attribution on work you are happy to have shared.",
                    "A mark across the subject is much harder to remove and much more damaging to the image — right for proofs and previews clients have not paid for.",
                    "A large, low-opacity tiled pattern is the hardest to remove cleanly, and the standard for stock previews.",
                    "A semi-transparent mark over a busy area survives inpainting better than one over flat colour, where a model can simply reconstruct the background.",
                ],
            },
            {
                "h": "Opacity and contrast",
                "p": [
                    "Around 30–50% opacity is the usual working range: visible enough to read, faint enough not to ruin the image. Below about 20% it disappears against busy areas; above 70% it dominates.",
                    "Pure white or pure black marks vanish against matching areas of the photo. A mark with a subtle outline or drop shadow stays legible over both light and dark regions, which matters because you rarely control where in the frame it lands across a batch.",
                ],
            },
            {
                "h": "Keep the original clean",
                "p": [
                    "Watermark on export, never on your master. Once a mark is burned into the pixels it cannot be cleanly removed, and the version you will want in two years — for a portfolio, a print, a client who did pay — is the clean one.",
                    "For batch work, that means keeping an unwatermarked archive and generating marked copies as needed. It is also worth keeping metadata authorship fields on the original: unlike a visible mark, they cost nothing and survive as long as nobody strips them.",
                ],
            },
        ],
    },
    "photo_filters": {
        "title": "Using filters and adjustments well",
        "sections": [
            {
                "h": "Adjustments versus looks",
                "p": [
                    "Two different things get called filters. Adjustments — exposure, contrast, saturation, temperature — are corrections that move an image towards what it should have looked like. Looks are stylistic presets that move it somewhere deliberately different.",
                    "The order matters. Correct first, then style. A preset applied to an underexposed, colour-cast photo bakes those problems in and makes them harder to fix, because the preset has already redistributed the tones you needed to work with.",
                ],
            },
            {
                "h": "What each slider actually does",
                "p": [
                    "Knowing the mechanism makes the results predictable:",
                ],
                "list": [
                    "Exposure shifts every tone up or down together, and clips highlights or shadows once they hit the ends of the range.",
                    "Contrast pushes tones away from the middle — brights brighter, darks darker — which also increases apparent saturation as a side effect.",
                    "Saturation scales all colour intensity uniformly, so already-vivid colours clip first. Vibrance boosts the muted ones more than the vivid ones, which is why it is gentler on skin.",
                    "Temperature and tint correct colour casts along the blue–orange and green–magenta axes respectively.",
                    "Sharpening increases contrast at edges. It adds no detail, and overdone it produces bright halos along high-contrast boundaries.",
                ],
            },
            {
                "h": "Where over-editing shows first",
                "p": [
                    "Skin tones and skies are the two places that give away a heavy hand. Skin turns orange with too much saturation or warmth and grey-green with too much correction the other way; the eye is extremely well calibrated for this and forgiving of almost nothing.",
                    "Skies band. A gradient pushed hard runs out of intermediate values, and the smooth transition becomes visible steps — made worse by any subsequent lossy compression, which handles gradients badly to begin with.",
                ],
            },
            {
                "h": "Edit non-destructively where you can",
                "p": [
                    "Every adjustment discards information: pushed highlights clip, crushed shadows merge, and neither comes back by moving the slider the other way. Doing it repeatedly on a saved JPEG compounds the loss with compression damage.",
                    "Work from the highest-quality original each time rather than re-editing an export, and keep that original untouched. If you are producing several versions of one image, generate each from the master instead of editing one into the next.",
                ],
            },
        ],
    },
    "text_behind": {
        "title": "The text-behind-subject effect",
        "sections": [
            {
                "h": "How the layering works",
                "p": [
                    "The effect is three layers. At the bottom, the original photo. In the middle, your text. On top, a cut-out of the subject with a transparent background, aligned exactly over its original position.",
                    "Because the top layer is the same subject in the same place, the text appears to pass behind them while the photo looks untouched. Everything depends on that alignment — the cut-out must sit pixel-for-pixel where it came from, which is why the effect is built from one photo rather than composited from two.",
                ],
            },
            {
                "h": "Choosing a photo that works",
                "p": [
                    "Not every image suits it. What you need is a clear subject with visible space around them for the text to occupy:",
                ],
                "list": [
                    "A subject that does not fill the frame — head-and-shoulders or full-body with room at the sides.",
                    "A background that is relatively plain where the text will sit, so the words stay readable.",
                    "Good separation between subject and background, since the whole effect rests on the quality of the cut-out.",
                    "Ideally a subject whose outline is interesting — text disappearing behind a shoulder or between an arm and the body sells the depth far better than text behind a plain silhouette.",
                ],
            },
            {
                "h": "Typography choices",
                "p": [
                    "Heavy, wide letterforms work best, because you want a substantial amount of text area for the subject to overlap. Thin type passes behind a subject almost invisibly and the effect is lost.",
                    "Set the text large — often larger than feels sensible, frequently spanning the full frame width. The most effective versions use one or two words at a scale that would be overwhelming if the subject were not breaking it up.",
                ],
            },
            {
                "h": "Selling the depth",
                "p": [
                    "Two touches make it convincing. Slightly reducing the text's opacity, or nudging its colour towards the background's, makes it read as further away rather than pasted between two layers — atmospheric perspective, the same reason distant hills look paler.",
                    "The other is checking the cut-out edge at full zoom. Since the subject is composited back onto its own photo, a halo of leftover background is subtle rather than obvious — but the eye still registers it as a slightly wrong outline, which undercuts the illusion the whole effect depends on.",
                ],
            },
        ],
    },
    "base64": {
        "title": "When to use a data URI",
        "sections": [
            {
                "h": "What Base64 encoding is",
                "p": [
                    "Base64 represents binary data using 64 printable ASCII characters, so an image can travel through anything that only handles text — HTML, CSS, JSON, email bodies, configuration files.",
                    "A data URI wraps that in a scheme the browser understands: `data:image/png;base64,` followed by the encoded bytes. Used as an img src or a CSS background, it embeds the image directly in the document rather than pointing at a separate file.",
                ],
            },
            {
                "h": "The 33% cost",
                "p": [
                    "Base64 encodes three bytes into four characters, so the result is about 33% larger than the original, plus padding. That penalty is unavoidable and applies every time the containing document is served.",
                    "Which is the crux: an external image is cached separately and downloaded once, while an embedded one is re-sent with every copy of the page that contains it. Inlining a large image can make a page slower rather than faster, and inlining it into a document that changes often is worse still, because it defeats caching for both.",
                ],
            },
            {
                "h": "When it is the right call",
                "p": [
                    "It genuinely wins in a few situations:",
                ],
                "list": [
                    "Very small images — icons, a 1×1 tracking pixel, a tiny placeholder — where one round trip costs more than 33% of a few hundred bytes.",
                    "Single-file deliverables: an HTML email, a self-contained report, a page that must work with no external requests.",
                    "Avoiding a flash of missing content for something critical above the fold.",
                    "Embedding an image in JSON, YAML or a database field that only accepts text.",
                    "Environments with a strict content policy that blocks external image hosts.",
                ],
            },
            {
                "h": "Where it goes wrong",
                "p": [
                    "The common mistake is inlining photographs. A 500 KB photo becomes about 665 KB of text sitting in your HTML, downloaded in full before the page can render and re-downloaded on every visit because it cannot be cached independently.",
                    "The rough threshold most people settle on is a few kilobytes: below that, inlining is usually a win; above it, an external file with proper caching almost always beats it. SVG is worth a special mention — it is already text, so it can be embedded directly with no Base64 step and no size penalty at all.",
                ],
            },
        ],
    },
    # --- Compress intent variants (all rendered by landing.html) -------------
    "compress_png": {
        "title": "Why PNGs get so large",
        "sections": [
            {
                "h": "PNG compresses patterns, not photographs",
                "p": [
                    "PNG is lossless: it reconstructs your pixels exactly. It achieves that by finding repetition — runs of identical colour, rows that resemble the row above — and encoding those patterns compactly.",
                    "A screenshot of a code editor is full of such repetition and compresses beautifully. A photograph has almost none: sensor noise means adjacent pixels differ slightly everywhere, so PNG ends up storing something close to raw pixel data. This is why a photo saved as PNG is routinely five to ten times larger than a visually identical JPG.",
                ],
            },
            {
                "h": "The fix depends on the content",
                "p": [
                    "Before compressing, decide which kind of PNG you have. If it is a photograph, the format is the problem and no amount of PNG optimisation will fix it — convert to JPG or WebP and expect an 80–90% reduction with no visible change.",
                    "If it is a screenshot, logo, diagram or anything with sharp edges and flat colour, PNG is the right format and should stay. Lossy compression would put visible haloing around text and edges.",
                ],
            },
            {
                "h": "Compressing a PNG that should stay a PNG",
                "p": [
                    "Two levers work without changing format. The first is dimensions: a screenshot from a high-density display is often twice the resolution it needs to be, and halving it cuts the file to roughly a quarter.",
                    "The second is colour depth. A PNG storing 16 million colours for an image that only uses forty is wasting most of its palette. Reducing to an indexed palette is technically lossy but often visually identical on flat-colour graphics, and can cut the file dramatically. On photographs it produces obvious banding, so it is a graphics technique only.",
                ],
            },
            {
                "h": "Keep the transparency in mind",
                "p": [
                    "The one thing that must survive is the alpha channel. Converting a transparent PNG to JPG discards it entirely and the background comes back as solid white or black.",
                    "If you need both small size and transparency, lossy WebP is the answer — it carries a full alpha channel at a fraction of PNG's size, and every current browser supports it. Keep the PNG as your master for anything you will hand to someone else.",
                ],
            },
        ],
    },
    "compress_jpeg": {
        "title": "Compressing JPEGs without compounding damage",
        "sections": [
            {
                "h": "Your JPEG is already compressed",
                "p": [
                    "This is what makes JPEGs different from other compression jobs: the file has already been through a lossy pass. Re-saving it applies a second, and the second pass works on data that already contains artefacts, which it treats as real detail worth preserving while discarding something else.",
                    "The damage accumulates and never comes back. Ten saves at quality 90 produce a visibly worse image than one save at quality 60, despite the higher nominal setting each time.",
                ],
            },
            {
                "h": "So compress once, from the best source",
                "p": [
                    "If you still have the original — the camera file, the export from your editor, a PNG master — compress from that rather than from a JPEG that has already been through the mill.",
                    "When the JPEG is all you have, make one pass and accept the result rather than nudging the slider repeatedly and re-saving. Each attempt costs quality even if the number goes up.",
                ],
            },
            {
                "h": "Where the quality scale bites",
                "p": [
                    "For photographic content: 90–80 is visually indistinguishable at roughly half the file size, 80–70 softens fine texture slightly, 70–60 makes artefacts visible in skies and skin, and below 60 blockiness is obvious.",
                    "The scale is non-linear because the quality number scales a quantisation table rather than removing a fixed fraction of data. That is why dropping from 100 to 85 costs almost nothing visible and dropping from 70 to 55 costs a great deal.",
                ],
            },
            {
                "h": "Resize first, and consider switching",
                "p": [
                    "Reducing dimensions is more powerful than reducing quality, because file size scales with pixel count. Bringing a 4000-pixel photo down to 1600 usually clears a size target on its own, at no perceptible cost.",
                    "And if the destination accepts it, converting to WebP typically saves another 25–35% at matched visual quality — often enough to avoid lowering the quality setting at all. Keep JPEG when the file is going somewhere you do not control, since it is the format that always works.",
                ],
            },
        ],
    },
    "compress_webp": {
        "title": "Getting the most out of WebP",
        "sections": [
            {
                "h": "Two modes, two different jobs",
                "p": [
                    "WebP is unusual in offering both lossy and lossless compression in one format, and choosing the wrong mode is the main way people fail to get the benefit.",
                    "Lossy WebP is for photographs, where it typically produces files 25–35% smaller than a JPEG of equivalent visual quality. Lossless WebP is for screenshots, logos and flat-colour graphics, where it beats PNG by roughly 20–25% while preserving every pixel.",
                ],
            },
            {
                "h": "The capability nothing before it had",
                "p": [
                    "WebP's genuinely new trick is lossy compression with an alpha channel. Before it, a cut-out with a transparent background had to be PNG, and was therefore large.",
                    "As lossy WebP the same cut-out can be a fraction of the size while looking identical, which makes it the correct format for transparent images on the web. This matters most for product cut-outs, logos and any image composited over a page background.",
                ],
            },
            {
                "h": "Where WebP is the wrong answer",
                "p": [
                    "Browser support has been universal since 2020, so for anything you serve on a website WebP is safe. Outside the browser it is patchier than people assume.",
                    "Plenty of desktop software, print workflows, older content systems and upload forms still reject it. The rule that avoids trouble: WebP for images you serve, JPG or PNG for images you hand to someone else.",
                ],
            },
            {
                "h": "Converting to WebP without losing twice",
                "p": [
                    "Converting an existing JPEG to lossy WebP means two lossy passes, and the second one inherits the first one's artefacts. The saving is usually still worth it, but the result is never as good as encoding WebP from an original.",
                    "Where you have the master — a PNG, a camera file, an editor export — convert from that instead. And if the source is a PNG of a graphic rather than a photo, use lossless WebP: converting it to lossy will put haloing around exactly the sharp edges PNG was protecting.",
                ],
            },
        ],
    },
    "compress_under_1mb": {
        "title": "Getting under 1 MB",
        "sections": [
            {
                "h": "A generous limit, usually met by resizing alone",
                "p": [
                    "1 MB is a common ceiling on job portals, CMS uploads, forum attachments and government forms, and it is roomy enough that most images clear it without touching quality.",
                    "A modern phone photo is often 3–6 MB at 4000 pixels wide. Reducing it to 1600 pixels — still larger than most screens display — typically lands somewhere around 300–500 KB at good quality. That single step solves the problem for the majority of images.",
                ],
            },
            {
                "h": "The order that wastes the least quality",
                "p": [
                    "Work down this list and stop as soon as you are under:",
                ],
                "list": [
                    "Resize to the largest dimension the image will actually be shown at.",
                    "Export at quality 85, which is visually indistinguishable from the original on most photographs.",
                    "Switch to WebP if the destination accepts it, for another 25–35%.",
                    "Only then drop quality further, checking the result at full size.",
                ],
            },
            {
                "h": "When 1 MB is genuinely tight",
                "p": [
                    "Some content resists. Screenshots and images containing text have sharp edges that lossy compression handles badly, so they stay large at any acceptable quality — keep those as PNG and reduce dimensions instead, which often beats a high-quality JPEG of the same content.",
                    "Scanned documents are the other awkward case. They are usually text on white, which means they behave like graphics rather than photographs: PNG or a high-quality JPEG at reduced dimensions will look far better at the same size than an aggressively compressed full-resolution scan.",
                ],
            },
            {
                "h": "Check what the limit actually applies to",
                "p": [
                    "Some forms cap each file at 1 MB; others cap the whole submission, which is a different problem if you are uploading several documents. Reading which one you are facing before compressing saves doing the work twice.",
                    "It is also worth checking whether the limit comes with a dimension or format restriction. Portals that specify 1 MB frequently also specify JPEG only, or a maximum pixel width, and an image that meets the size limit in the wrong format is rejected just as firmly as an oversized one.",
                ],
            },
        ],
    },
    "compress_under_100kb": {
        "title": "Getting under 100 KB",
        "sections": [
            {
                "h": "An aggressive target that changes the approach",
                "p": [
                    "100 KB is tight. It appears on older government portals, some exam and visa application systems, forum avatars and legacy content systems, and unlike a 1 MB limit it cannot usually be met by resizing alone.",
                    "At this budget you are deciding what to sacrifice rather than finding a free win, and the right answer depends entirely on what the image is.",
                ],
            },
            {
                "h": "Dimensions first, and be ruthless",
                "p": [
                    "File size scales with pixel count, so this is still the most powerful lever by a wide margin. For a 100 KB target, something in the range of 600–1000 pixels on the longest side is usually where you need to be.",
                    "That is smaller than feels comfortable, but a clean 800-pixel image at quality 80 looks considerably better than a 2000-pixel image mangled down to the same file size. Resolution you cannot afford to keep is worth giving up before quality is.",
                ],
            },
            {
                "h": "Then format, then quality",
                "p": [
                    "Switching format is the next lever and often decisive at this size. WebP saves 25–35% over JPEG at matched quality, and AVIF more again — at 100 KB that difference is the whole margin.",
                    "Quality comes last, and 70–75 is about as low as photographic content goes before artefacts become distracting. Below 60 you get visible blockiness in smooth areas and haloing around edges.",
                ],
            },
            {
                "h": "Know when the content will not cooperate",
                "p": [
                    "Some images cannot reach 100 KB while remaining useful. A detailed scanned document, a screenshot full of small text, or a photograph with fine repeating texture will either stay large or become unreadable.",
                    "When a form demands 100 KB for a document scan, the answer is usually to crop to just the region that matters and reduce to grayscale rather than compress the whole page harder. Both cut size substantially without touching legibility, which is the thing that actually has to survive.",
                ],
            },
        ],
    },
    "compress_email": {
        "title": "Sending images by email",
        "sections": [
            {
                "h": "The limits are lower than the headline number",
                "p": [
                    "Most providers advertise around 25 MB per message — Gmail and Outlook both do — but that is the size of the encoded message, not of your files. Attachments are Base64-encoded in transit, which inflates them by about 33%.",
                    "So a 25 MB ceiling is really about 18 MB of actual attachments. And the recipient's server has its own limit, which may be lower: corporate mail systems commonly cap at 10 MB and some still at 5 MB. A message that leaves your outbox fine can bounce at the other end.",
                ],
            },
            {
                "h": "Nobody needs the full resolution",
                "p": [
                    "Photos sent by email are almost always viewed on a screen, often on a phone, and usually just looked at rather than edited or printed. A 4000-pixel original is serving no purpose in that journey.",
                    "Resizing to 1600 pixels on the longest side keeps an image that looks perfect on any screen and is typically a tenth of the size. For a batch of holiday photos, that is the difference between one message and five.",
                ],
            },
            {
                "h": "When to send full quality anyway",
                "p": [
                    "Sometimes the recipient does need the original — a designer who will edit it, a printer, a client who commissioned the shoot, anyone who will crop into it.",
                    "In that case do not compress; use a file-sharing link instead. Compressing an image someone is going to edit hands them a file with baked-in artefacts that every subsequent edit will amplify.",
                ],
            },
            {
                "h": "Inline images and metadata",
                "p": [
                    "Images pasted into the message body rather than attached are usually not compressed by the client, and are frequently the reason a message is unexpectedly large. They are also not always downloadable as files by the recipient, which is a common frustration.",
                    "One thing worth remembering: email attachments preserve metadata. Unlike social platforms, which strip it, a photo emailed straight from your phone carries its GPS coordinates and timestamp intact. If the picture was taken at home, strip that before sending it to someone you do not know.",
                ],
            },
        ],
    },
    "compress_web": {
        "title": "Images and page speed",
        "sections": [
            {
                "h": "Images are usually most of the page",
                "p": [
                    "On a typical page, images account for the majority of transferred bytes — far more than scripts or stylesheets. That makes them the highest-leverage thing to optimise, and the one most often left untouched.",
                    "They also tend to be the Largest Contentful Paint element, the metric Google uses to judge loading performance. A slow hero image does not just make the page feel sluggish; it is literally what the score measures.",
                ],
            },
            {
                "h": "Serve the size you display",
                "p": [
                    "The most common waste on the web is a 3000-pixel image displayed in a 600-pixel slot. The browser downloads all of it and throws most away.",
                    "Export at the size it will actually be shown at, allowing for high-density screens — roughly twice the CSS pixel width is a sensible ceiling, beyond which the difference is imperceptible. For images whose display size varies with viewport, serve several sizes and let the browser choose with srcset.",
                ],
            },
            {
                "h": "Format and quality for the web",
                "p": [
                    "WebP is the sensible default: universally supported in browsers and 25–35% smaller than JPEG at matched quality. AVIF is smaller again and worth the slower encode for large hero images.",
                    "Quality 80–85 is right for almost everything. Above 90 is wasted bytes on an image nobody will inspect at full size, and the difference is invisible once the image is scaled into its slot.",
                ],
            },
            {
                "h": "Beyond the file itself",
                "p": [
                    "A few things matter as much as size:",
                ],
                "list": [
                    "Set explicit width and height so the browser reserves space — otherwise content jumps as images load, which is what Cumulative Layout Shift measures.",
                    "Lazy-load images below the fold, but never the hero image, which needs to load as early as possible.",
                    "Strip metadata from web images: it is a few kilobytes per file with no benefit to a visitor, and it may contain location data.",
                    "Keep the colour profile, though — removing it can make a wide-gamut image render flat and washed out.",
                ],
            },
        ],
    },
    # --- Comparison pages (rendered by landing.html) -------------------------
    "cmp_adobe": {
        "title": "An honest comparison",
        "sections": [
            {
                "h": "They are aimed at different jobs",
                "p": [
                    "Adobe Express is a design tool. Its centre of gravity is templates, layouts, brand kits, typography and multi-element compositions — making a social post, a flyer, a presentation slide. Background removal is one feature inside that.",
                    "ClearBG is a set of single-purpose image utilities. There are no templates, no canvas, no brand kit and no design surface. You bring an image, do one thing to it, and leave with the result.",
                ],
            },
            {
                "h": "Where Adobe Express is the better choice",
                "p": [
                    "If the job is design rather than image processing, use it. Nothing here competes with a template library, a layout canvas, collaborative editing, or an asset library shared across a team.",
                    "It also fits naturally if you are already in the Adobe ecosystem, since files move between Express and the rest of Creative Cloud without friction. And its generative features — text-to-image, generative fill — have no equivalent that runs in a browser tab.",
                ],
            },
            {
                "h": "Where this is the better choice",
                "p": [
                    "Three situations. First, privacy: Adobe Express uploads your files to Adobe's servers to process them, which is a problem for identity documents, medical images, unreleased work and anything under a confidentiality obligation. Here the processing happens on your device and nothing is transmitted.",
                    "Second, friction: there is no account, no sign-in and no export limit. Third, bulk: because there is no per-image cost to us, batch work has no quota attached to it.",
                ],
            },
            {
                "h": "The honest trade-off",
                "p": [
                    "Running in a browser tab imposes real limits. A server can run a model hundreds of times larger than one that fits in a page, so on the hardest cut-outs — fine hair against a busy background, semi-transparent fabric — a cloud service can still produce a better edge.",
                    "Speed also depends on your hardware rather than ours, so an older phone will be slower than a recent laptop, and very large files can exceed what a tab can hold in memory. Where maximum quality on a difficult image matters more than privacy, the cloud tool is the right recommendation.",
                ],
            },
        ],
    },
    "cmp_photoroom": {
        "title": "An honest comparison",
        "sections": [
            {
                "h": "Where PhotoRoom is strongest",
                "p": [
                    "PhotoRoom is built specifically for product and e-commerce photography, and it does more than remove backgrounds. Generative backgrounds, AI-suggested scenes, shadow generation and batch templates are genuinely useful for a seller producing a catalogue, and there is no equivalent here.",
                    "Its cut-out quality on hard subjects is also very good, because it runs large models on its own servers rather than in your browser — the structural advantage no on-device tool can match.",
                ],
            },
            {
                "h": "The differences that usually decide it",
                "p": [
                    "Three things separate them in practice:",
                ],
                "list": [
                    "Processing location. PhotoRoom uploads your images; here they never leave your device, which you can verify in the Network tab.",
                    "Cost model. PhotoRoom's free tier is limited, with full-resolution export and batch features on a paid plan. There are no limits here because there is no per-image cost to impose them for.",
                    "Watermarks and resolution caps. Free tiers commonly restrict one or both; exports here are always full resolution and never watermarked.",
                    "Account requirement. No sign-up here, which matters if you want to use a tool once without creating an account.",
                ],
            },
            {
                "h": "Which to use when",
                "p": [
                    "For a seller building a catalogue who wants generated backdrops and scene templates and does not mind the images going to a server, PhotoRoom does more.",
                    "For cut-outs on white for marketplace listings, for high volumes without a quota, or for anything you would rather not upload, on-device processing covers the job and removes the privacy question entirely.",
                ],
            },
            {
                "h": "What we cannot do",
                "p": [
                    "It is worth stating the limits plainly. There is no generative fill here, no AI-invented backgrounds, and no automatic shadow synthesis — those need models far larger than a browser tab can hold.",
                    "On the hardest edges, a large server-side model still wins. If your product photography is dominated by fur, glass, mesh or semi-transparent packaging, and the images are not sensitive, a cloud service will give you a cleaner result than anything running locally.",
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
    # --- Tool pages that shipped without a deep dive (1.11) ---
    'ecommerce': {
        "title": 'Product shots that pass marketplace review',
        "sections": [
            {
                "h": 'Pure white is a specific number, not a colour',
                "p": [
                    "Amazon's main-image rule is RGB 255,255,255 exactly. A backdrop that photographs as white almost never is — studio white typically lands somewhere around 240-250 per channel, which looks white next to a product and reads as light grey against the marketplace's own page background. The seam where your image ends becomes visible, and that is what a reviewer notices.",
                    'This is why compositing the cut-out onto a generated white canvas beats trying to shoot a perfect white background. The canvas is 255 by construction, and the only thing that has to be right is the edge of the cut-out.',
                ],
            },
            {
                "h": 'The 85% frame rule that quietly fails listings',
                "p": [
                    'Amazon expects the product to occupy roughly 85% of the image frame. A cut-out dropped onto a large square with comfortable margins satisfies every colour requirement and still fails this one, because the product ends up filling perhaps half the frame.',
                    "Crop after removing the background, not before. Removing first gives you a known product boundary, so the crop can be computed from the subject's actual bounding box with a fixed margin, rather than guessed from the original photo where the product sits wherever the photographer put it.",
                ],
            },
            {
                "h": 'Sizes worth exporting',
                "p": [
                    'Marketplaces differ less than their documentation suggests, and the practical answer is to export large and square.',
                ],
                "list": [
                    'Amazon: 2000x2000 px enables the zoom viewer; 1600 px is the minimum for it.',
                    'Etsy: 2000x2000 px, though it displays at a 4:3 crop, so keep the product centred.',
                    'Shopify: 2048x2048 px is the theme-friendly default.',
                    'Keep a transparent PNG master as well — resizing from a cut-out is free, re-cutting is not.',
                ],
            },
            {
                "h": 'Shadows: keep, fake, or drop',
                "p": [
                    'Background removal takes the original contact shadow with it, and a product floating with no shadow looks pasted on. Marketplaces vary on whether that matters: Amazon permits a shadow on the main image but forbids props and text, while a plain cut-out is always safe.',
                    'For a consistent catalogue the reliable choice is no shadow at all on the primary image, and a shadow only on secondary lifestyle shots. Inconsistent fake shadows across a catalogue look worse than none, because the eye reads the grid as a set and picks out the odd one immediately.',
                ],
            },
        ],
    },
    'ocr': {
        "title": 'Getting a clean read out of an image',
        "sections": [
            {
                "h": 'Why the same document reads twice differently',
                "p": [
                    "Recognition begins by deciding, pixel by pixel, what is ink and what is paper. That decision is made from local contrast, so anything that changes brightness across the page changes the answer — a shadow from your hand, a window on one side, the curve of a book's spine.",
                    'It is why a photo that looks perfectly legible to you can return nonsense from one half of the page and near-perfect text from the other. The half that failed was thresholded to solid black or solid white before any character was examined.',
                ],
            },
            {
                "h": 'The resolution floor',
                "p": [
                    "Accuracy is governed by how many pixels tall a lowercase letter is, not by the megapixels of the image. Around 20-30 pixels is comfortable. Below about 10, the shapes that distinguish similar characters — the gap in an 'e', the join on an 'a' — simply are not present in the data, and no amount of processing recovers them.",
                    'The practical consequence is that zooming in before you capture beats every post-processing step. A screenshot of a zoomed page outperforms a full-page screenshot scaled up afterwards, because one has the pixels and the other is inventing them.',
                ],
            },
            {
                "h": 'Choosing the language actually matters',
                "p": [
                    'The engine resolves ambiguous shapes against a model of the language you selected, so the wrong selection does not merely fail to help — it produces confident, wrong, real words. Portuguese text read as English comes back as English-looking nonsense, and accented characters tend to vanish because the model has no expectation of them.',
                    'If a document mixes languages, pick the dominant one rather than loading several. Multiple packs dilute each model and usually cost more accuracy than the mixed content does.',
                ],
            },
            {
                "h": 'What to fix before recognising',
                "p": [
                    'Almost every improvement is upstream of the recognition step.',
                ],
                "list": [
                    'Crop to the text block, so layout analysis has nothing else to interpret.',
                    'Straighten the page — small skew is corrected automatically, large skew defeats line detection.',
                    'Even out the lighting before raising contrast; contrast on an uneven image amplifies the problem.',
                    'Do not sharpen heavily — the haloes it creates get read as ink and merge adjacent characters.',
                ],
            },
        ],
    },
    'pdf_to_image': {
        "title": 'Turning PDF pages into usable images',
        "sections": [
            {
                "h": 'Rendering versus extracting',
                "p": [
                    "There are two different operations people call 'PDF to image'. Extracting pulls out photographs that were embedded in the file, at whatever resolution they were embedded. Rendering draws the page — text, vectors, images and all — into a new bitmap at a size you choose.",
                    'This tool renders. That is what you want for anything containing text or diagrams, because the characters are drawn from their vector outlines at the output size and stay crisp. Extraction would give you only the photos and none of the layout.',
                ],
            },
            {
                "h": 'Choosing a scale that is worth the megabytes',
                "p": [
                    'A PDF page has a nominal size in points, and rendering at 1x produces roughly 72 pixels per inch — fine for a thumbnail and too soft to read comfortably. 2x lands near 150 DPI, which is the sensible default for screen reading and the point where body text becomes properly legible.',
                    '4x approaches 300 DPI and is worth it only when the result will be printed or when you intend to run recognition over the output. The file size scales with the square of the factor, so a 4x render of a twenty-page document is a genuinely large download for output most people will view at a quarter of that size.',
                ],
            },
            {
                "h": 'Why a scanned PDF behaves differently',
                "p": [
                    'A PDF produced by a scanner has no text in it at all — each page is one large photograph. Rendering such a page above the resolution of the original scan cannot add detail; it enlarges the scan and inflates the file.',
                    'You can usually tell which kind you have by trying to select text in a PDF viewer. If nothing highlights, the page is an image, the useful export is JPG rather than PNG, and the natural next step is text recognition rather than a higher scale factor.',
                ],
            },
            {
                "h": 'PNG or JPG for the pages',
                "p": [
                    "Pages that are mostly text, tables or line diagrams should be PNG: the content is hard edges on flat white, which is exactly where lossless compression is small and where JPEG's ringing artefacts show up around every character.",
                    'Pages that are mostly photographs should be JPG, where PNG would be several times larger for no visible gain. A mixed document is usually better off as PNG, because damaged text is more noticeable than a slightly larger file.',
                ],
            },
        ],
    },
    'word_to_pdf': {
        "title": 'What actually happens when a .docx becomes a PDF',
        "sections": [
            {
                "h": 'Fonts are the reason no two conversions match',
                "p": [
                    'A Word file does not contain its fonts. It contains their names. When the document says Calibri, it is making a request of whatever machine opens it, and Calibri ships with Microsoft Office rather than with operating systems — so a Mac or a Linux box, and most web browsers on them, do not have it.',
                    'The substitute is never metrically identical. Characters are a fraction wider or narrower, so the point at which a line wraps moves, and once one line moves every line after it moves too. Two pages can become three. This is not a defect in a particular converter; it is what happens whenever a document is laid out somewhere other than where it was written, and it is why the preview here is shown before the save rather than after.',
                    'If you need a PDF that is guaranteed identical to what you see in Word, the only reliable route is to export it from Word itself, on the machine that has the fonts. Everything else — this tool, LibreOffice, an online converter — is re-laying the document out and hoping the fonts line up.',
                ],
            },
            {
                "h": 'Why the print dialog, and not a download button',
                "p": [
                    "A page cannot write a file to your disk unasked, so every in-browser converter has to choose how the PDF gets made. One option is to photograph each page and wrap the pictures in a PDF. That produces a file where the text is not text: nothing can be selected or searched, a screen reader finds nothing to read, and the size balloons because prose is being stored as pixels.",
                    "The other option is the browser's own print engine, which is a real PDF writer with real font embedding and real pagination. It produces selectable text at a fraction of the size. The price is that it opens the print dialog and you pick 'Save as PDF' as the destination. That extra click buys a file that behaves like a document instead of a scan of one.",
                ],
            },
            {
                "h": 'What converts cleanly and what does not',
                "p": [
                    'The reliable cases are the common ones: CVs, cover letters, reports, essays, minutes — anything that is mostly headings and paragraphs, with the occasional list or simple table.',
                ],
                "list": [
                    'Multi-column layouts and text boxes, which depend on precise frame positions.',
                    'Tracked changes and comments, which are editorial state rather than content and are not rendered.',
                    'Embedded charts and SmartArt, which are Office-specific drawing objects.',
                    'Anything relying on a font you own but your browser does not.',
                ],
            },
        ],
    },
    'pdf_to_word': {
        "title": 'Why PDF to Word is harder than Word to PDF',
        "sections": [
            {
                "h": 'A PDF has no paragraphs to find',
                "p": [
                    'The two directions look symmetrical and are not. A .docx is a description of intent: this run of text is a heading, this is a body paragraph, these cells form a table. Turning that into pages is a matter of following instructions that are already in the file.',
                    'A PDF is the finished result with the instructions thrown away. What remains is a list of drawing operations: put this glyph at this coordinate in this font at this size. There is no such thing as a paragraph in a PDF, only characters that happen to share a baseline, and there is no table — only text that happens to line up with some drawn rectangles.',
                    'So going backwards is not conversion, it is reconstruction. Structure has to be inferred from geometry, and every inference is a guess. This tool groups glyphs into lines by baseline and lines into paragraphs by vertical gap, treats noticeably larger text as a heading, and rejoins words that were hyphenated across a line break. Those rules are honest about what they are, and they are right most of the time on ordinary prose.',
                ],
            },
            {
                "h": 'Where reconstruction goes wrong',
                "p": [
                    'The failure cases all come from the same place: geometry that means something to a human but nothing to a rule about vertical gaps.',
                ],
                "list": [
                    'Two columns read as one, because the extractor works down the page and finds the left column then the right, interleaving them by baseline.',
                    'Tables lose their grid, because the cells were never cells — just text positioned near some lines.',
                    'Headers, footers and page numbers arrive as body text, since nothing marks them as furniture.',
                    'Scanned pages yield nothing at all, because there are no glyphs in the file to extract — only a photograph. That case is detected and sent to the OCR tool instead of producing an empty document.',
                ],
            },
            {
                "h": 'When to use this and when not to',
                "p": [
                    'Use it when you want the words: to quote from a report, rewrite a letter, translate a contract, or recover text from a document whose source you have lost. That is the majority of what people actually need from "PDF to Word", and it works well.',
                    'Do not use it expecting a visual replica. If the layout is the point — a designed form, a brochure, an invoice template — you are better off keeping the PDF and editing it as a PDF, or rebuilding the layout deliberately in Word around the extracted text. Any tool promising a pixel-perfect PDF-to-Word round trip on a complex page is overselling, whatever it costs.',
                ],
            },
        ],
    },
    'pdf_tools': {
        "title": 'Merging and splitting without touching the pages',
        "sections": [
            {
                "h": 'Why this is lossless and fast',
                "p": [
                    'A PDF is a tree of objects with a page list at the top. Each page points at its own content stream — the drawing commands — plus the fonts and images it needs. Merging two documents means building a new tree whose page list references the pages of both; splitting means building trees that reference a subset.',
                    'The content streams themselves are copied byte for byte and never decoded. Nothing is re-compressed, nothing is rasterised, no image is re-encoded. Text stays selectable because it is the same text objects; a scan keeps exactly the JPEG it arrived as. This is also why it is quick even on large files: the work is proportional to the number of objects, not to the number of pixels.',
                    'It is worth knowing what that implies about size. A merged file is roughly the sum of its inputs, because all the content is still there. Merging is not a way to make documents smaller, and any tool that shrinks a merged PDF noticeably has re-encoded something.',
                ],
            },
            {
                "h": 'Page ranges, and why bad ones are refused',
                "p": [
                    "Ranges are written the way people write them: 1-3, 5, 8- gives three files, and the open-ended 8- means page eight to the end. Each range becomes its own document, so you get one file per range rather than one file with the pages you chose.",
                    "A range that runs past the end of the document is rejected rather than quietly trimmed. Silently clamping 1-99 to 1-20 would hand you a file that looks complete and is missing everything you asked for beyond page twenty — a mistake you would find much later, when the submission was already sent.",
                ],
            },
            {
                "h": 'Encrypted files',
                "p": [
                    'A password-protected PDF is refused when you add it, and says so. That is deliberate: the alternative is discovering the problem partway through a merge, with an output file that is missing one input. Open it in a PDF reader, remove the protection, and add it again.',
                ],
            },
        ],
    },
    'csv_excel': {
        "title": 'The details that ruin spreadsheet conversions',
        "sections": [
            {
                "h": 'The delimiter is not always a comma',
                "p": [
                    'CSV stands for comma-separated values, and in much of Europe it usually is not. Where the decimal separator is a comma — Portugal, Spain, France, Germany, Italy, Brazil — a comma cannot also separate fields, so Excel writes and expects semicolons instead. The file extension is the same either way.',
                    'A converter that assumes commas turns such a file into a single column of text: every row becomes one long cell, and the damage is obvious immediately. The delimiter is therefore detected from the content rather than assumed, which is what lets an export straight out of a Portuguese Excel install open correctly here.',
                ],
            },
            {
                "h": 'Quoting, and the corruption you notice three rows later',
                "p": [
                    'A field containing the delimiter has to be wrapped in quotes — "Lisboa, Portugal" is one value, not two — and a field containing a quote has to escape it by doubling. A field can even contain a line break, quoted, which means a CSV row is not the same thing as a line of the file.',
                    'This is where naive conversion fails quietly. Splitting each line on the delimiter looks right on the first twenty rows and then shifts every column one place to the left at the first address containing a comma, silently, for the rest of the file. Proper quote handling is the difference between a conversion you can trust and one you have to audit.',
                ],
            },
            {
                "h": 'What a CSV cannot carry',
                "p": [
                    'Going from Excel to CSV is a lossy step by nature, and it is better to know what is lost than to discover it.',
                ],
                "list": [
                    'Formulas become their last computed value, which is what you want — the formula referenced cells that no longer exist in a flat file.',
                    'Formatting, colours, column widths, merged cells and frozen panes have nowhere to go.',
                    'Multiple sheets do not fit: a CSV file holds exactly one table, so each sheet has to be exported separately.',
                    'Number and date formats collapse to text, which is why a CSV can turn a date into something Excel later reinterprets differently.',
                ],
            },
            {
                "h": 'Getting a spreadsheet into Google Sheets privately',
                "p": [
                    'There is no button here that sends your file to Google Sheets, and that is a deliberate omission rather than a missing feature. Sheets is a cloud service; a direct "convert to Google Sheets" would have to upload your spreadsheet to Google under an OAuth grant, which is the exact thing this site exists not to do.',
                    'Sheets imports CSV natively, so the private route is two steps and no middleman: convert to CSV here, then File → Import in Sheets and pick the file. Your data goes from your machine to your own Google account without passing through anyone else\'s converter on the way.',
                ],
            },
        ],
    },
    'svg_to_png': {
        "title": 'Rasterising vector art without losing the edges',
        "sections": [
            {
                "h": 'Why exports from other tools come out soft',
                "p": [
                    'An SVG has a nominal size in its width, height or viewBox attributes, and many converters rasterise at that size and then scale the resulting bitmap to whatever you asked for. The vector is only consulted once, at the small size, and everything after that is a bitmap being stretched.',
                    'Rendering at the target size instead means the curves are evaluated at the resolution you actually want, so a 4x export contains four times the real detail rather than four times the pixels. The difference is most obvious on diagonal edges and small text, which is where stretched bitmaps go to pieces.',
                ],
            },
            {
                "h": 'Fonts are the usual surprise',
                "p": [
                    'SVG text is not shapes — it is characters plus a font name, resolved at render time. If the file names a font that is not available where it is rasterised, a fallback is substituted and the text reflows: different widths, different line breaks, sometimes overlapping other elements.',
                    'The fix belongs in the SVG rather than in the converter. Converting text to outlines in your vector editor before export makes the file self-contained and immune to this, at the cost of no longer being editable as text. For a logo destined for export that is almost always the right trade.',
                ],
            },
            {
                "h": 'External references do not travel',
                "p": [
                    'An SVG can reference images by URL rather than embedding them, and can pull in webfonts and stylesheets the same way. Rasterised in isolation, those references produce blank rectangles and fallback type, because nothing is fetched.',
                    'Embedding raster content as a data URI inside the SVG makes it self-contained. It grows the file, but the file then renders identically everywhere, which is the entire point of handing someone a vector.',
                ],
            },
            {
                "h": 'Transparency and what JPG does to it',
                "p": [
                    'PNG output keeps the alpha channel, so an icon exported at any size drops onto any background cleanly. That is normally what you want from vector art.',
                    'Exporting the same artwork as JPG flattens transparency onto white, and the result is a white box wherever the artwork was transparent. If the destination cannot take PNG, fill the background with the colour it will actually sit on rather than accepting the default.',
                ],
            },
        ],
    },
    'upscale': {
        "title": 'What enlarging an image can and cannot do',
        "sections": [
            {
                "h": 'Resampling is interpolation, not invention',
                "p": [
                    'Enlarging computes new pixels from the ones around them. A good filter — Lanczos, here — weights a neighbourhood of source pixels to estimate each new one, which keeps edges clean where a naive method would produce stair-stepping or blur.',
                    'What it cannot do is add detail that was never captured. If a face occupies forty pixels in the original, no filter recovers the eyelashes, because that information does not exist in the file. Enlargement makes an image bigger and, done well, keeps it looking deliberate rather than stretched.',
                ],
            },
            {
                "h": 'Why this is not an AI upscaler, on purpose',
                "p": [
                    'Model-based super-resolution genuinely can hallucinate plausible detail, and on the right image it is impressive. In a browser tab it is also slow enough to lock the page for tens of seconds on a large photo, and memory-hungry enough to crash a phone.',
                    'There is a second, less discussed cost: an AI upscaler invents detail, and invented detail is wrong detail. On a document, a licence plate or a face, that is a liability rather than a feature. A resampled enlargement is honest about what it knows.',
                ],
            },
            {
                "h": 'Sharpening after, not before',
                "p": [
                    'Enlargement softens edges slightly no matter how good the filter is, so a gentle unsharp pass afterwards restores the appearance of crispness. Applied before enlargement, the same sharpening gets magnified along with everything else and turns into visible haloes.',
                    'Overdoing it is the common mistake. Sharpening amplifies noise and JPEG artefacts as readily as detail, so an already-compressed source will show its blocking pattern long before it looks sharp.',
                ],
            },
            {
                "h": 'When enlargement is the wrong answer',
                "p": [
                    'If you need a larger image for print and have access to the original file, go back to it. A camera original or a vector source beats any enlargement of a downscaled copy, and the difference is not subtle.',
                ],
                "list": [
                    'Logos and icons: find the SVG and rasterise it instead — infinitely better than any enlargement.',
                    'Screenshots of text: retake at a higher zoom rather than enlarging.',
                    'Heavily compressed images: compress artefacts enlarge too, and sharpening makes them worse.',
                    'Print: 2x from a good original is usually plenty; 4x from a thumbnail will not rescue it.',
                ],
            },
        ],
    },
    'remove_object': {
        "title": 'How content-aware fill decides what goes in the hole',
        "sections": [
            {
                "h": 'The fill is borrowed, not imagined',
                "p": [
                    'Erasing an object leaves a hole, and the fill is assembled from the pixels around it — colour, texture and gradient sampled from the boundary and propagated inward, coarse structure first and fine detail after.',
                    'This is why the surroundings decide the result far more than the object does. A person standing against open sky disappears completely, because the algorithm has an enormous amount of consistent sky to borrow from. The same person in front of a bookshelf leaves a smear, because there is no way to infer which book was behind them.',
                ],
            },
            {
                "h": 'Brush generously, but not too generously',
                "p": [
                    "Under-brushing is the most common mistake. Leaving a rim of the object's edge pixels means those colours get treated as legitimate surroundings and propagated into the fill, producing a ghost in roughly the object's shape.",
                    'Cover the object plus a small margin, including its shadow and any reflection — a removed object whose shadow remains reads as obviously wrong. But an unnecessarily huge selection forces the algorithm to invent more area than it has evidence for, so the fill turns mushy. Slightly larger than the object is the target.',
                ],
            },
            {
                "h": 'Several small passes beat one large one',
                "p": [
                    'A big object over varied background is better removed in stages. Erase a portion, let the fill settle, then erase the next — each pass has more plausible surroundings to work from than one enormous selection would.',
                    'It also lets you stop when it looks right rather than committing to a single result, and to work along a boundary — the edge of a wall, a horizon — instead of across it, which is where fills most visibly break down.',
                ],
            },
            {
                "h": 'Where this approach runs out',
                "p": [
                    'Straight lines that pass behind the object rarely reconnect convincingly: tiles, window frames, floorboards and railings all show a kink. Repeating patterns can drift out of phase. And anything that would require knowing what was genuinely hidden — a face behind a hand, text behind a sign — cannot be recovered by any amount of borrowing.',
                    'When the fill fails, cropping the object out of the frame is often the better edit, and an honest one.',
                ],
            },
        ],
    },
    'gif': {
        "title": 'Building an animated GIF that stays small',
        "sections": [
            {
                "h": 'Cost scales with area, so size the frame first',
                "p": [
                    'Every frame stores pixels, so halving the width and height of a GIF removes roughly three quarters of its data. No other setting comes close, which makes dimensions the first thing to decide rather than the last.',
                    'For a UI demonstration 320-480 pixels wide is usually enough, since the result is typically displayed inline at around that size anyway. Exporting at full screen width and letting the page scale it down means paying for pixels nobody sees.',
                ],
            },
            {
                "h": 'The palette is where the quality goes',
                "p": [
                    'A GIF frame can hold 256 colours. Everything else is approximated, and that approximation — not the compression, which is lossless — is what makes GIFs look coarse compared to the source.',
                    'Content with a narrow range of colours survives this well: screen recordings, line art, flat illustration. Photographic content with gradients does not, because a sky reduced to a handful of blues becomes visible bands.',
                ],
            },
            {
                "h": 'Why dithering can make the file bigger',
                "p": [
                    'Dithering hides banding by scattering pixels of the available colours so the eye blends them. It works, and it fights the compression directly: the algorithm shrinks files by finding repeated runs of pixels, and dithering deliberately replaces smooth areas with high-frequency noise that has no runs to find.',
                    'So the banding fix and the file-size goal pull in opposite directions. On flat-coloured content, turning dithering off entirely is often both smaller and cleaner.',
                ],
            },
            {
                "h": 'Frame rate and duration',
                "p": [
                    'GIF timing is stored per frame in hundredths of a second, and most viewers clamp very short delays, so extremely high frame rates do not play as intended anyway.',
                ],
                "list": [
                    '10-15 fps looks fine for screen recordings and interface demos.',
                    'Trim to the seconds that carry the point — duration costs linearly.',
                    'A static camera compresses far better than a panning one; crop to the moving region.',
                    'If the clip is longer than about five seconds, consider whether it should be a video.',
                ],
            },
        ],
    },
    # --- More tool pages (1.11) ---
    'heic': {
        "title": 'Converting iPhone photos without wasting quality',
        "sections": [
            {
                "h": 'What you give up in the conversion',
                "p": [
                    'HEIC stores 10 bits per colour channel; JPEG stores 8. That difference is invisible in most photographs and shows up as faint banding in large smooth gradients — a clear sky at dusk is the classic case. It cannot be recovered afterwards.',
                    'The container also carries things a flat image format has nowhere to put: Live Photo motion, the depth map that portrait blur relies on, and the edit history that makes Revert possible on the phone. Converting produces a finished picture and discards the rest.',
                ],
            },
            {
                "h": 'Convert once, from the original',
                "p": [
                    'JPEG is lossy, so every encode discards a little more. Converting an already-converted file compounds that for no reason. Go back to the HEIC each time rather than re-exporting a JPG you made earlier.',
                    'Keep the originals until you have checked the output. Deleting the HEIC masters is the only irreversible step in this process, and it is the one people do first.',
                ],
            },
            {
                "h": 'JPG or PNG out',
                "p": [
                    'Pick JPG when the destination is an upload form, an email or long-term storage — the size saving is the entire reason the format exists and the quality cost at a high setting is not visible.',
                    'Pick PNG when the photo is going into further editing. It is lossless, so the conversion adds no generational damage, at the cost of a file several times larger than the HEIC you started with.',
                ],
            },
            {
                "h": 'Order of operations for a camera roll',
                "p": [
                    'A holiday folder is the real case, and a few habits keep it clean.',
                ],
                "list": [
                    'Convert the whole batch in one pass so the generational loss happens once.',
                    'Convert first and compress second, as separate decisions — a converter that silently shrinks to hit a size target has chosen quality for you.',
                    'Strip metadata at the same time if the photos are going somewhere public; every file is being rewritten anyway.',
                    'Check a few outputs before deleting anything.',
                ],
            },
        ],
    },
    'qr': {
        "title": 'Designing a code that scans on the first try',
        "sections": [
            {
                "h": 'The blank margin is part of the code',
                "p": [
                    'The specification requires a quiet zone — four modules of empty space on every side, a module being one of the small squares. Scanners use it to find where the code begins, and it is not a design suggestion.',
                    'Printing a code flush against text, a border or a coloured panel is the single most common reason a technically valid code refuses to scan. Paper also absorbs ink and slightly thickens every module, which eats into the margin further, so a proof that scans on screen can fail in print.',
                ],
            },
            {
                "h": 'Error correction is what buys you a logo',
                "p": [
                    'Four levels of redundancy are available, recovering roughly 7%, 15%, 25% and 30% of the data. A logo dropped in the centre is simply damage, so whether the code survives is decided entirely by which level it was generated at.',
                    "At the highest level a centre logo covering up to about a quarter of the area still decodes. At the lowest, the same logo destroys the code. There is no way to place a logo 'safely' other than leaving enough redundancy to absorb it.",
                ],
            },
            {
                "h": 'Colour contrast is not brightness contrast',
                "p": [
                    'A scanner measures luminance, not hue. Red modules on a green field look strongly contrasting to a person and can be nearly identical in brightness to a camera, which is why colourful codes fail in ways their designers find baffling.',
                    'Check any coloured design in greyscale before committing. If the modules and the background are hard to tell apart there, the code will struggle. Keep the modules darker than the background, too — inverted codes are decoded by many scanners and not all.',
                ],
            },
            {
                "h": 'Size follows viewing distance',
                "p": [
                    'The working rule is that a code should be at least one tenth as wide as the distance it will be scanned from. A metre away wants 10 cm; across a room wants far more than most posters allocate.',
                ],
                "list": [
                    'Shorter URLs produce fewer modules, so each one is physically larger and easier to read.',
                    'Below roughly 2 cm, print becomes unreliable regardless of distance.',
                    'Test with a default camera app, not a dedicated scanner — that is how people scan.',
                    'Test on the actual material under the actual lighting before a print run.',
                ],
            },
        ],
    },
    'exif': {
        "title": 'What the file says about you after you send it',
        "sections": [
            {
                "h": 'The fields that actually matter',
                "p": [
                    'Cameras and phones write a block of metadata into every photo. Most of it is harmless — exposure, focal length, orientation. Three fields are not: GPS coordinates, the timestamp, and the device identifier.',
                    'The coordinates are precise enough to identify a building, and a photo taken indoors is usually taken at home. A set of photos shared over months carries a movement history nobody intended to publish, which is the part people underestimate.',
                ],
            },
            {
                "h": 'Which platforms strip it, and why that is not a plan',
                "p": [
                    'Large social networks generally strip metadata on upload, partly for privacy and partly because they re-encode everything anyway. That protects the public copy and nothing else.',
                    "The file you emailed, put in a shared folder, sent over a chat app that preserves originals, or attached to a marketplace listing keeps every field. Stripping before sending is the only approach that does not depend on each destination's current behaviour.",
                ],
            },
            {
                "h": 'Why stripping costs no quality on a JPEG',
                "p": [
                    'A JPEG is a sequence of marker segments, and metadata lives in its own segments alongside the compressed image data. Removing them is a matter of dropping those segments and rewriting the file — the pixels are never decoded, so there is no re-encode and no generational loss.',
                    'This is worth knowing because the alternative people reach for — opening the photo in an editor and re-saving it — does re-encode, and loses a little quality every time.',
                ],
            },
            {
                "h": 'What metadata will not tell you',
                "p": [
                    'Absent metadata is not evidence of anything. Screenshots never had any, messaging apps remove it, and any re-save can drop it, so a photo with no EXIF is unremarkable rather than suspicious.',
                    'Equally, present metadata is not proof: every field is editable. It is a convenience for organising your own photos and a privacy risk when sharing, and it is not a chain of custody.',
                ],
            },
        ],
    },
    'redact': {
        "title": 'Hiding information so it stays hidden',
        "sections": [
            {
                "h": 'Blur and pixelation are reversible in principle',
                "p": [
                    'Both are deterministic transforms that discard detail without discarding structure. Given the method and its parameters, an attacker can blur candidate text the same way and compare — which is how pixelated text has been recovered in practice more than once.',
                    "The risk is highest for content drawn from a small set: a six-digit number, a card's last four, a name from a short list. Brute-forcing every candidate through the same filter and matching the output is entirely feasible.",
                ],
            },
            {
                "h": 'A solid bar is the only honest redaction',
                "p": [
                    'Drawing an opaque rectangle replaces the pixels with one colour, and no information survives that. It is the boring option and it is the correct one whenever the content genuinely matters.',
                    "Blur and pixelation are better thought of as de-emphasis — fine for a bystander's face in a screenshot you are posting for a different reason, wrong for an account number.",
                ],
            },
            {
                "h": 'Flatten, and check what you exported',
                "p": [
                    'The most damaging failures are not weak filters but redactions that were never applied to the pixels: a shape sitting on a layer above the image, or a PDF annotation drawn over text that is still selectable underneath. Copying the text out of such a document returns everything.',
                    'Exporting a flattened image is what makes a redaction permanent. Verify by opening the export fresh and attempting to select or zoom into the covered area — check the file you are about to send, not the editor you made it in.',
                ],
            },
            {
                "h": 'The parts people forget to cover',
                "p": [
                    'Sensitive information is rarely only in the obvious place.',
                ],
                "list": [
                    'Reflections in glasses, screens and windows.',
                    'The browser tab strip, bookmarks bar and notifications in a screenshot.',
                    'Document headers, footers, reference numbers and barcodes — a barcode encodes the number in plain sight.',
                    'The filename itself, which often contains a name or an account number.',
                    'Metadata: the pixels can be clean while the file still names the device and location.',
                ],
            },
        ],
    },
    'screenshot': {
        "title": 'Why a raw screenshot looks worse than it should',
        "sections": [
            {
                "h": 'The problem is the edge, not the content',
                "p": [
                    'A raw screenshot is a rectangle of interface that ends abruptly at the crop. Placed on a page or a slide it reads as a fragment: nothing indicates where the interface stopped and the document began, so the eye treats the boundary as damage.',
                    'Padding on a contrasting backdrop fixes this by giving the rectangle somewhere to sit. That is the entire mechanism behind the polished look — the screenshot has not been improved, it has been framed.',
                ],
            },
            {
                "h": 'Shadow and radius do the separating',
                "p": [
                    'A soft drop shadow lifts the image off the background and makes the boundary intentional rather than accidental. It wants to be large and faint; a tight dark shadow looks like a sticker.',
                    "Rounded corners work because almost every interface being screenshotted already has them, so square corners on the export contradict the content inside. Matching the radius roughly to the window's own is enough.",
                ],
            },
            {
                "h": 'Capture at the resolution you will publish',
                "p": [
                    'Screenshots are pixel data, so an image captured small and enlarged afterwards has soft text that no amount of framing rescues. Capture on a high-density display, or zoom the interface before capturing, and scale down rather than up.',
                    'Text is also the reason to export PNG. It is nothing but hard edges, which is where JPEG puts visible speckle around every character, and where lossless compression is small anyway because interfaces are mostly flat colour.',
                ],
            },
            {
                "h": 'Check the frame before you publish it',
                "p": [
                    'Screenshots leak more than any other image type, because the whole screen was captured and only the middle was examined.',
                ],
                "list": [
                    'Open tabs, bookmarks and the window title.',
                    'Notification banners that arrived during the capture.',
                    'Autofill suggestions and browser history in a dropdown.',
                    'Real names, email addresses and internal URLs in the interface itself.',
                ],
            },
        ],
    },
    'video_gif': {
        "title": 'Turning a clip into a GIF worth sending',
        "sections": [
            {
                "h": 'You are trading a good codec for a bad one',
                "p": [
                    "Video formats describe motion: a frame is stored as 'this block moved, here is a small correction'. GIF has no such concept and stores frames close to whole, so a clip that was a few hundred kilobytes as video routinely becomes several megabytes as a GIF.",
                    'That is not a flaw in the conversion, it is the format. The reason to accept it is placement — GIF plays as an image, so it works in email, chat boxes and forums that will not take a video element at all.',
                ],
            },
            {
                "h": 'Trim before anything else',
                "p": [
                    'Duration costs linearly, and most clips contain two or three seconds that carry the point plus several that do not. Cutting to the useful moment is usually a larger saving than every quality setting combined.',
                    'A loop also reads better when it is short. A two-second loop is understood as a loop; an eight-second one is watched once and then becomes a distraction on the page.',
                ],
            },
            {
                "h": 'Camera movement is the expensive part',
                "p": [
                    'Because GIF cannot describe motion, a panning or handheld shot changes every pixel in every frame and nothing can be skipped. A locked-off shot where only one element moves compresses dramatically better.',
                    'If the source moves, cropping to the region that actually matters recovers much of the difference — you remove pixels that were being re-stored on every single frame.',
                ],
            },
            {
                "h": 'Settings, in the order worth adjusting them',
                "p": [
                    'Each of these is more effective than the one after it.',
                ],
                "list": [
                    'Dimensions: 320-480 px wide is plenty for most uses and cost scales with area.',
                    'Duration: cut to the seconds that carry the point.',
                    'Frame rate: 10-15 fps reads as smooth for screen content.',
                    'Palette: fewer colours, and turn dithering off on flat-coloured content.',
                ],
            },
        ],
    },
    'video_converter': {
        "title": 'Trimming and converting video in a browser tab',
        "sections": [
            {
                "h": 'Why MP4 is the format to land on',
                "p": [
                    'MP4 carrying H.264 video is the closest thing to a universal video format. It plays on phones, desktops, televisions, in every browser and in every editor, and hardware decoding for it exists on essentially everything.',
                    'Newer codecs compress better, and that matters when you are serving millions of views. For a clip you need someone else to be able to open, compatibility is worth more than the bytes.',
                ],
            },
            {
                "h": 'What trimming does and does not re-encode',
                "p": [
                    'Video is stored as occasional complete keyframes with dependent frames between them, so a cut that does not land on a keyframe requires re-encoding the surrounding section to produce a valid file.',
                    'That is why a trimmed clip can be slightly softer than its source even though nothing else changed, and why trimming is slower than the file size suggests. Cutting from an original rather than from an already-trimmed export keeps the damage to one generation.',
                ],
            },
            {
                "h": 'Speed changes and audio',
                "p": [
                    'Changing playback speed rewrites timing rather than pixels, so the video itself does not degrade. Audio is the awkward part: raising speed raises pitch unless the track is resampled, which is why a sped-up clip can sound comical.',
                    'For a silent demonstration this is moot and dropping the audio track entirely is usually the right call — it removes a surprising share of the file size and avoids autoplay restrictions on the web.',
                ],
            },
            {
                "h": "Working within a browser's limits",
                "p": [
                    "Everything here runs in the page, which means it runs in the tab's memory. Long or high-resolution sources are the practical ceiling.",
                ],
                "list": [
                    'Short clips convert comfortably; a feature-length file is the wrong job for a browser tab.',
                    'Keep the tab in the foreground — background tabs are throttled and the work stalls.',
                    'Trim first, then convert, so the encode processes only the part you are keeping.',
                    'Nothing is uploaded, which is also why your machine does all the work and can take a while.',
                ],
            },
        ],
    },
    'pdf': {
        "title": 'Assembling images into a PDF that behaves',
        "sections": [
            {
                "h": 'A PDF of photos is a container, not a compressor',
                "p": [
                    'Placing images in a PDF does not shrink them. JPEG data is normally embedded as-is, so the document is roughly the sum of its images plus a small amount of structure — twenty 4 MB photos produce a document around 80 MB.',
                    'If the result needs to fit an upload limit, compress the images before assembling rather than looking for a setting afterwards. That ordering also keeps you in control of the quality trade instead of leaving it to a generic optimiser.',
                ],
            },
            {
                "h": 'Page size versus image shape',
                "p": [
                    'A4 and Letter are both close to a 1:1.41 and 1:1.29 ratio, while phone photos are 4:3 or 16:9. Something has to give: fit the image inside the page and accept margins, or size the page to the image and get a document whose pages are all different shapes.',
                    'For anything that will be printed, choose the standard page size — a printer handling twenty differently shaped pages produces twenty differently scaled results. For a document that will only ever be viewed on screen, fitting the page to the image looks better.',
                ],
            },
            {
                "h": 'Order, orientation and the scanning case',
                "p": [
                    'The most common real use is turning photographed documents into one file to send. Two things make that pass without a complaint: pages in the right order, and every page the same way up.',
                    'Photographs carry an orientation flag that viewers honour inconsistently, so a page that looked upright in your gallery can arrive sideways. Rotating before assembly, rather than relying on the flag, removes the problem.',
                ],
            },
            {
                "h": 'What a PDF of images cannot do',
                "p": [
                    'The output contains pictures of text, not text. Nobody can search it, select from it, or have a screen reader read it aloud, and some organisations reject exactly this kind of submission.',
                    'If searchable text matters, run recognition over the pages and keep the text alongside the document. It is also worth remembering that photographs of documents carry the metadata of the photograph, including where it was taken.',
                ],
            },
        ],
    },
    # --- Landing + comparison pages (1.11) ---
    'priv_hub': {
        "title": "What 'runs on your device' means technically",
        "sections": [
            {
                "h": 'Where the computation physically happens',
                "p": [
                    "A conventional image service accepts an upload, processes the file on a server it controls, and sends a result back. Your file exists on that machine for at least the duration of the job, and in practice for as long as the operator's retention policy says.",
                    "These tools compile the same work — segmentation models, image codecs, PDF rendering, text recognition — to WebAssembly and run it inside the browser tab. The file is read from disk into the page's memory, transformed there, and written back out. There is no request carrying it anywhere, because no part of the pipeline lives anywhere else.",
                ],
            },
            {
                "h": 'Why this is a structural property, not a policy',
                "p": [
                    'A privacy policy is a promise about what a company will do with data it already holds. It can be revised, misapplied, or made irrelevant by a breach or an acquisition, and none of those events require anyone to act in bad faith.',
                    'An architecture that never receives the data has nothing to revise. The distinction matters most for exactly the files people are most careful with — identity documents, medical letters, photographs of children — and it is the one claim an upload-based competitor cannot copy without rebuilding their product.',
                ],
            },
            {
                "h": 'What the server still sees',
                "p": [
                    'It would be dishonest to claim nothing is observable. Requesting a page is a request, so the hosting provider sees an IP address, a timestamp and which URL was fetched, exactly as it does for any website.',
                    'The AI model weights are fetched once from a public CDN, so that CDN sees a download of a public file. What none of them see is your image, because it is never part of any request.',
                ],
            },
            {
                "h": 'The costs of doing it this way',
                "p": [
                    'Local processing is a real trade rather than a free win, and it is worth being straight about the losses.',
                ],
                "list": [
                    'The first background removal downloads a model, which is a genuine wait on a slow connection.',
                    'Your device does the work, so an old phone is slower than a rented GPU would be.',
                    "Very large files are bounded by the tab's memory rather than by a server's.",
                    'Cloud services with far larger models beat these tools on the hardest inputs.',
                ],
            },
        ],
    },
    'priv_no_upload': {
        "title": 'How to check a no-upload claim yourself',
        "sections": [
            {
                "h": 'Watch the network panel',
                "p": [
                    'Every browser ships developer tools with a network tab that lists every request the page makes. Open it, clear it, then run the tool on an image and watch what appears.',
                    "A tool that processes locally shows requests for its own code and assets and then nothing while the work happens. A tool that uploads shows a request carrying a payload roughly the size of your file — which is unmistakable, because a photograph is orders of magnitude larger than the page's own traffic.",
                ],
            },
            {
                "h": 'The offline test is simpler and harder to fake',
                "p": [
                    'Load the page, then disconnect from the network entirely, then use the tool. Software that needs a server cannot work without one, so if the result still appears, the computation happened on your machine.',
                    'This is a stronger check than reading any policy, because it tests the thing itself rather than a description of it. The one caveat is the first run, which may need to fetch a model before it can go offline.',
                ],
            },
            {
                "h": 'What a claim of deletion actually promises',
                "p": [
                    'Services that upload frequently promise deletion after an interval — an hour, a day. That is a meaningful commitment and a much weaker one than it sounds: it concedes the file was transmitted, stored, and readable by that system for the window in question.',
                    'It also cannot cover copies that left the primary store: backups, logs, the CDN, a queue, an error report containing the file. Deletion is a process rather than an event, which is why not receiving the file is a different category of assurance.',
                ],
            },
            {
                "h": 'Signals that a tool is not local',
                "p": [
                    'Some behaviours are only possible with a server, whatever the marketing says.',
                ],
                "list": [
                    "A progress bar that tracks 'uploading' rather than processing.",
                    'A result delivered as a link to a hosted file rather than a direct download.',
                    'A hard file-size cap in the low megabytes — a server cost, not a browser limit.',
                    'An account requirement for processing, which implies work tied to an identity.',
                    'Nothing works with the network off, after the page has loaded.',
                ],
            },
        ],
    },
    'priv_offline': {
        "title": 'Why these tools keep working without a connection',
        "sections": [
            {
                "h": 'A service worker holds the app',
                "p": [
                    "The first visit installs a small script that sits between the page and the network and keeps a copy of the site's own files — the HTML shell, the stylesheet, the scripts each tool needs.",
                    'On later visits it can answer from that cache. So a tool loads with no connection at all, which is why the site behaves like an installed application rather than a page you have to be online to reach.',
                ],
            },
            {
                "h": 'The model is cached separately, and it is the big one',
                "p": [
                    'Background removal needs neural network weights, which are far larger than the rest of the site combined. They are fetched once and then stored, so the wait happens on the first cut-out and not again.',
                    'This is the one part that genuinely requires a connection the first time. Tools that need no model — cropping, converting, compressing, resizing — work offline from the first visit onward.',
                ],
            },
            {
                "h": 'Offline as evidence rather than convenience',
                "p": [
                    'The useful property here is not that you can edit photos on a plane. It is that working offline is only possible if the processing was never remote, which makes it a demonstration rather than a claim.',
                    "Any tool that stops working when the network does was sending your file somewhere. That inference runs one way and needs no trust in anybody's documentation.",
                ],
            },
            {
                "h": 'How updates reach a cached copy',
                "p": [
                    "Caching aggressively creates the opposite problem: a stale copy that never changes. The worker fetches from the network first for the site's own files when a connection exists, and falls back to the cache when it does not.",
                    'In practice a deployment is picked up the next time you load the site online, while an offline visit continues to work from what was stored. The model is treated the other way round — cache first, since a fixed set of weights has no reason to be re-checked.',
                ],
            },
        ],
    },
    'alternative': {
        "title": 'The economics behind per-image pricing',
        "sections": [
            {
                "h": 'Why cloud removal has to be metered',
                "p": [
                    'Running a segmentation model on a server means renting a GPU by the second. Every image has a marginal cost, so the business is obliged to count images — credits, subscriptions and per-image tiers are consequences of the architecture rather than pricing strategy.',
                    "Moving the model into the visitor's browser removes that cost entirely. An additional image costs the operator nothing, which is why there is no counter here: there is nothing to meter.",
                ],
            },
            {
                "h": 'What paid services genuinely buy you',
                "p": [
                    'It would be misleading to suggest the paid tools offer nothing. They run larger models than a browser can download, which shows on the hardest inputs — fine hair against a busy background, motion blur, semi-transparent fabric.',
                    'They also offer batch APIs, service levels and integrations that matter if background removal is part of an automated pipeline processing thousands of images a day. If that is the job, an API is the right tool and this is not.',
                ],
            },
            {
                "h": 'The resolution and watermark question',
                "p": [
                    'The most common complaint about free tiers is not the image limit but what arrives at the end: a preview at reduced resolution, or a watermark, with the full-quality file behind a payment step. The work is done and then withheld.',
                    'Nothing is withheld here because there is no paid tier to protect. Exports are full resolution and unwatermarked, which is a consequence of having nothing to upsell rather than generosity.',
                ],
            },
            {
                "h": 'Choosing between them honestly',
                "p": [
                    'The decision is usually straightforward once framed by volume and sensitivity.',
                ],
                "list": [
                    'Occasional images, done by hand: a local tool, with no account and no per-image cost.',
                    'Sensitive images: local, because the file is never transmitted.',
                    'Thousands of images through an automated pipeline: a paid API.',
                    'One unusually difficult image where quality matters more than anything: try both.',
                ],
            },
        ],
    },
    'cmp_tinypng': {
        "title": 'How image compressors actually differ',
        "sections": [
            {
                "h": 'Quantisation versus quality settings',
                "p": [
                    'The best-known PNG compressors work largely by reducing the number of distinct colours in an image and storing it as an indexed palette. On interface graphics, logos and flat illustration this is close to free — such images contain few colours to begin with — and it produces the dramatic reductions those tools are known for.',
                    'On a photograph the same technique is much less effective, because photographs contain thousands of colours that cannot be discarded without visible banding. That is why compression results vary so much by image type rather than by tool.',
                ],
            },
            {
                "h": 'Targeting a size instead of a quality',
                "p": [
                    "Most compressors expose a quality slider, which answers the wrong question when you have a hard limit to meet. Being told an image is 'quality 80' does not tell you whether it fits under a two megabyte cap.",
                    'Searching for the quality that lands just under a target size answers the actual question, at the cost of encoding the image several times. Done in the browser that is only your own processing time, which is why the approach is practical here.',
                ],
            },
            {
                "h": 'Changing the format usually beats tuning the quality',
                "p": [
                    'A JPEG squeezed hard develops blocking artefacts long before it approaches the size of the same image encoded as WebP at a comfortable quality. Format choice moves the whole curve; the quality slider only moves you along it.',
                    'The reason to stay with the original format is compatibility with wherever the file is going, which is a real constraint for email attachments and upload forms. Where you control the destination, converting is usually the larger win.',
                ],
            },
            {
                "h": 'The batch and privacy trade',
                "p": [
                    'Upload-based compressors typically cap free use by file count or size per month, because each image consumes their bandwidth twice.',
                ],
                "list": [
                    'Local compression has no monthly quota, because there is no bandwidth to consume.',
                    'Your device does the encoding, so a large batch takes real time on an old machine.',
                    'Nothing is transmitted, which matters for unreleased product shots and personal photos.',
                    'Dedicated encoders can still edge out a browser on absolute ratio for a given format.',
                ],
            },
        ],
    },
    'cmp_canva': {
        "title": 'Design suites and utilities solve different problems',
        "sections": [
            {
                "h": 'Composition versus a single transformation',
                "p": [
                    'A design suite exists to help you make something new: a layout with type, shapes, images and a brand system, assembled on a canvas and revisited over time. That work needs projects, templates, fonts and collaboration, and a cloud account is a reasonable price for it.',
                    'A utility exists to apply one transformation to a file you already have. Cropping to an exact ratio or stripping a background is a job with a beginning and an end, and wrapping it in a document model adds steps rather than capability.',
                ],
            },
            {
                "h": 'The account is the actual difference',
                "p": [
                    'Cloud design tools require an account because the document lives on their servers — that is what makes it openable from another machine and editable with a colleague. The requirement follows from the feature.',
                    'For a one-off transformation the same requirement is pure overhead: a signup, a verification email and a stored copy of your image, in exchange for an operation that finishes in seconds and produces a file you download immediately.',
                ],
            },
            {
                "h": 'Where the free tier tends to stop',
                "p": [
                    'Free tiers of design suites are generous with templates and restrictive at the export step, which is where the value is captured — resolution limits, watermarks, or a background-removal feature reserved for the paid plan.',
                    'That is a coherent business model and it means the last step of your work is the one you cannot finish. A utility with nothing to sell has no reason to place a gate there.',
                ],
            },
            {
                "h": 'Using both, which is the usual answer',
                "p": [
                    'These are complements far more often than alternatives.',
                ],
                "list": [
                    'Cut out, crop, compress or convert the asset here, with no account and at full resolution.',
                    'Take the finished asset into a design tool for layout, type and brand work.',
                    'Keep sensitive source images out of a cloud project by transforming them locally first.',
                    'Use a design suite when the output is a composition; use a utility when it is a file.',
                ],
            },
        ],
    },
    'cmp_cloudconvert': {
        "title": 'What a browser can convert, and what it cannot',
        "sections": [
            {
                "h": 'Formats a browser already understands',
                "p": [
                    'Browsers ship with decoders and encoders for the image formats the web runs on, and a canvas can move pixels between them. That covers the overwhelming majority of real conversion requests — JPEG, PNG, WebP and, in current browsers, AVIF.',
                    'Formats the browser does not know can still be handled by shipping a decoder compiled to WebAssembly, which is how HEIC from an iPhone and PDF rendering work here. The cost is a one-time download of that decoder.',
                ],
            },
            {
                "h": 'Where a conversion service is genuinely the right tool',
                "p": [
                    'General-purpose converters cover hundreds of formats, including proprietary and professional ones — CAD drawings, camera raw files from every manufacturer, legacy office documents, archive video codecs.',
                    'Supporting that breadth means running a large collection of specialised binaries, which is server work. If you need a Photoshop file flattened or a raw file developed, that is what those services are for and a browser is not a substitute.',
                ],
            },
            {
                "h": 'Queues, quotas and the round trip',
                "p": [
                    'A server-side conversion has a shape: upload, wait in a queue, convert, download. For a large file on a domestic connection the transfer dominates, and free tiers add queue priority as one of the things you are paying to skip.',
                    'A local conversion has no upload, no queue and no download — it starts immediately and is bounded by your own processor. For a common format that is usually faster in wall-clock terms even when the server is more powerful.',
                ],
            },
            {
                "h": 'Choosing between the two',
                "p": [
                    'The dividing line is format breadth against transmission.',
                ],
                "list": [
                    'Everyday web and phone image formats: local, with no upload and no quota.',
                    'Professional, proprietary or archival formats: a dedicated conversion service.',
                    'Anything confidential, in a common format: local, because it never leaves.',
                    'Automated conversion inside a pipeline: an API, which a browser cannot provide.',
                ],
            },
        ],
    },
    'heic_iphone': {
        "title": 'Two iPhone settings that decide what you get',
        "sections": [
            {
                "h": 'The capture format',
                "p": [
                    "Settings, then Camera, then Formats offers 'High Efficiency' and 'Most Compatible'. The first captures HEIC and roughly halves the storage each photo uses. The second captures JPEG and produces files that open anywhere.",
                    'The trade is storage and colour depth against compatibility. Nothing here changes photos you have already taken, which is why switching it rarely solves the problem someone actually has.',
                ],
            },
            {
                "h": 'The transfer setting most people never see',
                "p": [
                    "At the bottom of Settings, then Photos, there is 'Transfer to Mac or PC' with two options. On 'Automatic' the phone converts HEIC to JPEG as it copies over a cable. On 'Keep Originals' it hands across the HEIC untouched.",
                    'A great many people have this on Keep Originals without knowing, which is why photos that display perfectly on the phone arrive on a laptop as files nothing will open. Changing it fixes future cable transfers and does nothing for files already copied.',
                ],
            },
            {
                "h": 'Why the route off the phone matters',
                "p": [
                    'The same photo arrives in different formats depending on how it travelled. AirDrop to a Mac preserves HEIC. Most messaging apps convert to JPEG and heavily recompress. Email attachments are often converted. A cable transfer depends on the setting above.',
                    "So 'I already sent it to myself' is not a reliable conversion step — it frequently produces a much lower quality JPEG than converting deliberately would, because a chat app optimises for bandwidth rather than for your photo.",
                ],
            },
            {
                "h": 'Converting a backlog',
                "p": [
                    'For photos already taken, converting is the only route, and the order of operations matters.',
                ],
                "list": [
                    'Work from the HEIC originals rather than from anything a chat app returned.',
                    'Convert the batch once — repeated JPEG encodes compound the loss.',
                    'Choose PNG instead if the photo is going into further editing.',
                    'Keep the originals until you have checked the output, then reclaim the space.',
                ],
            },
        ],
    },
    'heic_windows': {
        "title": 'Making Windows open iPhone photos',
        "sections": [
            {
                "h": 'Why Windows needs an extension at all',
                "p": [
                    'HEIC images are compressed with HEVC, a codec covered by a large and fragmented set of patent pools. Bundling a decoder with the operating system means licensing from several of them, which is why Microsoft ships it as a separate component rather than including it.',
                    'The practical result is a file the operating system recognises by name and cannot display, producing an error that suggests corruption when the file is perfectly valid.',
                ],
            },
            {
                "h": 'The extensions, and the confusing part',
                "p": [
                    'Two items are involved: HEIF Image Extensions, which handles the container, and HEVC Video Extensions, which handles the actual decoding. Photos need both, and the second has at various times been a paid listing while a device-manufacturer variant was free.',
                    'This is why instructions found online contradict each other — they were written at different points in that history, and availability has also varied by region and Windows version.',
                ],
            },
            {
                "h": 'What installing them does not fix',
                "p": [
                    'The extensions teach Windows itself to display HEIC. They do not teach every application: older editors, many upload forms, and a great deal of third-party software still refuse the format, because each carries its own image loading code.',
                    "So installing them solves 'I want to look at my photos on this laptop' and does not solve 'I need to attach this to a form' or 'I need to send it to someone else'. Those need an actual conversion.",
                ],
            },
            {
                "h": 'Converting instead of installing',
                "p": [
                    'Converting to JPEG sidesteps the codec question entirely and produces files that work in every application on every machine, including the ones you are sending them to.',
                ],
                "list": [
                    'No system component to install, and no administrator rights required.',
                    'The result opens on Windows, Android, older software and web forms alike.',
                    'A browser-based converter carries its own decoder, so it works on a machine that cannot display HEIC at all.',
                    'Convert from the originals, once, and keep them until you have checked the output.',
                ],
            },
        ],
    },
    'ocr_extract': {
        "title": 'Pulling text out of a screenshot in practice',
        "sections": [
            {
                "h": 'Capture at the size you will recognise',
                "p": [
                    'The single biggest determinant of accuracy is how many pixels tall the letters are, and a screenshot is the one input where you fully control that. Zoom the page or application before capturing rather than enlarging the image afterwards.',
                    'Enlarging a small screenshot cannot add the detail that distinguishes similar characters, so the recognised text degrades in exactly the places that matter — digits, punctuation and short words.',
                ],
            },
            {
                "h": 'Crop to the text and nothing else',
                "p": [
                    'Before characters are identified, the page is analysed for structure: blocks, columns, reading order. Interface furniture around your text — toolbars, sidebars, tab strips — is analysed too, and can produce output interleaved in an order nobody wanted.',
                    "Cropping tightly to the passage removes that ambiguity and usually fixes 'the words are right but jumbled' without touching any other setting.",
                ],
            },
            {
                "h": 'Interfaces that are hard to read',
                "p": [
                    'Modern interface design works against recognition in two specific ways. Low-contrast grey text on a slightly lighter grey thresholds unpredictably, and text placed over photographs or gradients has no consistent background to separate from.',
                    'Dark mode is worth mentioning: light text on a dark background is handled by most engines, but a screenshot mixing dark panels and light ones can threshold inconsistently across the image. Capturing in light mode is a surprisingly effective fix.',
                ],
            },
            {
                "h": 'Expect to proofread the ambiguous characters',
                "p": [
                    'Recognition resolves uncertain shapes using a model of the language, which is why errors cluster where that model has no help to offer.',
                ],
                "list": [
                    'Digits and letters that share shapes: 0/O, 1/l/I, 5/S, 8/B.',
                    'Serial numbers, licence keys and codes — no language model can validate them.',
                    'Line breaks, which are guessed from spacing rather than read.',
                    'Accented characters when the language is set wrongly.',
                ],
            },
        ],
    },
    'compress_video': {
        "title": 'Why video files are large and what actually shrinks them',
        "sections": [
            {
                "h": 'Bitrate is the number that matters',
                "p": [
                    "A video's size is essentially its bitrate multiplied by its duration. Resolution, frame rate and codec all matter because of how they push the bitrate needed for a given appearance, but the file size follows the bitrate.",
                    'This is why a short 4K clip can dwarf a long, low-resolution one, and why trimming is such an effective saving: it reduces the multiplier directly, with no quality cost at all.',
                ],
            },
            {
                "h": 'Resolution is usually the honest cut',
                "p": [
                    'Halving the width and height quarters the pixels the encoder has to describe, and for footage destined for a phone screen or a chat window the difference is frequently invisible.',
                    'Most footage is captured at a resolution chosen by the camera rather than by the use. A clip shot in 4K and destined for a messaging app is carrying four times the pixels of a 1080p version that would look identical at its viewing size.',
                ],
            },
            {
                "h": 'Audio is a bigger share than people expect',
                "p": [
                    'Uncompressed or high-bitrate audio can account for a surprising portion of a short clip. Reducing it to a sensible compressed bitrate, or dropping it entirely for a silent demonstration, is a quick and visually free saving.',
                    'Dropping audio has a second benefit on the web, where autoplay policies are far more permissive for silent video than for anything with a soundtrack.',
                ],
            },
            {
                "h": "Working within the browser's limits",
                "p": [
                    'Encoding video in a page is genuinely demanding, and being realistic about the ceiling saves frustration.',
                ],
                "list": [
                    'Trim first so the encoder only processes what you are keeping.',
                    'Drop the resolution to the viewing size before adjusting anything else.',
                    'Remove the audio track when the clip is a silent demonstration.',
                    'Keep the tab in the foreground; background tabs are throttled and the encode stalls.',
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
