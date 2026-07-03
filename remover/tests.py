"""Tests for the remover views and SEO endpoints."""
import json

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from remover.views import FAQS, USE_CASES, faq_jsonld


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
        self.assertContains(response, "Frequently asked questions")
        self.assertContains(response, "Batch processing")
        self.assertContains(response, '"@type": "FAQPage"')

    def test_index_sets_security_headers(self):
        response = self.client.get(reverse("remover:index"))
        self.assertIn("Content-Security-Policy", response)
        self.assertIn("Permissions-Policy", response)
        self.assertIn("wasm-unsafe-eval", response["Content-Security-Policy"])


class FaqStructuredDataTests(SimpleTestCase):
    """The FAQ rich-result markup must stay in sync with the visible FAQ."""

    def test_jsonld_covers_every_faq(self):
        data = json.loads(faq_jsonld(FAQS))
        self.assertEqual(data["@type"], "FAQPage")
        names = {q["name"] for q in data["mainEntity"]}
        self.assertEqual(names, {f["q"] for f in FAQS})

    def test_jsonld_escapes_angle_brackets(self):
        # The payload sits inside a <script> tag, so a raw "<" would be unsafe.
        self.assertNotIn("<", faq_jsonld([{"q": "a <b>", "a": "c"}]))

    def test_page_renders_every_faq_question_in_markup(self):
        response = self.client.get(reverse("remover:index"))
        for faq in FAQS:
            self.assertContains(response, faq["q"])


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
