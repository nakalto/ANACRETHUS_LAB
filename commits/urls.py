
from django.urls import path
from . import views

app_name = 'commits'


urlpatterns = [
    
    path('create/', views.commit_create, name='create'),
    path('list/<int:branch_id>/', views.commit_list, name='list'),

    path('<int:repo_id>/<int:branch_id>/push/', views.commit_push, name='push'),
    path('<int:commit_id>/', views.commit_detail, name='detail'),
]
