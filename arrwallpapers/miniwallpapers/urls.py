from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static



urlpatterns=[
    path('',views.index ,name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('userprofile', views.userprofile, name='userprofile'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('Premium_signup', views.Premium_signup, name='Premium_signup'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),


    path('upload_wallpaper/', views.upload_wallpaper, name='upload_wallpaper'),
    path('view_delete_wallpaper/', views.view_delete_wallpaper, name='view_delete_wallpaper'),
     path('view_delete_wallpaper/', views.view_delete_wallpaper, name='view_delete_wallpaper'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)