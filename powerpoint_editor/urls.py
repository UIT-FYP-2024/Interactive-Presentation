from django.urls import path
from . import views

urlpatterns = [
    path('powerpoint_editor', views.powerpoint_editor, name='powerpoint_editor'),
]
