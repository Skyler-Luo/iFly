from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('cities/', views.CityListView.as_view(), name='city_list'),
    path('popular-routes/', views.PopularRouteListView.as_view(), name='popular_routes'),
]