import asyncio
from typing import Literal

import click
import pytz
import uvicorn
from fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from price_loaders.tradingview import load_asset_price

mcp = FastMCP("Asset Price")


@mcp.tool()
def get_asset_price(
    symbol: str,
    look_back_bars: int = 100,
    time_frame: Literal[
        "1",
        "3",
        "5",
        "15",
        "45",
        "1h",
        "2h",
        "3h",
        "4h",
        "1D",
        "1W",
        "1M",
        "3M",
        "6M",
        "12M",
    ] = "1D",
    timezone: str = "America/New_York",
) -> dict:
    """Fetch historical price data from TradingView for a given asset symbol.

    Args:
        symbol (str): TradingView symbol identifier (e.g. "NASDAQ:META", "SET:BH", "BITSTAMP:BTCUSD")
        look_back_bars (int, optional): Number of historical bars to retrieve. Defaults to 100.
        time_frame (str, optional): Time interval for each bar. Valid values are "1", "3", "5", "15", "45" (minutes),
            "1h", "2h", "3h", "4h" (hours), "1D" (day), "1W" (week), "1M", "3M", "6M", "12M" (months).
            Defaults to "1D".
        timezone (str, optional): Timezone name as string (e.g. "America/New_York"). Defaults to "America/New_York".

    Returns:
        dict: Price data as a dictionary of records, where each record represents a price bar containing
            timestamp and OHLCV (Open, High, Low, Close, Volume) data.
    """  # noqa: E501

    timezone_obj = pytz.timezone(timezone)
    df = load_asset_price(symbol, look_back_bars, time_frame, timezone_obj)
    return df.to_dict(orient="records")


async def run_sse_async(mcp: FastMCP, host: str, port: int) -> None:
    """Run the server using SSE transport."""
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp._mcp_server.run(
                streams[0],
                streams[1],
                mcp._mcp_server.create_initialization_options(),
            )

    starlette_app = Starlette(
        debug=mcp.settings.debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    config = uvicorn.Config(
        starlette_app,
        host=host,
        port=port,
        log_level=mcp.settings.log_level.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option("--host", default="0.0.0.0", help="Host to listen on")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(transport: str, host: str, port: int) -> int:
    if transport == "stdio":
        mcp.run(transport=transport)
    elif transport == "sse":
        asyncio.run(run_sse_async(mcp, host, port))


if __name__ == "__main__":
    main()
