from .chat import get_security_system_prompt

def get_plan_security_test_prompt(target: str, user_message: str) -> str:
    return f"""
{get_security_system_prompt()}

You are an expert security testing planner creating a comprehensive security assessment plan.

TARGET: {target}
USER REQUEST: {user_message}

Create a detailed security testing plan following industry best practices and frameworks:

SECURITY TESTING PHASES:
1. Information Gathering (Reconnaissance)
   - Network discovery and enumeration
   - Service identification and version detection
   - OSINT and public information gathering
   - Infrastructure mapping

2. Spidering (Web Application Mapping)
   - Web application discovery
   - Endpoint enumeration
   - Technology stack identification
   - Directory and file discovery

3. Active Scanning (Vulnerability Assessment)
   - Automated vulnerability scanning
   - Manual testing for common vulnerabilities
   - Configuration review
   - Security misconfiguration assessment

4. Evaluation (Analysis and Reporting)
   - Risk assessment and prioritization
   - False positive analysis
   - Remediation recommendations
   - Executive and technical reporting

PLANNING CONSIDERATIONS:
- Target scope and authorization
- Risk assessment and impact analysis
- Compliance requirements (if applicable)
- Resource allocation and timeline
- Legal and ethical considerations
- Reporting requirements

Determine:
- Target: {target}
- Phases: All phases or specific ones based on user request
- Priority: low, medium, high, critical (based on target sensitivity and user requirements)
- Scope: comprehensive, focused, or specific (based on user request and target complexity)
- Methodology: Automated, manual, or hybrid approach
- Tools: Appropriate security testing tools for each phase
- Timeline: Estimated duration for each phase
- Deliverables: Expected outputs and reports

Provide a structured, professional security testing plan that follows industry standards and best practices.
""" 