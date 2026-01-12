from src.mcp_server import MCPServer
import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    mcp = MCPServer()
    log.info("Starting MCP Server...")
    mcp.run_mcp_server()