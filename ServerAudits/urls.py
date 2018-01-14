"""ServerAudits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from audit import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^login/', views.auth_login,name='login'),
    url(r'^logout/', views.auth_logout, name='logout'),
    url(r'^host_list/', views.get_host_list, name='get_host_list'),
    url(r'^generate_token/', views.generate_token, name='generate_token'),
    url(r'^massive_cmd/', views.massive_cmd, name='massive_cmd'),
    url(r'^massive_process/', views.massive_process, name='massive_process'),
    url(r'^massive_process_result/', views.massive_process_result, name='massive_process_result'),
    url(r'^massive_files/', views.massive_files, name='massive_files'),
    url(r'^file_receive/', views.file_receive, name='file_receive'),
    url(r'^tansfer_file_to_user/', views.tansfer_file_to_user, name='tansfer_file_to_user'),

]
