from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns=[
    path('',views.index ,name='index'),
    path('retrival', views.retrival, name='retrival'),
    path('ai_wallpaper_generator/', views.ai_wallpaper_generator, name='ai_wallpaper_generator'),
    #  path('upscaleimage/', views.upscaleimage, name='upscaleimage'),
    path('add_comment/<int:wallpaper_id>/', views.add_comment, name='add_comment'),

    path('set_premium_status/', views.set_premium_status, name='set_premium_status'),
    path('login/', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('logout/', views.custom_logout, name='logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('userprofile', views.user_profile, name='userprofile'),
    path('profile/<str:username>/', views.profileview, name='profileview'),

    path('category/<str:category>/', views.category_filter, name='category_filter'),

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
    path('restore_wallpaper/', views.restore_wallpaper, name='restore_wallpaper'),
    path('recyclebin/', views.recyclebin, name='recyclebin'),
           
    path('wallpaper/<int:wallpaper_id>/', views.wallpaper_details, name='wallpaper_details'),
    path('liked_wallpapers/', views.liked_wallpapers, name='liked_wallpapers'),
    path('subscribe_page/', views.subscribe_page, name='subscribe_page'),
    path('premiumuserpage/', views.premiumuserpage, name='premiumuserpage'),
    path('paymentform/', views.paymentform, name='paymentform'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),


    path('successpage/', views.successpage, name='successpage'),
    path('errorpage/', views.errorpage, name='errorpage'),
    path('Billinginfo/', views.Billinginfo, name='Billinginfo'),


    path('contactform/', views.contactform, name='contactform'),
    path('about/', views.about, name='about'),
    path('termsofservice/', views.termsofservice, name='termsofservice'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),


    path('community/', views.community, name='community'),
    path('send_message/', views.send_message, name='send_message'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
