# cal_server.py

from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


if __name__ == "__main__":
    # Run with explicit host and port configuration
    mcp.run(
        transport="sse",
    )
