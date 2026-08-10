"""
Passport / ID photo specifications by country.

Powers the programmatic SEO landing pages at ``/passport-photo/<country>/`` —
each targets high-intent, low-competition queries like "<country> passport photo
size" and "<country> passport photo online". Sizes are the widely-published
official requirements; every page also tells visitors to confirm their own
government's exact rules (this is a free helper, not an official service).

Each entry carries a block of genuinely country-specific editorial content
(issuing authority, glasses/expression/headwear rules, how children are handled,
how the application actually works, and the reasons photos get rejected). That
detail is the point: with only the shared spec table, the nine pages were 79%
identical to each other and ~124 unique words apiece, which is what a search or
ad-network quality review reads as scaled, low-value content. Anything written
here must be true of THAT country specifically — if a sentence would read the
same for every country, it belongs in the shared template, not in this file.
"""
DPI = 300


def _px(mm):
    """Pixels for a millimetre length at 300 DPI (print resolution)."""
    return round(mm * DPI / 25.4)


# Head-height guidance (crown → chin) by frame size.
_HEAD_3545 = "32–36 mm tall — roughly 70–80% of the photo — centred, with the eyes level and looking straight ahead."
_HEAD_US = "1 to 1⅜ inches (25–35 mm), about 50–69% of the photo, with the eyes 1⅛–1⅜ in from the bottom."


def _entry(slug, name, flag, w_mm, h_mm, *, imperial=None, bg="plain white", head=None, note="",
           authority, authority_url, recency, intro, rules, children, process, rejections):
    """One country page's data.

    The first block of arguments is the printable spec (shared table); the
    keyword-only block after it is the country-specific editorial content and is
    mandatory — a country without it would regress into the near-duplicate page
    this module exists to avoid. ``PassportContentTests`` enforces the same rule.

    rules       list of (label, text) — the requirements that actually differ
                between countries (glasses, expression, headwear, copies).
    process     list of paragraphs on how the application really works, including
                whether the photo is taken for you at a counter.
    rejections  list of the concrete reasons this country's photos get refused.
    """
    return {
        "slug": slug,
        "name": name,
        "flag": flag,
        "w_mm": w_mm,
        "h_mm": h_mm,
        "w_px": _px(w_mm),
        "h_px": _px(h_mm),
        "imperial": imperial,           # e.g. "2 × 2 in" for the US, else None
        "bg": bg,
        "head": head or (_HEAD_US if imperial else _HEAD_3545),
        "note": note,
        "authority": authority,
        "authority_url": authority_url,
        "recency": recency,
        "intro": intro,
        "rules": [{"label": lab, "text": txt} for lab, txt in rules],
        "children": children,
        "process": process,
        "rejections": rejections,
    }


