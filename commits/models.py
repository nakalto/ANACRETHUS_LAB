from django.db import models
from django.contrib.auth.models import User
from repos.models import Repository
from branches.models import Branch

class Commit(models.Model):
    
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='commits')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commits')
    message = models.CharField(max_length=255)


    snapshot = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    parent_commit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    # Human readable representation
    def __str__(self):
        return f"{self.branch.name}: {self.message[:30]}"
