"""
Information Gathering phase strategy and prompts.
"""

from typing import List, Dict, Any
from ..models import SecurityPhase


class InformationGatheringStrategy:
    """Strategy for the Information Gathering phase."""
    
    @staticmethod
    def get_phase_prompt(target: str) -> str:
        """Get the main prompt for information gathering phase."""
        return f"""
You are conducting the Information Gathering phase of a security assessment for target: {target}

Your objectives:
1. Discover the target's network infrastructure and services
2. Identify subdomains and web applications
3. Gather publicly available information about the target
4. Understand the target's technology stack and potential attack vectors

Available tools:
- nmap: Network scanning and service detection
- sublist3r: Subdomain enumeration
- whatweb: Web technology identification
- google_dork: Advanced search queries for sensitive information
- websearch: General web search for target information
- rag_search: Knowledge base search for relevant methodologies

Guidelines:
- Be thorough but respectful of the target's infrastructure
- Focus on publicly accessible information
- Document all findings for the next phases
- Use appropriate scan intensity based on target scope
- Look for common misconfigurations and exposed services

Proceed with the information gathering phase for {target}.
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
1. What additional information is needed?
2. Which tools should be executed next?
3. Are there any immediate security concerns to investigate?

Consider:
- Missing information about the target
- Potential vulnerabilities or misconfigurations
- Areas that need deeper investigation
- Tools that complement the current findings

Provide your analysis and tool selection strategy.
"""

    @staticmethod
    def get_phase_completion_prompt(target: str, findings: List[str]) -> str:
        """Get prompt for completing the information gathering phase."""
        findings_text = "\n".join([f"- {finding}" for finding in findings])
        
        return f"""
Information Gathering phase completed for target: {target}

Findings:
{findings_text}

Evaluate the information gathered and provide:
1. Summary of discovered infrastructure and services
2. Identified potential attack vectors
3. Recommendations for the next phase (Spidering)
4. Any immediate security concerns that need attention

Prepare this information for the Spidering phase.
"""

    @staticmethod
    def get_phase_goals() -> List[str]:
        """Get the goals for the information gathering phase."""
        return [
            "Discover target's network infrastructure and open services",
            "Identify subdomains and web applications",
            "Gather publicly available information about the target",
            "Understand technology stack and potential vulnerabilities",
            "Document findings for subsequent phases"
        ]

    @staticmethod
    def get_success_criteria() -> List[str]:
        """Get success criteria for the information gathering phase."""
        return [
            "Target's network infrastructure mapped",
            "Subdomains and web applications identified",
            "Technology stack and services documented",
            "Potential attack vectors identified",
            "Findings documented for next phases"
        ] 