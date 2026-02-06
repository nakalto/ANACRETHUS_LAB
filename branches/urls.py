from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    
    path('<int:repo_id>/create/', views.branch_create, name='create'),

    path('<int:repo_id>/merge/', views.branch_merge, name='merge'),
]
