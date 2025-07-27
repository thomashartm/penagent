#!/usr/bin/env python3
"""
Test suite for Discovery (OWASP) MCP Server using FastMCP
This allows manual testing of all Discovery MCP server capabilities.
"""

import asyncio
from fastmcp import Client

class DiscoveryMCPServerTester:
    """Test suite for Discovery (OWASP) MCP Server."""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def start_server(self):
        """Start the Discovery MCP server."""
        print("🚀 Starting Discovery MCP Server...")
        try:
            # Connect to the FastMCP server running in the container
            self.client = Client("docker exec -i mcp-discovery python owasp_server.py")
            await self.client.__aenter__()
            print("✅ Discovery MCP Server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Discovery MCP Server: {e}")
            return False
    
    async def send_request(self, method: str, params: dict = None) -> dict:
        """Send a request to the MCP server and get response."""
        if not self.client:
            raise Exception("Server not started")
        
        try:
            if method == "initialize":
                return await self.client.initialize()
            elif method == "tools/list":
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
    
    async def test_initialize(self):
        """Test MCP initialize method."""
        print("\n🔧 Testing MCP Initialize...")
        
        response = await self.send_request("initialize")
        print(f"Response: {response}")
        
        if "result" in response and "serverInfo" in response["result"]:
            print("✅ Initialize test passed")
            self.test_results.append(("Initialize", "PASS"))
        else:
            print("❌ Initialize test failed")
            self.test_results.append(("Initialize", "FAIL"))
    
    async def test_list_tools(self):
        """Test MCP tools/list method."""
        print("\n📋 Testing Tools List...")
        
        response = await self.send_request("tools/list")
        print(f"Response: {response}")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ Tools list test passed - Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            self.test_results.append(("Tools List", "PASS"))
        else:
            print("❌ Tools list test failed")
            self.test_results.append(("Tools List", "FAIL"))
    
    async def test_spider_tool(self):
        """Test spider tool execution."""
        print("\n🕷️ Testing Spider Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "spider",
            "arguments": {
                "url": "https://example.com",
                "max_urls": 5
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Spider tool test passed")
            self.test_results.append(("Spider Tool", "PASS"))
        else:
            print("❌ Spider tool test failed")
            self.test_results.append(("Spider Tool", "FAIL"))
    
    async def test_check_headers_tool(self):
        """Test check_headers tool execution."""
        print("\n🔒 Testing Check Headers Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "check_headers",
            "arguments": {
                "url": "https://example.com"
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Check Headers tool test passed")
            self.test_results.append(("Check Headers Tool", "PASS"))
        else:
            print("❌ Check Headers tool test failed")
            self.test_results.append(("Check Headers Tool", "FAIL"))
    
    async def test_check_ssl_tool(self):
        """Test check_ssl tool execution."""
        print("\n🔐 Testing Check SSL Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "check_ssl",
            "arguments": {
                "url": "https://example.com"
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Check SSL tool test passed")
            self.test_results.append(("Check SSL Tool", "PASS"))
        else:
            print("❌ Check SSL tool test failed")
            self.test_results.append(("Check SSL Tool", "FAIL"))
    
    async def test_check_open_redirects_tool(self):
        """Test check_open_redirects tool execution."""
        print("\n🔄 Testing Check Open Redirects Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "check_open_redirects",
            "arguments": {
                "url": "https://example.com"
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Check Open Redirects tool test passed")
            self.test_results.append(("Check Open Redirects Tool", "PASS"))
        else:
            print("❌ Check Open Redirects tool test failed")
            self.test_results.append(("Check Open Redirects Tool", "FAIL"))
    
    async def test_check_sql_injection_tool(self):
        """Test check_sql_injection tool execution."""
        print("\n💉 Testing Check SQL Injection Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "check_sql_injection",
            "arguments": {
                "url": "https://example.com"
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Check SQL Injection tool test passed")
            self.test_results.append(("Check SQL Injection Tool", "PASS"))
        else:
            print("❌ Check SQL Injection tool test failed")
            self.test_results.append(("Check SQL Injection Tool", "FAIL"))
    
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
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting Discovery MCP Server Tests")
        print("=" * 50)
        
        if not await self.start_server():
            return
        
        try:
            await self.test_initialize()
            await self.test_list_tools()
            await self.test_spider_tool()
            await self.test_check_headers_tool()
            await self.test_check_ssl_tool()
            await self.test_check_open_redirects_tool()
            await self.test_check_sql_injection_tool()
            await self.test_invalid_tool()
            await self.test_invalid_method()
        finally:
            await self.stop_server()
        
        self.print_summary()
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            print("🛑 Discovery MCP Server stopped")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 Discovery MCP Server Test Summary")
        print("=" * 50)
        
        passed = sum(1 for _, status in self.test_results if status == "PASS")
        total = len(self.test_results)
        
        for test_name, status in self.test_results:
            print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed!")

async def main():
    """Main test runner."""
    tester = DiscoveryMCPServerTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 