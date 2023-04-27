from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render

from signage.models import Display

def diagnosis_view(request, display_code):
    display = get_object_or_404(Display, code=display_code)

    schedule_item = display.get_current_schedule_item()
    page = None

    if schedule_item:
        sequence_item = schedule_item.get_current_sequence_item()
        if sequence_item:
            page = sequence_item.page
    
    return render(request, 'signage/debug.html', {'display': display, 'schedule': schedule_item, 'page': page})

def display_view(request, display_code):
    display = get_object_or_404(Display, code=display_code)
    
    return render(request, 'signage/display.html', {'display': display})

def connected_view(request):
    return render(request, 'signage/connected.html')

def grid_view(request):
    displays = Display.objects.order_by('code')[:16]

    return render(request, 'signage/grid.html', {'displays': displays})

def landing_view(request):
    displays = Display.objects.all()

    return render(request, 'signage/landing.html', {'displays': displays})