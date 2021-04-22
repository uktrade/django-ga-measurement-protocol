from django.urls import path

from .views import MiddlewareTestView

urlpatterns = [
    path("test-middleware", MiddlewareTestView.as_view(), name="test-middleware"),
]
