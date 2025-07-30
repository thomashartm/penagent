def get_intent_detection_prompt(user_message: str) -> str:
    return f"""
You are an AI assistant that can either engage in conversation or conduct security testing.

Analyze the following user input and determine their intent:

User Input: {user_message}

Determine if the user wants to:
1. CHAT - Have a conversation, ask questions, or get general information
2. SECURITY_TESTING - Conduct security testing, vulnerability scanning, or pentesting

If the user requests security testing, EXTRACT the target domain, IP, or URL from the input. If the input contains a URL, domain, or IP, return it exactly as provided by the user. If not, return 'None'.

Respond in the following format:
Intent: CHAT or SECURITY_TESTING
Confidence: <float between 0.0 and 1.0>
Reasoning: <brief explanation>
Target: <extracted target domain, IP, or URL, or None>
""" 