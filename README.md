# ANACRETHUS_LAB

<!-- Explain project purpose -->
This project is a mini-GitHub built with Django and PostgreSQL, featuring repositories, branches, commits, and secret-blocking.

<!-- Explain local pre-commit hook -->
## Local secret-blocking pre-commit hook
- Create `.git/hooks/pre-commit` with executable permissions.
- Script checks staged changes for secret patterns and blocks the commit.

<!-- Provide sample hook -->
```sh
# Define patterns likely to indicate secrets
PATTERNS="(AKIA[0-9A-Z]{16}|SECRET_KEY\s*=|api_key\s*=|password\s*=|Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+)"
# Check staged diff for matches
if git diff --cached | grep -E "$PATTERNS" > /dev/null; then
  echo "Commit blocked: potential secrets detected."
  exit 1
fi
# Allow commit if no secrets found
exit 0
