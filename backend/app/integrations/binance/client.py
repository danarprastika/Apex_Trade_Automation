import ccxt.async_support as ccxt


class BinanceClient:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None, testnet: bool = False):
        config = {
            "apiKey": api_key or "",
            "secret": api_secret or "",
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
        if testnet:
            config["urls"] = {"api": "https://testnet.binance.vision/api"}
        self.exchange = ccxt.binance(config)

    async def get_assets(self):
        markets = await self.exchange.load_markets()
        assets = set()
        for symbol in markets:
            parts = symbol.split("/")
            if len(parts) == 2:
                assets.update(parts)
        return sorted(list(assets))

    async def get_trading_pairs(self):
        markets = await self.exchange.load_markets()
        pairs = []
        for symbol, market in markets.items():
            pairs.append(
                {
                    "symbol": symbol,
                    "base": market.get("base"),
                    "quote": market.get("quote"),
                    "active": market.get("active", False),
                }
            )
        return pairs

    async def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 500):
        ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        return [
            {
                "timestamp": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
            }
            for candle in ohlcv
        ]

    async def close(self):
        await self.exchange.close()
