from django.urls import path

from .views import (
    home,
    register_page,
    login_page,
    profile_page,
    logout_page,
    registration_api,
    registration_detail_api
)


urlpatterns = [


    path(
        '',
        home,
        name='home'
    ),



    path(
        'register/',
        register_page,
        name='register'
    ),



    path(
        'login/',
        login_page,
        name='login'
    ),

    path(
        'profile/',
        profile_page,
        name='profile'
    ),



    path(
        'logout/',
        logout_page,
        name='logout'
    ),


    path(
        'api/registrations/',
        registration_api,
        name='registrations'
    ),


    path(
        'api/registrations/<int:id>/',
        registration_detail_api,
        name='registration_detail'
    ),
]