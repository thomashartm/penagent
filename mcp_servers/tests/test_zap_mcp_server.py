#!/usr/bin/env python3
"""
Test suite for ZAP MCP Server using FastMCP
This allows manual testing of all ZAP MCP server capabilities.
"""

import asyncio
from fastmcp import Client

class ZAPMCPServerTester:
    """Test suite for ZAP MCP Server."""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def start_server(self):
        """Start the ZAP MCP server."""
        print("🚀 Starting ZAP MCP Server...")
        try:
            # Connect to the FastMCP server running in the container
            self.client = Client("docker exec -i mcp-zap python3 zap_server.py")
            await self.client.__aenter__()
            print("✅ ZAP MCP Server started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start ZAP MCP Server: {e}")
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
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-tools-list",
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
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
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-spider",
            "method": "tools/call",
            "params": {
                "name": "spider",
                "arguments": {
                    "url": "https://example.com"
                }
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Spider tool test passed")
            self.test_results.append(("Spider Tool", "PASS"))
        else:
            print("❌ Spider tool test failed")
            self.test_results.append(("Spider Tool", "FAIL"))
    
    async def test_alerts_tool(self):
        """Test alerts tool execution."""
        print("\n🚨 Testing Alerts Tool...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-alerts",
            "method": "tools/call",
            "params": {
                "name": "alerts",
                "arguments": {
                    "risk_level": "High"
                }
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Alerts tool test passed")
            self.test_results.append(("Alerts Tool", "PASS"))
        else:
            print("❌ Alerts tool test failed")
            self.test_results.append(("Alerts Tool", "FAIL"))
    
    async def test_urls_tool(self):
        """Test URLs tool execution."""
        print("\n🔗 Testing URLs Tool...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-urls",
            "method": "tools/call",
            "params": {
                "name": "urls",
                "arguments": {
                    "base_url": "https://example.com"
                }
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ URLs tool test passed")
            self.test_results.append(("URLs Tool", "PASS"))
        else:
            print("❌ URLs tool test failed")
            self.test_results.append(("URLs Tool", "FAIL"))
    
    async def test_alerts_no_filter(self):
        """Test alerts tool without risk level filter."""
        print("\n🚨 Testing Alerts Tool (No Filter)...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-alerts-no-filter",
            "method": "tools/call",
            "params": {
                "name": "alerts",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ Alerts tool (no filter) test passed")
            self.test_results.append(("Alerts Tool (No Filter)", "PASS"))
        else:
            print("❌ Alerts tool (no filter) test failed")
            self.test_results.append(("Alerts Tool (No Filter)", "FAIL"))
    
    async def test_urls_no_filter(self):
        """Test URLs tool without base URL filter."""
        print("\n🔗 Testing URLs Tool (No Filter)...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-urls-no-filter",
            "method": "tools/call",
            "params": {
                "name": "urls",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "result" in response and "content" in response["result"]:
            print("✅ URLs tool (no filter) test passed")
            self.test_results.append(("URLs Tool (No Filter)", "PASS"))
        else:
            print("❌ URLs tool (no filter) test failed")
            self.test_results.append(("URLs Tool (No Filter)", "FAIL"))
    
    async def test_invalid_tool(self):
        """Test invalid tool handling."""
        print("\n🚫 Testing Invalid Tool Handling...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-invalid",
            "method": "tools/call",
            "params": {
                "name": "invalid_tool",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if "error" in response:
            print("✅ Invalid tool test passed (correctly returned error)")
            self.test_results.append(("Invalid Tool", "PASS"))
        else:
            print("❌ Invalid tool test failed (should have returned error)")
            self.test_results.append(("Invalid Tool", "FAIL"))
    
    async def test_invalid_method(self):
        """Test invalid method handling."""
        print("\n🚫 Testing Invalid Method Handling...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "test-invalid-method",
            "method": "invalid_method",
            "params": {}
        }
        
        response = await self.send_request(request)
        print(f"Request: {json.dumps(request, indent=2)}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
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
            print("🛑 ZAP MCP Server stopped")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*50)
        print("📊 ZAP MCP SERVER TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, status in self.test_results if status == "PASS")
        failed_tests = total_tests - passed_tests
        
        for test_name, status in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {status}")
        
        print(f"\n📈 Results: {passed_tests}/{total_tests} tests passed")
        
        if failed_tests == 0:
            print("🎉 All tests passed! ZAP MCP Server is working correctly.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Check the output above for details.")

async def main():
    """Main test function."""
    print("🧪 ZAP MCP SERVER TEST SUITE")
    print("="*50)
    
    tester = ZAPMCPServerTester()
    
    try:
        # Start server
        if not await tester.start_server():
            print("❌ Cannot run tests - server failed to start")
            return
        
        # Run tests
        await tester.test_initialize()
        await tester.test_list_tools()
        await tester.test_spider_tool()
        await tester.test_alerts_tool()
        await tester.test_urls_tool()
        await tester.test_alerts_no_filter()
        await tester.test_urls_no_filter()
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