# Curated, confidently-sourced set. 35×45 mm is the international default used by
# the majority of countries; the exceptions (US, Canada, China, Brazil) carry
# their own dimensions.
# Only countries with a genuinely distinct spec or real standalone search intent
# keep their own page. A wider list (Germany, France, Japan, …) shared the
# identical 35×45 mm / plain-white spec with no distinguishing content, so those
# pages were 85%-similar near-duplicates Google discovered but refused to index
# (measured: 0.83 sibling similarity vs a 0.32 boilerplate floor). They now 301
# to the main tool (see FOLDED_COUNTRY_SLUGS) — the tool still makes photos for
# every country via its own preset list in passport.js; only the thin SEO pages
# are gone. Portugal stays deliberately: it's the home market where the .pt ccTLD
# is a ranking advantage rather than a handicap.
COUNTRIES = [
    _entry(
        "united-states", "United States", "🇺🇸", 51, 51, imperial="2 × 2 in",
        note="The 2×2 inch size is used for the US passport, visa, Green Card and DV lottery.",
        authority="U.S. Department of State — Bureau of Consular Affairs",
        authority_url="https://travel.state.gov/content/travel/en/passports/how-apply/photos.html",
        recency="the last 6 months",
        intro=[
            "The United States is one of the few countries that has never adopted the 35×45 mm international standard. A US passport photo is square — 2 × 2 inches, or 51 × 51 mm — and the same square photo is used for the passport, most visa applications, the Green Card (Form I-485), and the Diversity Visa lottery. If you have photos left over from a European application, they are the wrong shape and will be rejected.",
            "The head is also sized differently. Rather than the 70–80% frame fill common in Europe, the State Department measures from the bottom of your chin to the top of your head and wants that distance between 1 and 1⅜ inches (25–35 mm), with your eyes sitting 1⅛ to 1⅜ inches above the bottom edge. In practice that leaves noticeably more space around the head than a UK or Schengen photo.",
        ],
        rules=[
            ("Glasses", "Not permitted. Glasses have been banned in US passport photos since 1 November 2016 — the only exception is a documented medical reason, which requires a signed statement from a doctor. Take them off; do not rely on the removal being noticed later."),
            ("Expression", "Neutral, or a natural unforced smile. Both eyes open and visible, mouth closed or barely open. Exaggerated expressions are refused."),
            ("Headwear", "Not permitted except for religious or medical reasons, and then only with a signed statement — and your full face from the bottom of the chin to the top of the forehead must still be visible."),
            ("Clothing", "Everyday clothing. Uniforms, camouflage-pattern clothing and anything resembling a uniform are refused. White tops are risky against the required white background — pick a darker colour."),
            ("Digital uploads", "If you apply or renew online the file must be square, between 600×600 and 1200×1200 pixels, in JPEG, and under 10 MB. A 2×2 inch export at 300 DPI is 600×600, so it meets the minimum exactly."),
        ],
        children="Infants and small children get real latitude. A baby may be photographed lying on a plain white sheet or in a car seat covered with a white blanket, and for newborns the eyes do not have to be open. What is not allowed is anyone else appearing in the frame — no supporting hands, no arms, no chair back. Children over about one year are held to the same standards as adults.",
        process=[
            "Most first-time applicants apply in person at a passport acceptance facility (many post offices and libraries) using Form DS-11, and bring one printed 2×2 photo with them. Renewals by mail on Form DS-82 also need one printed photo.",
            "The State Department has been rolling out online renewal, which takes a digital upload instead of a print. The uploaded file is checked automatically for head size, background and sharpness, and a photo that fails is bounced immediately — which is a faster way to find out you have a problem than waiting for a mailed rejection.",
        ],
        rejections=[
            "Wearing glasses — still the single most common cause of rejection since the 2016 ban.",
            "Shadows on the face or cast onto the background behind the head.",
            "A photo taken with a phone at arm's length, which distorts the nose and cheeks.",
            "Head too large in the frame — European-style framing applied to a US photo.",
            "Visible filters, beauty smoothing or any digital alteration of your features.",
        ],
    ),
    _entry(
        "united-kingdom", "United Kingdom", "🇬🇧", 35, 45, bg="plain light-coloured (white, cream or light grey)",
        note="Used for the UK passport and most UK visa applications.",
        authority="HM Passport Office (GOV.UK)",
        authority_url="https://www.gov.uk/photos-for-passports",
        recency="the last month",
        intro=[
            "The UK uses the 35 × 45 mm international size on a plain light-coloured background. GOV.UK does not name a single required shade — white, cream and light grey are all acceptable — but it does require clear contrast between you and the background, which is the part that actually catches people out. Pale hair or a light top against a white wall gives the checker nothing to find an edge in.",
            "The detail that genuinely differs from most countries is recency. Where the international norm is six months, the UK asks for a photo taken within the last month. If you are digging out prints from an application earlier in the year, they are already too old.",
        ],
        rules=[
            ("Glasses", "Strongly discouraged. If you must wear them, the frames must not cover your eyes, there must be no glare on the lenses, and tinted or reflective lenses are refused outright. Removing them is the safer choice."),
            ("Expression", "Neutral with the mouth closed. The UK is explicit that you must not smile — a natural smile that is fine for a US photo will fail here."),
            ("Headwear", "Not permitted unless worn for religious or medical reasons, and your facial features from chin to crown must be clearly visible with no shadow cast by the covering."),
            ("Head size", "For printed photos, HM Passport Office specifies 29 mm to 34 mm from chin to crown. That is a tighter window than the 32–36 mm used across much of Europe, so a photo cut for a Schengen application will usually be over."),
            ("Digital uploads", "Applying online needs a digital photo at least 600 × 750 pixels, between 50 KB and 10 MB. The GOV.UK service runs an automatic quality check and tells you immediately if it fails, which is faster than finding out by post."),
        ],
        children="Children under 6 do not have to hold a neutral expression or look straight at the camera, and babies under 1 may have their eyes closed. For any child, nobody else may be visible in the shot — that includes a supporting hand — and a baby must not be holding a toy or using a dummy. Photographing a baby on a plain light-grey sheet from directly above is the usual way round this.",
        process=[
            "Almost everyone now applies online through GOV.UK and uploads a digital photo rather than posting prints. You can either upload a picture taken at home against a plain wall, or use a photo booth that gives you a digital code to type in.",
            "Paper applications still exist and need two identical printed photos, one of which must be signed on the back by someone who can confirm your identity. If you are applying for a first child passport by post, that countersignature is mandatory.",
        ],
        rejections=[
            "Too little contrast between you and the background — pale hair or a light top against a white wall.",
            "A photo more than a month old, which is stricter than most countries expect.",
            "A shadow behind the head from standing too close to the wall.",
            "Hair falling across the eyes, or a fringe that obscures the eyebrows.",
            "Glare on glasses, or frames covering any part of the eyes.",
        ],
    ),
    # France is the one 35×45 country that does NOT want a white background, which
    # is why it earns a page where Germany and Ireland did not: the single most
    # common thing a user arrives here already holding — a cut-out on white — is
    # automatically wrong for France, and no generic 35×45 page tells them so.
    _entry(
        # `bg` is interpolated mid-sentence ("set a {bg} backdrop"), so it has to
        # stay a noun phrase — the white-is-forbidden rule is carried by the intro
        # and the rules table, where it can be a sentence.
        "france", "France", "🇫🇷", 35, 45, bg="plain light grey or light blue (never white)",
        note="The 35×45 mm photo is used for the French passport, the CNI identity card and the driving licence.",
        authority="Service-Public / ANTS (Agence nationale des titres sécurisés)",
        authority_url="https://www.service-public.gouv.fr/particuliers/vosdroits/F10619",
        recency="the last 6 months",
        intro=[
            "France uses the same 35 × 45 mm frame as the rest of Europe and then breaks the rule everyone assumes is universal: a white background is explicitly forbidden. Service-Public states it flatly — «le fond blanc est interdit». The background must be a plain light grey or light blue, and a photo that would sail through a UK, German or Schengen visa application is refused here for the one thing most people never think to check.",
            "This catches out anyone reusing a photo, and it catches out anyone who has just removed a background, because a transparent cut-out exported straight to a print or a JPG almost always lands on white. If you are preparing a French photo, the background is the setting to change first, not last.",
            "There is a second requirement worth knowing before you spend any time on this: for the passport itself, the photo must come from a photographer or a photo booth approved by ANTS. A photo you produce at home does not satisfy that rule, however precisely it matches the spec.",
        ],
        rules=[
            ("Background", "Plain light grey or light blue. White is forbidden outright, and so is any pattern, texture or visible shadow. This is the rule that most distinguishes France from its neighbours, and the most common reason a reused photo fails."),
            ("Approved source", "For a passport, CNI or driving licence, the photo must come from an ANTS-approved photographer or booth — the ones marked with the official blue pictogram. An approved source can also issue a digital ePhoto code you enter into your ANTS application instead of handing over prints."),
            ("Glasses", "Permitted, unlike in the United States or Canada. The frames must be thin and must not cover the eyes, and the lenses must not be tinted, coloured or reflective. Glare on the lens is still a refusal."),
            ("Expression", "Neutral with the mouth closed, head straight, facing the camera, both eyes open. A smile that would be acceptable on a US photo fails here."),
            ("Headwear", "Not permitted. The head must be bare — «la tête doit être nue» — which explicitly includes hats, headscarves and even hairbands."),
            ("Head size", "32 to 36 mm from chin to crown, about 70–80% of the frame height — the standard European window, so the framing of a Schengen photo is right even when its background is not."),
        ],
        children="A child needs their own photo meeting the same rules, and nobody else may appear in the frame — no supporting hands, no parent holding the child up. For babies, the practical approach is to lay the child on a plain light grey or light blue sheet and shoot from directly above, which gets the even background and the head-on angle at once. Children are not exempt from the neutral expression in the way UK rules exempt under-6s, though in practice a sleeping infant's closed eyes are tolerated. A minor's application is made by a parent or guardian, who must attend with them.",
        process=[
            "A passport application starts as a pre-demande on the ANTS website, but it cannot be finished there: you must book an appointment at a mairie equipped with a biometric station to give fingerprints in person. Not every town hall has one, and in cities the wait for a slot is often the longest part of the process.",
            "At the photo step ANTS asks whether you have an ePhoto code. If you do, you type it in and the photo is pulled from ANTS's own servers — no prints change hands. If you do not, you bring a printed photo to the appointment. The code is issued by approved booths and by a small number of approved online services, and it expires after six months like the photo itself.",
            "Where this tool genuinely helps is everything that is not the passport: French administrative forms, school and workplace ID, visa applications abroad that ask for a French-format photo, and preparing a compliant image so you know what you are getting before you pay at a booth. For the passport, CNI or driving licence, use an approved source — we would rather say so than have your appointment wasted.",
        ],
        rejections=[
            "A white background — the single most common French rejection, and the one that surprises people who have applied elsewhere.",
            "A photo not taken by an ANTS-approved photographer or booth, for a passport, CNI or driving licence.",
            "Glare on glasses, tinted lenses, or thick frames covering part of the eyes.",
            "Any headwear at all, including a hairband, since the head must be bare.",
            "A visible shadow on the background from standing too close to the wall.",
            "An ePhoto code more than six months old, which ANTS invalidates automatically.",
        ],
    ),
    _entry(
        "canada", "Canada", "🇨🇦", 50, 70,
        note="Canada uses a larger 50×70 mm photo for passports.",
        authority="Passport Program, Immigration, Refugees and Citizenship Canada (IRCC)",
        authority_url="https://www.canada.ca/en/immigration-refugees-citizenship/services/canadian-passports/photos.html",
        recency="the last 6 months",
        intro=[
            "Canada uses 50 × 70 mm — a distinctly larger photo than the 35 × 45 mm European standard, and larger again than the US square. Photos cut for any other country will not fit the Canadian frame, and the passport office does not accept trimmed-down substitutes.",
            "There is one requirement here that no online tool can satisfy on its own, and it is worth knowing before you start: Canadian passport photos must be taken by a commercial photographer, and the back of one of the two prints must carry the studio's name and address along with the date the photo was taken. A photo you produce entirely at home does not meet that rule.",
        ],
        rules=[
            ("Copies", "Two identical prints are required. One is left blank; the other must be annotated on the back by the photographer with the studio name, the full address, and the date the photo was taken."),
            ("Photographer", "The photo must come from a commercial establishment. This is the requirement that most distinguishes Canada — self-taken photos, however technically perfect, do not satisfy it for a passport application."),
            ("Glasses", "Not permitted. Canada removed the glasses allowance and now asks for them to be taken off, with an exception only for documented medical necessity supported by a note from a doctor — the same position as the United States."),
            ("Expression", "Neutral, with the mouth closed and both eyes open and looking straight at the camera. No tilting or rotating the head."),
            ("Head size", "31 mm to 36 mm measured from the chin to the natural top of the head — the skull, not the top of your hair. The overall photo is larger than a European one but the head is a similar size, so there is more margin around it."),
        ],
        children="Newborns and infants may have their eyes partly closed and do not need a neutral expression, but the rest of the rules still apply — including the commercial-photographer requirement. No other person may appear in the photo, so the usual approach is to lay the baby on a plain white sheet. A child's photo still needs the studio annotation on the back.",
        process=[
            "Applications are made on paper and submitted in person at a Service Canada or passport office, or by mail. Both photos go in with the form, and the guarantor who signs your application must also sign the back of one photo.",
            "Because the annotation is checked, this is a case where the sensible use of an online tool is preparation rather than production: get your framing, background and head position right at home so you know exactly what you want, then have a studio shoot and stamp the final prints.",
        ],
        rejections=[
            "Missing the photographer's name, address and date on the back of the print.",
            "Head measuring outside the 31–36 mm chin-to-crown window.",
            "Photos printed at the wrong size — 35×45 mm brought over from a European application.",
            "Any retouching, including removing blemishes or softening skin.",
            "Wearing glasses, which are no longer accepted without a documented medical reason.",
        ],
    ),
    _entry(
        "australia", "Australia", "🇦🇺", 35, 45, bg="plain white or light grey",
        note="Australian passport photos use a plain white or light grey background.",
        authority="Australian Passport Office (Department of Foreign Affairs and Trade)",
        authority_url="https://www.passports.gov.au/getting-passport-how-it-works/photo-guidelines",
        recency="the last 6 months",
        intro=[
            "Australia uses the 35 × 45 mm international size on a plain white or light grey background. The Australian Passport Office is noticeably strict about glasses: its guidance asks you to remove them for the photo, without the medical-exception carve-out that some other countries offer.",
            "Two identical prints are required for a paper application, and one of them has to be endorsed on the back by your guarantor — the person who confirms your identity on the form. That endorsement is part of the application, not an optional extra.",
        ],
        rules=[
            ("Glasses", "Remove them. The APO asks for photos without glasses and a prescription on its own is not a reason to keep them on; only a medical reason you cannot work around is, and then the lenses must be untinted."),
            ("Copies", "Two identical prints. Your guarantor writes a declaration on the back of one confirming it is a true likeness of you, and signs it."),
            ("Expression", "Neutral, mouth closed, eyes open and looking straight at the lens. No smiling."),
            ("Headwear", "Only for religious or medical reasons, and the covering must not cast a shadow or obscure any part of the face from the bottom of the chin to the top of the forehead."),
            ("Head size", "Chin to crown between 32 mm and 36 mm, centred in the frame with roughly even space on both sides."),
        ],
        children="Children need their own passport and their own photos from birth. Babies may have their eyes closed and their mouth open, and can be photographed lying on a plain white or light grey sheet. No other person, hand or arm may be visible. A child's photos also need the guarantor endorsement on the back of one print.",
        process=[
            "Australian passport applications are completed online but lodged in person at a participating Australia Post outlet or a passport office, where you hand over the printed photos and have your identity checked.",
            "Australia Post outlets offer a photo service at the counter, and using it removes any argument about compliance — but preparing your own framing first is still useful, particularly for children, where getting a usable shot at a counter under time pressure is the hard part.",
        ],
        rejections=[
            "Wearing glasses, which the APO refuses without a medical exemption.",
            "A missing or incomplete guarantor endorsement on the back of the photo.",
            "Uneven lighting leaving one side of the face brighter than the other.",
            "Photos older than six months, or an appearance that no longer matches.",
            "A background that is patterned, coloured, or shows a visible wall edge.",
        ],
    ),
    _entry(
        "india", "India", "🇮🇳", 35, 45,
        note="Common size for the Indian passport (Passport Seva) application.",
        authority="Passport Seva, Ministry of External Affairs",
        authority_url="https://www.passportindia.gov.in/",
        recency="the last 6 months",
        intro=[
            "There is an important thing to know before you spend time on an Indian passport photo: for most applicants, you do not supply one. When you attend your appointment at a Passport Seva Kendra (PSK) or Post Office Passport Seva Kendra, your photograph and fingerprints are captured on site by the officer at Counter A. Bringing photos is not part of the standard process.",
            "Photos are still needed in specific cases — applications submitted on the manual form where an appointment is not involved, certain minor and tatkaal categories, and a range of adjacent documents (PAN, visa applications to other countries, university and government forms) that use the same 35 × 45 mm format on a white background. Those are the cases these guidelines cover.",
        ],
        rules=[
            ("When photos are needed", "Manual/paper applications and some minor categories require photos affixed to the form. Standard online applications processed at a PSK do not — the photo is taken there."),
            ("Background", "Plain white, with the face fully visible and evenly lit. A light grey background is generally accepted for adjacent documents but white is the safe default."),
            ("Glasses", "Permitted if your eyes are clearly visible with no glare and no tint. Removing them avoids the most common objection."),
            ("Expression", "Neutral, facing the camera directly, with both eyes open and the mouth closed."),
            ("Minors", "For a minor's application, the photo requirements are applied to the child, and one parent's details are recorded on the form. The 4.5 × 3.5 cm size is standard across minor categories."),
        ],
        children="There is one clear exception to the rule that you do not bring photos: children under four. Passport Seva asks for a recent 4.5 × 3.5 cm colour photograph on a white background to be carried to the appointment for them, because capturing a small child reliably at the counter is not practical. Older minors still attend in person and are photographed there. In either case nobody else may appear in the frame, and a parent's documents are verified separately from the photo itself.",
        process=[
            "The normal route is to register on the Passport Seva portal, fill the form online, pay, and book an appointment at your nearest PSK. Everything biometric — photograph, fingerprints, signature — happens at the centre.",
            "Because of that, the most useful thing an online tool does for an Indian applicant is prepare 35 × 45 mm photos for the surrounding paperwork: visa applications to other countries, PAN and bank forms, university admissions and employment records, which do all need supplied prints.",
        ],
        rejections=[
            "Bringing photos to a PSK appointment for an adult, where they are not used at all.",
            "A background that is off-white, cream or shows shadow gradients.",
            "Photos smaller than 35 × 45 mm, trimmed down from a larger print.",
            "Low-resolution prints where the face is soft or pixelated.",
            "Hair or a dupatta covering the hairline or the edges of the face.",
        ],
    ),
    _entry(
        "schengen-visa", "Schengen Visa (EU)", "🇪🇺", 35, 45,
        note="Accepted across Schengen-area visa and residence applications.",
        authority="Consulate of your destination country (standard set by ICAO 9303)",
        authority_url="https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/visa-policy_en",
        recency="the last 6 months",
        intro=[
            "A Schengen visa photo follows the ICAO 9303 standard that underpins machine-readable travel documents across the whole area: 35 × 45 mm, a light and uniform background, and the face occupying roughly 70–80% of the frame. Because the standard is shared, one compliant photo works whether you are applying through the French, German, Spanish or Portuguese consulate.",
            "Where consulates differ is in the background shade they prefer. Light grey is the most widely accepted and the safest single choice; some accept off-white or pale blue. A pure white background is occasionally refused because it leaves no contrast against light hair or clothing, which is the opposite of the US requirement.",
        ],
        rules=[
            ("Which consulate", "You apply to the country that is your main destination, or your first point of entry if the trip is evenly split. That consulate's published photo sheet is the one that governs your application."),
            ("Glasses", "Permitted only if the eyes are fully visible — no tint, no reflection, and frames that do not cross the eyes. Many consulates simply advise removing them."),
            ("Expression", "Neutral, mouth closed, looking directly at the camera. The photo has to work as a biometric template, which is why expression is enforced closely."),
            ("Head size", "32–36 mm from chin to crown, roughly 70–80% of the frame height, centred with the eyes on a horizontal line about halfway up."),
            ("Biometrics", "Fingerprints are collected at your appointment and are valid across applications for 59 months, but the photo must be recent for every application."),
        ],
        children="Children need their own visa application and their own photo, including infants. Under-12s are exempt from fingerprinting but not from the photo requirement. Babies may be photographed lying on a plain light-grey sheet, with the eyes open where possible and no other person in the frame — a hand supporting the head is the most common reason an infant photo is sent back.",
        process=[
            "Applications are lodged at the consulate or, increasingly, at an outsourced visa centre such as VFS Global or TLScontact. The centre will usually check your photo at the counter and sell you a compliant one on the spot if it fails.",
            "Arriving with a photo you know is compliant is worth doing anyway: the counter check is quick and the fallback booth is expensive, and a photo rejected there means paying twice on a day you have already taken off work.",
        ],
        rejections=[
            "A background that is too dark, patterned, or shows a visible shadow.",
            "Head too small in the frame — the most common single failure against ICAO framing.",
            "Reflections on glasses under the consulate's own lighting check.",
            "A photo reused from a previous application and now older than six months.",
            "Prints on ordinary paper rather than photographic stock, which read as soft.",
        ],
    ),
    _entry(
        "portugal", "Portugal", "🇵🇹", 35, 45,
        note="Portugal uses the EU-standard 35×45 mm size for passport photos.",
        authority="Instituto dos Registos e do Notariado (IRN)",
        authority_url="https://www.irn.justica.gov.pt/",
        recency="the last 6 months",
        intro=[
            "Portugal issues both the Cartão de Cidadão and the Passaporte Eletrónico Português (PEP) through the IRN, and for both of them the photograph is normally captured at the counter when you attend your appointment at a Loja do Cidadão or Conservatória. As in India, the standard route does not ask you to bring prints.",
            "Supplied photos still matter for everything around those documents: Schengen and third-country visa applications, residence paperwork, driving-licence and IMT forms, university enrolment, and renewals handled through a consulate abroad. All of them use the same EU-standard 35 × 45 mm format, which is why preparing one good photo covers most of what you will be asked for.",
        ],
        rules=[
            ("At the counter", "For the Cartão de Cidadão and the passport, the photo and fingerprints are taken on site by the IRN operator. What you wear and how your hair sits still matters — you just do not supply the file."),
            ("Consular renewals", "Portuguese citizens renewing abroad through a consulate are often asked for supplied photos, and those must meet the 35 × 45 mm ICAO specification."),
            ("Glasses", "Permitted if the eyes are clearly visible without glare or tint. Removing them is the safer option, particularly under the strong counter lighting used at a Loja do Cidadão."),
            ("Expression", "Neutral, mouth closed, facing the camera. The image feeds a biometric chip, so expression and head angle are checked automatically."),
            ("Head size", "32–36 mm from chin to crown, filling roughly 70–80% of the frame — the same ICAO framing used across the Schengen area."),
        ],
        children="Children need their own Cartão de Cidadão and their own passport, and must attend the appointment in person with a parent or legal guardian, who signs the application. The photo is captured at the counter for them too. Where a consulate asks for supplied prints for a minor, infants may have their eyes closed and can be photographed against a plain light background with nobody else in frame.",
        process=[
            "Appointments are booked through the IRN or the Loja do Cidadão network, and the whole capture — photo, fingerprints, signature — happens in a few minutes at the desk. The document is then posted to you or collected.",
            "For everything that does need supplied prints, a 35 × 45 mm export at 300 DPI (413 × 531 pixels) is the right file. The 6×4 inch sheet option tiles several copies onto one standard print, which any Portuguese pharmacy or photo counter can produce cheaply.",
        ],
        rejections=[
            "Bringing prints to a Cartão de Cidadão appointment, where they are not used.",
            "For consular applications, photos that have drifted past six months old.",
            "Backgrounds with visible texture — a painted wall with a rough finish is a common culprit.",
            "Glare on glasses under the counter's own lighting.",
            "Hair covering the eyebrows or the outline of the face.",
        ],
    ),
    _entry(
        "china", "China", "🇨🇳", 33, 48,
        note="China visa photos use a 33×48 mm size on a white background.",
        authority="Chinese Embassy / Consulate-General (visa); National Immigration Administration (passports)",
        authority_url="http://cs.mfa.gov.cn/",
        recency="the last 6 months",
        intro=[
            "China uses 33 × 48 mm — a size shared with almost no other country, and one that no European or American photo can be trimmed to fit. On top of the outer dimensions, the Chinese visa specification constrains the head itself: 15–22 mm wide and 28–33 mm from chin to crown, on a pure white background.",
            "The rules are also enforced more literally than most. Chinese visa centres run an automated check against the specification and refuse photos that miss it, rather than exercising judgement — which makes this one of the few applications where getting the numbers exactly right genuinely matters more than the photo looking good.",
        ],
        rules=[
            ("Head dimensions", "Head width 15–22 mm and height 28–33 mm, measured within the 33 × 48 mm frame. These are checked, not estimated."),
            ("Glasses", "Not permitted for Chinese visa photos, and enforced since 2016 across every visa category — tourist, business and work alike. A medical exception exists but requires a doctor's letter submitted with the application, so for practical purposes take them off."),
            ("Background", "Pure white, with no shadow and no gradient. Unlike the Schengen preference for light grey, China wants white and refuses off-white."),
            ("Expression", "Neutral, mouth closed, ears visible where hair permits, and the face square to the camera with no tilt."),
            ("Digital uploads", "The online visa application takes a digital file, typically 354 × 472 to 420 × 560 pixels, in JPEG and under 100 KB — a much tighter file-size ceiling than most systems impose."),
        ],
        children="Children of any age, including newborns, need their own visa and their own photo meeting the same 33 × 48 mm specification — China grants very little latitude here compared with the UK or Australia. No other person may appear in the frame, and the head-size rules still apply, which makes a baby's photo genuinely difficult. Photographing from directly above onto a white sheet, then cropping to the required proportions, is the usual approach.",
        process=[
            "Most visa applications go through a Chinese Visa Application Service Centre (CVASC) rather than the embassy directly. You complete the form online, print it, and attend in person with your photo.",
            "The centre checks the photo against the specification before accepting the file, and has a booth on site for photos that fail. Because the tolerance is narrow and the check is mechanical, arriving with a photo cropped to the exact millimetre figures is worth the effort.",
        ],
        rejections=[
            "Wearing glasses — refused outright for visa photos.",
            "Head outside the 15–22 mm wide, 28–33 mm tall window.",
            "An off-white or light grey background where pure white is required.",
            "A digital file over the 100 KB limit for the online application.",
            "Photos cropped down from the 35 × 45 mm European size, which never fits.",
        ],
    ),
    _entry(
        "brazil", "Brazil", "🇧🇷", 50, 70,
        note="Brazil commonly uses a 5×7 cm (50×70 mm) photo.",
        authority="Polícia Federal (passport); Detran and civil registry offices (other documents)",
        authority_url="https://www.gov.br/pf/pt-br/assuntos/passaporte",
        recency="the last 6 months",
        intro=[
            "Brazil is the country where the answer depends most on which document you are applying for. For the passport, you do not supply a photo at all: the Polícia Federal photographs you during your appointment, along with fingerprints and signature. Turning up with prints is a wasted trip to the photo shop.",
            "Supplied photos are used almost everywhere else, and the two sizes that matter are 5 × 7 cm (50 × 70 mm), covered here, and the classic 3 × 4 cm format that Brazilian paperwork has used for decades — carteira de trabalho, school and university enrolment, employment records, and many Detran and registry forms.",
        ],
        rules=[
            ("Passport", "No photo is supplied. The Polícia Federal captures it at your agendamento, so the useful preparation is your appearance and clothing, not a print."),
            ("3 × 4 cm", "The traditional Brazilian document photo, used across employment, education and registry paperwork. It is a different aspect ratio from 5 × 7 and cannot be cropped from it without redoing the framing."),
            ("Background", "Plain white for most official uses. Some registry offices still accept light grey; white is the safe default."),
            ("Glasses", "Generally permitted where the eyes are clearly visible without glare, though individual offices vary. Removing them avoids the argument."),
            ("Expression", "Neutral, facing forward, both eyes open, mouth closed, with the ears visible where the hairstyle allows."),
        ],
        children="This is the one case where you do bring a photo to a Brazilian passport appointment. For a child under five, the Polícia Federal asks for a printed 5 × 7 cm colour photo on a white background, taken within the last six months and printed on photographic paper — specifically 5 × 7, not the 3 × 4 used elsewhere in Brazilian paperwork. Anyone aged five or over is photographed at the counter. A child's application also requires attendance with both parents or a legal guardian, and nobody else may appear in the frame.",
        process=[
            "Passport applications start on the gov.br portal: fill the form, pay the GRU fee, and book an appointment at a Polícia Federal unit. Everything biometric happens at that appointment.",
            "For the surrounding paperwork, exporting both a 5 × 7 cm and a 3 × 4 cm version from the same portrait covers nearly every Brazilian form you are likely to meet, and the 6×4 inch print sheet tiles copies for a photo counter.",
        ],
        rejections=[
            "Bringing photos to a Polícia Federal appointment for anyone aged five or over, where they are not used.",
            "Bringing a 3 × 4 cm photo for a child under five, where 5 × 7 cm is required.",
            "Supplying 5 × 7 cm where another Brazilian form specifically asks for 3 × 4 cm.",
            "Backgrounds that are cream or grey where the office requires white.",
            "Prints on plain paper rather than photographic stock.",
            "Photos older than six months, or predating a significant change in appearance.",
        ],
    ),
]

