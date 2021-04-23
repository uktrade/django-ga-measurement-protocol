# Django Google Analytics Measurement Protocol integration

## Usage

### Installation

```bash
pip install django-ga-measurement-protocol
```

### Middleware

The most basic usage is to install the page view middleware:

```python
MIDDLEWARE = [
    ...
    "django_ga_measurement_protocol.middleware.page_view_tracking_middleware",
    ...
]
```

and configure the required settings:

```python
GA_MEASUREMENT_PROTOCOL_UA = "<tracking id>"  # The tracking id for your property
GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS = True  # By default the package won't do any tracking unless explicitly set
```

### Additional functions

There are additional functions that allow for custom tracking beyond what the the middleware provides.

```python
from django_ga_measurement_protocol.track import (
    track_event,
    track_page_view,
)

def a_view(request):
    # Tracks an event in Google Analytics
    track_event(
        request,
        category="Category",  # required
        action="Action",  # required
        label="Label",  # optional
        value="5",  # optional
    )

    # Tracks a page view in Google Analytics
    track_page_view(request)
```

The above functions will extract the basic required information from the Django request that is required to register an event/page view in Google Analytics.

If more customisation is required there are additional functions that allow fully custom data to be sent to Google Analytics.

```python
from django_ga_measurement_protocol.track import (
    build_tracking_data,
    send_tracking_data,
)

def a_view(request):
    # Builds tracking data with default information from the Django request
    tracking_data = build_tracking_data(
        request,
        {
            "additional-value": "value",
        },
    )

    # Sends tracking data to Google analytics
    send_tracking_data(tracking_data)
```

The values that are accepted by the measurement protocol can be found [here](https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters).

### Debug

When sending data to Google Analytics, by default, nearly all data is accepted even if it is missing required data or is corrupted in some other way. However, there is a facility for Google Analytics to respond with some validation data for your events.

To turn this on set the following settings:

```python
GA_MEASUREMENT_PROTOCOL_DEBUG = True

LOGGING = {
    ...
    'loggers': {
        ...
        'django_ga_measurement_protocol': {
            'level': logging.DEBUG,
            'handlers': 'console'
        },
    },
}
```

This will log the validation in the response returned from Google Analytics.

This should **not** be used in production.

## Development

### Installation

It is recommended to initialise a virtualenv of your choice.

```bash
pip install -r requirements.txt
```

### Formatting

Formatting is done via Black and a pre-commit hook should be installed.

```bash
pre-commit install
```
