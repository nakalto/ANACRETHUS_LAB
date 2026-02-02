from django.urls import path
from . import views

app_name = 'repos'

urlpatterns = [
    
    # Dashboard + Repo Management
    path('', views.home_dashboard, name='home'),              
    path('list/', views.repo_list, name='list'),              
    path('create/', views.repo_create, name='create'),        

    
    
    path('<int:repo_id>/', views.repo_detail, name='detail'), 
    path('<int:repo_id>/code/', views.repo_code, name='code'),
    path('<int:repo_id>/pull/', views.repo_pull, name='pull'),
    path('<int:repo_id>/<int:branch_id>/<path:filename>/', 
         views.file_view, name='file_view'),                  

    # Commits
    path('<int:repo_id>/commits/', views.repo_commits, name='repo_commits'),

    # Branches
    path('<int:repo_id>/branches/', views.repo_branches, name='repo_branches'),

    # Issues (placeholder)
    path('<int:repo_id>/issues/', views.repo_issues, name='repo_issues'),

    # Pull Requests (collaboration workflow, placeholder)
    path('<int:repo_id>/pulls/', views.repo_pulls, name='repo_pulls'),

    # CI Dashboard
    path('<int:repo_id>/ci/', views.repo_ci, name='repo_ci'),

    # Security Dashboard
    path('<int:repo_id>/security/', views.repo_security, name='repo_security'),

    # Repo Settings
    path('<int:repo_id>/settings/', views.repo_settings, name='repo_settings'),

    
    path('<int:repo_id>/delete/', views.repo_delete, name='delete'),

]
