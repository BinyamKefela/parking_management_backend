"""
URL configuration for parking_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include


from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView)

from django.conf import settings
from vpms.views import CustomTokenObtainPairView
from django.conf.urls.static import static

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('vpms.urls')),                     # login, logout
    #path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # registration
    #path('api/auth/social/', include('allauth.socialaccount.urls')),     # for account connections
    #path('api/auth/social/login/', include('dj_rest_auth.social_urls')),


    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path("api/v1/auth/social/login/", GoogleLogin.as_view(), name="google_login"),




    path('api/token',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh'),
    path('api/token/verify/',TokenVerifyView.as_view(),name='token_verify'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
