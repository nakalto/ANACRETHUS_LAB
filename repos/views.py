# Import decorator to require login for views
from django.contrib.auth.decorators import login_required

# Import shortcuts for rendering templates, redirecting, and fetching objects or 404
from django.shortcuts import render, redirect, get_object_or_404

# Import Django messages framework for success/error notifications
from django.contrib import messages

# Import HttpResponse for returning file downloads
from django.http import HttpResponse

# Import Python standard libraries for in-memory streams and ZIP file creation
import io
import zipfile

# Import Repository model from current app
from .models import Repository

# Import Branch model from branches app
from branches.models import Branch

# Import Commit model from commits app
from commits.models import Commit

from ci.models import ScanResult
from django.db.models import Count




# Dashboard view (homepage)
@login_required  # Require user to be logged in
def home_dashboard(request):
    # Query repositories owned by the current user, newest first
    user_repos = Repository.objects.filter(owner=request.user).order_by('-created_at')
    # Render dashboard template with repos context
    return render(request, 'repos/home_dashboard.html', {'user_repos': user_repos})



# List repositories
@login_required  # Require login
def repo_list(request):
    # Query repositories owned by the current user, newest first
    repos = Repository.objects.filter(owner=request.user).order_by('-created_at')
    # Render list template with repos context
    return render(request, 'repos/repo_list.html', {'repos': repos})



# Create a new repository
@login_required  # Require login
def repo_create(request):
    # If request is POST, process submitted form data
    if request.method == 'POST':
        # Extract repository name from form input
        name = request.POST.get('name', '').strip()
        # Extract optional description from form input
        description = request.POST.get('description', '').strip()
        # Extract visibility option (public/private)
        is_private = request.POST.get('visibility') == 'private'
        # Extract checkbox for README creation
        add_readme = request.POST.get('add_readme') == 'on'
        # Extract gitignore option (future extension)
        gitignore = request.POST.get('gitignore', '')
        # Extract license option (future extension)
        license = request.POST.get('license', '')

        # Validate presence of repository name
        if not name:
            # Add error message if name is missing
            messages.error(request, 'Repository name is required.')
            # Re-render form template
            return render(request, 'repos/repo_create.html')

        # Prevent duplicate repo names per user
        if Repository.objects.filter(owner=request.user, name=name).exists():
            # Show error if repo already exists
            messages.error(request, f'A repository named "{name}" already exists.')
            # Re-render form template
            return render(request, 'repos/repo_create.html')

        # Create repository record linked to current user
        repo = Repository.objects.create(
            owner=request.user,
            name=name,
            description=description,
            is_private=is_private

            
        )

        # Auto-create default branch "main"
        branch = Branch.objects.create(repo=repo, name='main', owner=request.user)

        # If "Add README" selected, create first commit with README content
        if add_readme:
            readme_content = "# " + name + "\n\n" + (description or "Initial README")
            # Build snapshot dictionary with README file
            snapshot_data = {
                "README.md": {
                    "content": readme_content,
                    "is_text": True,
                    "size": len(readme_content),
                }
            }
            # Create commit record linked to branch and repo
            Commit.objects.create(
                repo=repo,
                branch=branch,
                author=request.user,
                message="Add README",
                snapshot=snapshot_data,
                status='pending'
            )

        # Inform user of successful repository creation
        messages.success(request, f'Repository "{repo.name}" created successfully.')
        # Redirect to repository detail page
        return redirect('repos:detail', repo_id=repo.id)

    # For GET requests, render repository creation form
    return render(request, 'repos/repo_create.html')



# Function to build a file tree from the latest commit snapshot
def build_file_tree_with_commit(latest_commit):
    """
    Convert the latest commit snapshot into a nested tree structure.
    Each node is either a folder (is_dir=True, children={}) or a file (is_dir=False).
    Attach commit metadata to each file node.
    Handles both dict-style snapshot entries and legacy string entries.
    """
    tree = {}
    if latest_commit and latest_commit.snapshot:
        for path, file_entry in latest_commit.snapshot.items():
            # Normalize path
            parts = path.strip("/").split("/")
            node = tree
            # Traverse folders except last part
            for part in parts[:-1]:
                node = node.setdefault(part, {"is_dir": True, "children": {}})["children"]

            # Handle both dict and string cases
            if isinstance(file_entry, dict):
                content = file_entry.get("content")
                is_text = file_entry.get("is_text", True)
                size = file_entry.get("size", 0)
            else:
                # Legacy case: file_entry is just a string
                content = str(file_entry)
                is_text = True
                size = len(content)

            # Add file node with commit info
            node[parts[-1]] = {
                "is_dir": False,
                "path": path,
                "content": content,
                "is_text": is_text,
                "size": size,
                "commit_message": latest_commit.message,
                "commit_date": latest_commit.created_at,
                "commit_hash": latest_commit.id,
                "commit_author": latest_commit.author.username,
            }
    return tree




