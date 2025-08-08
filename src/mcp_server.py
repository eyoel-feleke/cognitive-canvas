from src.tools import store_content, generate_quiz, query_content
from mcp.server.fastmcp import FastMCP
# TODO: decorate with @mcp.tool 
#
# @mcp.tools()
# store_content

# mcp = FastMCP("Tools server")

class MCPServer:
    
    def __init__(self, name="cognitive-canvas"):
        self.mcp = FastMCP(name)
        self._setup_tools()

    def _setup_tools(self):
        self.mcp.tool()(self.store_content_tool)
        self.mcp.tool()(self.query_content_tool)
        self.mcp.tool()(self.generate_quiz_tool)
        
    
    def store_content_tool(self):

        try:
            return store_content()
        except Exception as e:
            return f"Error storing content: {(e)}"

    def query_content_tool(self):
        
        try:
            return query_content()
        except Exception as e:
            return f"Error querying content: {(e)}"

    def generate_quiz_tool(self):
        
        try:
            return generate_quiz()
        except Exception as e:
            return f"Error generating quiz: {(e)}"
    
    def run_mcp_server(self):
        self.mcp.run()

