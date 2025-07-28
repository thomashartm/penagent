"""
Active Scanning phase strategy and prompts.
"""

from typing import List, Dict, Any
from ..models import SecurityPhase


class ActiveScanningStrategy:
    """Strategy for the Active Scanning phase."""
    
    @staticmethod
    def get_phase_prompt(target: str, previous_findings: List[str]) -> str:
        """Get the main prompt for active scanning phase."""
        findings_text = "\n".join([f"- {finding}" for finding in previous_findings])
        
        return f"""
You are conducting the Active Scanning phase of a security assessment for target: {target}

Previous findings from Spidering:
{findings_text}

Your objectives:
1. Actively test for vulnerabilities in discovered services and applications
2. Perform vulnerability scanning against identified targets
3. Test for common security weaknesses and misconfigurations
4. Validate potential security issues discovered in previous phases
5. Identify exploitable vulnerabilities and security gaps

Available tools:
- nuclei: Vulnerability scanning with predefined templates
- nikto: Web server vulnerability scanning
- hydra: Password brute forcing (use responsibly)
- metasploit: Exploitation framework (use responsibly)
- websearch: Search for target-specific vulnerabilities
- rag_store: Store findings for analysis

Guidelines:
- Focus on targets discovered in previous phases
- Use appropriate scanning intensity based on scope
- Document all vulnerabilities and findings
- Be responsible with exploitation tools
- Respect the target's infrastructure and rate limits
- Store all findings for the Evaluation phase

Proceed with the active scanning phase for {target}.
"""

    @staticmethod
    def get_tool_selection_prompt(tool_results: List[Dict[str, Any]]) -> str:
        """Get prompt for selecting next tools based on previous results."""
        results_summary = "\n".join([
            f"- {result['tool_name']}: {'Success' if result['success'] else 'Failed'}"
            for result in tool_results
        ])
        
        return f"""
Based on the following tool execution results:

{results_summary}

Analyze the findings and determine:
1. What additional vulnerabilities should be tested?
2. Which services or applications need deeper scanning?
3. Are there any potential security issues to validate?
4. What exploitation attempts should be considered?

Consider:
- Undiscovered vulnerabilities
- Services that need deeper testing
- Potential security weaknesses
- Areas that need exploitation testing
- Tools that complement the current findings

Provide your analysis and tool selection strategy.
"""

    @staticmethod
    def get_phase_completion_prompt(target: str, findings: List[str]) -> str:
        """Get prompt for completing the active scanning phase."""
        findings_text = "\n".join([f"- {finding}" for finding in findings])
        
        return f"""
Active Scanning phase completed for target: {target}

Findings:
{findings_text}

Evaluate the vulnerability scanning results and provide:
1. Summary of discovered vulnerabilities and their severity
2. Identified security weaknesses and misconfigurations
3. Potential exploitation paths and risks
4. Recommendations for the Evaluation phase
5. Any critical security issues that need immediate attention

Prepare this information for the Evaluation phase.
"""

    @staticmethod
    def get_phase_goals() -> List[str]:
        """Get the goals for the active scanning phase."""
        return [
            "Actively test for vulnerabilities in discovered services",
            "Perform vulnerability scanning against identified targets",
            "Test for common security weaknesses and misconfigurations",
            "Validate potential security issues from previous phases",
            "Identify exploitable vulnerabilities and security gaps"
        ]

    @staticmethod
    def get_success_criteria() -> List[str]:
        """Get success criteria for the active scanning phase."""
        return [
            "Vulnerabilities identified and documented",
            "Security weaknesses and misconfigurations found",
            "Potential exploitation paths identified",
            "All discovered services tested",
            "Findings prepared for evaluation"
        ] 