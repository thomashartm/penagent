import json
import re

def generate_report(input_json, output_md):
    """
    Generate a professional Markdown report from process_logs.json.
    Includes executive summary, steps, vulnerabilities, and recommendations.
    """
    # Read all log lines
    with open(input_json, 'r') as f:
        logs = [json.loads(line) for line in f if line.strip()]

    # Executive summary: summarize the goal and number of steps
    goal = None
    steps = []
    vulnerabilities = []
    recommendations = []
    outputs = []

    for entry in logs:
        t = entry.get('type')
        c = entry.get('content')
        if t == 'Thought' and not goal:
            # Try to extract goal from first thought
            m = re.search(r'goal: (.+?)(?:\\n|$)', str(c), re.IGNORECASE)
            if m:
                goal = m.group(1)
        if t == 'Action':
            steps.append(c)
        if t == 'Observation':
            outputs.append(c)
            # Extract vulnerabilities and recommendations if mentioned
            if isinstance(c, dict):
                obs_text = str(c)
            else:
                obs_text = c
            vulns = re.findall(r'(?:vulnerability|vulnerabilities)[:\s]+(.+?)(?:\\n|$)', obs_text, re.IGNORECASE)
            recs = re.findall(r'(?:recommendation|remediation)[:\s]+(.+?)(?:\\n|$)', obs_text, re.IGNORECASE)
            vulnerabilities.extend(vulns)
            recommendations.extend(recs)

    with open(output_md, 'w') as f:
        f.write("# Pentest Report\n\n")
        f.write("## Executive Summary\n\n")
        if goal:
            f.write(f"**Goal:** {goal}\n\n")
        f.write(f"**Total Steps:** {len(steps)}\n\n")
        f.write("## Steps & Outputs\n\n")
        for i, (step, output) in enumerate(zip(steps, outputs), 1):
            f.write(f"### Step {i}\n\n")
            f.write("**Action:**\n\n```")
            f.write(f"{step}\n")
            f.write("```\n\n")
            f.write("**Observation:**\n\n```")
            f.write(f"{output}\n")
            f.write("```\n\n")
        f.write("## Vulnerabilities Found\n\n")
        if vulnerabilities:
            for v in vulnerabilities:
                f.write(f"- {v}\n")
        else:
            f.write("None explicitly found in logs.\n")
        f.write("\n## Remediation Recommendations\n\n")
        if recommendations:
            for r in recommendations:
                f.write(f"- {r}\n")
        else:
            f.write("None explicitly found in logs.\n") 