COUNTRIES_BY_SLUG = {c["slug"]: c for c in COUNTRIES}

# Retired per-country pages (identical 35×45 mm / plain-white spec, no unique
# content). They 301 to the main passport tool so any link equity and stray index
# entries consolidate onto a page that can actually rank, instead of 404-ing.
FOLDED_COUNTRY_SLUGS = frozenset({
    # France came back (2026-08): not as the 35×45/white near-duplicate that was
    # folded, but on the strength of a spec that genuinely differs — white
    # backgrounds are forbidden — plus the ANTS approved-source rule. It also had
    # live search demand while folded ("french passport size photo").
    "germany", "italy", "ireland", "netherlands", "japan",
    "new-zealand", "south-africa", "singapore", "philippines",
    "south-korea", "nigeria", "pakistan",
})


def size_label(c):
    """Human size string, e.g. '2 × 2 in (51 × 51 mm)' or '35 × 45 mm'."""
    metric = f"{c['w_mm']} × {c['h_mm']} mm"
    return f"{c['imperial']} ({metric})" if c["imperial"] else metric


def country_faqs(c):
    """Generate the FAQ list for a country page from its spec.

    The last two answers are drawn from the country's own editorial content
    rather than the shared spec — an FAQ block that reads identically on nine
    pages is exactly the duplication these pages are trying to escape, and
    FAQPage structured data is compared across a site.
    """
    name = c["name"]
    return [
        {"q": f"What size is a {name} passport photo?",
         "a": f"A {name} passport photo is {size_label(c)}, which is {c['w_px']} × {c['h_px']} pixels at 300 DPI."},
        {"q": f"What background should a {name} passport photo have?",
         "a": f"It should be a {c['bg']} background with even lighting and no shadows. This tool removes your original background and replaces it automatically."},
        {"q": f"How big should the head be in a {name} passport photo?",
         "a": f"The head should be {c['head']}"},
        {"q": f"Can I wear glasses in a {name} passport photo?",
         "a": next((r["text"] for r in c["rules"] if r["label"] == "Glasses"),
                   "Check the current guidance from " + c["authority"] + " before your application.")},
        {"q": f"Why do {name} passport photos get rejected?",
         "a": "The most common reasons are: " + "; ".join(r.rstrip(".").lower() for r in c["rejections"][:3]) + "."},
        {"q": f"Can I print my {name} passport photo at home?",
         "a": "Yes. Use the 6×4 inch print-sheet option to tile several copies onto a standard print you can order at any pharmacy or photo kiosk."},
    ]
