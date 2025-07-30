from .chat import get_security_system_prompt

def get_generate_report_prompt(target: str, findings: list) -> str:
    findings_str = '\n'.join([f"- {finding}" for finding in findings])
    return f"""
{get_security_system_prompt()}

You are an expert security analyst creating a comprehensive security assessment report.

TARGET: {target}
FINDINGS FROM ALL PHASES:
{findings_str}

Create a professional security assessment report following industry standards and best practices:

REPORT STRUCTURE:

1. EXECUTIVE SUMMARY
   - High-level overview of the assessment
   - Key findings and risk levels
   - Business impact and recommendations
   - Executive audience focus

2. METHODOLOGY
   - Assessment approach and scope
   - Tools and techniques used
   - Testing phases and procedures
   - Limitations and assumptions

3. DETAILED FINDINGS
   - Categorized by severity (Critical, High, Medium, Low, Info)
   - Technical details and evidence
   - Impact assessment for each finding
   - References to security frameworks (OWASP, CWE, etc.)

4. RISK ASSESSMENT
   - Risk scoring and prioritization
   - Business impact analysis
   - Threat modeling considerations
   - Compliance implications (if applicable)

5. RECOMMENDATIONS
   - Remediation strategies for each finding
   - Implementation priorities
   - Security best practices
   - Long-term security improvements

6. APPENDICES
   - Technical details and evidence
   - Tool outputs and logs
   - Configuration recommendations
   - Additional resources and references

REPORTING GUIDELINES:
- Use clear, professional language
- Include actionable recommendations
- Prioritize findings by risk level
- Provide technical and business context
- Follow industry reporting standards
- Include risk mitigation strategies
- Emphasize compliance and best practices

Generate a comprehensive, professional security assessment report that provides clear insights and actionable recommendations for improving the security posture of the target.
""" 