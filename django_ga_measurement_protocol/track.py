import logging
import requests
import scrubadub
import uuid

from ipware import get_client_ip
from urllib.parse import parse_qsl, urlencode, urlparse

from django.conf import settings


logger = logging.getLogger(__name__)

# For an overview of all of the available parameters available to be sent to GA:
# https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters

API_VERSION = "1"

GOOGLE_ANALYTICS_ENDPOINT = "https://www.google-analytics.com/collect"
DEBUG_GOOGLE_ANALYTICS_ENDPOINT = "https://www.google-analytics.com/debug/collect"

UNKNOWN_IP_ADDRESS = "192.0.2.0"


_scrubber = scrubadub.Scrubber()
_scrubber.remove_detector("name")


def _scrub_data(data):
    scrubbed_data = data.copy()

    if "dl" in data:
        components = urlparse(scrubbed_data["dl"])
        scrubbed_query = [
            (k, _scrubber.clean(v)) for k, v in parse_qsl(components.query)
        ]
        scrubbed_query = urlencode(scrubbed_query, safe="{}")
        components = components._replace(query=scrubbed_query)
        scrubbed_data["dl"] = components.geturl()

    to_scrub = ["el", "ea"]
    for key in to_scrub:
        if key not in scrubbed_data:
            continue
        value = scrubbed_data[key]
        scrubbed_data[key] = _scrubber.clean(value)

    return scrubbed_data


def build_tracking_data(request, additional_data):
    client_ip, _ = get_client_ip(request)
    client_ip = client_ip or UNKNOWN_IP_ADDRESS

    data = {
        "v": API_VERSION,  # API Version.
        "tid": settings.GA_MEASUREMENT_PROTOCOL_UA,  # Tracking aID / Property ID.
        "cid": str(
            uuid.uuid4()
        ),  # This needs to be cid not uid or your events won't register in the behaviour section
        "uip": client_ip,  # User ip override
        "aip": "1",  # Anonymise user ip
        "ua": request.META.get("HTTP_USER_AGENT"),  # User agent override
        "dr": request.META.get("HTTP_REFERER"),  # Document referrer
        "dl": request.build_absolute_uri(),  # Document location URL
        **additional_data,
    }

    data = _scrub_data(data)

    return data


def send_tracking_data(tracking_data):
    if not getattr(settings, "GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS", False):
        return

    if getattr(settings, "GA_MEASUREMENT_PROTOCOL_DEBUG", False):
        response = requests.post(
            DEBUG_GOOGLE_ANALYTICS_ENDPOINT,
            params=tracking_data,
        )
        logger.debug("Tracking response: %s", response.json())
    else:
        response = requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
            params=tracking_data,
        )

    return response


def track_event(request, category, action, label=None, value=None):
    event_data = {
        "t": "event",
        "ec": category,
        "ea": action,
    }
    if label:
        event_data["el"] = label

    if value:
        event_data["ev"] = value

    data = build_tracking_data(request, event_data)

    return send_tracking_data(data)


def track_page_view(request):
    page_view_data = {
        "t": "pageview",
    }

    data = build_tracking_data(request, page_view_data)

    return send_tracking_data(data)
