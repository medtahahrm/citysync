from django.http import HttpResponse
from django.urls import reverse

def test_view(request):
    try:
        url = reverse('incidents:incident_list')
        return HttpResponse(f"URL works: {url}")
    except Exception as e:
        return HttpResponse(f"Error: {e}")
