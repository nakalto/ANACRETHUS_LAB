# Import models to define database tables
from django.db import models
# Import Commit to link scan results to specific commits
from commits.models import Commit

# Define a ScanResult representing the outcome of a secret scan
class ScanResult(models.Model):
    # Link result to the commit being scanned
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE, related_name='scan_results')
    # Store textual summary of findings
    report = models.TextField()
    # Store normalized status: passed or failed
    status = models.CharField(max_length=20)
    # Timestamp when the scan was performed
    scanned_at = models.DateTimeField(auto_now_add=True)

    # Human-readable representation for admin and debugging
    def __str__(self):
        # Show commit ID and status for quick inspection
        return f"Commit {self.commit.id} — {self.status}"
