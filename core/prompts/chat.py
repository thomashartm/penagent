def get_chat_response_prompt(user_message: str) -> str:
    return f"""
You are a helpful AI assistant. Respond to the user's message in a friendly and informative way.

User message: {user_message}

Provide a helpful response.
""" 