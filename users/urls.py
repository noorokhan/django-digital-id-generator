from django.urls import path
from users import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('user_details/', views.user_details, name='user_details'),
    path('next-view/', views.next_view, name='next_view'),
    path('generate_id/', views.generate_id, name='generate_id'),
    path('download_id/', views.download_id, name='download_id'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
