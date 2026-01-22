from django.urls import path
from .import views

app_name = 'repos'

urlpatterns = [
    path('', views.home_dashboard, name='home'),
    path('list/', views.repo_list, name='list' ),
    path('create/', views.repo_create, name='create'),
    path('<int:repo_id>/', views.repo_detail, name='detail'),
    
    
]