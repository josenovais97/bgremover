"""Template context processors."""
from django.conf import settings

from config.middleware import ISOLATED_VIEWS

from .views import USE_CASES


def seo(request):
    """Expose SEO verification tokens and shared nav/ad data to all templates."""
    # Ads run on the marketing / SEO landing pages ONLY — the interactive tool
    # pages stay ad-free and fast (and the cross-origin-isolated ones would block
    # ad frames via COEP anyway). `ISOLATED_VIEWS` is imported so this decision
    # stays visibly tied to the middleware's isolation logic.
    match = getattr(request, "resolver_match", None)
    url_name = match.url_name if match is not None else None
    ads_allowed = url_name == "use_case" and url_name not in ISOLATED_VIEWS
    return {
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
        # Landing pages are surfaced in the footer of every page so internal
        # links reach them from anywhere on the site.
        "use_cases": USE_CASES,
        # Monetization: expose the AdSense config only where ads are allowed.
        "adsense_client": settings.ADSENSE_CLIENT if ads_allowed else "",
        "adsense_slot_landing": settings.ADSENSE_SLOT_LANDING,
    }
