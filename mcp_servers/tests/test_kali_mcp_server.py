#!/usr/bin/env python3
"""
Test suite for Kali MCP Server using FastMCP
This allows manual testing of all Kali MCP server capabilities.
"""

import asyncio
from fastmcp import Client

class KaliMCPServerTester:
    """Test suite for Kali MCP Server."""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def start_server(self):
        """Start the Kali MCP server."""
        print("🚀 Starting Kali MCP Server...")
        try:
            from fastmcp.client.transports import StdioTransport
            self.client = Client(StdioTransport("docker", ["exec", "-i", "mcp-kali", "python3", "kali_server.py"]))
            await self.client.__aenter__()
            print("✅ Kali MCP Server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Kali MCP Server: {e}")
            return False
    
    async def send_request(self, method: str, params: dict = None) -> dict:
        """Send a request to the MCP server and get response."""
        if not self.client:
            raise Exception("Server not started")
        
        try:
            if method == "tools/list":
                return await self.client.list_tools()
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.client.call_tool(tool_name, arguments)
                return {"result": {"content": [{"type": "text", "text": result.text}]}}
            else:
                return {"error": f"Unknown method: {method}"}
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    async def test_list_tools(self):
        """Test MCP tools/list method."""
        print("\n📋 Testing Tools List...")
        
        response = await self.send_request("tools/list")
        print(f"Response: {response}")
        
        if isinstance(response, list) and len(response) > 0 and all(hasattr(tool, 'name') and hasattr(tool, 'description') for tool in response):
            print("✅ Tools list test passed")
            self.test_results.append(("Tools List", "PASS"))
        else:
            print("❌ Tools list test failed")
            self.test_results.append(("Tools List", "FAIL"))
    
    async def test_nmap_tool(self):
        """Test nmap tool execution."""
        print("\n🔍 Testing Nmap Tool...")
        
        result = await self.client.call_tool("nmap", {"target": "127.0.0.1"})
        print(f"Response: {result}")
        output = getattr(result, 'data', None)
        if not output and hasattr(result, 'content') and result.content:
            output = getattr(result.content[0], 'text', str(result.content[0]))
        if output:
            print("✅ Nmap tool test passed")
            self.test_results.append(("Nmap Tool", "PASS"))
        else:
            print("❌ Nmap tool test failed")
            self.test_results.append(("Nmap Tool", "FAIL"))
    
    async def test_gobuster_tool(self):
        """Test gobuster tool execution."""
        print("\n🌐 Testing Gobuster Tool...")
        
        result = await self.client.call_tool("gobuster", {"url": "https://example.com"})
        print(f"Response: {result}")
        output = getattr(result, 'data', None)
        if not output and hasattr(result, 'content') and result.content:
            output = getattr(result.content[0], 'text', str(result.content[0]))
        if output:
            print("✅ Gobuster tool test passed")
            self.test_results.append(("Gobuster Tool", "PASS"))
        else:
            print("❌ Gobuster tool test failed")
            self.test_results.append(("Gobuster Tool", "FAIL"))
    
    async def test_shell_command_tool(self):
        """Test shell command tool execution."""
        print("\n💻 Testing Shell Command Tool...")
        
        result = await self.client.call_tool("shell_command", {"command": "echo hello"})
        print(f"Response: {result}")
        output = getattr(result, 'data', None)
        if not output and hasattr(result, 'content') and result.content:
            output = getattr(result.content[0], 'text', str(result.content[0]))
        if output:
            print("✅ Shell command tool test passed")
            self.test_results.append(("Shell Command Tool", "PASS"))
        else:
            print("❌ Shell command tool test failed")
            self.test_results.append(("Shell Command Tool", "FAIL"))
    
    async def test_invalid_tool(self):
        """Test invalid tool handling."""
        print("\n🚫 Testing Invalid Tool Handling...")
        
        response = await self.send_request("tools/call", {
            "name": "invalid_tool",
            "arguments": {}
        })
        print(f"Response: {response}")
        
        if "error" in response:
            print("✅ Invalid tool test passed (correctly returned error)")
            self.test_results.append(("Invalid Tool", "PASS"))
        else:
            print("❌ Invalid tool test failed (should have returned error)")
            self.test_results.append(("Invalid Tool", "FAIL"))
    
    async def test_invalid_method(self):
        """Test invalid method handling."""
        print("\n🚫 Testing Invalid Method Handling...")
        
        response = await self.send_request("invalid_method", {})
        print(f"Response: {response}")
        
        if "error" in response:
            print("✅ Invalid method test passed (correctly returned error)")
            self.test_results.append(("Invalid Method", "PASS"))
        else:
            print("❌ Invalid method test failed (should have returned error)")
            self.test_results.append(("Invalid Method", "FAIL"))
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            print("🛑 Kali MCP Server stopped")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*50)
        print("📊 KALI MCP SERVER TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, status in self.test_results if status == "PASS")
        failed_tests = total_tests - passed_tests
        
        for test_name, status in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {status}")
        
        print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
        
        if failed_tests == 0:
            print("🎉 All tests passed! Kali MCP Server is working correctly.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Check the output above for details.")

async def main():
    """Main test function."""
    print("🧪 KALI MCP SERVER TEST SUITE")
    print("="*50)
    
    tester = KaliMCPServerTester()
    
    try:
        # Start server
        if not await tester.start_server():
            print("❌ Cannot run tests - server failed to start")
            return
        
        # Run tests
        await tester.test_list_tools()
        await tester.test_nmap_tool()
        await tester.test_gobuster_tool()
        await tester.test_shell_command_tool()
        await tester.test_invalid_tool()
        await tester.test_invalid_method()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test suite error: {e}")
    finally:
        await tester.stop_server()

if __name__ == "__main__":
    asyncio.run(main()) 