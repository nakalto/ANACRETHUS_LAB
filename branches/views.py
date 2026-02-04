
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Branch
from repos.models import Repository
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



@login_required
def branch_merge(request, repo_id):

    # Fetch the repository and ensure it belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve all branches inside this repository
    branches = Branch.objects.filter(repo=repo)

    # If request is POST, it means user submitted the merge form
    if request.method == "POST":

        # Get selected source branch ID from form submission
        source_branch_id = request.POST.get("source_branch_id")

        # Get selected target branch ID from form submission
        target_branch_id = request.POST.get("target_branch_id")

        # Fetch source branch and ensure it belongs to this repository
        source_branch = get_object_or_404(Branch, id=source_branch_id, repo=repo)

        # Fetch target branch and ensure it belongs to this repository
        target_branch = get_object_or_404(Branch, id=target_branch_id, repo=repo)

        # Prevent user from merging a branch into itself
        if source_branch == target_branch:
            messages.error(request, "Cannot merge a branch into itself.")
            return redirect("branches:merge", repo_id=repo.id)

        # Get latest commit from source branch 
        source_commit = source_branch.commits.order_by("-created_at").first()

        # Get latest commit from target branch
        target_commit = target_branch.commits.order_by("-created_at").first()

        # If source branch has no commits, merging is meaningless
        if not source_commit:
            messages.error(request, f'No commits found in source branch "{source_branch.name}".')
            return redirect("branches:merge", repo_id=repo.id)

        # Start with target snapshot if it exists, otherwise start empty
        merged_snapshot = target_commit.snapshot.copy() if target_commit else {}

        # Update target snapshot with source snapshot (simple overwrite strategy)
        merged_snapshot.update(source_commit.snapshot)

        # Create a new merge commit in the target branch
        Commit.objects.create(
            repo=repo,                         # Link to repository
            branch=target_branch,              # Merge goes into target branch
            author=request.user,               # Logged-in user is the author
            message=f'Merge "{source_branch.name}" into "{target_branch.name}"',
            snapshot=merged_snapshot,          # Save merged file state
            status="merged"                    # Mark commit as merged
        )

        # Notify user that merge was successful
        messages.success(
            request,
            f'Branch "{source_branch.name}" successfully merged into "{target_branch.name}".'
        )

        # Redirect back to repository detail page
        return redirect("repos:detail", repo_id=repo.id)

    # If request is GET, render the merge form page
    return render(request, "branches/branch_merge.html", {
        "repo": repo,           # Pass repository to template
        "branches": branches,   # Pass branch list for dropdown selection
    })

