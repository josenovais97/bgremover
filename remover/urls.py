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
    path("upscale/", views.upscaler, name="upscaler"),
    path("instagram/", views.instagram, name="instagram"),
    path("crop/", views.crop, name="crop"),
    path("favicon-generator/", views.favicon_generator, name="favicon"),
    path("sticker-maker/", views.sticker, name="sticker"),
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
]
