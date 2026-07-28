"""Tests for the remover views and SEO endpoints."""
import json
import re
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation
from django.utils.html import escape

from remover.context_processors import CHAIN_EXCLUDED, TOOL_ACCENTS, TOOL_NAV
from remover.guides import GUIDES
from remover.translations import JS_UI
from remover.views import (
    SHELL_ASSETS,
    SHELL_PAGES,
    SITEMAP_PATHS,
    TOOL_PATHS,
    TRANSLATED_PATHS,
    USE_CASES,
    is_translated_path,
)


class PageTests(SimpleTestCase):
    """The app is stateless, so SimpleTestCase (no DB) is sufficient."""

    def test_index_renders(self):
        response = self.client.get(reverse("remover:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remover/index.html")
        self.assertContains(response, "Remove Image Backgrounds")

    def test_index_has_seo_tags(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, 'name="twitter:card"')
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, 'rel="canonical"')

    def test_index_rejects_post(self):
        response = self.client.post(reverse("remover:index"))
        self.assertEqual(response.status_code, 405)

    def test_index_has_landing_content(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, "How it works")
        self.assertContains(response, "Drag &amp; drop your images")
        self.assertContains(response, "live demo, nothing uploaded")

    def test_index_sets_security_headers(self):
        response = self.client.get(reverse("remover:index"))
        self.assertIn("Content-Security-Policy", response)
        self.assertIn("Permissions-Policy", response)
        self.assertIn("wasm-unsafe-eval", response["Content-Security-Policy"])

    def test_csp_allows_the_hosts_adsense_actually_loads(self):
        """A blocked ad host is silent in tests and throws in the browser.

        adtrafficquality.google (Sodar) was missing, so every ad-bearing page
        raised an uncaught rejection and Google's invalid-traffic check could not
        run — invisible server-side, which is why this is pinned here.
        """
        csp = self.client.get(reverse("remover:index"))["Content-Security-Policy"]
        directives = dict(
            (d.split(" ", 1) + [""])[:2] for d in (x.strip() for x in csp.split(";")) if d
        )
        for host in ("https://pagead2.googlesyndication.com", "https://*.adtrafficquality.google"):
            with self.subTest(host=host):
                self.assertIn(host, directives["script-src"])
        self.assertIn("https://*.adtrafficquality.google", directives["frame-src"])


class UseCaseTests(SimpleTestCase):
    def test_every_use_case_page_renders(self):
        for case in USE_CASES:
            url = reverse("remover:use_case", args=[case["slug"]])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, case["h1"])
            self.assertContains(response, case["description"])
            self.assertContains(response, "BreadcrumbList")

    def test_unknown_slug_is_404(self):
        response = self.client.get(reverse("remover:use_case", args=["not-a-real-page"]))
        self.assertEqual(response.status_code, 404)

    def test_homepage_links_to_use_cases(self):
        response = self.client.get(reverse("remover:index"))
        for case in USE_CASES:
            self.assertContains(response, reverse("remover:use_case", args=[case["slug"]]))

    def test_sitemap_lists_use_cases(self):
        response = self.client.get(reverse("remover:sitemap"))
        for case in USE_CASES:
            self.assertContains(response, f"/remove-background/{case['slug']}/")

    def test_footer_links_site_wide(self):
        # The context processor should surface use-case links on every page.
        response = self.client.get(reverse("remover:convert"))
        for case in USE_CASES:
            self.assertContains(response, reverse("remover:use_case", args=[case["slug"]]))


