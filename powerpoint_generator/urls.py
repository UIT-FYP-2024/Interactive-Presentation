from django.urls import path
from . import views

urlpatterns = [
    path('powerpoint_generator', views.powerpoint_generator, name='powerpoint_generator'),
    path('generate_presentation', views.generate_presentation, name='generate_presentation'),
]
