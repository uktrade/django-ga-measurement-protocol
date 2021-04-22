from django.urls import path

from .testapp.views import MiddlewareTestView

urlpatterns = [
    path("test-middleware", MiddlewareTestView.as_view(), name="test-middleware"),
]
