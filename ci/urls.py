
from django.urls import path
from . import views


app_name = 'ci'


urlpatterns = [
    
    path('run/<int:commit_id>/', views.run_scan, name='run'),
]
