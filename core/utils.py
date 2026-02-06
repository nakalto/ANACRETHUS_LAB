
import re


SECRET_PATTERNS = [

    r'AKIA[0-9A-Z]{16}',
    
    r'SECRET_KEY\s*=\s*.+',

    r'api_key\s*=\s*.+',
    
    r'password\s*=\s*.+',

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
