from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Branch
from repos.models import Repository 
# Create your views here.tory 


#view to list branches of the repository 
@login_required
def branch_list(request, repo_id):
    #fetch repository or return 404 if not found 
    repo = get_object_or_404(Repository, id=repo_id)
    #Query branch belonging to this repository 
    branches = Branch.objects.filter(repo=repo).order_by('-created_at')
    #render template with repository and branches context 
    return render(request, 'branches/branch_list.html', {'repo':repo, 'branches':branches})


#difine view to create new branch 
@login_required
def branch_create(request, repo_id):
    #fetch repository or return 404 if not found 
    repo = get_object_or_404(Repository, id=repo_id)
    #if request is post process form submission
    if request.method == 'POST':
        #Extract the branch name from form input
        name = request.POST.get('name', '').strip()
        #validate branch name from form input 
        if not name:
            #Add error message for missing branch name 
            messages.error(request, "branch name is required")
            #RE-render form template 
            return render(request, 'branches/branch_create.html', {'repo':repo})
        #check if branch already exists in repository 
        if Branch.objects.filter(repo=repo, name=name).exists():
            #Add error message for duplicate branch 
            messages.error(request, f'Brach "{Branch.name}" created in {repo.name}.')
            #Re-render form templates
            return render(request, 'branches/branch_create.html', {'repo':repo})
        
        #create branch record linked to repository and user 
        branch = Branch.objects.create(repo=repo, name=name, owner=request.user)
        #Add success message
        messages.success(request, f'Branch "{Branch.name}" created in {repo.name}.')

        #Redirect branch to list view 
        return redirect('branches:list', repo_id=repo.id)
    
    #for Get request, render branch creation form 
    return render(request, 'branches/branch_create.html', {'repo':repo})

        
        


        
        
