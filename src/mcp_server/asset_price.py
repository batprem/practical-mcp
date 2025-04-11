from typing import Literal
from fastmcp import FastMCP
from price_loaders.tradingview import load_asset_price
import click
import pytz
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

    if timezone is None:
        timezone = pytz.timezone("America/New_York")
    timezone_obj = pytz.timezone(timezone)
    df = load_asset_price(symbol, look_back_bars, time_frame, timezone_obj)
    return df.to_dict(orient="records")


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
