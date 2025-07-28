def get_generate_report_prompt(target: str, findings: list) -> str:
    findings_str = '\n'.join([f"- {finding}" for finding in findings])
    return f"""
Generate a comprehensive security assessment report for target: {target}

Findings from all phases:
{findings_str}

Create a professional security assessment report including:
1. Executive Summary
2. Methodology
3. Detailed Findings
4. Risk Assessment
5. Recommendations
6. Appendices

Make it comprehensive and actionable.
""" 