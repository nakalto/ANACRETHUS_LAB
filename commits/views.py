from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Commit
from branches.models import Branch
from repos.models import Repository
from core.utils import contains_secret
from django.contrib.auth.decorators import login_required

# Create your views here.
#Difine a view to create a commit with secret blocking 
@login_required
def commit_create(request):
    if request.method == 'POST':
        #Extract branch_id from form to associate commit 
        branch_id = request.POST.get('branch_id')
        #Extract commit message describing the changes 
        message = request.POST.get('message', '').strip()
        #Extract snapshot_text that simulates code changes 
        snapshot_text = request.POST.get('snapshot_text', '')
        #Fetch the target branch or return 404 if valid
        branch = get_object_or_404(Branch, id=branch_id)
        #Ensure the branch belongs to a repository 
        repo = branch.repo
        #if the snapshot contains secrets, block commit and show error 
        if contains_secret(snapshot_text):
            #Notify user about secret detection 
            messages.error(request, 'commit blocked: potential secret detected in snapshot. ')
            #Re - render the form with current context for correction 
            return render(request, 'commits/commit_create.html', {'branch': branch, })
        #create the commit record linked to branch, author and repo
        commit = Commit.objects.create(
            repo=repo,
            branch=branch,
            author=request.user,
            message=message,
            snapshot_text=snapshot_text,
            status='pending',

        )
        #Inform user of successful commit creation 
        messages.success(request, 'commit created and queuued for scanning ')
        #redirect to the commit list view for the branch 
        return redirect('commits:list', branch_id=branch_id)
    #for Get request require a branch_id via query string to prfill the form 
    branch_id = request.GET.get('branch_id')
    #fetch the branch or render a minimal page if missing
    branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
    #render the commit creation form template
    return render(request, 'commits/commit_create.html' {'branch':branch})

#Define a view to list commits for specific branch
@login_required
def commit_list(request, branch_id):
    #fetch the target branch or return 404 if not found 
    branch = get_object_or_404(Branch, id=branch_id)
    #Query commits associated with this branch ordered by newest first 
    commits = Commit.objects.objects.filter(branch=branch).order_by('-created_at')
    #render the commit list template with branch and commits context 
    return render(request, 'commits/commit_list.html', {'branch':branch, 'commits':commits})


