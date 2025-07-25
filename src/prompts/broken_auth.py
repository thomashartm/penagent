BROKEN_AUTH_SYSTEM_PROMPT = """
When testing for broken authentication, try default credentials, brute-force common passwords, and bypass techniques (e.g., session fixation, JWT tampering).
Analyze responses for authentication bypass or privilege escalation.
"""
BROKEN_AUTH_PAYLOADS = [
    ('admin', 'admin'),
    ('admin', 'password'),
    ('user', 'user'),
    ('test', 'test'),
    ('root', 'toor'),
    # Add more as needed
] 