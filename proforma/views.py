from django.http import HttpResponse

def ping(request):
    return HttpResponse("Proforma app está funcionando.")
