from django.urls import path
from . import views

urlpatterns = [
    path('chat_image_editor/', views.chat_image_editor, name='chat_image_editor'),
    path('generate_chat_image_editor/', views.generate_chat_image_editor, name='generate_chat_image_editor'),
]
