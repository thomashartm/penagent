#!/usr/bin/env python3
"""
Test suite for WebSearch MCP Server using FastMCP
This allows manual testing of all WebSearch MCP server capabilities.
"""

import asyncio
from fastmcp import Client

class WebSearchMCPServerTester:
    """Test suite for WebSearch MCP Server."""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def start_server(self):
        """Start the WebSearch MCP server."""
        print("🚀 Starting WebSearch MCP Server...")
        try:
            # Connect to the FastMCP server running in the container
            self.client = Client("docker exec -i mcp-websearch python websearch_server.py")
            await self.client.__aenter__()
            print("✅ WebSearch MCP Server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start WebSearch MCP Server: {e}")
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
    
    async def test_search_tool(self):
        """Test search tool execution."""
        print("\n🔍 Testing Search Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "search",
            "arguments": {
                "query": "python programming",
                "max_results": 3
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Search tool test passed")
            self.test_results.append(("Search Tool", "PASS"))
        else:
            print("❌ Search tool test failed")
            self.test_results.append(("Search Tool", "FAIL"))
    
    async def test_search_news_tool(self):
        """Test search_news tool execution."""
        print("\n📰 Testing Search News Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "search_news",
            "arguments": {
                "query": "artificial intelligence",
                "max_results": 3
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Search News tool test passed")
            self.test_results.append(("Search News Tool", "PASS"))
        else:
            print("❌ Search News tool test failed")
            self.test_results.append(("Search News Tool", "FAIL"))
    
    async def test_search_images_tool(self):
        """Test search_images tool execution."""
        print("\n🖼️ Testing Search Images Tool...")
        
        response = await self.send_request("tools/call", {
            "name": "search_images",
            "arguments": {
                "query": "cats",
                "max_results": 3
            }
        })
        print(f"Response: {response}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Search Images tool test passed")
            self.test_results.append(("Search Images Tool", "PASS"))
        else:
            print("❌ Search Images tool test failed")
            self.test_results.append(("Search Images Tool", "FAIL"))
    
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
        print("🧪 Starting WebSearch MCP Server Tests")
        print("=" * 50)
        
        if not await self.start_server():
            return
        
        try:
            await self.test_initialize()
            await self.test_list_tools()
            await self.test_search_tool()
            await self.test_search_news_tool()
            await self.test_search_images_tool()
            await self.test_invalid_tool()
            await self.test_invalid_method()
        finally:
            await self.stop_server()
        
        self.print_summary()
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            print("🛑 WebSearch MCP Server stopped")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 WebSearch MCP Server Test Summary")
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
    tester = WebSearchMCPServerTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 