from django.urls import include, path

# No admin: the app has no models or database. All routes live in the app.
urlpatterns = [
    path("", include("remover.urls")),
]
