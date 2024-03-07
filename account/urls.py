from django.contrib import admin
from django.urls import path, include
from .views import UserRegistrationsview,UserLoginView,UserDetail,changeUserPasswordView,SendPasswordResetView,UserPasswordRestView

urlpatterns = [
    path('register/user/',UserRegistrationsview.as_view(),name='user_registrations'),
    path('login/user/',UserLoginView.as_view(),name='user_login'),
    path('user/user-details/',UserDetail.as_view(),name='user_detail'),
    path('changepassword/',changeUserPasswordView.as_view(),name='change-password'),
    path('send-reset-password-email/',SendPasswordResetView.as_view(),name='send-rest-password-email'),
    path('password-reset/<uid>/<token>/',UserPasswordRestView.as_view(),name='rest-password'),
]
