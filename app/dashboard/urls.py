from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"introduction", IntroductionViewSet, basename="introduction")
router.register(r"couevent", CouEventViewSet, basename="couevent")
router.register(r"couevent-types", CouEventTypeViewSet, basename="couevent-type")
router.register(r"news", NewsViewSet, basename="news")
router.register(r"news-types", NewsTypeViewSet, basename="news-type")
router.register(r"faq", FaqViewSet, basename="faq")
router.register(r"faq-types", FaqTypeViewSet, basename="faq-type")
router.register(r"literature", LiteratureViewSet, basename="literature")
router.register(r"literature-types", LiteratureTypeViewSet, basename="literature-type")
router.register(r"form-link", FormLinkViewSet, basename="form-link")

urlpatterns = [
    path("", include(router.urls)),
]
