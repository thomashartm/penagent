from .chat import get_security_system_prompt

def get_intent_detection_prompt(user_message: str) -> str:
    return f"""
{get_security_system_prompt()}

You are an AI assistant specialized in cybersecurity and security testing. Analyze the following user input and determine their intent:

User Input: {user_message}

Determine if the user wants to:
1. CHAT - Have a conversation about cybersecurity, ask questions about security concepts, tools, methodologies, or get general security information
2. SECURITY_TESTING - Conduct actual security testing, vulnerability scanning, penetration testing, or security assessment on a specific target

**IMPORTANT**: If the user mentions any of the following, treat it as SECURITY_TESTING:
- "scan", "test", "check", "audit", "assess", "pentest", "vulnerability assessment"
- Domain names, IP addresses, URLs, or website names
- Security testing tools (nmap, nikto, etc.)
- Security phases (reconnaissance, information gathering, etc.)
- "security test", "security scan", "vulnerability scan", "penetration test"

If the user requests security testing, EXTRACT the target domain, IP, or URL from the input. If the input contains a URL, domain, or IP, return it exactly as provided by the user. If not, return 'None'.

Consider security-related conversations as CHAT intent, while actual testing requests (with specific targets) as SECURITY_TESTING intent.

Respond in the following format:
Intent: CHAT or SECURITY_TESTING
Confidence: <float between 0.0 and 1.0>
Reasoning: <brief explanation>
Target: <extracted target domain, IP, or URL, or None>
""" 