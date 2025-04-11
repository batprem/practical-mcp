import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    async with stdio_client(
        StdioServerParameters(
            command="uv", args="run python -m mcp_server.asset_price".split()
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available resources
            resources = await session.list_tools()
            print(resources)

            result = await session.call_tool(
                "get_asset_price",
                dict(
                    symbol="NASDAQ:META",
                    look_back_bars=100,
                    time_frame="1D",
                    timezone="America/New_York",
                ),
            )
            print(result)

asyncio.run(main())
