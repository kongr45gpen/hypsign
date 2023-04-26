from django.urls import path

from . import views

urlpatterns = [
    path('connected/', views.connected_view, name='connected_view'),
    path('diag/<display_code>/', views.diagnosis_view, name='diagnosis_view'),
    path('display/<display_code>/', views.display_view, name='display_view'),
    path('grid/', views.grid_view, name='grid_view'),
]