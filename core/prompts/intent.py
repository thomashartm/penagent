def get_intent_detection_prompt(user_message: str) -> str:
    return f"""
You are an AI assistant that can either engage in conversation or conduct security testing.

Analyze the following user input and determine their intent:

User Input: {user_message}

Determine if the user wants to:
1. CHAT - Have a conversation, ask questions, or get general information
2. SECURITY_TESTING - Conduct security testing, vulnerability scanning, or pentesting

For SECURITY_TESTING intent, also extract the target (domain, IP, or URL).

Respond with:
- Intent: CHAT or SECURITY_TESTING
- Confidence: 0.0 to 1.0
- Reasoning: Brief explanation
- Target: Extracted target (if security testing)
""" 