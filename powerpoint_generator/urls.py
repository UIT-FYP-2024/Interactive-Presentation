from django.urls import path
from . import views

urlpatterns = [
    path('powerpoint_generator', views.powerpoint_generator, name='powerpoint_generator'),
]
