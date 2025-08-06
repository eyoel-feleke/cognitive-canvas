import mcp
from tools import store_content, generate_quiz, query_content
from mcp.server.fastmcp import FastMCP
# TODO: decorate with @mcp.tool 
#
# @mcp.tools()
# store_content


@mcp.tool()
def run_server():
    # Entry point for MCP server
    print("Hello world from MCP server")
    mcp = FastMCP("Tools server")
    
    @mcp.tool()
    def store_content_tool():
        try:
            return store_content()
        except Exception as e:
            return f"Error storing content: {(e)}"
    
    @mcp.tool()
    def query_content_tool():
        try:
            return query_content()
        except Exception as e:
            return f"Error querying content: {(e)}"
    
    @mcp.tool()
    def generate_quiz_tool():
        try:
            return generate_quiz()
        except Exception as e:
            return f"Error generating quiz: {(e)}"
    
    return mcp

    pass
if __name__ == "__main__":
    mcp.run()