class ConvertPageTests(SimpleTestCase):
    def test_convert_renders(self):
        response = self.client.get(reverse("remover:convert"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remover/convert.html")
        self.assertContains(response, "Convert Images")
        self.assertContains(response, "convert-dropzone")

    def test_convert_has_format_options(self):
        response = self.client.get(reverse("remover:convert"))
        self.assertContains(response, 'data-format="image/webp"')
        self.assertContains(response, "convert-card-template")

    def test_tool_nav_links_present(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, reverse("remover:convert"))
        self.assertContains(response, "Remove BG")


class NewToolTests(SimpleTestCase):
    def test_passport_renders(self):
        response = self.client.get(reverse("remover:passport"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remover/passport.html")
        self.assertContains(response, "pp-dropzone")
        self.assertContains(response, "Passport")

    def test_upscale_is_back(self):
        # The AI upscaler was removed (super-resolution froze the tab) and the
        # URL 301'd home; it has since returned as a safe Lanczos resampler, so
        # the indexed URL serves a real page again.
        response = self.client.get("/upscale/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remover/upscale.html")

    def test_new_tools_in_sitemap(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "/passport-photo/")
        self.assertContains(response, "/upscale/")

    def test_new_tools_in_nav(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, reverse("remover:passport"))


class EcommerceBlurTests(SimpleTestCase):
    def test_ecommerce_renders(self):
        response = self.client.get(reverse("remover:ecommerce"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ec-dropzone")
        self.assertContains(response, "Amazon")
        self.assertContains(response, "FAQPage")

    def test_blur_renders(self):
        response = self.client.get(reverse("remover:blur"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bl-dropzone")
        self.assertContains(response, "portrait")

    def test_in_sitemap_and_nav(self):
        sitemap = self.client.get(reverse("remover:sitemap"))
        self.assertContains(sitemap, "/ecommerce/")
        self.assertContains(sitemap, "/blur-background/")
        index = self.client.get(reverse("remover:index"))
        self.assertContains(index, reverse("remover:ecommerce"))
        self.assertContains(index, reverse("remover:blur"))

    def test_both_are_isolated(self):
        for name in ("ecommerce", "blur"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertEqual(response["Cross-Origin-Embedder-Policy"], "credentialless", name)


class StatsCounterTests(SimpleTestCase):
    def test_disabled_when_upstash_unset(self):
        # No Upstash env in tests → counter reports disabled with no number.
        get = self.client.get(reverse("remover:stats"))
        self.assertEqual(get.status_code, 200)
        self.assertJSONEqual(get.content, {"enabled": False, "count": None})

    def test_post_increment_disabled_gracefully(self):
        post = self.client.post(
            reverse("remover:stats"), data='{"n": 3}', content_type="application/json"
        )
        self.assertEqual(post.status_code, 200)
        self.assertJSONEqual(post.content, {"enabled": False, "count": None})

    def test_home_has_social_proof_placeholder(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, 'id="social-proof"')

    # The stats POST is the only public, unauthenticated write endpoint, so it
    # carries a per-IP fixed-window rate limit (Upstash-backed). These tests
    # enable Upstash via override_settings and mock the REST helper so nothing
    # touches the network.
    _UPSTASH = dict(
        UPSTASH_REDIS_REST_URL="https://example.upstash.io",
        UPSTASH_REDIS_REST_TOKEN="test-token",
        STATS_KEY="clearbg:processed",
    )

    @override_settings(**_UPSTASH)
    def test_post_over_rate_limit_is_rejected_without_incrementing(self):
        def fake(path):
            if path.startswith("incr/") and ":rl:" in path:
                return 61  # over STATS_POST_LIMIT (60)
            return 0

        with mock.patch("remover.views._upstash", side_effect=fake) as m:
            post = self.client.post(
                reverse("remover:stats"),
                data='{"n": 3, "event": "processed", "tool": "crop"}',
                content_type="application/json",
            )
        self.assertEqual(post.status_code, 429)
        # The vanity counter must NOT have been touched for a rejected request.
        self.assertFalse(
            any(str(c.args[0]).startswith("incrby/") for c in m.call_args_list),
            "a rate-limited POST still incremented the counter",
        )

    @override_settings(**_UPSTASH)
    def test_post_under_rate_limit_increments(self):
        def fake(path):
            if path.startswith("incr/") and ":rl:" in path:
                return 1  # first hit of the window → allowed
            return 7      # incrby / get both report a live count

        with mock.patch("remover.views._upstash", side_effect=fake):
            post = self.client.post(
                reverse("remover:stats"),
                data='{"n": 3, "event": "processed"}',
                content_type="application/json",
            )
        self.assertEqual(post.status_code, 200)
        self.assertJSONEqual(post.content, {"enabled": True, "count": 7})

    def test_client_ip_reads_clean_forwarded_header(self):
        from django.test import RequestFactory

        from remover.views import _client_ip

        req = RequestFactory().post(
            "/api/stats/", HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.1"
        )
        self.assertEqual(_client_ip(req), "1.2.3.4")

    def test_client_ip_rejects_injection_attempt(self):
        # A spoofed X-Forwarded-For must never inject extra Upstash path
        # segments — a non-IP value collapses to a single shared bucket.
        from django.test import RequestFactory

        from remover.views import _client_ip

        req = RequestFactory().post(
            "/api/stats/", HTTP_X_FORWARDED_FOR="1.2.3.4/flushall"
        )
        ip = _client_ip(req)
        self.assertNotIn("/", ip)
        self.assertEqual(ip, "unknown")


class PassportCountryTests(SimpleTestCase):
    def test_every_country_page_renders(self):
        from remover.passport_data import COUNTRIES
        for c in COUNTRIES:
            url = reverse("remover:passport_country", args=[c["slug"]])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, c["slug"])
            self.assertContains(response, c["name"])
            self.assertContains(response, f"{c['w_px']} × {c['h_px']} px")
            self.assertContains(response, "FAQPage")

    def test_unknown_country_is_404(self):
        response = self.client.get(reverse("remover:passport_country", args=["atlantis"]))
        self.assertEqual(response.status_code, 404)

    def test_folded_countries_redirect_to_the_hub(self):
        # Retired near-duplicate pages 301 to the main tool (not 404) so any
        # link equity / stale index entries consolidate onto a rankable page.
        from remover.passport_data import FOLDED_COUNTRY_SLUGS
        hub = reverse("remover:passport")
        for slug in FOLDED_COUNTRY_SLUGS:
            response = self.client.get(reverse("remover:passport_country", args=[slug]))
            self.assertRedirects(response, hub, status_code=301, target_status_code=200)

    def test_folded_countries_are_not_in_the_sitemap(self):
        from remover.passport_data import FOLDED_COUNTRY_SLUGS
        response = self.client.get(reverse("remover:sitemap"))
        for slug in FOLDED_COUNTRY_SLUGS:
            self.assertNotContains(response, f"/passport-photo/{slug}/")

    def test_country_pages_in_sitemap(self):
        from remover.passport_data import COUNTRIES
        response = self.client.get(reverse("remover:sitemap"))
        for c in COUNTRIES:
            self.assertContains(response, f"/passport-photo/{c['slug']}/")

    def test_passport_tool_links_countries(self):
        response = self.client.get(reverse("remover:passport"))
        self.assertContains(response, reverse("remover:passport_country", args=["united-states"]))


class PassportContentTests(SimpleTestCase):
    """These pages have to earn their place, not just interpolate a spec.

    Built from the shared table alone they were ~124 unique words each and 79%
    identical to one another — indistinguishable from scaled content, and the
    reason most of them sat in "Discovered — currently not indexed". The floors
    below are what separates a page worth indexing from a template fill.
    """

    def _country_paths(self):
        from remover.passport_data import COUNTRIES
        return [(c, reverse("remover:passport_country", args=[c["slug"]])) for c in COUNTRIES]

    @staticmethod
    def _visible_text(html):
        html = re.sub(r"(?is)<(script|style|svg|noscript|nav|footer|header).*?</\1>", " ", html)
        return " ".join(re.sub(r"(?s)<[^>]+>", " ", html).split())

    def test_every_country_carries_its_own_editorial_content(self):
        for c, _ in self._country_paths():
            with self.subTest(country=c["slug"]):
                self.assertTrue(c["intro"], "no intro paragraphs")
                self.assertGreaterEqual(len(c["rules"]), 4, "fewer than 4 specific rules")
                self.assertGreaterEqual(len(c["rejections"]), 4, "fewer than 4 rejection reasons")
                self.assertTrue(c["children"], "no children/infant guidance")
                self.assertTrue(c["process"], "no application-process copy")
                self.assertTrue(c["authority"] and c["authority_url"], "no cited authority")

    def test_pages_clear_a_real_word_count(self):
        for c, url in self._country_paths():
            with self.subTest(country=c["slug"]):
                words = len(self._visible_text(self.client.get(url).content.decode()).split())
                self.assertGreater(words, 900, f"{c['slug']}: only {words} visible words")

    def test_sibling_pages_are_not_near_duplicates(self):
        """The measurement that drove this work: pairwise similarity across siblings.

        Two country pages sharing the same 35×45 mm spec will always overlap on the
        shared chrome and the spec table; what must differ is the prose. 65% is set
        above the ~56% the pages currently measure and well below the 79% they
        started at, so it catches a regression without being brittle.
        """
        import difflib
        import itertools

        pages = {
            c["slug"]: self._visible_text(self.client.get(url).content.decode())
            for c, url in self._country_paths()
        }
        for a, b in itertools.combinations(sorted(pages), 2):
            ratio = difflib.SequenceMatcher(None, pages[a], pages[b]).ratio()
            with self.subTest(pair=f"{a}/{b}"):
                self.assertLess(ratio, 0.65, f"{a} and {b} are {ratio:.0%} identical")

    def test_country_specific_facts_reach_the_page(self):
        """Spot-check that the differentiating detail actually renders."""
        cases = {
            "canada": "commercial photographer",       # Canada's studio-annotation rule
            "united-states": "1 November 2016",        # the US glasses ban
            "united-kingdom": "light grey or cream",   # not the usual white
            "china": "15–22 mm",                  # China's head-width window
            "india": "Passport Seva Kendra",           # photo taken at the centre
            "brazil": "Polícia Federal",          # photo taken at the appointment
        }
        for slug, needle in cases.items():
            with self.subTest(country=slug):
                url = reverse("remover:passport_country", args=[slug])
                self.assertContains(self.client.get(url), needle)

    def test_every_page_cites_its_official_authority(self):
        for c, url in self._country_paths():
            with self.subTest(country=c["slug"]):
                response = self.client.get(url)
                self.assertContains(response, c["authority_url"])
                # Outbound links to government sites carry no endorsement weight.
                self.assertContains(response, 'rel="nofollow noopener"')


class ThinPageTests(SimpleTestCase):
    """No page may go back to being 130 words of copy around an interface.

    The tool and use-case pages each carried ~65–190 unique words, which is what
    a search or ad-network quality review reads as thin. They are now backed by
    page_content.DEEP, rendered through partials/deep_dive.html. These tests pin
    the floor sitewide rather than per-page, so a NEW thin page fails too.
    """

    @staticmethod
    def _visible_text(html):
        html = re.sub(r"(?is)<(script|style|svg|noscript|nav|footer|header).*?</\1>", " ", html)
        return " ".join(re.sub(r"(?s)<[^>]+>", " ", html).split())

    def _unique_words(self):
        """Words in blocks that appear on this page and no other. Cached per call."""
        from collections import Counter

        def blocks(path):
            html = self.client.get(path).content.decode()
            html = re.sub(r"(?is)<(script|style|svg|noscript).*?</\1>", " ", html)
            text = " ".join(re.sub(r"(?s)<[^>]+>", "|", html).split())
            return {s.strip() for s in text.split("|") if len(s.strip().split()) > 4}

        per = {p: blocks(p) for p in SITEMAP_PATHS}
        seen = Counter()
        for group in per.values():
            seen.update(group)
        return {
            path: sum(len(b.split()) for b in group if seen[b] == 1)
            for path, group in per.items()
        }

    def test_no_page_is_thin(self):
        for path, words in sorted(self._unique_words().items(), key=lambda kv: kv[1]):
            with self.subTest(path=path):
                self.assertGreaterEqual(
                    words, 200,
                    f"{path} has only {words} words that appear nowhere else on the site",
                )

    @staticmethod
    def _rendered_html(response):
        """Response HTML minus <template> contents, which the browser never renders.

        Two tool pages define a card <template> for cloning at runtime. An include
        that lands inside one is present in the source and invisible on the page —
        which a plain assertContains happily passes, because it only sees a string.
        Strip those blocks so the assertion means what it appears to mean.
        """
        return re.sub(r"(?is)<template\b.*?</template>", " ", response.content.decode())

    def test_every_deep_entry_actually_renders(self):
        """A DEEP entry whose template forgot the include is invisible work."""
        from remover.page_content import DEEP

        for key, content in DEEP.items():
            slug = key.split(":", 1)[1] if key.startswith("use_case:") else None
            url = (
                reverse("remover:use_case", args=[slug]) if slug
                else reverse(f"remover:{key}")
            )
            with self.subTest(page=key):
                # escape(): the copy contains apostrophes, which Django renders as
                # &#x27; — comparing the raw string would fail on correct output.
                html = self._rendered_html(self.client.get(url))
                self.assertIn(escape(content["title"]), html)
                self.assertIn(escape(content["sections"][0]["h"]), html)

    def test_deep_sections_are_page_specific(self):
        """Copy that would read the same on a sibling belongs in the template."""
        from remover.page_content import DEEP

        headings = [s["h"] for c in DEEP.values() for s in c["sections"]]
        duplicates = {h for h in headings if headings.count(h) > 1}
        self.assertFalse(duplicates, f"section headings reused across pages: {duplicates}")

        paragraphs = [p for c in DEEP.values() for s in c["sections"] for p in s.get("p", [])]
        repeated = {p[:60] for p in paragraphs if paragraphs.count(p) > 1}
        self.assertFalse(repeated, f"paragraphs copy-pasted between pages: {repeated}")

    def test_every_deep_page_has_real_substance(self):
        from remover.page_content import DEEP

        for key, content in DEEP.items():
            with self.subTest(page=key):
                self.assertGreaterEqual(len(content["sections"]), 3, "fewer than 3 sections")
                words = sum(
                    len(p.split())
                    for s in content["sections"]
                    for p in s.get("p", []) + s.get("list", [])
                )
                self.assertGreater(words, 250, f"{key}: only {words} words of deep copy")


class OrphanedFaqTests(SimpleTestCase):
    """A view that computes FAQs its template never renders is wasted work.

    Seven tool views passed `faqs` and `faq_jsonld` into templates with no FAQ
    include, so the copy AND the FAQPage structured data were built and thrown
    away on every request — silent, and invisible in any per-page test.
    """

    FAQ_PAGES = [
        "convert", "compress", "instagram", "crop", "favicon", "sticker", "meme",
        "resize", "border", "palette", "passport", "index",
    ]

    def test_pages_that_build_faqs_render_them(self):
        for name in self.FAQ_PAGES:
            with self.subTest(tool=name):
                response = self.client.get(reverse(f"remover:{name}"))
                # Strip <template> blocks: markup inside one is inert, so an
                # accordion that lands there is in the source and off the page.
                html = re.sub(r"(?is)<template\b.*?</template>", " ", response.content.decode())
                self.assertIn("FAQPage", html)
                self.assertIn("Frequently asked questions", html)

    def test_use_case_pages_have_their_own_faqs(self):
        from remover.page_content import USE_CASE_FAQS

        for case in USE_CASES:
            with self.subTest(case=case["slug"]):
                self.assertIn(case["slug"], USE_CASE_FAQS, "no FAQ set for this use case")
                response = self.client.get(reverse("remover:use_case", args=[case["slug"]]))
                self.assertContains(response, "FAQPage")
                self.assertContains(response, USE_CASE_FAQS[case["slug"]][0]["q"])

    def test_use_case_faqs_are_not_a_shared_template(self):
        """FAQPage markup is compared sitewide; eleven identical sets is worse than none."""
        from remover.page_content import USE_CASE_FAQS

        questions = [f["q"] for faqs in USE_CASE_FAQS.values() for f in faqs]
        repeated = {q for q in questions if questions.count(q) > 1}
        self.assertFalse(repeated, f"the same question appears on several pages: {repeated}")


class GuideTests(SimpleTestCase):
    """Routing, rendering and structured data for the editorial section."""

    def test_hub_renders_and_lists_every_guide(self):
        response = self.client.get(reverse("remover:guides"))
        self.assertEqual(response.status_code, 200)
        for guide in GUIDES:
            self.assertContains(response, reverse("remover:guide", args=[guide["slug"]]))
            self.assertContains(response, guide["h1"])

    def test_every_guide_renders(self):
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                response = self.client.get(reverse("remover:guide", args=[guide["slug"]]))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "remover/guide.html")
                self.assertContains(response, guide["h1"])

    def test_unknown_guide_is_404(self):
        response = self.client.get(reverse("remover:guide", args=["not-a-real-guide"]))
        self.assertEqual(response.status_code, 404)

    def test_guides_are_in_the_sitemap(self):
        sitemap = self.client.get(reverse("remover:sitemap")).content.decode()
        self.assertIn("/guides/</loc>", sitemap)
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                self.assertIn(f"/guides/{guide['slug']}/</loc>", sitemap)

    def test_every_section_heading_has_a_working_anchor(self):
        """The contents box is only useful if its targets exist."""
        for guide in GUIDES:
            body = self.client.get(reverse("remover:guide", args=[guide["slug"]])).content.decode()
            for section in guide["sections"]:
                with self.subTest(guide=guide["slug"], section=section["id"]):
                    self.assertIn(f'href="#{section["id"]}"', body)
                    self.assertIn(f'id="{section["id"]}"', body)

    def test_articles_emit_valid_article_jsonld(self):
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                body = self.client.get(reverse("remover:guide", args=[guide["slug"]])).content.decode()
                blocks = [
                    json.loads(m)
                    for m in re.findall(
                        r'<script type="application/ld\+json">(.*?)</script>', body, re.S
                    )
                ]
                types = {b.get("@type") for b in blocks}
                self.assertIn("Article", types)
                self.assertIn("BreadcrumbList", types)
                self.assertIn("FAQPage", types)
                article = next(b for b in blocks if b.get("@type") == "Article")
                self.assertEqual(article["wordCount"], guide["words"])

    def test_guides_are_linked_from_the_footer_of_every_page(self):
        """A new section is crawled at the speed its internal links allow."""
        for path in ("/", "/crop/", "/about/", "/passport-photo/canada/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, reverse("remover:guides"))
                self.assertContains(
                    response, reverse("remover:guide", args=[GUIDES[0]["slug"]])
                )

    def test_ads_run_on_guides_but_not_on_tool_pages(self):
        # The guides are the long-form editorial an ad unit belongs on; the
        # interactive tools stay ad-free (and the isolated ones would block frames).
        with override_settings(ADSENSE_CLIENT="ca-pub-test", ADSENSE_SLOT_LANDING="123"):
            guide = self.client.get(reverse("remover:guide", args=[GUIDES[0]["slug"]]))
            self.assertContains(guide, "ca-pub-test")
            for name in ("index", "crop", "compress"):
                with self.subTest(tool=name):
                    self.assertNotContains(self.client.get(reverse(f"remover:{name}")), "ca-pub-test")


class GuideContentTests(SimpleTestCase):
    """The guides only do their job if they stay substantial and distinct.

    This section exists because the rest of the site is tool pages: ~130 unique
    words of supporting copy wrapped around an interface. That is what a search or
    ad-network quality review calls thin. An article that decayed into another
    landing page would put the problem straight back, so the floors are pinned.
    """

    @staticmethod
    def _visible_text(html):
        html = re.sub(r"(?is)<(script|style|svg|noscript|nav|footer|header).*?</\1>", " ", html)
        return " ".join(re.sub(r"(?s)<[^>]+>", " ", html).split())

    def test_every_guide_clears_the_length_floor(self):
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                self.assertGreater(
                    guide["words"], 800,
                    f"{guide['slug']} is {guide['words']} words — too short to be worth indexing",
                )

    def test_every_guide_has_the_structural_pieces(self):
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                self.assertGreaterEqual(len(guide["sections"]), 5, "fewer than 5 sections")
                self.assertGreaterEqual(len(guide["takeaways"]), 4, "fewer than 4 takeaways")
                self.assertGreaterEqual(len(guide["faqs"]), 3, "fewer than 3 FAQs")
                self.assertTrue(guide["intro"], "no intro")
                self.assertTrue(all(s.get("p") for s in guide["sections"]),
                                "a section has a heading but no prose")

    def test_guides_are_not_near_duplicates_of_each_other(self):
        import difflib
        import itertools

        pages = {
            g["slug"]: self._visible_text(
                self.client.get(reverse("remover:guide", args=[g["slug"]])).content.decode()
            )
            for g in GUIDES
        }
        for a, b in itertools.combinations(sorted(pages), 2):
            ratio = difflib.SequenceMatcher(None, pages[a], pages[b]).ratio()
            with self.subTest(pair=f"{a}/{b}"):
                self.assertLess(ratio, 0.5, f"{a} and {b} are {ratio:.0%} identical")

    def test_guides_are_not_rewrites_of_the_tool_pages(self):
        """An article that restates its tool page adds a near-duplicate, not content."""
        import difflib

        for guide in GUIDES:
            article = self._visible_text(
                self.client.get(reverse("remover:guide", args=[guide["slug"]])).content.decode()
            )
            for tool in guide["tools"]:
                tool_page = self._visible_text(
                    self.client.get(reverse(f"remover:{tool}")).content.decode()
                )
                ratio = difflib.SequenceMatcher(None, article, tool_page).ratio()
                with self.subTest(guide=guide["slug"], tool=tool):
                    self.assertLess(ratio, 0.5, f"{guide['slug']} reads like /{tool}/")

    def test_every_referenced_tool_resolves(self):
        """A typo in `tools` would silently drop the cross-link, so fail on it."""
        from remover.views import _guide_tool_links

        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                links = _guide_tool_links(guide["tools"])
                self.assertEqual(
                    len(links), len(guide["tools"]),
                    f"{guide['slug']} names a tool that does not resolve: {guide['tools']}",
                )

    def test_every_guide_has_a_footer_label(self):
        for guide in GUIDES:
            with self.subTest(guide=guide["slug"]):
                self.assertTrue(guide["nav"])
                self.assertLess(len(guide["nav"]), 30, "footer label too long for the column")

    def test_slugs_and_titles_are_unique(self):
        for field in ("slug", "title", "h1", "nav"):
            values = [g[field] for g in GUIDES]
            with self.subTest(field=field):
                self.assertEqual(len(values), len(set(values)), f"duplicate {field}")


class InfoPageTests(SimpleTestCase):
    def test_info_pages_render(self):
        for name in ("about", "privacy", "terms"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertEqual(response.status_code, 200, name)

    def test_privacy_covers_key_points(self):
        response = self.client.get(reverse("remover:privacy"))
        self.assertContains(response, "never leave your device")
        self.assertContains(response, "AdSense")

    def test_footer_links_legal_pages(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, reverse("remover:privacy"))
        self.assertContains(response, reverse("remover:terms"))
        self.assertContains(response, reverse("remover:about"))

    def test_info_pages_in_sitemap(self):
        response = self.client.get(reverse("remover:sitemap"))
        for path in ("/about/", "/privacy/", "/terms/"):
            self.assertContains(response, path)

    def test_sitemap_has_lastmod_and_priorities(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "<lastmod>")
        self.assertContains(response, "<priority>1.0</priority>")  # home
        self.assertContains(response, "<priority>0.9</priority>")  # a tool

    def test_organization_schema_present(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, '"@type": "Organization"')


class FaqTests(SimpleTestCase):
    def test_index_has_faq_schema(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, "FAQPage")
        self.assertContains(response, "Frequently asked questions")

    def test_tool_pages_have_faq(self):
        for name in ("passport", "blur"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertContains(response, "FAQPage")


class I18nTests(SimpleTestCase):
    def tearDown(self):
        # Requesting /pt/ activates Portuguese on the thread; reset it so the
        # language doesn't leak into other tests (production re-activates per
        # request via LocaleMiddleware, so this is a test-only concern).
        translation.activate("en")

    def test_portuguese_home_renders(self):
        response = self.client.get("/pt/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remova Fundos de Imagens")   # translated H1
        self.assertContains(response, 'lang="pt"')

    def test_english_home_unprefixed(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove Image Backgrounds")

    def test_portuguese_landing_page_translated(self):
        response = self.client.get("/pt/remove-background/product-photos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remova Fundos de Fotos de Produtos")

    def test_hreflang_alternates_present(self):
        response = self.client.get("/")
        self.assertContains(response, 'hreflang="pt"')
        self.assertContains(response, 'hreflang="x-default"')
        self.assertContains(response, "/pt/")

    def test_language_switcher_present(self):
        response = self.client.get("/")
        self.assertContains(response, "Português")

    def test_nav_translated_in_pt(self):
        response = self.client.get("/pt/")
        self.assertContains(response, "Remover Fundo")  # "Remove BG" nav label


class CrossOriginIsolationTests(SimpleTestCase):
    """COOP+COEP (isolation) is scoped to the WASM background-removal pages."""

    def test_isolated_pages_get_coep(self):
        for name in ("index", "instagram", "sticker", "passport"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertEqual(response["Cross-Origin-Embedder-Policy"], "credentialless", name)

    def test_convert_is_not_isolated(self):
        # The converter is pure canvas work (no in-browser removal model), so it
        # must NOT be cross-origin isolated.
        response = self.client.get(reverse("remover:convert"))
        self.assertNotIn("Cross-Origin-Embedder-Policy", response)

    def test_landing_pages_are_not_isolated(self):
        response = self.client.get(reverse("remover:use_case", args=["logo"]))
        self.assertNotIn("Cross-Origin-Embedder-Policy", response)


class MonetizationTests(SimpleTestCase):
    @override_settings(ADSENSE_CLIENT="ca-pub-test")
    def test_ads_only_on_landing_pages(self):
        landing = self.client.get(reverse("remover:use_case", args=["logo"]))
        self.assertContains(landing, "ca-pub-test")
        # Tool pages (isolated and non-isolated) stay ad-free.
        for name in ("index", "convert"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertNotContains(response, "adsbygoogle")

    @override_settings(ADSENSE_CLIENT="")
    def test_ads_disabled_when_client_unset(self):
        response = self.client.get(reverse("remover:use_case", args=["logo"]))
        self.assertNotContains(response, "adsbygoogle")


class PWATests(SimpleTestCase):
    def test_service_worker(self):
        response = self.client.get(reverse("remover:sw"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertContains(response, "caches.open")

    def test_manifest(self):
        response = self.client.get(reverse("remover:manifest"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/manifest+json")
        self.assertContains(response, '"display": "standalone"')

    def test_index_links_manifest_and_icons(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, 'rel="manifest"')
        self.assertContains(response, "apple-touch-icon")

    def test_service_worker_precaches_every_tool_page(self):
        # The shell used to be hand-written and fell nine tools behind, while
        # /offline-image-editor/ advertised those tools as working offline.
        sw = self.client.get(reverse("remover:sw")).content.decode()
        for path in TOOL_PATHS:
            with self.subTest(path=path):
                self.assertIn(f"'{path}'", sw)

    def test_service_worker_precaches_every_tool_script(self):
        sw = self.client.get(reverse("remover:sw")).content.decode()
        for asset in SHELL_ASSETS:
            with self.subTest(asset=asset):
                self.assertIn(asset, sw)

    def test_shell_pages_track_the_tool_list(self):
        self.assertEqual(SHELL_PAGES, ["/"] + TOOL_PATHS)

    def test_manifest_has_a_dedicated_maskable_icon(self):
        # "any maskable" on every icon is the documented anti-pattern: the same
        # art is then used both full-bleed and safe-zone-cropped.
        manifest = self.client.get(reverse("remover:manifest")).content.decode()
        self.assertIn('"purpose": "maskable"', manifest)
        self.assertNotIn('"any maskable"', manifest)

    def test_manifest_has_shortcuts(self):
        manifest = self.client.get(reverse("remover:manifest")).content.decode()
        self.assertIn('"shortcuts"', manifest)


class AssetHostingTests(SimpleTestCase):
    """Fonts and icons are self-hosted; only the canvas display fonts are remote."""

    def test_ui_font_is_self_hosted(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, "css/inter.css")
        # No render-blocking Google Fonts request on a page that only uses Inter.
        self.assertNotContains(response, "fonts.googleapis.com/css2")

    def test_pages_that_paint_display_fonts_still_load_them(self):
        # The meme/sticker/text-behind/Instagram canvases genuinely need Anton &
        # friends, so those pages keep the request — with a preconnect.
        response = self.client.get(reverse("remover:meme"))
        self.assertContains(response, "fonts.googleapis.com/css2")
        self.assertContains(response, 'rel="preconnect" href="https://fonts.googleapis.com"')

    def test_absolute_urls_use_site_url_not_the_request_host(self):
        # A www/apex or http/https variant must not advertise a different image
        # or identity than the canonical it points at.
        response = self.client.get(reverse("remover:index"), HTTP_HOST="localhost")
        body = response.content.decode()
        self.assertIn('<meta property="og:image" content="http://localhost:8000/static/img/og-image.png">', body)
        self.assertNotIn('content="http://localhost/static/img/og-image.png"', body)


class EveryToolTests(SimpleTestCase):
    """One pass over TOOL_NAV so no tool ships without basic coverage.

    Most tools had none: they were verified by hand, so a broken template, a
    missing script tag or a tool dropped from the sitemap could reach production
    unnoticed. This walks the single list that already defines the toolkit, so a
    new tool is covered the moment it appears in the nav.
    """

    def test_every_tool_page_renders(self):
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                response = self.client.get(reverse(f"remover:{item['name']}"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "<h1")

    def test_every_tool_loads_its_script(self):
        # A tool page that renders but never loads its module is an inert page —
        # exactly the failure that looks fine in a screenshot.
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                response = self.client.get(reverse(f"remover:{item['name']}"))
                self.assertRegex(
                    response.content.decode(),
                    r'<script[^>]+src="[^"]*/static/js/[^"]+\.js"',
                    f"{item['name']} renders but loads no tool script",
                )

    def test_every_tool_is_in_the_sitemap(self):
        response = self.client.get(reverse("remover:sitemap")).content.decode()
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                self.assertIn(reverse(f"remover:{item['name']}"), response)

    def test_every_tool_has_an_accent(self):
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                self.assertIn(
                    item["name"], TOOL_ACCENTS,
                    f"{item['name']} has no entry in TOOL_ACCENTS and would fall back to indigo",
                )

    def test_tool_grid_links_every_tool(self):
        response = self.client.get(reverse("remover:index")).content.decode()
        for item in TOOL_NAV:
            if item["name"] == "index":
                continue
            with self.subTest(tool=item["name"]):
                self.assertIn(reverse(f"remover:{item['name']}"), response)


class BatchToolTests(SimpleTestCase):
    """Tools whose settings are image-independent accept a batch."""

    BATCH_TOOLS = ["resize", "watermark", "exif", "pdf", "photo_filters", "upscale"]

    def test_file_inputs_accept_multiple(self):
        for name in self.BATCH_TOOLS:
            with self.subTest(tool=name):
                response = self.client.get(reverse(f"remover:{name}"))
                self.assertContains(response, "multiple")

    def test_batch_bar_present(self):
        # pdf has its own page list rather than the shared bar.
        for name in ["resize", "watermark", "exif", "photo_filters", "upscale"]:
            with self.subTest(tool=name):
                response = self.client.get(reverse(f"remover:{name}"))
                self.assertContains(response, "data-batch-zip")


class HealthCheckTests(SimpleTestCase):
    def test_healthz(self):
        response = self.client.get(reverse("remover:healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class SitemapContentTests(SimpleTestCase):
    def test_sitemap_lists_convert(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "/convert/")

    def test_sitemap_lists_the_translated_portuguese_pages(self):
        # The /pt/ pages were absent entirely, so they were only reachable via
        # footer links — the sitemap claimed the site was English-only.
        response = self.client.get(reverse("remover:sitemap")).content.decode()
        self.assertIn("/pt/</loc>", response)
        self.assertIn("/pt/remove-background/logo/</loc>", response)

    def test_sitemap_omits_untranslated_portuguese_pages(self):
        # /pt/convert/ resolves, but convert.html has no {% t %} — it serves the
        # English page. Submitting it duplicated /convert/ and claimed a
        # translation that does not exist.
        response = self.client.get(reverse("remover:sitemap")).content.decode()
        self.assertIn("/convert/</loc>", response)
        self.assertNotIn("/pt/convert/</loc>", response)
        self.assertNotIn("/pt/about/</loc>", response)

    def test_sitemap_pt_url_count_matches_translated_paths(self):
        response = self.client.get(reverse("remover:sitemap")).content.decode()
        pt_locs = re.findall(r"<loc>[^<]*/pt/[^<]*</loc>", response)
        self.assertEqual(len(pt_locs), len(TRANSLATED_PATHS))

    def test_sitemap_declares_hreflang_alternates(self):
        response = self.client.get(reverse("remover:sitemap")).content.decode()
        self.assertIn('xmlns:xhtml="http://www.w3.org/1999/xhtml"', response)
        self.assertIn('hreflang="pt"', response)
        self.assertIn('hreflang="x-default"', response)
        # Where alternates are declared they must be declared from BOTH sides —
        # Google treats a page that names its siblings one-way as unlinked. So
        # the alternate count is two entries per translated path, not one.
        self.assertEqual(
            response.count('hreflang="en"'), 2 * len(TRANSLATED_PATHS)
        )
        self.assertEqual(
            response.count('hreflang="en"'), response.count('hreflang="pt"')
        )


class TranslationCoverageTests(SimpleTestCase):
    """`TRANSLATED_PATHS` must describe reality, in both directions.

    The list decides which pages advertise a Portuguese alternate to crawlers,
    so an entry that isn't really translated is a false claim to Google — and a
    translated page missing from the list is finished work that never ships.
    Both directions are checked against the rendered page rather than against a
    hand-kept note, because the hand-kept version is what drifted before.

    "Really translated" is measured by counting how many distinct Portuguese
    phrases the /pt/ page renders that its English twin does not. A page with a
    translated body sits far above one that merely inherits the translated header
    and footer, so the two form separate bands (currently 71+ vs under 60). The
    test asserts the BANDS DO NOT OVERLAP rather than picking a threshold: no
    magic number to re-tune, and it fails from either direction — a listed page
    that isn't translated sinks into the low band, and a newly translated page
    that nobody listed rises out of it.
    """

    def _pt_phrase_count(self, path):
        """How many distinct Portuguese translations appear on /pt/<path>."""
        from remover.translations import UI

        body = self.client.get(f"/pt{path}").content.decode()
        # Compared against the English render so a phrase that is spelled the
        # same in both languages ("Meme", "Favicon") is not counted as evidence.
        english = self.client.get(path).content.decode()
        return sum(
            1
            for en, pt in UI.items()
            if pt != en and pt in body and pt not in english
        )

    def test_translated_paths_are_in_the_sitemap(self):
        self.assertTrue(TRANSLATED_PATHS)
        self.assertTrue(TRANSLATED_PATHS.issubset(set(SITEMAP_PATHS)))

    def test_translated_paths_match_what_the_pages_actually_render(self):
        counts = {p: self._pt_phrase_count(p) for p in SITEMAP_PATHS}
        declared = {p: n for p, n in counts.items() if p in TRANSLATED_PATHS}
        rest = {p: n for p, n in counts.items() if p not in TRANSLATED_PATHS}
        if not declared or not rest:
            self.skipTest("needs both a translated and an untranslated page")

        weakest = min(declared, key=declared.get)
        strongest = max(rest, key=rest.get)
        self.assertGreater(
            declared[weakest],
            rest[strongest],
            f"TRANSLATED_PATHS no longer matches what the site renders.\n"
            f"  weakest declared-translated page: {weakest} "
            f"({declared[weakest]} Portuguese phrases)\n"
            f"  most-translated page NOT declared: {strongest} "
            f"({rest[strongest]} Portuguese phrases)\n"
            f"Either {weakest} was listed before its template was translated "
            f"(drop it), or {strongest} has since been translated (add it).",
        )


class HreflangGateTests(SimpleTestCase):
    """Only genuinely translated pages may advertise a Portuguese alternate."""

    def test_translated_page_declares_alternates(self):
        for path in ("/", "/pt/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, 'hreflang="pt"')
                self.assertContains(response, 'hreflang="x-default"')

    def test_untranslated_page_declares_no_alternates(self):
        for path in ("/crop/", "/pt/crop/", "/about/", "/pt/about/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertNotContains(response, 'rel="alternate" hreflang')

    def test_untranslated_pt_page_canonicalises_to_its_english_twin(self):
        # /pt/crop/ serves the English page, so pointing it at itself would put
        # two URLs with the same content in the index competing for one query.
        response = self.client.get("/pt/crop/").content.decode()
        canonical = re.search(r'rel="canonical" href="([^"]+)"', response).group(1)
        self.assertTrue(canonical.endswith("/crop/"))
        self.assertNotIn("/pt/", canonical)

    def test_translated_pt_page_canonicalises_to_itself(self):
        response = self.client.get("/pt/").content.decode()
        canonical = re.search(r'rel="canonical" href="([^"]+)"', response).group(1)
        self.assertTrue(canonical.endswith("/pt/"))

    def test_language_switcher_survives_on_untranslated_pages(self):
        # The switcher is a UX affordance, not an SEO claim: a Portuguese visitor
        # who lands on /crop/ must still be able to reach the translated part of
        # the site. It used to share the hreflang flag, so gating that would have
        # silently removed the switcher from most of the site.
        for path in ("/crop/", "/about/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, 'hreflang="pt"', html=False)
                self.assertContains(response, "Portugu")


class RobotsMetaTests(SimpleTestCase):
    """A /pt/ URL that still renders English must not be indexable.

    The canonical already points these at their English twin, but a canonical is
    a hint. Left indexable, 59 English-bodied Portuguese URLs form the largest
    block of near-duplicates on the site — the kind of crawlable surface that
    reads as low-value content to a search or ad-network quality review.
    """

    def _robots(self, path):
        response = self.client.get(path).content.decode()
        return re.search(r'name="robots" content="([^"]+)"', response).group(1)

    def test_untranslated_pt_page_is_noindex(self):
        for path in ("/pt/crop/", "/pt/qr-code-generator/", "/pt/about/"):
            with self.subTest(path=path):
                self.assertEqual(self._robots(path), "noindex, follow")

    def test_translated_pt_page_stays_indexable(self):
        # These have real Portuguese bodies (TRANSLATED_PATHS) and must keep
        # ranking — a blanket /pt/ noindex would have thrown them away too.
        for path in ("/pt/", "/pt/remove-background/logo/", "/pt/heic-to-jpg/"):
            with self.subTest(path=path):
                self.assertEqual(self._robots(path), "index, follow")

    def test_english_pages_are_untouched(self):
        for path in ("/", "/crop/", "/about/", "/passport-photo/canada/"):
            with self.subTest(path=path):
                self.assertEqual(self._robots(path), "index, follow")

    def test_noindexed_pt_urls_are_absent_from_the_sitemap(self):
        # Submitting a URL we tell Google not to index is a contradictory signal.
        sitemap = self.client.get(reverse("remover:sitemap")).content.decode()
        for path in ("/pt/crop/", "/pt/qr-code-generator/"):
            with self.subTest(path=path):
                self.assertNotIn(f"<loc>{settings.SITE_URL.rstrip('/')}{path}</loc>", sitemap)

    def test_every_pt_url_is_either_translated_or_noindexed(self):
        # The invariant, checked across the whole site rather than on samples:
        # no /pt/ URL may serve English while remaining indexable.
        for path in SITEMAP_PATHS:
            pt = "/pt/" if path == "/" else f"/pt{path}"
            with self.subTest(path=pt):
                expected = "index, follow" if is_translated_path(pt) else "noindex, follow"
                self.assertEqual(self._robots(pt), expected)


class JsTranslationTests(SimpleTestCase):
    """The runtime strings the tools raise must be translatable, and translated.

    Template copy has {% t %} and a reviewer who notices English on a /pt/ page.
    Runtime messages are invisible until something succeeds or fails, which is
    exactly when a wrong language is most jarring — so the catalogue is checked
    mechanically instead.
    """

    JS_DIR = Path(__file__).resolve().parent.parent / "static" / "js"
    # t('…') / t("…") — the second group is the key. Template literals are not
    # matched: a key with a ${} hole in it could never be looked up anyway.
    CALL = re.compile(r"[^\w.]t\((['\"])(.+?)\1")

    def _keys_used(self):
        found = {}
        for path in sorted(self.JS_DIR.glob("*.js")):
            for _, key in self.CALL.findall(path.read_text()):
                found.setdefault(key, path.name)
        return found

    def test_every_translated_string_is_in_the_catalogue(self):
        missing = {k: f for k, f in self._keys_used().items() if k not in JS_UI}
        self.assertFalse(
            missing,
            "these strings are wrapped in t() but have no entry in "
            "translations.JS_UI, so they stay English on /pt/: "
            + ", ".join(f"{k!r} ({f})" for k, f in sorted(missing.items())),
        )

    def test_no_tool_raises_an_untranslated_message(self):
        # Toast.show('literal') rather than Toast.show(t('literal')). This is
        # the drift that reintroduces English into the Portuguese site.
        bare = re.compile(r"Toast\.show\(\s*['\"`]")
        offenders = [
            p.name for p in sorted(self.JS_DIR.glob("*.js")) if bare.search(p.read_text())
        ]
        self.assertFalse(
            offenders,
            "raw message passed to Toast.show in: " + ", ".join(offenders)
            + " — wrap it in t() and add the string to translations.JS_UI",
        )

    def test_placeholders_survive_translation(self):
        # A dropped {placeholder} renders a sentence with a hole in it.
        holes = re.compile(r"\{(\w+)\}")
        for en, pt in JS_UI.items():
            with self.subTest(key=en):
                self.assertEqual(
                    sorted(holes.findall(en)),
                    sorted(holes.findall(pt)),
                    f"placeholders differ between {en!r} and {pt!r}",
                )

    def test_catalogue_is_served_on_portuguese_pages_only(self):
        # English keys ARE the English text, so an English page needs no payload.
        self.assertNotContains(self.client.get("/crop/"), 'id="cbg-i18n"')
        self.assertContains(self.client.get("/pt/crop/"), 'id="cbg-i18n"')


class ChainTests(SimpleTestCase):
    """Cross-tool image chaining (kit.js Chain + the "keep editing" bar)."""

    def test_every_tool_page_offers_chain_destinations(self):
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                response = self.client.get(reverse(f"remover:{item['name']}"))
                self.assertContains(response, 'id="chain-targets"')

    def test_a_tool_is_never_a_destination_from_itself(self):
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                url = reverse(f"remover:{item['name']}")
                targets = json.loads(
                    re.search(
                        r'id="chain-targets"[^>]*>(.*?)</script>',
                        self.client.get(url).content.decode(),
                        re.S,
                    ).group(1)
                )
                self.assertTrue(targets)
                self.assertNotIn(url, [t["url"] for t in targets])

    def test_excluded_tools_are_never_destinations(self):
        # The QR generator builds a code from a link; handing it a photo is
        # meaningless, and its only file input is an optional centre logo.
        for name in CHAIN_EXCLUDED:
            excluded_url = reverse(f"remover:{name}")
            for item in TOOL_NAV:
                with self.subTest(tool=item["name"], excluded=name):
                    body = self.client.get(reverse(f"remover:{item['name']}")).content.decode()
                    targets = json.loads(
                        re.search(r'id="chain-targets"[^>]*>(.*?)</script>', body, re.S).group(1)
                    )
                    self.assertNotIn(excluded_url, [t["url"] for t in targets])

    def test_tool_pages_mark_a_primary_input_for_incoming_images(self):
        # kit.js delivers a chained image by firing `change` on this input, so a
        # page without the marker silently drops what the user sent to it.
        for item in TOOL_NAV:
            if item["name"] in CHAIN_EXCLUDED:
                continue
            with self.subTest(tool=item["name"]):
                body = self.client.get(reverse(f"remover:{item['name']}")).content.decode()
                self.assertEqual(
                    body.count("data-chain-input"), 1,
                    f"{item['name']} must mark exactly one primary file input",
                )


class SharedKitTests(SimpleTestCase):
    """No tool may go back to carrying private copies of the shared helpers."""

    JS_DIR = Path(__file__).resolve().parent.parent / "static" / "js"

    def test_no_tool_defines_its_own_toast(self):
        # There were sixteen of these, all building their markup with innerHTML
        # — which interpolated the user's own file name into HTML. CBG.Toast
        # uses textContent.
        offenders = [
            p.name
            for p in sorted(self.JS_DIR.glob("*.js"))
            if p.name != "kit.js" and "const Toast = {" in p.read_text()
        ]
        self.assertFalse(offenders, "private Toast copy in: " + ", ".join(offenders))

    def test_no_tool_hand_rolls_a_download_anchor(self):
        # CBG.download is what registers a result with the chain, so a tool that
        # builds its own anchor exports fine but drops out of "keep editing".
        anchor = re.compile(r"\.download\s*=\s*")
        offenders = [
            p.name
            for p in sorted(self.JS_DIR.glob("*.js"))
            if p.name != "kit.js" and anchor.search(p.read_text())
        ]
        self.assertFalse(
            offenders,
            "hand-rolled download anchor in: " + ", ".join(offenders)
            + " — use CBG.download(blob, name)",
        )


class SiteVerificationTests(SimpleTestCase):
    def test_no_meta_when_unset(self):
        response = self.client.get(reverse("remover:index"))
        self.assertNotContains(response, "google-site-verification")

    @override_settings(GOOGLE_SITE_VERIFICATION="test-token-123")
    def test_meta_rendered_when_set(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, 'name="google-site-verification" content="test-token-123"')


class SeoEndpointTests(SimpleTestCase):
    def test_robots_txt(self):
        response = self.client.get(reverse("remover:robots"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "Sitemap:")
        self.assertContains(response, "Allow: /")

    def test_sitemap_xml(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        self.assertContains(response, "<urlset")
        self.assertContains(response, "<loc>")


class AccentContrastTests(SimpleTestCase):
    """Every per-tool accent must stay legible in both themes.

    TOOL_ACCENTS is hand-edited, and a colour that looks fine on white can be
    unreadable on the dark surface (and vice versa) — the failure the surface/text
    token split exists to prevent. Rather than trust the table, recompute WCAG
    contrast for all three roles so a bad shade fails here instead of shipping.
    """

    AA = 4.5
    WHITE = (255, 255, 255)
    # The dark glass surface (rgba(22,22,34,.74) over gray-950) that dark-mode
    # accent text actually sits on — stricter than gray-950 itself.
    DARK = (18, 18, 28)

    @staticmethod
    def _luminance(rgb):
        def channel(c):
            c /= 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = (channel(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @classmethod
    def _ratio(cls, a, b):
        la, lb = cls._luminance(a), cls._luminance(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    @staticmethod
    def _rgb(value):
        return tuple(int(c) for c in value.split())

    def test_accents_meet_aa_in_both_themes(self):
        for tool, (surface, hover, text_dark, text_dark_alt) in TOOL_ACCENTS.items():
            with self.subTest(tool=tool):
                # The surface pair carries white text, in both themes. Both stops
                # matter: they're also the light-theme gradient headline.
                for role, value in (("surface", surface), ("surface_hover", hover)):
                    ratio = self._ratio(self._rgb(value), self.WHITE)
                    self.assertGreaterEqual(
                        ratio, self.AA,
                        f"{tool} {role} ({value}) is {ratio:.2f}:1 against white text; "
                        f"needs {self.AA}:1 — use a darker shade.",
                    )
                # The text pair is the accent as text on the dark surface. Both
                # stops matter: the hero gradient headline paints text_dark ->
                # text_dark_alt, so checking only the first would miss a headline
                # whose far end fades into the background.
                for role, value in (("text_dark", text_dark), ("text_dark_alt", text_dark_alt)):
                    ratio = self._ratio(self._rgb(value), self.DARK)
                    self.assertGreaterEqual(
                        ratio, self.AA,
                        f"{tool} {role} ({value}) is {ratio:.2f}:1 on the dark "
                        f"surface; needs {self.AA}:1 — use a lighter shade.",
                    )

    def test_accent_table_is_well_formed(self):
        for tool, value in TOOL_ACCENTS.items():
            with self.subTest(tool=tool):
                self.assertEqual(
                    len(value), 4,
                    f"{tool}: expected (surface, surface_hover, text_dark, text_dark_alt)",
                )
                for part in value:
                    self.assertEqual(len(self._rgb(part)), 3, f"{tool}: {part!r} is not 'R G B'")


class AccentWiringTests(SimpleTestCase):
    """The accent only reaches the page if the view actually emits the variables."""

    def test_tool_page_emits_every_accent_var(self):
        response = self.client.get(reverse("remover:resize"))
        surface, hover, text_dark, text_dark_alt = TOOL_ACCENTS["resize"]
        self.assertContains(response, f"--color-primary: {surface}")
        self.assertContains(response, f"--color-primary-hover: {hover}")
        self.assertContains(response, f"--accent-text-dark: {text_dark}")
        self.assertContains(response, f"--accent-text-dark-alt: {text_dark_alt}")

    def test_gradient_headlines_use_the_text_pair_not_the_surface_pair(self):
        """A gradient painted as text must read from the text tokens.

        `from-primary to-primaryHover` is correct on a button (a real surface) and
        wrong on `bg-clip-text`, where it renders the headline in surface shades —
        illegible in dark mode. The distinction is invisible in review, so pin it.
        """
        import re
        from pathlib import Path

        offenders = []
        root = Path(__file__).resolve().parent.parent
        for path in (root / "templates").rglob("*.html"):
            for i, line in enumerate(path.read_text().split("\n"), 1):
                if "bg-clip-text" in line and re.search(r"from-primary\b(?!Text)", line):
                    offenders.append(f"{path.relative_to(root)}:{i}")
        self.assertFalse(
            offenders,
            "Gradient text using the surface tokens (use from-primaryText / "
            "to-primaryTextAlt instead):\n  " + "\n  ".join(offenders),
        )

    def test_theme_color_follows_the_tool_accent(self):
        response = self.client.get(reverse("remover:resize"))
        # resize = orange 700 (194 65 12) -> #c2410c, not the brand indigo.
        self.assertContains(response, '<meta name="theme-color" content="#c2410c">', html=False)


class IconSubsetTests(SimpleTestCase):
    """Every `fa-` icon used must exist in the committed Font Awesome subset.

    static/webfonts/* is subsetted to exactly the glyphs in fontawesome.css and has
    no build script, so referencing any other icon renders a blank box with no error
    anywhere — invisible until someone looks at that page. This catches it instead.
    Adding a genuinely new icon means re-subsetting the woff2, not just adding CSS.
    """

    # Structural/utility classes that style an icon rather than name a glyph.
    UTILITY = {
        "fa-solid", "fa-regular", "fa-brands", "fa-spin", "fa-border",
        "fa-rotate-by", "fa-flip-horizontal", "fa-fw", "fa-lg",
    }
    # Substrings of the webfont FILENAMES (fa-solid-900.woff2), not icon classes.
    NOT_ICONS = {"fa-solid-900", "fa-regular-400", "fa-brands-400"}

    def test_no_icon_outside_the_subset(self):
        import re
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        css = (root / "static/css/fontawesome.css").read_text()
        available = set(re.findall(r"\.(fa-[a-z0-9-]+)::before", css))
        self.assertGreater(len(available), 50, "subset CSS looks empty — wrong path?")

        sources = [
            p for d in ("templates", "static/js")
            for p in (root / d).rglob("*")
            if p.suffix in {".html", ".js"} and p.is_file()
        ]
        missing = {}
        for path in sources:
            # Lookbehind skips CSS custom properties (--fa-rotate-angle), which are
            # settings for a utility class rather than glyph names.
            for name in re.findall(r"(?<![-\w])fa-[a-z0-9-]+", path.read_text()):
                if name in self.UTILITY or name in self.NOT_ICONS or name in available:
                    continue
                missing.setdefault(name, set()).add(str(path.relative_to(root)))

        self.assertFalse(
            missing,
            "Icons used but absent from the Font Awesome subset (they render as blank "
            "boxes). Either use a glyph already in static/css/fontawesome.css, or "
            "re-subset the webfont to include these:\n"
            + "\n".join(f"  {n} <- {', '.join(sorted(f))}" for n, f in sorted(missing.items())),
        )


class NewToolSpecificsTests(SimpleTestCase):
    """Static (no-browser) guards for the 1.10 tools' plumbing.

    EveryToolTests already checks they render, load a script, own an accent and
    reach the sitemap. These assert the details that a template edit could break
    silently — file-type filters, the object-remover worker, per-tool OG cards,
    and that the localized FAQ actually swaps in on /pt/.
    """

    ACCEPT = {
        "heic": [".heic", ".heif"],
        "pdf_to_image": ["application/pdf"],
        "svg_to_png": [".svg"],
    }

    def test_format_specific_inputs_accept_the_right_files(self):
        for name, tokens in self.ACCEPT.items():
            body = self.client.get(reverse(f"remover:{name}")).content.decode()
            for tok in tokens:
                with self.subTest(tool=name, token=tok):
                    self.assertIn(tok, body)

    def test_object_remover_references_its_worker(self):
        # The off-thread fill is resolved relative to the module; if the file is
        # renamed the tool silently falls back to the main thread. Assert the
        # module names the worker and the file exists.
        from pathlib import Path

        js = (Path(__file__).resolve().parent.parent / "static/js/remove-object.js").read_text()
        self.assertIn("remove-object-worker.js", js)
        self.assertTrue(
            (Path(__file__).resolve().parent.parent / "static/js/remove-object-worker.js").exists()
        )

    def test_new_tools_have_a_per_tool_og_image(self):
        from remover.context_processors import OG_IMAGES

        for name, path in OG_IMAGES.items():
            with self.subTest(tool=name):
                body = self.client.get(reverse(f"remover:{name}")).content.decode()
                self.assertIn(path, body)
                # The static file must actually exist, or the card 404s.
                self.assertTrue(
                    (Path(__file__).resolve().parent.parent / "static" / path).exists(),
                    f"{path} declared in OG_IMAGES but missing on disk",
                )

    def test_untitled_pages_fall_back_to_the_default_og_image(self):
        body = self.client.get(reverse("remover:crop")).content.decode()
        self.assertIn("img/og-image.png", body)

    def test_stale_twitter_title_is_gone(self):
        # It used to hard-code a generic title on every page; Twitter now falls
        # back to og:title. A reintroduced twitter:title would re-stale it.
        body = self.client.get(reverse("remover:heic")).content.decode()
        self.assertNotIn("twitter:title", body)

    def test_new_tools_report_to_the_stats_counter(self):
        # A tool absent from STATS_TOOLS has its reports silently dropped.
        from remover.views import STATS_TOOLS

        for name in ("remove_object", "photo_filters", "upscale", "heic",
                     "pdf_to_image", "ocr", "svg_to_png"):
            with self.subTest(tool=name):
                self.assertIn(name, STATS_TOOLS)

    def test_new_tool_pages_localize_their_faq_in_portuguese(self):
        # localize_faqs must swap the FAQ (accordion + JSON-LD) on /pt/. Check a
        # known Portuguese answer fragment appears on each.
        cases = {
            "/pt/heic-to-jpg/": "por predefinição",          # "iPhones guardam... por predefinição"
            "/pt/image-to-text/": "no seu dispositivo",
            "/pt/svg-to-png/": "no tamanho exato",
        }
        for path, fragment in cases.items():
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), fragment)


class ToolLandingTests(SimpleTestCase):
    """The HEIC/OCR intent landings and the CloudConvert comparison."""

    def test_tool_landings_render_and_funnel_to_their_tool(self):
        from remover.views import TOOL_LANDINGS

        for page in TOOL_LANDINGS:
            with self.subTest(slug=page["slug"]):
                response = self.client.get(f"/{page['slug']}/")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page["h1"])
                self.assertContains(response, reverse(f"remover:{page['cta']['url_name']}"))

    def test_tool_landings_in_sitemap(self):
        from remover.views import TOOL_LANDINGS

        sitemap = self.client.get(reverse("remover:sitemap")).content.decode()
        for page in TOOL_LANDINGS:
            with self.subTest(slug=page["slug"]):
                self.assertIn(f"/{page['slug']}/", sitemap)

    def test_cloudconvert_comparison_renders(self):
        response = self.client.get("/cloudconvert-alternative/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CloudConvert")
        self.assertContains(response, reverse("remover:heic"))


class FooterTests(SimpleTestCase):
    """The footer Tools column is generated from TOOL_NAV, so it can't drift."""

    def test_footer_lists_every_tool(self):
        body = self.client.get(reverse("remover:index")).content.decode()
        # Grab the footer Tools <nav> and assert every tool URL appears in it.
        import re

        match = re.search(r'aria-label="Tools">(.*?)</nav>', body, re.S)
        self.assertIsNotNone(match, "footer Tools nav not found")
        footer = match.group(1)
        for item in TOOL_NAV:
            with self.subTest(tool=item["name"]):
                self.assertIn(reverse(f"remover:{item['name']}"), footer)
