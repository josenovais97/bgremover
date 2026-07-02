from django.urls import path

from . import views

app_name = "remover"

urlpatterns = [
    path("", views.index, name="index"),
    path("convert/", views.convert, name="convert"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
]
