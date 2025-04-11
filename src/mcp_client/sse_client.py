import asyncio
import json
from io import StringIO

import pandas as pd
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def main():
    async with sse_client(
        url="http://localhost:8000/sse",
        # headers={"Authorization": "Bearer your_token"},
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available resources
            print("Listing tools...")
            resources = await session.list_tools()
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
