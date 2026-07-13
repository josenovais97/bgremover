from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

# No admin: the app has no models or database. All routes live in the app.
#
# Everything is wrapped in i18n_patterns so the site is available in English at
# the root and in Portuguese under /pt/. `prefix_default_language=False` keeps
# the English URLs unprefixed (so existing links, the sitemap and the service
# worker at the root are unchanged), while Portuguese pages live at /pt/….
urlpatterns = i18n_patterns(
    path("", include("remover.urls")),
    prefix_default_language=False,
)
