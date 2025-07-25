# OWASP Top 10 Prompts and Payloads for Web and API Testing

from src.prompts.sqli import SQLI_SYSTEM_PROMPT, SQLI_PAYLOADS
from src.prompts.broken_auth import BROKEN_AUTH_SYSTEM_PROMPT, BROKEN_AUTH_PAYLOADS
from src.prompts.sensitive_data import SENSITIVE_DATA_SYSTEM_PROMPT
from src.prompts.xxe import XXE_SYSTEM_PROMPT, XXE_PAYLOADS
from src.prompts.idor import IDOR_SYSTEM_PROMPT, IDOR_PAYLOADS
from src.prompts.misconfig import MISCONFIG_SYSTEM_PROMPT
from src.prompts.xss_loop import XSS_SYSTEM_PROMPT, XSS_PAYLOADS
from src.prompts.deserialization import DESERIALIZATION_SYSTEM_PROMPT
from src.prompts.components import COMPONENTS_SYSTEM_PROMPT
from src.prompts.logging import LOGGING_SYSTEM_PROMPT
from src.prompts.api_security import API_SECURITY_SYSTEM_PROMPT

OWASP_TOP10_PROMPTS = {
    'sqli': (SQLI_SYSTEM_PROMPT, SQLI_PAYLOADS),
    'broken_auth': (BROKEN_AUTH_SYSTEM_PROMPT, BROKEN_AUTH_PAYLOADS),
    'sensitive_data': (SENSITIVE_DATA_SYSTEM_PROMPT, None),
    'xxe': (XXE_SYSTEM_PROMPT, XXE_PAYLOADS),
    'idor': (IDOR_SYSTEM_PROMPT, IDOR_PAYLOADS),
    'misconfig': (MISCONFIG_SYSTEM_PROMPT, None),
    'xss': (XSS_SYSTEM_PROMPT, XSS_PAYLOADS),
    'deserialization': (DESERIALIZATION_SYSTEM_PROMPT, None),
    'components': (COMPONENTS_SYSTEM_PROMPT, None),
    'logging': (LOGGING_SYSTEM_PROMPT, None),
    'api_security': (API_SECURITY_SYSTEM_PROMPT, None),
} 