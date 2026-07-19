

from django.urls import path
from internal import views
urlpatterns = [
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    path('internal_dashboard', views.internal_dashboard, name='internal_dashboard'),
    path('players_who_visited/', views.players_who_visited_view, name='players_who_visited'),
    path('players_with_a_profile/', views.players_with_a_profile_view, name='players_with_a_profile'),
    path('get_cities_for_state/', views.get_cities_for_state, name='get_cities_for_state'),

]
