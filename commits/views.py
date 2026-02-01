from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Commit
from branches.models import Branch
from repos.models import Repository
from core.utils import contains_secret
from django.contrib.auth.decorators import login_required

# Create your views here.
# Define a view to create a commit with secret blocking
@login_required
def commit_create(request):
    if request.method == 'POST':
        # Extract branch_id from form to associate commit
        branch_id = request.POST.get('branch_id')
        # Extract commit message describing the changes
        message = request.POST.get('message', '').strip()
        # Extract snapshot_text that simulates code changes
        snapshot_text = request.POST.get('snapshot_text', '').strip()

        # Fetch the target branch or return 404 if invalid
        branch = get_object_or_404(Branch, id=branch_id)
        # Ensure the branch belongs to a repository
        repo = branch.repo

        # If the snapshot contains secrets, block commit and show error
        if contains_secret(snapshot_text):
            messages.error(request, 'Commit blocked: potential secret detected in snapshot.')
            return render(request, 'commits/commit_create.html', {'branch': branch})

        # Build snapshot dictionary (for now treat snapshot_text as a single file)
        snapshot_data = {
            "code.txt": snapshot_text or "# Empty commit"
        }

        # Create the commit record linked to branch, author and repo
        commit = Commit.objects.create(
            repo=repo,
            branch=branch,
            author=request.user,
            message=message or "Initial commit",
            snapshot=snapshot_data,
            status='pending',
        )

        # Inform user of successful commit creation
        messages.success(request, 'Commit created and queued for scanning.')
        # Redirect to the commit list view for the branch
        return redirect('commits:list', branch_id=branch_id)

    # For GET request require a branch_id via query string to prefill the form
    branch_id = request.GET.get('branch_id')
    branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
    return render(request, 'commits/commit_create.html', {'branch': branch})


# Define a view to list commits for a specific branch
@login_required  # Require the user to be logged in
def commit_list(request, branch_id):
    # Retrieve the branch object by ID, or return 404 if not found
    branch = get_object_or_404(Branch, id=branch_id)

    # Query all commits for this branch, ordered by newest first
    commits = Commit.objects.filter(branch=branch).order_by('-created_at')

    # Render the commit list template, passing branch and commits
    return render(request, 'commits/commit_list.html', {
        'branch': branch,   # Branch object
        'commits': commits  # List of commits
    })


# Define a view to handle commit pushes (uploading files to a branch)
@login_required  # Require the user to be logged in
def commit_push(request, repo_id, branch_id):

    # Fetch the repository and ensure it belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Fetch the branch and ensure it belongs to the repository
    branch = get_object_or_404(Branch, id=branch_id, repo=repo)

    # Only process form submission (POST request)
    if request.method == 'POST':

        # Get commit message from form (default if empty)
        message = request.POST.get('message', 'Push code')

        # Dictionary to store all uploaded files and their metadata
        snapshot_data = {}

        # Define extensions that should ALWAYS be treated as text
        text_extensions = (
            '.html', '.xml', '.css', '.js', '.md',
            '.py', '.java', '.c', '.cpp', '.h',
            '.php', '.rb', '.go', '.ts', '.json',
            '.txt', '.ini', '.cfg', '.yml', '.yaml'
        )

        # Loop through all uploaded files (supports folder upload via webkitdirectory)
        for file in request.FILES.getlist('files'):

            # Preserve relative path (important for folder structure)
            relative_path = file.name

            # Read raw file bytes ONCE
            data = file.read()

            # Default classification
            content = None
            is_text = False

            # Normalize extension check (case insensitive)
            if relative_path.lower().endswith(text_extensions):

                # 🔥 Force decode as UTF-8 text for known source files
                # Use 'replace' so decoding never crashes
                content = data.decode('utf-8', errors='replace')
                is_text = True

            else:
                # Attempt to decode unknown files as UTF-8 first
                try:
                    content = data.decode('utf-8')
                    is_text = True
                except UnicodeDecodeError:
                    # If decoding fails → treat as binary and store Base64
                    import base64
                    content = base64.b64encode(data).decode('ascii')
                    is_text = False

            # Store file entry in snapshot dictionary
            snapshot_data[relative_path] = {
                'content': content,   # Text content OR Base64 string
                'is_text': is_text,   # Whether file is text or binary
                'size': len(data),    # File size in bytes
            }

        # Create commit record in database
        Commit.objects.create(
            repo=repo,
            branch=branch,
            author=request.user,
            message=message,
            snapshot=snapshot_data,
            status='pending'
        )

        # Notify user of successful push
        messages.success(
            request,
            f'Pushed {len(snapshot_data)} files to branch "{branch.name}".'
        )

        # Redirect back to repository detail page
        return redirect('repos:detail', repo_id=repo.id)

    # If GET request → render push form page
    return render(request, 'commits/commit_push.html', {
        'repo': repo,
        'branch': branch
    })



# Commit detail view
def commit_detail(request, commit_id):
    # Fetch commit by ID
    commit = get_object_or_404(Commit, id=commit_id)
    # Render template with commit info
    return render(request, 'commits/commit_detail.html', {
        'commit': commit,
        'repo': commit.repo,
        'branch': commit.branch,
    })
