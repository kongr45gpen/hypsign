from django.urls import path

from . import views

urlpatterns = [
    path('display/<display_code>/', views.display_view, name='display_view'),
]