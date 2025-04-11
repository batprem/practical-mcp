import asyncio
import pandas as pd
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from io import StringIO
import json


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
            print("Listing tools...")
            for tool in resources.tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")
                print(f"Input Schema: {tool.inputSchema}")
                print("-" * 100)

            result = await session.call_tool(
                "get_asset_price",
                dict(
                    symbol="NASDAQ:META",
                    look_back_bars=100,
                    time_frame="1D",
                    timezone="America/New_York",
                ),
            )
            records = ",".join(
                [
                    json.loads(record.model_dump_json())["text"]
                    for record in result.content
                ]
            )
            records = f"[{records}]"
            print(records)
            print(pd.read_json(StringIO(records), orient="records"))

asyncio.run(main())
