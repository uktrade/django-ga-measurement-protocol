from django.urls import path

from .testapp.views import MiddlewareTestView, MiddlewareTestErrorView

urlpatterns = [
    path("test-middleware", MiddlewareTestView.as_view(), name="test-middleware"),
    path(
        "test-middleware-error-from-view",
        MiddlewareTestErrorView.as_view(),
        name="test-middleware-error-from-view",
    ),
]
