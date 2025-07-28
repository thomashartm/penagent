"""
Evaluation phase strategy and prompts.
"""

from typing import List, Dict, Any
from ..models import SecurityPhase


class EvaluationStrategy:
    """Strategy for the Evaluation phase."""
    
    @staticmethod
    def get_phase_prompt(target: str, all_findings: List[str]) -> str:
        """Get the main prompt for evaluation phase."""
        findings_text = "\n".join([f"- {finding}" for finding in all_findings])
        
        return f"""
You are conducting the Evaluation phase of a security assessment for target: {target}

All findings from previous phases:
{findings_text}

Your objectives:
1. Analyze and evaluate all security findings
2. Assess the severity and impact of discovered vulnerabilities
3. Provide detailed recommendations for remediation
4. Generate a comprehensive security assessment report
5. Prioritize findings based on risk and business impact

Available tools:
- rag_search: Search knowledge base for remediation guidance
- rag_get_category: Retrieve stored findings for analysis
- websearch: Search for additional context and remediation information
- shell_command: Execute analysis commands if needed

Guidelines:
- Thoroughly analyze all findings from previous phases
- Assess the business impact of each vulnerability
- Provide actionable remediation recommendations
- Consider the target's specific context and requirements
- Generate a professional, comprehensive report
- Prioritize findings by severity and exploitability

Proceed with the evaluation phase for {target}.
"""

    @staticmethod
    def get_analysis_prompt(findings: List[str]) -> str:
        """Get prompt for analyzing findings."""
        findings_text = "\n".join([f"- {finding}" for finding in findings])
        
        return f"""
Analyze the following security findings:

{findings_text}

Provide a comprehensive analysis including:
1. Severity assessment for each finding
2. Potential business impact
3. Exploitability and attack vectors
4. Risk prioritization
5. Remediation recommendations
6. Compliance implications (if applicable)

Consider:
- Technical severity vs business impact
- Exploitation complexity and prerequisites
- Remediation effort and cost
- Regulatory and compliance requirements
- Industry best practices and standards

Provide your detailed analysis.
"""

    @staticmethod
    def get_report_generation_prompt(target: str, analysis: str) -> str:
        """Get prompt for generating the final report."""
        return f"""
Generate a comprehensive security assessment report for target: {target}

Based on the analysis:
{analysis}

The report should include:
1. Executive Summary
   - Overall security posture
   - Key findings and risks
   - High-level recommendations

2. Methodology
   - Phases conducted
   - Tools and techniques used
   - Scope and limitations

3. Detailed Findings
   - Vulnerability descriptions
   - Severity and impact assessment
   - Evidence and proof of concept
   - Remediation recommendations

4. Risk Assessment
   - Risk matrix and prioritization
   - Business impact analysis
   - Compliance considerations

5. Recommendations
   - Immediate actions required
   - Short-term remediation plan
   - Long-term security improvements
   - Best practices implementation

6. Appendices
   - Technical details
   - Tool outputs
   - References and resources

Generate a professional, actionable security assessment report.
"""

    @staticmethod
    def get_phase_goals() -> List[str]:
        """Get the goals for the evaluation phase."""
        return [
            "Analyze and evaluate all security findings",
            "Assess severity and impact of vulnerabilities",
            "Provide detailed remediation recommendations",
            "Generate comprehensive security assessment report",
            "Prioritize findings based on risk and business impact"
        ]

    @staticmethod
    def get_success_criteria() -> List[str]:
        """Get success criteria for the evaluation phase."""
        return [
            "All findings analyzed and evaluated",
            "Severity and impact assessed",
            "Remediation recommendations provided",
            "Comprehensive report generated",
            "Findings prioritized by risk"
        ] 