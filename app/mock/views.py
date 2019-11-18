from django.http import HttpResponse

def index(request):
    return HttpResponse("<html>This is a mock page <body><h1>Hey you!</body></html>")
