from django.urls import path
from dashboard import views

urlpatterns = [

    path('index/', views.index, name='index'),
    path('documents/', views.recent_documents, name='recent_documents'),
    path('tutorials/', views.tutorials, name='tutorials'),
]
