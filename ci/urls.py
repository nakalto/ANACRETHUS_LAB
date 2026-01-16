# Import path to define URL routes
from django.urls import path
# Import local views to handle scanning
from . import views

# Set namespace for URL reversing
app_name = 'ci'

# Declare URL pattern for running a scan on a given commit ID
urlpatterns = [
    # Map /run/<commit_id>/ to the run_scan view
    path('run/<int:commit_id>/', views.run_scan, name='run'),
]
