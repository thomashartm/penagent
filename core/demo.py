#!/usr/bin/env python3
"""
Demonstration script for the Core Security Testing Orchestration System.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demo_models():
    """Demonstrate the Pydantic models."""
    print("🔧 Demonstrating Core Models")
    print("=" * 40)
    
    try:
        # Import models
        from models import SecurityPhase, UserIntent, UserInput, IntentDecision, SecurityTestPlan
        
        # Create sample data
        user_input = UserInput(
            message="Scan example.com for vulnerabilities",
            target="example.com"
        )
        
        intent_decision = IntentDecision(
            intent=UserIntent.SECURITY_TESTING,
            confidence=0.9,
            reasoning="User requested security scanning",
            target="example.com"
        )
        
        security_plan = SecurityTestPlan(
            target="example.com",
            phases=[SecurityPhase.INFORMATION_GATHERING, SecurityPhase.SPIDERING],
            priority="medium",
            scope="comprehensive"
        )
        
        print(f"✅ User Input: {user_input.message}")
        print(f"✅ Intent: {intent_decision.intent}")
        print(f"✅ Target: {security_plan.target}")
        print(f"✅ Phases: {[p.value for p in security_plan.phases]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model demo failed: {e}")
        return False

def demo_strategies():
    """Demonstrate the strategy prompts."""
    print("\n🎯 Demonstrating Security Testing Strategies")
    print("=" * 40)
    
    try:
        from strategies.information_gathering import InformationGatheringStrategy
        from strategies.spidering import SpideringStrategy
        from strategies.active_scanning import ActiveScanningStrategy
        from strategies.evaluation import EvaluationStrategy
        
        target = "example.com"
        
        # Information Gathering
        ig_strategy = InformationGatheringStrategy()
        ig_prompt = ig_strategy.get_phase_prompt(target)
        print(f"✅ Information Gathering prompt generated ({len(ig_prompt)} chars)")
        
        # Spidering
        sp_strategy = SpideringStrategy()
        sp_prompt = sp_strategy.get_phase_prompt(target, ["Found web server", "Discovered subdomains"])
        print(f"✅ Spidering prompt generated ({len(sp_prompt)} chars)")
        
        # Active Scanning
        as_strategy = ActiveScanningStrategy()
        as_prompt = as_strategy.get_phase_prompt(target, ["Web app mapped", "Endpoints discovered"])
        print(f"✅ Active Scanning prompt generated ({len(as_prompt)} chars)")
        
        # Evaluation
        ev_strategy = EvaluationStrategy()
        ev_prompt = ev_strategy.get_phase_prompt(target, ["Vulnerabilities found", "Security issues identified"])
        print(f"✅ Evaluation prompt generated ({len(ev_prompt)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy demo failed: {e}")
        return False

def demo_workflow():
    """Demonstrate the workflow structure."""
    print("\n🔄 Demonstrating LangGraph Workflow Structure")
    print("=" * 40)
    
    try:
        from models import WorkflowState, UserInput, SecurityPhase
        
        # Create workflow state
        state = WorkflowState(
            user_input=UserInput(
                message="Conduct security assessment of example.com",
                target="example.com"
            )
        )
        
        print("✅ Workflow state created")
        print(f"   Target: {state.user_input.target}")
        print(f"   Message: {state.user_input.message}")
        
        # Simulate workflow phases
        phases = [
            SecurityPhase.INFORMATION_GATHERING,
            SecurityPhase.SPIDERING,
            SecurityPhase.ACTIVE_SCANNING,
            SecurityPhase.EVALUATION
        ]
        
        print("\n📋 Security Testing Phases:")
        for i, phase in enumerate(phases, 1):
            print(f"   {i}. {phase.value.replace('_', ' ').title()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow demo failed: {e}")
        return False

def demo_cli_structure():
    """Demonstrate the CLI structure."""
    print("\n💻 Demonstrating CLI Structure")
    print("=" * 40)
    
    try:
        from cli import app
        
        print("✅ CLI application created")
        print("   Available commands:")
        print("   - scan <target> [--message] [--model] [--verbose]")
        print("   - chat <message> [--model]")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI demo failed: {e}")
        return False

def main():
    """Run all demonstrations."""
    print("🚀 Core Security Testing Orchestration System")
    print("=" * 50)
    print("This system provides intelligent security testing orchestration")
    print("using LangGraph and MCP servers for comprehensive assessments.\n")
    
    demos = [
        ("Models", demo_models),
        ("Strategies", demo_strategies),
        ("Workflow", demo_workflow),
        ("CLI", demo_cli_structure),
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        if demo_func():
            passed += 1
            print(f"✅ {demo_name} demo completed")
        else:
            print(f"❌ {demo_name} demo failed")
    
    print(f"\n📊 Demo Results: {passed}/{total} demos completed")
    
    if passed == total:
        print("\n🎉 All demonstrations completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Install dependencies: poetry install")
        print("2. Start MCP servers: cd mcp_servers && docker-compose up -d")
        print("3. Run security scan: python -m core.cli scan example.com")
        print("4. Chat with AI: python -m core.cli chat 'Hello, how can you help me?'")
        return 0
    else:
        print("\n❌ Some demonstrations failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 