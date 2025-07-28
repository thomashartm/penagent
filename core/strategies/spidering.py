"""
Spidering phase strategy and prompts.
"""

from typing import List, Dict, Any
from ..models import SecurityPhase


class SpideringStrategy:
    """Strategy for the Spidering phase."""
    
    @staticmethod
    def get_phase_prompt(target: str, previous_findings: List[str]) -> str:
        """Get the main prompt for spidering phase."""
        findings_text = "\n".join([f"- {finding}" for finding in previous_findings])
        
        return f"""
You are conducting the Spidering phase of a security assessment for target: {target}

Previous findings from Information Gathering:
{findings_text}

Your objectives:
1. Crawl and map the target's web applications
2. Discover directories, files, and endpoints
3. Identify web technologies and frameworks in use
4. Map the application structure and functionality
5. Identify potential entry points for testing

Available tools:
- gobuster: Directory and file enumeration
- nikto: Web server vulnerability scanning
- whatweb: Web technology identification
- websearch: Search for target-specific information
- rag_store: Store findings for later analysis

Guidelines:
- Focus on web applications discovered in the previous phase
- Be systematic in directory/file discovery
- Document all discovered endpoints and technologies
- Look for common web vulnerabilities and misconfigurations
- Respect robots.txt and rate limiting
- Store findings for the Active Scanning phase

Proceed with the spidering phase for {target}.
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
1. What additional web resources need to be discovered?
2. Which directories or files should be investigated further?
3. Are there any web technologies that need deeper analysis?
4. What potential vulnerabilities should be prioritized?

Consider:
- Undiscovered directories and files
- Web technologies and frameworks
- Potential entry points for testing
- Areas that need deeper crawling
- Tools that complement the current findings

Provide your analysis and tool selection strategy.
"""

    @staticmethod
    def get_phase_completion_prompt(target: str, findings: List[str]) -> str:
        """Get prompt for completing the spidering phase."""
        findings_text = "\n".join([f"- {finding}" for finding in findings])
        
        return f"""
Spidering phase completed for target: {target}

Findings:
{findings_text}

Evaluate the web application mapping and provide:
1. Summary of discovered web applications and structure
2. Identified web technologies and frameworks
3. Potential entry points for active testing
4. Recommendations for the Active Scanning phase
5. Any immediate web security concerns

Prepare this information for the Active Scanning phase.
"""

    @staticmethod
    def get_phase_goals() -> List[str]:
        """Get the goals for the spidering phase."""
        return [
            "Crawl and map target's web applications",
            "Discover directories, files, and endpoints",
            "Identify web technologies and frameworks",
            "Map application structure and functionality",
            "Identify potential entry points for testing"
        ]

    @staticmethod
    def get_success_criteria() -> List[str]:
        """Get success criteria for the spidering phase."""
        return [
            "Web applications fully mapped",
            "Directories and files discovered",
            "Web technologies identified",
            "Application structure documented",
            "Entry points identified for active testing"
        ] 