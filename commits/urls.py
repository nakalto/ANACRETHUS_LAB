# Import path for URL route declarations
from django.urls import path
# Import local views for commit actions
from . import views

# Set namespace for URL reversing
app_name = 'commits'

# Declare URLs for commit creation and listing
urlpatterns = [
    # Map /create/ to commit creation view
    path('create/', views.commit_create, name='create'),
    # Map /list/<int:branch_id>/ to list commits for a branch
    path('list/<int:branch_id>/', views.commit_list, name='list'),
]
