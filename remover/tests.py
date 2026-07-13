"""Tests for the remover views and SEO endpoints."""
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

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

    def test_upscaler_renders(self):
        response = self.client.get(reverse("remover:upscaler"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "remover/upscaler.html")
        self.assertContains(response, "up-dropzone")
        self.assertContains(response, "Upscaler")

    def test_new_tools_in_sitemap(self):
        response = self.client.get(reverse("remover:sitemap"))
        self.assertContains(response, "/passport-photo/")
        self.assertContains(response, "/upscale/")

    def test_new_tools_in_nav(self):
        response = self.client.get(reverse("remover:index"))
        self.assertContains(response, reverse("remover:passport"))
        self.assertContains(response, reverse("remover:upscaler"))


class CrossOriginIsolationTests(SimpleTestCase):
    """COOP+COEP (isolation) is scoped to the WASM background-removal pages."""

    def test_isolated_pages_get_coep(self):
        for name in ("index", "instagram", "sticker", "passport"):
            response = self.client.get(reverse(f"remover:{name}"))
            self.assertEqual(response["Cross-Origin-Embedder-Policy"], "credentialless", name)

    def test_upscaler_is_not_isolated(self):
        # The upscaler uses the WebGL/GPU backend and must NOT be isolated, so
        # its third-party model fetches aren't constrained by COEP.
        response = self.client.get(reverse("remover:upscaler"))
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
        for name in ("index", "upscaler", "convert"):
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
