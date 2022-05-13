"""apply_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path

from apply_system.views.main import Main
mainobject = Main()

urlpatterns = [
    path('reset_password/', mainobject.handle_request),
    path('', mainobject.handle_request),
    path('login/', mainobject.handle_request),
    path('logout/', mainobject.handle_request),
    path('apply_enterprise/', mainobject.handle_request),
    path('get_remained_info/', mainobject.handle_request),
    path('desc/', mainobject.handle_request),
    path('confirm_data/', mainobject.handle_request),
    path('get_confirm_data/', mainobject.handle_request),
    path('meeting/', mainobject.handle_request),
]

# urlpatterns = [
#     path('reset_password/', reset_password.handle_request),
#     path('', main.handle_main_page_request),
#     path('login/', apply_enterprise.handle_login_request),
#     path('logout/', apply_enterprise.handle_logout_request),
#     path('apply_enterprise/', apply_enterprise.handle_apply_enterprise_request),
#     path('get_remained_info/', apply_enterprise.handle_get_remained_info_request),
#     path('desc/', main.handle_desc_request),
# ]
