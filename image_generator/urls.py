from django.urls import path
from . import views

urlpatterns = [
    path('chat_image/', views.chat_image, name='chat_image'),
    path('generate_chat/', views.generate_chat_image, name='generate_chat'),
]
