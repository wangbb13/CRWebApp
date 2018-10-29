# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_index'),
    path('auxiliary/', views.auxiliary, name='main_auxiliary'),
    path('auxiliary/add/', views.add_city, name='main_add'),
    path('auxiliary/search/', views.search_city, name='main_search_city'),
    path('auxiliary/add_search_city/', views.add_search_data, name='main_add_search_data'),
]
