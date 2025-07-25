IDOR_SYSTEM_PROMPT = """
When testing for IDOR, try accessing resources with different IDs, incrementing/decrementing IDs, or using another user's identifier.
"""
IDOR_PAYLOADS = [
    '/api/users/1',
    '/api/users/2',
    '/api/users/9999',
    '/api/accounts/1',
    '/api/accounts/2',
] 