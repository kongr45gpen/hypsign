from django.urls import path

from . import views

urlpatterns = [
    path('diag/<display_code>/', views.diagnosis_view, name='diagnosis_view'),
    path('display/<display_code>/', views.display_view, name='display_view'),
]