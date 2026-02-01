from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    # Create a new branch in a repo
    path('<int:repo_id>/create/', views.branch_create, name='create'),

    # Merge two branches in a repo
    path('<int:repo_id>/merge/', views.branch_merge, name='merge'),
]
