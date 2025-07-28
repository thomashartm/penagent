def get_plan_security_test_prompt(target: str, user_message: str) -> str:
    return f"""
You are planning a security assessment for target: {target}

Based on the user's request: {user_message}

Create a security testing plan with the following phases:
1. Information Gathering - Discover infrastructure and services
2. Spidering - Map web applications and endpoints
3. Active Scanning - Test for vulnerabilities
4. Evaluation - Analyze findings and generate report

Determine:
- Target: {target}
- Phases: All phases or specific ones based on user request
- Priority: low, medium, high, critical
- Scope: comprehensive, focused, or specific

Provide a structured plan.
""" 