from .track import track_page_view


def page_view_tracking_middleware(get_response):
    def middleware(request):
        response = get_response(request)

        if response.status_code == 200:
            track_page_view(request)

        return response

    return middleware
