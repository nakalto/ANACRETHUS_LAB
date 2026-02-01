from django.db import models
from django.contrib.auth.models import User
from repos.models import Repository
from branches.models import Branch

class Commit(models.Model):
    # Link commit to a repository for grouping
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits')
    # Link commit to a specific branch
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='commits')
    # Link commit to the author user
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commits')
    # Short message describing the change
    message = models.CharField(max_length=255)
    # Store snapshot of files as JSON (filename → metadata dict)

    snapshot = models.JSONField(default=dict)
    # Track status for CI simulation: pending, passed, failed
    status = models.CharField(max_length=20, default='pending')
    # Timestamp when the commit was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional: parent commit for history/diff simulation
    parent_commit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    # Human readable representation
    def __str__(self):
        return f"{self.branch.name}: {self.message[:30]}"
