from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView

from . import views
from .views import COMPARISONS, COMPRESS_PAGES, TOOL_LANDINGS

app_name = "remover"

urlpatterns = [
    path("", views.index, name="index"),
    path("convert/", views.convert, name="convert"),
    path("compress/", views.compress, name="compress"),
    path("meme-maker/", views.meme, name="meme"),
    path("passport-photo/", views.passport, name="passport"),
    path("passport-photo/<slug:country>/", views.passport_country, name="passport_country"),
    # The AI upscaler once lived here, was removed (super-resolution froze the
    # tab), and the URL 301'd to home. It is now back as a safe Lanczos-resample
    # upscaler, reclaiming the indexed URL.
    path("upscale/", views.upscale, name="upscale"),
    path("remove-object/", views.remove_object, name="remove_object"),
    path("photo-filters/", views.photo_filters, name="photo_filters"),
    path("heic-to-jpg/", views.heic, name="heic"),
    path("pdf-to-image/", views.pdf_to_image, name="pdf_to_image"),
    path("word-to-pdf/", views.word_to_pdf, name="word_to_pdf"),
    path("pdf-to-word/", views.pdf_to_word, name="pdf_to_word"),
    path("merge-pdf/", views.pdf_tools, name="pdf_tools"),
    path("csv-to-excel/", views.csv_excel, name="csv_excel"),
    path("image-to-text/", views.ocr, name="ocr"),
    path("svg-to-png/", views.svg_to_png, name="svg_to_png"),
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
    path("qr-code-generator/", views.qr, name="qr"),
    path("redact-image/", views.redact, name="redact"),
    path("exif-remover/", views.exif, name="exif"),
    path("resize-image/", views.resize, name="resize"),
    path("watermark-image/", views.watermark, name="watermark"),
    path("gif-maker/", views.gif, name="gif"),
    path("video-to-gif/", views.video_gif, name="video_gif"),
    path("video-converter/", views.video_converter, name="video_converter"),
    path("image-to-pdf/", views.image_to_pdf, name="pdf"),
    path("color-palette/", views.palette, name="palette"),
    path("collage/", views.collage, name="collage"),
    path("add-border/", views.border, name="border"),
    path("base64-image/", views.base64_image, name="base64"),
    path("screenshot-beautifier/", views.screenshot, name="screenshot"),
    path("remove-bg-alternative/", views.alternative, name="alternative"),
    # Privacy-angle landing pages (see PRIVACY_PAGES). Explicit routes keep the
    # keyword-rich top-level URLs; each maps to the shared privacy_page view.
    path("private-image-tools/", views.privacy_page, {"slug": "private-image-tools"}, name="priv_hub"),
    path("remove-background-without-uploading/", views.privacy_page, {"slug": "remove-background-without-uploading"}, name="priv_no_upload"),
    path("offline-image-editor/", views.privacy_page, {"slug": "offline-image-editor"}, name="priv_offline"),
    # Compress intent-variants (see COMPRESS_PAGES) — keyword-rich top-level URLs,
    # generated from the data so a new variant is a one-line data addition.
    *[
        path(f"{p['slug']}/", views.compress_page, {"slug": p["slug"]}, name=p["url_name"])
        for p in COMPRESS_PAGES
    ],
    # Comparison pages (see COMPARISONS), generated from the data.
    *[
        path(f"{p['slug']}/", views.comparison, {"slug": p["slug"]}, name=p["url_name"])
        for p in COMPARISONS
    ],
    # Tool intent-variant landings (see TOOL_LANDINGS), generated from the data.
    *[
        path(f"{p['slug']}/", views.tool_landing, {"slug": p["slug"]}, name=p["url_name"])
        for p in TOOL_LANDINGS
    ],
    path("remove-background/<slug:slug>/", views.use_case, name="use_case"),
    # Editorial guides (see remover/guides.py). Unlike every other route here,
    # these do not front a tool — they are the site's only standalone content.
    path("guides/", views.guides_index, name="guides"),
    path("guides/<slug:slug>/", views.guide_detail, name="guide"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("sw.js", views.service_worker, name="sw"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("favicon.ico", RedirectView.as_view(url=static("img/favicon.ico"), permanent=False)),
    path("healthz", views.healthz, name="healthz"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    # Yandex Webmaster site-ownership verification file.
    path("yandex_ee6a725348d1a333.html", views.yandex_verify, name="yandex_verify"),
]