# View function to display repository details
def repo_detail(request, repo_id):
    # Fetch the repository object by ID, ensuring it belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve the default branch (commonly named "main") for this repository
    default_branch = Branch.objects.filter(repo=repo, name='main').first()

    # Get all commits associated with the default branch, ordered from oldest to newest
    # If no default branch exists, return an empty list
    commits = Commit.objects.filter(branch=default_branch).order_by('created_at') if default_branch else []

    # If commits exist, build a file tree from the latest commit snapshot
    if commits:
        # Get the most recent commit on the branch
        latest_commit = commits.last()
        # Build a nested file tree structure from the commit snapshot
        file_tree = build_file_tree_with_commit(latest_commit)
    else:
        # If no commits exist, set file_tree to None
        file_tree = None

    # Render the repository detail template with the context data
    return render(request, 'repos/repo_detail.html', {
        'repo': repo,                 # Repository object
        'default_branch': default_branch,  # Default branch object
        'commits': commits,           # List of commits for the branch
        'file_tree': file_tree,       # Nested file tree from the latest commit snapshot
    })


    



# Pull latest commit snapshot as ZIP
@login_required  # Require login
def repo_pull(request, repo_id):
    # Fetch repository by ID for current user, or return 404 if not found
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Get default branch "main"
    branch = Branch.objects.filter(repo=repo, name='main').first()

    # Get latest commit for that branch
    latest_commit = Commit.objects.filter(branch=branch).order_by('-created_at').first()

    # If no commit exists, show error and redirect
    if not latest_commit:
        messages.error(request, "No commits to pull.")
        return redirect('repos:detail', repo_id=repo.id)

    # Create in-memory buffer for ZIP file
    buffer = io.BytesIO()
    # Open ZIP file in write mode
    with zipfile.ZipFile(buffer, 'w') as zf:
        # Loop through files in snapshot and add to ZIP
        for filename, entry in latest_commit.snapshot.items():
            if isinstance(entry, dict):
                # Handle new dict-style entries
                if entry.get("is_text", True):
                    # Text files → write content directly
                    zf.writestr(filename, entry.get("content", ""))
                else:
                    # Binary files → decode Base64 before writing
                    import base64
                    zf.writestr(filename, base64.b64decode(entry.get("content", "")))
            else:
                # Legacy case: entry is just a string
                zf.writestr(filename, str(entry))

    # Reset buffer pointer to start
    buffer.seek(0)

    # Build HTTP response with ZIP file
    response = HttpResponse(buffer, content_type='application/zip')
    # Set filename for download
    response['Content-Disposition'] = f'attachment; filename={repo.name}.zip'
    return response




# Require the user to be logged in before accessing repository code
@login_required
def repo_code(request, repo_id, path=""):
    # Fetch the repository object by ID, ensuring it belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve the default branch (commonly 'main') for this repository
    branch = Branch.objects.filter(repo=repo, name='main').first()

    # Get the latest commit on this branch (ordered newest first)
    latest_commit = Commit.objects.filter(branch=branch).order_by('-created_at').first()

    # If no commit exists or snapshot is empty, render an empty code page
    if not latest_commit or not latest_commit.snapshot:
        return render(request, 'repos/repo_code.html', {
            'repo': repo,       # Repository object
            'branch': branch,   # Branch object
            'files': [],        # No files to display
            'path': path,       # Current path (empty or provided)
        })

    # NOTE: This implementation only shows files from the latest commit snapshot (GitHub-style).
    # If you want to show all files ever pushed, you would need to merge snapshots from all commits.

    # Initialize dictionary to hold files/folders for the current path
    files = {}

    # Loop through each file path in the latest commit snapshot
    for filename, content in latest_commit.snapshot.items():
        # Only include files that start with the current path (to support folder navigation)
        if filename.startswith(path):
            # Strip the current path prefix to get relative path
            relative = filename[len(path):].lstrip("/")

            # Split relative path into parts (folders/files)
            parts = relative.split("/")

            # If only one part, it's a file directly under this path
            if len(parts) == 1:
                files[parts[0]] = {
                    "is_dir": False,       # Flag indicating this is a file
                    "content": content,    # File content or metadata
                }
            # Otherwise, it's a folder containing deeper files
            else:
                files[parts[0]] = {
                    "is_dir": True,        # Flag indicating this is a folder
                }

    # Render the code template with repository, branch, files, and current path
    return render(request, 'repos/repo_code.html', {
        'repo': repo,       # Repository object
        'branch': branch,   # Branch object
        'files': files,     # Dictionary of files/folders for current path
        'path': path,       # Current path being viewed
    })



