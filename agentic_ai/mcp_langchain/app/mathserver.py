# MCP Math server
# to test out things locally
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

#Transport ="stdio" argument tells the server to:
#Use the standard input/output streams (stdin/stdout) for communication.
# to receive and respond to tool function calls

if __name__ == "__main__":
    mcp.run(transport="stdio")
