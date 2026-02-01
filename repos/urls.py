# Import Django path function for URL routing
from django.urls import path

# Import views from current app
from . import views

# Define app namespace for reverse URL lookups
app_name = 'repos'

# URL patterns for repository app
urlpatterns = [
    # Dashboard (homepage) – shows overall user dashboard
    path('', views.home_dashboard, name='home'),

    # List repositories – shows all repos owned by the logged-in user
    path('list/', views.repo_list, name='list'),

    # Create repository – form to create a new repo
    path('create/', views.repo_create, name='create'),

    # Repository detail – requires repo_id, shows repo overview
    path('<int:repo_id>/', views.repo_detail, name='detail'),

    # Pull latest commit snapshot as ZIP – download repo contents
    path('<int:repo_id>/pull/', views.repo_pull, name='pull'),

    # File view – open individual file from latest commit
    # Use <path:filename> instead of <str:filename> so nested paths like "src/main/App.java" work
    path('<int:repo_id>/<int:branch_id>/<path:filename>/', views.file_view, name='file_view'),

    # Repository code view – shows file tree and commit history
    path('<int:repo_id>/code/', views.repo_code, name='code'),
]
