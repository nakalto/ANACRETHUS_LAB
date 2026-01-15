
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Repository

# Define a view to list repositories for the current user
@login_required
def repo_list(request):
    # Query repositories owned by the authenticated user
    repos = Repository.objects.filter(owner=request.user).order_by('-created_at')
    # Render the list template with repositories context
    return render(request, 'repos/repo_list.html', {'repos': repos})

# Define a view to create a new repository
@login_required
def repo_create(request):
    # If the request is POST, process submitted form data
    if request.method == 'POST':
        # Extract the repository name from the form input
        name = request.POST.get('name', '').strip()
        # Extract optional description from the form input
        description = request.POST.get('description', '').strip()
        # Validate presence of a repository name before creation
        if not name:
            # Add an error message for missing name
            messages.error(request, 'Repository name is required.')
            # Re-render the form template with current context
            return render(request, 'repos/repo_create.html')
        # Create the repository record linked to the current user
        repo = Repository.objects.create(owner=request.user, name=name, description=description)
        # Inform the user that the repository was created successfully
        messages.success(request, f'Repository "{repo.name}" created.')
        # Redirect to the repository list page after creation
        return redirect('repos:list')
    # For GET requests, render the creation form template
    return render(request, 'repos/repo_create.html')
