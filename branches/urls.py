# Import path for URL routing
from django.urls import path
# Import views from current app
from . import views

# Define app namespace for reverse URL lookups
app_name = 'branches'

# Define URL patterns for branch actions
urlpatterns = [
    # Route for listing branches of a repository
    path('list/<int:repo_id>/', views.branch_list, name='list'),
    # Route for creating a new branch in a repository
    path('create/<int:repo_id>/', views.branch_create, name='create'),
]
