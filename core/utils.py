# Import re to compile and run regular expressions
import re

# Define a list of regex patterns that commonly indicate secrets
SECRET_PATTERNS = [
    # Match AWS Access Key IDs starting with AKIA followed by 16 uppercase alphanumerics
    r'AKIA[0-9A-Z]{16}',
    # Match typical environment variable assignments for secret key
    r'SECRET_KEY\s*=\s*.+',
    # Match common api_key assignments
    r'api_key\s*=\s*.+',
    # Match password assignments in code or configs
    r'password\s*=\s*.+',
    # Match bearer JWT tokens (rough heuristic)
    r'Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+',
]

# Compile patterns once for performance
COMPILED_PATTERNS = [re.compile(p) for p in SECRET_PATTERNS]

# Define a function that checks a text blob for any secret patterns
def contains_secret(text: str) -> bool:
    # Iterate through each compiled regex pattern
    for pattern in COMPILED_PATTERNS:
        # If any pattern finds a match, return True indicating a secret found
        if pattern.search(text):
            return True
    # If no patterns matched, return False indicating clean content
    return False