# Require the user to be logged in before allowing file view
@login_required
def file_view(request, repo_id, branch_id, filename):
    # Retrieve the repository object by ID, ensuring it belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve the branch object by ID, ensuring it belongs to the repository
    branch = get_object_or_404(Branch, id=branch_id, repo=repo)

    # Find the latest commit that contains this file in its snapshot
    commit = Commit.objects.filter(branch=branch, snapshot__has_key=filename).order_by('-created_at').first()

    # If no commit contains this file, show an error and redirect back to code view
    if not commit:
        messages.error(request, f"File '{filename}' not found in commits.")
        return redirect('repos:code', repo_id=repo.id)

    # Extract the file entry from the snapshot
    file_entry = commit.snapshot[filename]

    # Handle both dict-style entries (new commits) and string-style entries (legacy commits)
    if isinstance(file_entry, dict):
        # Extract metadata from dictionary
        is_text = file_entry.get('is_text', True)
        file_size = file_entry.get('size', 0)

        if is_text:
            # Safe to render text content directly
            content = file_entry.get('content', '')
        else:
            # Binary file → never render Base64 directly
            # Instead show a safe placeholder
            content = "[Binary file not displayed]"
    else:
        # Legacy case: file_entry is just a string
        content = str(file_entry)
        is_text = True
        file_size = len(content)

    # Pass all relevant data to the template
    return render(request, 'repos/file_view.html', {
        'repo': repo,                         # Repository object
        'branch': branch,                     # Branch object
        'filename': filename,                 # File name/path
        'content': content,                   # File content or placeholder
        'is_text': is_text,                   # Flag: text or binary
        'file_size': file_size,               # File size in bytes
        'commit_message': commit.message,     # Commit message
        'commit_author': commit.author.username,  # Commit author username
        'commit_date': commit.created_at,     # Commit timestamp
    })





# Repository Commits Page


@login_required
def repo_commits(request, repo_id):

    # Ensure the repository exists and belongs to the logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Fetch all commits for this repository ordered newest first
    commits = Commit.objects.filter(repo=repo).order_by('-created_at')

    # Render repository commits page
    return render(request, "repos/repo_commits.html", {
        "repo": repo,
        "commits": commits,
    })


# Repository Branches Page

@login_required
def repo_branches(request, repo_id):

    # Ensure repository belongs to user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve all branches ordered by creation date
    branches = Branch.objects.filter(repo=repo).order_by('created_at')

    # Attach latest commit to each branch (for display purposes)
    branch_data = []
    for branch in branches:
        latest_commit = Commit.objects.filter(branch=branch).order_by('-created_at').first()
        branch_data.append({
            "branch": branch,
            "latest_commit": latest_commit
        })

    # Render branch management page
    return render(request, "repos/repo_branches.html", {
        "repo": repo,
        "branch_data": branch_data,
    })



# Repository CI Dashboard


@login_required
def repo_ci(request, repo_id):

    # Ensure repository belongs to current user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve commits with their CI status
    commits = Commit.objects.filter(repo=repo).order_by('-created_at')

    # Count CI status summary for quick stats
    ci_summary = commits.values('status').annotate(count=Count('status'))

    # Render CI dashboard
    return render(request, "repos/repo_ci.html", {
        "repo": repo,
        "commits": commits,
        "ci_summary": ci_summary,
    })



# Repository Security Dashboard


@login_required
def repo_security(request, repo_id):

    # Ensure repository belongs to current user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Retrieve all failed scan results linked to this repository
    failed_scans = ScanResult.objects.filter(
        commit__repo=repo,
        status='failed'
    ).order_by('-scanned_at')

    # Render security alert dashboard
    return render(request, "repos/repo_security.html", {
        "repo": repo,
        "failed_scans": failed_scans,
    })



# Repository Settings Page
@login_required
def repo_settings(request, repo_id):

    # Ensure repository belongs to logged-in user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Handle form submission
    if request.method == "POST":

        
        # Update repository name
        new_name = request.POST.get("name", "").strip()
        if new_name:
            repo.name = new_name

        
        # Update description
        repo.description = request.POST.get("description", "").strip()

    
        # Update visibility
        repo.is_private = request.POST.get("visibility") == "private"

        
        #  Secret Scanning button its post request
        repo.secret_scanning_enabled = (
            "secret_scanning_enabled" in request.POST
        )

        # Save everything
        repo.save()

        # Success message
        messages.success(request, "Repository settings updated successfully.")

        # Redirect back to settings page
        return redirect("repos:repo_settings", repo_id=repo.id)

    # Render settings page (GET request)
    return render(request, "repos/repo_settings.html", {
        "repo": repo,
    })


# Placeholder: Issues Page
@login_required
def repo_issues(request, repo_id):

    # Ensure repository exists and belongs to user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Until Issue model is built, show empty page
    return render(request, "repos/repo_issues.html", {
        "repo": repo,
    })


# Placeholder: Pull Requests Page

@login_required
def repo_pulls(request, repo_id):

    # Ensure repository exists and belongs to user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    # Until PullRequest model exists, render placeholder
    return render(request, "repos/repo_pulls.html", {
        "repo": repo,
    })


@login_required
def repo_delete(request, repo_id):

    # Ensure repository belongs to user
    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    if request.method == "POST":
        repo_name = repo.name
        repo.delete()

        messages.success(request, f'Repository "{repo_name}" deleted successfully.')
        return redirect("repos:list")

    return redirect("repos:repo_settings", repo_id=repo.id)
