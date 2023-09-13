from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



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
    path('update_wallpaper/', views.update_wallpaper, name='update_wallpaper'),


     path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
     path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
     path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
     path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),



    path('user_upload/', views.user_upload, name='user_upload'),
    path('user_edit/', views.user_edit_wallpaper, name='user_edit'),
    path('view_delete_userwallpaper/', views.view_delete_userwallpaper, name='view_delete_userwallpaper'),  
       
           
    path('wallpaper/<int:wallpaper_id>/', views.wallpaper_details, name='wallpaper_details'),
    # path('search/', views.search_wallpapers, name='search_wallpapers'),
    path('liked_wallpapers/', views.liked_wallpapers, name='liked_wallpapers'),
    path('subscribe_page/', views.subscribe_page, name='subscribe_page'),
    
    
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
