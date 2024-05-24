from django.urls import path
from . import views

urlpatterns = [
    path('powerpoint_generator', views.generate_presentation, name='powerpoint_generator'),
]
