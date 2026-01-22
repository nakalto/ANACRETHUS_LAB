
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import Repository
from branches.models import Branch
from commits.models import Commit


#Dashboard view 
@login_required
def home_dashboard(request):
    #Get repository owned by log-in user 
    user_repos = Repository.objects.filter(owner=request.user).order_by('-created_at')
    #Render dashboard template with repos
    return render(request, 'repos/home_dashboard.html', {'user_repos': user_repos})


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
        #add readme
        add_readme = request.POST.get('add_readme') == 'on'
        # Validate presence of a repository name before creation
        if not name:
            # Add an error message for missing name
            messages.error(request, 'Repository name is required.')
            # Re-render the form template with current context
            return render(request, 'repos/repo_create.html')
        # Create the repository record linked to the current user
        repo = Repository.objects.create(owner=request.user, name=name, description=description)
        # Inform the user that the repository was created successfully

        #auto-create default branch "main "
        branch = Branch.objects.create(repo=repo, name='main', owner=request.user)

        #if "add README " selected, create first commit 
        if add_readme:
            Commit.objects.create(
                branch=branch,
                message="Add README",
                snapshot_text="#" + name + "\n\n" + (description or "Initial README "),
                author=request.user
            )
        messages.success(request, f'Repository "{repo.name}" created.')
        # Redirect to the repository list page after creation
        return redirect('repos:list')
    # For GET requests, render the creation form template
    return render(request, 'repos/repo_create.html')


#Repository detail page 
@login_required
def repo_detail(request, repo_id):
    #fetch repository or return 404 
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    #get branch default main 
    default_branch  = Branch.objects.filter(repo=repo, name='main').first()

    #get commits for default branch
    commits = Commit.objects.filter(branch=default_branch).order_by('-created_at') if default_branch else []

    #Render template with repo, branch and commits 
    return render(request, 'repos/repo_detail.html', {
        'repo':repo,
        'default_branch': default_branch,
        'commits': commits,
    }) 