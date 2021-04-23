import requests_mock
import uuid

from unittest import mock

from django.test import override_settings, RequestFactory, TestCase

from ..track import (
    API_VERSION,
    build_tracking_data,
    DEBUG_GOOGLE_ANALYTICS_ENDPOINT,
    GOOGLE_ANALYTICS_ENDPOINT,
    send_tracking_data,
    track_event,
    track_page_view,
)


FAKE_GA_ID = "ua-12345-1"


def get_request_data(request):
    return request.qs


@override_settings(
    GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS=True,
    GA_MEASUREMENT_PROTOCOL_UA=FAKE_GA_ID,
)
class TrackingTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch("django_ga_measurement_protocol.track.uuid")
    def test_build_tracking_data(self, mock_uuid):
        mock_uuid_value = uuid.uuid4()
        mock_uuid.uuid4.return_value = mock_uuid_value

        url = "/test-url/"
        remote_addr = "127.0.0.1"
        http_user_agent = "user-agent-string"
        http_referer = "http://example.com"

        request = self.factory.get(
            url,
            REMOTE_ADDR=remote_addr,
            HTTP_USER_AGENT=http_user_agent,
            HTTP_REFERER=http_referer,
        )

        tracking_data = build_tracking_data(
            request,
            {
                "test-key": "test-value",
            },
        )

        self.assertEqual(
            tracking_data,
            {
                "aip": "1",
                "cid": str(mock_uuid_value),
                "dl": f"http://testserver{url}",
                "dr": http_referer,
                "tid": FAKE_GA_ID,
                "ua": http_user_agent,
                "uip": remote_addr,
                "v": API_VERSION,
                "test-key": "test-value",
            },
        )

    @requests_mock.Mocker()
    def test_send_tracking_data(self, mock_requests):
        m = mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        send_tracking_data({"test-key": "test-value"})
        request = m.request_history[0]
        data = get_request_data(request)

        self.assertEqual(
            data,
            {"test-key": ["test-value"]},
        )

    @override_settings(
        GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS=False,
    )
    @requests_mock.Mocker()
    def test_send_tracking_data_settings_disabled(self, mock_requests):
        m = mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        send_tracking_data({"test-key": "test-value"})
        self.assertEqual(len(m.request_history), 0)

    @override_settings(
        GA_MEASUREMENT_PROTOCOL_DEBUG=True,
    )
    @requests_mock.Mocker()
    @mock.patch("django_ga_measurement_protocol.track.logger")
    def test_send_tracking_data_settings_disabled(self, mock_requests, mock_logger):
        mock_body = {
            "key": "value",
        }
        m = mock_requests.post(
            DEBUG_GOOGLE_ANALYTICS_ENDPOINT,
            json=mock_body,
        )

        send_tracking_data({})
        self.assertEqual(len(m.request_history), 1)
        mock_logger.debug.assert_called_with(
            "Tracking response: %s",
            mock_body,
        )

    @requests_mock.Mocker()
    @mock.patch("django_ga_measurement_protocol.track.uuid")
    def test_track_event(self, mock_requests, mock_uuid):
        mock_uuid_value = uuid.uuid4()
        mock_uuid.uuid4.return_value = mock_uuid_value
        m = mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        original_request = self.factory.get(
            "/test-url/",
            HTTP_USER_AGENT="user-agent-string",
            HTTP_REFERER="http://example.com",
        )
        common_data_params = {
            "v": [API_VERSION],
            "tid": [FAKE_GA_ID],
            "cid": [str(mock_uuid_value)],
            "uip": ["127.0.0.1"],
            "aip": ["1"],
            "ua": ["user-agent-string"],
            "dr": ["http://example.com"],
            "dl": ["http://testserver/test-url/"],
            "t": ["event"],
        }

        track_event(
            original_request,
            "test_category",
            "test_action",
        )
        request = m.request_history[0]
        data = get_request_data(request)
        self.assertEqual(
            data,
            {
                **common_data_params,
                **{
                    "ec": ["test_category"],
                    "ea": ["test_action"],
                },
            },
        )

        track_event(
            original_request,
            "test_category_2",
            "test_action_2",
            "test_label",
            "test_value",
        )
        request = m.request_history[1]
        data = get_request_data(request)
        self.assertEqual(
            data,
            {
                **common_data_params,
                **{
                    "ec": ["test_category_2"],
                    "ea": ["test_action_2"],
                    "el": ["test_label"],
                    "ev": ["test_value"],
                },
            },
        )

    @requests_mock.Mocker()
    @mock.patch("django_ga_measurement_protocol.track.uuid")
    def test_track_page_view(self, mock_requests, mock_uuid):
        mock_uuid_value = uuid.uuid4()
        mock_uuid.uuid4.return_value = mock_uuid_value
        m = mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        original_request = self.factory.get(
            "/test-url/",
            HTTP_USER_AGENT="user-agent-string",
            HTTP_REFERER="http://example.com",
        )

        track_page_view(original_request)

        request = m.request_history[0]
        data = get_request_data(request)
        self.assertEqual(
            data,
            {
                "v": [API_VERSION],
                "tid": [FAKE_GA_ID],
                "cid": [str(mock_uuid_value)],
                "uip": ["127.0.0.1"],
                "aip": ["1"],
                "ua": ["user-agent-string"],
                "dr": ["http://example.com"],
                "dl": ["http://testserver/test-url/"],
                "t": ["pageview"],
            },
        )

    @requests_mock.Mocker()
    def test_unique_user_id(self, mock_requests):
        m = mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        original_request = self.factory.get("/test-url/")

        user_ids = []
        for i in range(20):
            track_event(
                original_request,
                "test_category",
                "test_action",
            )
            request = m.request_history[i]
            data = get_request_data(request)
            user_ids.append(data["cid"][0])

        self.assertEqual(
            len(user_ids),
            len(set(user_ids)),
        )

        m.reset()

        user_ids = []
        for i in range(20):
            track_page_view(original_request)
            request = m.request_history[i]
            data = get_request_data(request)
            user_ids.append(data["cid"][0])

        self.assertEqual(
            len(user_ids),
            len(set(user_ids)),
        )
