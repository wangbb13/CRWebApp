# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_index'),
    path('yard_info/', views.yard_info, name='main_yard_info'),
    path('auxiliary/', views.auxiliary, name='main_auxiliary'),
    path('auxiliary/add/', views.add_city, name='main_add'),
    path('auxiliary/search/', views.search_city, name='main_search_city'),
    path('auxiliary/add_search_city/', views.add_search_data, name='main_add_search_data'),
    path('get_stream_info/', views.get_stream_info, name='get_stream_info')
]
