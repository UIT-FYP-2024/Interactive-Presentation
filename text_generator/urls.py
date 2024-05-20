from django.urls import path
from . import views

urlpatterns = [
    path('chat_text', views.chat_text, name='chat_text'),
    path('generate_chat/', views.generate_chat, name='generate_chat'),
]
