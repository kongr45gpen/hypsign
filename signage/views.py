from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render

from signage.models import Display

def diagnosis_view(request, display_code):
    display = get_object_or_404(Display, code=display_code)

    schedule_item = display.get_current_schedule_item()
    
    return render(request, 'signage/debug.html', {'display': display, 'schedule': schedule_item})

def display_view(request, display_code):
    display = get_object_or_404(Display, code=display_code)
    
    return render(request, 'signage/display.html', {'display': display})

def connected_view(request):
    return render(request, 'signage/connected.html')