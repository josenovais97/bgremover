"""Template context processors."""
from django.conf import settings


def seo(request):
    """Expose search-engine verification tokens to all templates."""
    return {
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "bing_site_verification": settings.BING_SITE_VERIFICATION,
    }
