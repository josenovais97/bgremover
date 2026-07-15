from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "remover"

urlpatterns = [
    path("", views.index, name="index"),
    path("convert/", views.convert, name="convert"),
    path("compress/", views.compress, name="compress"),
    path("meme-maker/", views.meme, name="meme"),
    path("passport-photo/", views.passport, name="passport"),
    path("passport-photo/<slug:country>/", views.passport_country, name="passport_country"),
    # The AI upscaler was removed (client-side super-resolution froze the tab).
    # Keep the indexed URL alive with a 301 to home so it never 404s — for search
    # engines and for old service-worker caches that still request it.
    path("upscale/", RedirectView.as_view(pattern_name="remover:index", permanent=True)),
    path("ecommerce/", views.ecommerce, name="ecommerce"),
    path("blur-background/", views.blur, name="blur"),
    # /portrait-mode/ was merged into /blur-background/ (same tool). 301 so the
    # indexed URL keeps its link equity instead of 404-ing.
    path("portrait-mode/", RedirectView.as_view(pattern_name="remover:blur", permanent=True)),
    path("api/stats/", views.stats, name="stats"),
    path("instagram/", views.instagram, name="instagram"),
    path("crop/", views.crop, name="crop"),
    path("favicon-generator/", views.favicon_generator, name="favicon"),
    path("sticker-maker/", views.sticker, name="sticker"),
    path("text-behind-image/", views.text_behind, name="text_behind"),
    path("remove-background/<slug:slug>/", views.use_case, name="use_case"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("sw.js", views.service_worker, name="sw"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("favicon.ico", RedirectView.as_view(url=static("img/favicon.ico"), permanent=False)),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    # Yandex Webmaster site-ownership verification file.
    path("yandex_ee6a725348d1a333.html", views.yandex_verify, name="yandex_verify"),
]
