
from django.contrib.auth.decorators import login_required


from django.shortcuts import redirect, get_object_or_404

from django.contrib import messages

from commits.models import Commit

from .models import ScanResult
from core.utils import contains_secret


@login_required
def run_scan(request, commit_id):

    # Fetch commit or return 404
    commit = get_object_or_404(Commit, id=commit_id)

    # If commit has no snapshot, fail safely
    if not commit.snapshot:
        messages.error(request, "No files found in commit.")
        return redirect('commits:list', branch_id=commit.branch.id)

    secret_detected = False
    report_lines = []

    # Loop through all files in snapshot
    for path, file_data in commit.snapshot.items():

        # Only scan text files
        if isinstance(file_data, dict) and file_data.get("is_text", True):

            content = file_data.get("content", "")

            # Run secret detection
            if contains_secret(content):
                secret_detected = True
                report_lines.append(f"Secret detected in file: {path}")

    # If any secret found
    if secret_detected:

        report = "\n".join(report_lines)

        # Save scan result
        ScanResult.objects.create(
            commit=commit,
            status='failed',
            report=report
        )

        # Update commit status
        commit.status = 'failed'
        commit.save()

        messages.error(request, "CI scan failed: secret detected.")

    else:

        report = "No secrets detected. Commit passed."

        ScanResult.objects.create(
            commit=commit,
            status='passed',
            report=report
        )

        commit.status = 'passed'
        commit.save()

        messages.success(request, "CI scan passed.")

    return redirect('commits:list', branch_id=commit.branch.id)
