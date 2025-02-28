from .views import (
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)
from django.urls import path
from dance import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name="home"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path('app_users_login/', views.app_users_login, name='app_users_login'),
    path('app_users_logout/', views.app_users_logout, name='app_users_logout'),
    path('check-username/', views.check_username, name='check_username'),
    path('register/', views.register, name='register'),
    # 用户设置
    path('management_platform/user_settings/', views.user_settings, name='user_settings'),
    path('change_password/', views.change_password, name='change_password'),
    path('api/update_personal_info/', views.update_personal_info, name='update_personal_info'),
    path('password_reset/', 
         CustomPasswordResetView.as_view(), 
         name='password_reset'),
    
    path('password_reset/done/', 
         CustomPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    # 舞蹈管理平台
    path('management_platform/dashboard/', views.dashboard, name='dashboard'),
    path('management_platform/artists_info/', views.artists_info, name='artists_info'),
    path('save_artist/', views.save_artist, name='save_artist'),
    path('management_platform/artist_detail/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('api/artist/<int:artist_id>/performances', views.get_performances_by_date, name='artist_performances'),
    path('api/performance/<int:performance_id>', views.get_performance_detail, name='performance_detail'),
    path('api/performance/<int:performance_id>/attendance', views.update_performance_attendance, name='update_performance_attendance'),
    path('api/artist/<int:artist_id>/trainings', views.get_trainings_by_date, name='artist_trainings'),
    path('api/training/<int:training_id>', views.get_training_detail, name='training_detail'),
    path('api/training/<int:training_id>/attendance', views.update_training_attendance, name='update_training_attendance'),
    path('delete_artist/<int:artist_id>/', views.delete_artist, name='delete_artist'),
    path('management_platform/performances/', views.performances, name='performances'),
    path('management_platform/performance_detail/<int:performance_id>/', views.performance_detail, name='performance_detail'),
    path('save_performance/', views.save_performance, name='save_performance'),
    path('delete_performance/<int:performance_id>/', views.delete_performance, name='delete_performance'),
    path('management_platform/trainings/', views.trainings, name='trainings'),
    path('management_platform/training_detail/<int:training_id>/', views.training_detail, name='training_detail'),
    path('save_training/', views.save_training, name='save_training'),
    path('delete_training/<int:training_id>/', views.delete_training, name='delete_training'),
    path('management_platform/activities/', views.activities, name='activities'),
    path('management_platform/settings/', views.settings_page, name='settings_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
