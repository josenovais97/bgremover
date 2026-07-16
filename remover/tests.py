"""Tests for the remover views and SEO endpoints."""
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from remover.context_processors import TOOL_ACCENTS
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
        for tool, (surface, hover, text_dark) in TOOL_ACCENTS.items():
            with self.subTest(tool=tool):
                # Surface + hover carry white text, in both themes.
                for role, value in (("surface", surface), ("hover", hover)):
                    ratio = self._ratio(self._rgb(value), self.WHITE)
                    self.assertGreaterEqual(
                        ratio, self.AA,
                        f"{tool} {role} ({value}) is {ratio:.2f}:1 against white text; "
                        f"needs {self.AA}:1 — use a darker shade.",
                    )
                # text_dark is the accent as text on the dark surface.
                ratio = self._ratio(self._rgb(text_dark), self.DARK)
                self.assertGreaterEqual(
                    ratio, self.AA,
                    f"{tool} text_dark ({text_dark}) is {ratio:.2f}:1 on the dark "
                    f"surface; needs {self.AA}:1 — use a lighter shade.",
                )

    def test_accent_table_is_well_formed(self):
        for tool, value in TOOL_ACCENTS.items():
            with self.subTest(tool=tool):
                self.assertEqual(len(value), 3, f"{tool}: expected (surface, hover, text_dark)")
                for part in value:
                    self.assertEqual(len(self._rgb(part)), 3, f"{tool}: {part!r} is not 'R G B'")


class AccentWiringTests(SimpleTestCase):
    """The accent only reaches the page if the view actually emits the variables."""

    def test_tool_page_emits_all_three_accent_vars(self):
        response = self.client.get(reverse("remover:resize"))
        surface, hover, text_dark = TOOL_ACCENTS["resize"]
        self.assertContains(response, f"--color-primary: {surface}")
        self.assertContains(response, f"--color-primary-hover: {hover}")
        self.assertContains(response, f"--accent-text-dark: {text_dark}")

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
