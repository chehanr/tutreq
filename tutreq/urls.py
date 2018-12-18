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

import core.views as views
import core.views_ajax as ajax_views
import core.views_gen as gen_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('feedback/', views.feedback, name='feedback'),
    path('feedback/<str:ref>/', views.feedback, name='feedback'),

    path('manage/', views.manage, name='manage'),

    path('about/', views.about, name='about'),

    path('gen/pdf/', gen_views.generate_pdf, name='generate_pdf'),
    path('gen/csv/', gen_views.generate_csv, name='generate_csv'),

    path('ajax/slots_search/', ajax_views.slots_search, name='ajax_slots_search'),
    path('ajax/request_info/', ajax_views.request_info,
         name='ajax_request_info'),
    path('ajax/request_count/', ajax_views.request_count,
         name='ajax_request_count'),
    path('ajax/dismiss_relodge_request/', ajax_views.dismiss_relodge_request,
         name='ajax_dismiss_relodge_request'),
    path('ajax/archive_unarchive_request/', ajax_views.archive_unarchive_request,
         name='ajax_archive_unarchive_request'),
]
