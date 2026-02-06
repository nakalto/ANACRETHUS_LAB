
from django.db import models
from commits.models import Commit


class ScanResult(models.Model):
    
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE, related_name='scan_results')
    
    report = models.TextField()
    
    status = models.CharField(max_length=20)
    
    scanned_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        # Show commit ID and status for quick inspection
        return f"Commit {self.commit.id} — {self.status}"
