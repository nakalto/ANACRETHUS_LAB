from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from repos.models import Repository
from branches.models import Branch

class Commit(models.Model):
    #link commit to a repository for grouping 
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits')
    #link commit to a specific branch 
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,related_name='commits')
    #link commit to the author user 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commits')
    #short message describing the change 
    message = models.CharField(max_length=255)
    #store a text snapshot of the changes made in this commits
    snapshot_text = models.TextField()
    #Track status for CI simulation: pending, passed, failed 
    status = models.CharField(max_length=20, default='pending')
    #Timestamp when the commit was created
    created_at = models.DateTimeField(auto_now_add=True) 

    #human readable representation 
    def __str__(self):
        return f"{self.branch.name}: {self.message[:30]}"