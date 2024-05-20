from django.urls import path
from authentication import views


urlpatterns = [

    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('sign_out', views.sign_out, name='sign_out'),
    path('recover_password', views.recover_password, name='recover_password'),
    path('reset_password', views.reset_password, name='reset_password'),
]
