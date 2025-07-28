#!/usr/bin/env python3
"""
Basic test script to verify the core project structure.
"""

import sys
import os

# Add the core directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core modules can be imported."""
    try:
        from core.models import SecurityPhase, UserIntent, WorkflowState
        print("✅ Models imported successfully")
        
        from core.mcp_client import MCPClientManager
        print("✅ MCP Client imported successfully")
        
        from core.strategies.information_gathering import InformationGatheringStrategy
        from core.strategies.spidering import SpideringStrategy
        from core.strategies.active_scanning import ActiveScanningStrategy
        from core.strategies.evaluation import EvaluationStrategy
        print("✅ Strategies imported successfully")
        
        from core.orchestrator import SecurityOrchestrator
        print("✅ Orchestrator imported successfully")
        
        from core.cli import app
        print("✅ CLI imported successfully")
        
        print("\n🎉 All core modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_models():
    """Test model creation and validation."""
    try:
        from core.models import SecurityPhase, UserIntent, WorkflowState, UserInput
        
        # Test enum values
        assert SecurityPhase.INFORMATION_GATHERING == "information_gathering"
        assert UserIntent.CHAT == "chat"
        assert UserIntent.SECURITY_TESTING == "security_testing"
        
        # Test model creation
        user_input = UserInput(message="test message", target="example.com")
        assert user_input.message == "test message"
        assert user_input.target == "example.com"
        
        print("✅ Models created and validated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_strategies():
    """Test strategy prompt generation."""
    try:
        from core.strategies.information_gathering import InformationGatheringStrategy
        
        strategy = InformationGatheringStrategy()
        prompt = strategy.get_phase_prompt("example.com")
        assert "example.com" in prompt
        assert "Information Gathering" in prompt
        
        print("✅ Strategy prompts generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Core Project Structure")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Test", test_models),
        ("Strategy Test", test_strategies),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core project structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 