#!/usr/bin/env python3
"""
Personal Resume MCP Server - Schema Compliant Version
Minimal MCP server focused on strict schema compliance
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional

from personal_resume_agent import PersonalResumeAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalResumeMCPServer:
    """Minimal, schema-compliant MCP Server for Personal Resume Agent"""

    def __init__(self):
        """Initialize the MCP server"""
        self.agent = PersonalResumeAgent()
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the server and agent"""
        try:
            success = await self.agent.initialize()
            if success:
                self.initialized = True
                logger.info("✅ Personal Resume MCP Server initialized")
            return success
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            return False

    def create_response(self, request_id: Optional[str], result: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a properly formatted JSON-RPC response"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id if request_id is not None else 0
        }

        if error:
            response["error"] = error
        else:
            response["result"] = result if result is not None else {}

        return response

    async def handle_initialize(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle MCP initialization"""
        if not self.initialized:
            await self.initialize()

        return self.create_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "personal-resume-server",
                "version": "1.0.0"
            }
        })

    async def handle_tools_list(self, request_id: Optional[str]) -> Dict[str, Any]:
        """Handle tool listing request"""
        tools = [
            {
                "name": "query_resume",
                "description": "Query personal resume information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Question about resume"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

        return self.create_response(request_id, {"tools": tools})

    async def handle_tool_call(self, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call requests"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "query_resume":
            query = arguments.get("query", "")
            if not query:
                return self.create_response(request_id, error={
                    "code": -32602,
                    "message": "Missing required parameter: query"
                })

            result = await self.agent.process_query(query)
            response_text = result.get('response', 'No response available')

            return self.create_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            })

        return self.create_response(request_id, error={
            "code": -32602,
            "message": f"Unknown tool: {tool_name}"
        })

    async def run_stdio_server(self):
        """Run the MCP server using stdio transport"""
        logger.info("🚀 Starting Personal Resume MCP Server (stdio)")

        try:
            while True:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse JSON-RPC request
                    request = json.loads(line)
                    method = request.get("method")
                    request_id = request.get("id")
                    params = request.get("params", {})

                    # Handle request
                    if method == "initialize":
                        response = await self.handle_initialize(request_id)
                    elif method == "tools/list":
                        response = await self.handle_tools_list(request_id)
                    elif method == "tools/call":
                        response = await self.handle_tool_call(request_id, params)
                    elif method == "prompts/list":
                        response = self.create_response(request_id, {"prompts": []})
                    elif method == "resources/list":
                        response = self.create_response(request_id, {"resources": []})
                    else:
                        response = self.create_response(request_id, error={
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        })

                    # Send response
                    try:
                        print(json.dumps(response))
                        sys.stdout.flush()
                    except BrokenPipeError:
                        logger.info("Client disconnected")
                        break

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = self.create_response(0, error={
                        "code": -32700,
                        "message": "Parse error"
                    })
                    try:
                        print(json.dumps(error_response))
                        sys.stdout.flush()
                    except BrokenPipeError:
                        break

                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    error_response = self.create_response(request.get("id", 0), error={
                        "code": -32000,
                        "message": f"Server error: {str(e)}"
                    })
                    try:
                        print(json.dumps(error_response))
                        sys.stdout.flush()
                    except BrokenPipeError:
                        break

        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            logger.info("Personal Resume MCP Server stopped")


async def main():
    """Main entry point"""
    server = PersonalResumeMCPServer()
    await server.run_stdio_server()


if __name__ == "__main__":
    asyncio.run(main())