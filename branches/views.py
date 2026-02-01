# Import shortcut functions for rendering templates, redirects, and fetching objects or 404
from django.shortcuts import render, redirect, get_object_or_404
# Import decorator to require login for views
from django.contrib.auth.decorators import login_required
# Import Django messages framework for success/error notifications
from django.contrib import messages
# Import Branch model (represents branches inside repos)
from .models import Branch
# Import Repository model (represents repositories)
from repos.models import Repository
# Import Commit model (represents commits inside branches)
from commits.models import Commit



# View to create a new branch
@login_required  # Require user to be logged in
def branch_create(request, repo_id):
    # Fetch repository by ID for current user, or return 404 if not found
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # If request is POST, process submitted form data
    if request.method == 'POST':
        # Extract branch name from form input
        name = request.POST.get('name', '').strip()

        # Validate presence of branch name
        if not name:
            # Add error message if name is missing
            messages.error(request, 'Branch name is required.')
            # Re-render form template with repo context
            return render(request, 'branches/branch_create.html', {'repo': repo})

        # Prevent duplicate branch names per repo
        if Branch.objects.filter(repo=repo, name=name).exists():
            # Show error if branch already exists
            messages.error(request, f'Branch "{name}" already exists in this repository.')
            # Re-render form template with repo context
            return render(request, 'branches/branch_create.html', {'repo': repo})

        # Create branch record linked to repo and current user
        Branch.objects.create(repo=repo, name=name, owner=request.user)
        # Inform user of successful branch creation
        messages.success(request, f'Branch "{name}" created successfully.')
        # Redirect to repository detail page
        return redirect('repos:detail', repo_id=repo.id)

    # For GET requests, render branch creation form
    return render(request, 'branches/branch_create.html', {'repo': repo})


# View to merge two branches
@login_required  # Require user to be logged in
def branch_merge(request, repo_id, source_branch_id, target_branch_id):
    # Fetch repository by ID for current user, or return 404 if not found
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)
    # Fetch source branch by ID for this repo, or return 404 if not found
    source_branch = get_object_or_404(Branch, id=source_branch_id, repo=repo)
    # Fetch target branch by ID for this repo, or return 404 if not found
    target_branch = get_object_or_404(Branch, id=target_branch_id, repo=repo)

    # Get latest commit from source branch
    source_commit = source_branch.commit_set.order_by('-created_at').first()
    # Get latest commit from target branch
    target_commit = target_branch.commit_set.order_by('-created_at').first()

    # If source branch has no commits, block merge
    if not source_commit:
        # Show error message
        messages.error(request, f'No commits found in source branch "{source_branch.name}".')
        # Redirect back to repo detail page
        return redirect('repos:detail', repo_id=repo.id)

    # Merge snapshots (simple overwrite: source overwrites target)
    merged_snapshot = target_commit.snapshot if target_commit else {}
    merged_snapshot.update(source_commit.snapshot)

    # Create merge commit in target branch
    Commit.objects.create(
        repo=repo,
        branch=target_branch,
        author=request.user,
        message=f'Merge branch "{source_branch.name}" into "{target_branch.name}"',
        snapshot=merged_snapshot,
        status='merged'
    )

    # Inform user of successful merge
    messages.success(request, f'Branch "{source_branch.name}" merged into "{target_branch.name}".')
    # Redirect back to repo detail page
    return redirect('repos:detail', repo_id=repo.id)
