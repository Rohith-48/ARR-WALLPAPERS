from django.urls import path
from . import views

urlpatterns=[
    path('',views.index ,name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('userprofile', views.userprofile, name='userprofile'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('Premium_signup', views.Premium_signup, name='Premium_signup'),
]