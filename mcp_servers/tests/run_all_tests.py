#!/usr/bin/env python3
"""
Test Runner for all MCP Servers
This script runs all MCP server tests and provides a comprehensive summary.
"""

import asyncio
import subprocess
import sys
import os
from typing import List, Tuple

class MCPTestRunner:
    """Test runner for all MCP servers."""
    
    def __init__(self):
        self.test_results = []
        self.test_files = [
            "test_kali_mcp_server.py",
            "test_zap_mcp_server.py",
            "test_websearch_mcp_server.py",
            "test_rag_mcp_server.py",
            "test_discovery_mcp_server.py"
        ]
    
    async def run_test(self, test_file: str) -> Tuple[str, bool]:
        """Run a single test file."""
        print(f"\n{'='*60}")
        print(f"🧪 RUNNING TEST: {test_file}")
        print(f"{'='*60}")
        
        try:
            # Run the test file
            process = await asyncio.create_subprocess_exec(
                sys.executable, test_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(test_file))
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if test passed (look for success indicators in output)
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            
            # Determine if test passed based on output
            passed = (
                process.returncode == 0 and
                "All tests passed" in output and
                "FAIL" not in output
            )
            
            # Print output
            print(output)
            if error_output:
                print(f"STDERR: {error_output}")
            
            return test_file, passed
            
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            return test_file, False
    
    async def check_containers(self) -> bool:
        """Check if required containers are running."""
        print("🔍 Checking if required containers are running...")
        
        required_containers = ["mcp-kali", "mcp-zap", "mcp-websearch", "mcp-rag", "mcp-discovery"]
        running_containers = []
        
        try:
            # Get running containers
            process = await asyncio.create_subprocess_exec(
                "docker", "ps", "--format", "{{.Names}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            running_containers = stdout.decode('utf-8').strip().split('\n')
            
            # Check if required containers are running
            missing_containers = []
            for container in required_containers:
                if container not in running_containers:
                    missing_containers.append(container)
            
            if missing_containers:
                print(f"❌ Missing containers: {', '.join(missing_containers)}")
                print("💡 Please start the containers first:")
                print("   cd mcp_servers && docker-compose up -d kali zap websearch rag discovery")
                return False
            else:
                print("✅ All required containers are running")
                return True
                
        except Exception as e:
            print(f"❌ Error checking containers: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all MCP server tests."""
        print("🚀 MCP SERVER TEST RUNNER")
        print("="*60)
        
        # Check if containers are running
        if not await self.check_containers():
            print("❌ Cannot run tests - containers not ready")
            return
        
        # Run each test
        for test_file in self.test_files:
            test_path = os.path.join(os.path.dirname(__file__), test_file)
            if os.path.exists(test_path):
                result = await self.run_test(test_path)
                self.test_results.append(result)
            else:
                print(f"❌ Test file not found: {test_file}")
                self.test_results.append((test_file, False))
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*60}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} test suites passed")
        
        for test_file, passed in self.test_results:
            status_icon = "✅" if passed else "❌"
            status_text = "PASS" if passed else "FAIL"
            print(f"{status_icon} {test_file}: {status_text}")
        
        print(f"\n{'='*60}")
        if failed_tests == 0:
            print("🎉 ALL TEST SUITES PASSED!")
            print("✅ All MCP servers are working correctly")
        else:
            print(f"⚠️  {failed_tests} test suite(s) failed")
            print("💡 Check the individual test outputs above for details")
        
        print(f"{'='*60}")
        
        # Provide next steps
        print("\n📋 Next Steps:")
        if failed_tests == 0:
            print("✅ All MCP servers are ready for use")
            print("🔧 You can now integrate them with your AI agents")
        else:
            print("🔧 Fix the failing tests before proceeding")
            print("📖 Check the CLI_README.md for troubleshooting tips")

async def main():
    """Main function."""
    runner = MCPTestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 