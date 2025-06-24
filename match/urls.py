from django.urls import path
from . import views

urlpatterns = [
    
    path('matches/', views.match_list_create, name='match-list-create'),
    path('matches/<int:pk>/', views.match_detail, name='match-detail'),
    path('matches/filter/', views.match_filter, name='match-filter'),  # New endpoint
   
]