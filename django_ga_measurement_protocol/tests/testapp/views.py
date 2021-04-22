from django.http import HttpResponse
from django.views import View


class MiddlewareTestView(View):

    def get(self, request):
        return HttpResponse("OK")
