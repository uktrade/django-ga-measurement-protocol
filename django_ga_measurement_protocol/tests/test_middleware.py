from unittest import mock

from django.test import override_settings, TestCase
from django.urls import reverse


@override_settings(
    MIDDLEWARE=[
        "django_ga_measurement_protocol.middleware.page_view_tracking_middleware"
    ],
    ROOT_URLCONF="django_ga_measurement_protocol.tests.urls",
)
class PageViewTrackingMiddlewareTestCase(TestCase):
    @mock.patch("django_ga_measurement_protocol.middleware.track_page_view")
    def test_page_view_called_on_view(self, mock_track_page_view):
        response = self.client.get(reverse("test-middleware"))
        mock_track_page_view.assert_called_once_with(response.wsgi_request)

    @mock.patch("django_ga_measurement_protocol.middleware.track_page_view")
    def test_page_view_with_error_not_called_on_view(self, mock_track_page_view):
        with self.assertRaises(Exception):
            self.client.get(reverse("test-middleware-error-from-view"))
        mock_track_page_view.assert_not_called()

    @mock.patch("django_ga_measurement_protocol.middleware.track_page_view")
    def test_page_view_with_404_not_called_on_view(self, mock_track_page_view):
        self.client.get("/madeup-url/")
        mock_track_page_view.assert_not_called()
