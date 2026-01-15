from django.urls import path
from .import views

app_name = 'repos'

urlpatterns = [
    path('', views.repo_list, name='list' ),
    path('create/', views.repo_create, name='create'),
    
]