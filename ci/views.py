from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from core.utils import contains_secret
from commits.models import Commit
from .models import ScanResult
# Create your views here.

#define a view to run a secret scan agaist a commit
@login_required
def run_scan(request, commit_id):
    #fetch the commit object or return 404 if missing 
    commit = get_object_or_404(Commit,id=commit_id)
    #Run detection using snapshot_text from the commit 
    secret_found = contains_secret(commit.snapshot_text)

    #if secret is found, mark , mark the status as failed and create a report 
    if secret_found:
        #build a simple report message summarizing failure 
        report = "secret detected in commit snapshot. please remove and retry ."
        #create a ScanResults entry with failed status 
        ScanResult.objects.create(
            commit=commit,
            status='failed',
            report=report
        )
        #update commits status to failed 
        commit.status = 'failed'
        #persist the change to the database 
        commit.save()
        #notify  user about failure 
        messages.error(request, "scan failed: secret detected")

    #if no secret found 
    else:
        #build a sucess report message 
        report = "No secrets detected. Commit passed. "
        #create a scan result entry with passed status 
        ScanResult.objects.create(commit=commit, report=report, status='passed')
        #update commit status to passed 
        commit.save()
        #notify user about success 
        messages.success(request,  'scan passed: no secret found ')


    #Redirect back to the brach commit list for content 
    return redirect ('commits:list', branch_id=commit.branch.id)    
