"""tutreq URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

import core.views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.request_form, name='request_form'),
    path('feedback/', core_views.request_feedback, name='request_feedback'),
    path('feedback/<str:ref>/', core_views.request_feedback,
         name='request_feedback'),
    path('manage/', core_views.requests_manage, name='requests_manage'),

    path('generate_pdf/', core_views.generate_pdf, name='generate_pdf'),
    path('generate_csv/', core_views.generate_csv, name='generate_csv'),
    path('generate_csv/<str:rid>/', core_views.generate_csv, name='generate_csv'),

    path('slots_info_json/', core_views.slots_info_json, name='slots_info_json'),
    path('request_info_json/', core_views.request_info_json,
         name='request_info_json'),
    path('dismiss_relodge_request/', core_views.dismiss_relodge_request,
         name='dismiss_relodge_request'),
]
