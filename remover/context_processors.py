"""Template context processors."""
from django.conf import settings

from .views import USE_CASES


def seo(request):
    """Expose SEO verification tokens and shared nav data to all templates."""
    return {
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
        # Landing pages are surfaced in the footer of every page so internal
        # links reach them from anywhere on the site.
        "use_cases": USE_CASES,
    }
