"""Tests for the remover views and SEO endpoints."""
import json
import re
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from remover.context_processors import CHAIN_EXCLUDED, TOOL_ACCENTS, TOOL_NAV
from remover.translations import JS_UI
from remover.views import (
    SHELL_ASSETS,
    SHELL_PAGES,
    SITEMAP_PATHS,
    TOOL_PATHS,
    TRANSLATED_PATHS,
    USE_CASES,
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

    def test_upscale_redirects_to_home(self):
        # The upscaler was removed (client-side super-resolution froze the tab);
        # its indexed URL 301-redirects to home so it never 404s.
        response = self.client.get("/upscale/")
        self.assertRedirects(response, "/", status_code=301, target_status_code=200)

    def test_new_tools_in_sitemap(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "/passport-photo/")
        self.assertNotContains(response, "/upscale/")

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

    def test_country_pages_in_sitemap(self):
        from remover.passport_data import COUNTRIES
        response = self.client.get(reverse("remover:sitemap"))
        for c in COUNTRIES:
            self.assertContains(response, f"/passport-photo/{c['slug']}/")

    def test_passport_tool_links_countries(self):
        response = self.client.get(reverse("remover:passport"))
        self.assertContains(response, reverse("remover:passport_country", args=["united-states"]))


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

    BATCH_TOOLS = ["resize", "watermark", "exif", "pdf"]

    def test_file_inputs_accept_multiple(self):
        for name in self.BATCH_TOOLS:
            with self.subTest(tool=name):
                response = self.client.get(reverse(f"remover:{name}"))
                self.assertContains(response, "multiple")

    def test_batch_bar_present(self):
        # pdf has its own page list rather than the shared bar.
        for name in ["resize", "watermark", "exif"]:
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
