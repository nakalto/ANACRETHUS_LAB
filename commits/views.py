from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Commit
from branches.models import Branch
from repos.models import Repository
from core.utils import contains_secret
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def commit_create(request):
    if request.method == 'POST':
        
        branch_id = request.POST.get('branch_id')
        
        message = request.POST.get('message', '').strip()
        
        snapshot_text = request.POST.get('snapshot_text', '').strip()

        
        branch = get_object_or_404(Branch, id=branch_id)
        
        repo = branch.repo

        # If the snapshot contains secrets, block commit and show error
        if repo.secret_scanning_enabled:

            #check if snapshot contains secrets
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
        
        return redirect('commits:list', branch_id=branch_id)

    # For GET request require a branch_id via query string to prefill the form
    branch_id = request.GET.get('branch_id')
    branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
    return render(request, 'commits/commit_create.html', {'branch': branch})



@login_required  
def commit_list(request, branch_id):
    
    branch = get_object_or_404(Branch, id=branch_id)

    
    commits = Commit.objects.filter(branch=branch).order_by('-created_at')

    
    return render(request, 'commits/commit_list.html', {
        'branch': branch,   #
        'commits': commits  
    })



@login_required
def commit_push(request, repo_id, branch_id):

    repo = get_object_or_404(Repository, id=repo_id, owner=request.user)

    
    branch = get_object_or_404(Branch, id=branch_id, repo=repo)


    if request.method == 'POST':

        
        message = request.POST.get('message', 'Push code')

        # Dictionary to store uploaded files
        snapshot_data = {}

        
        text_extensions = (
            '.html', '.xml', '.css', '.js', '.md',
            '.py', '.java', '.c', '.cpp', '.h',
            '.php', '.rb', '.go', '.ts', '.json',
            '.txt', '.ini', '.cfg', '.yml', '.yaml'
        )

        # Loop through uploaded files
        for file in request.FILES.getlist('files'):

            relative_path = file.name
            data = file.read()

            content = None
            is_text = False

            # Force text decoding for known source files
            if relative_path.lower().endswith(text_extensions):
                content = data.decode('utf-8', errors='replace')
                is_text = True

            else:
                try:
                    content = data.decode('utf-8')
                    is_text = True
                except UnicodeDecodeError:
                    import base64
                    content = base64.b64encode(data).decode('ascii')
                    is_text = False

            snapshot_data[relative_path] = {
                'content': content,
                'is_text': is_text,
                'size': len(data),
            }

        
        # AUTOMATIC SECRET SCANNING
    

        if repo.secret_scanning_enabled:

            for path, file_data in snapshot_data.items():

                # Only scan text files
                if file_data["is_text"]:

                    if contains_secret(file_data["content"]):

                        messages.error(
                            request,
                            f"Commit blocked: secret detected in '{path}'."
                        )

                        # Stop execution — do NOT create commit
                        return redirect('repos:detail', repo_id=repo.id)

        
        # CREATE COMMIT ONLY IF CLEAN

        Commit.objects.create(
            repo=repo,
            branch=branch,
            author=request.user,
            message=message,
            snapshot=snapshot_data,
            status='pending'
        )

        messages.success(
            request,
            f'Pushed {len(snapshot_data)} files to branch "{branch.name}".'
        )

        return redirect('repos:detail', repo_id=repo.id)

    # If GET request → show push page
    return render(request, 'commits/commit_push.html', {
        'repo': repo,
        'branch': branch
    })





def commit_detail(request, commit_id):
    
    commit = get_object_or_404(Commit, id=commit_id)
    
    return render(request, 'commits/commit_detail.html', {
        'commit': commit,
        'repo': commit.repo,
        'branch': commit.branch,
    })
