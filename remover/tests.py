"""Tests for the remover views and SEO endpoints."""
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from remover.views import USE_CASES


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
        for name in ("passport", "portrait"):
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


class HealthCheckTests(SimpleTestCase):
    def test_healthz(self):
        response = self.client.get(reverse("remover:healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class SitemapContentTests(SimpleTestCase):
    def test_sitemap_lists_convert(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "/convert/")


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
