from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("api/ask/", views.ask),
    path("sw.js", views.service_worker),
]
