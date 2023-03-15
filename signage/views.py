from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render

from signage.models import Display

# Create your views here.
def display_view(request, display_code):
    display = get_object_or_404(Display, code=display_code)
    
    return render(request, 'signage/display.html', {'display': display})