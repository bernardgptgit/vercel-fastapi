import ccxt.async_support as ccxt


class KucoinFuturesClient:
    def __init__(self):
        self.api_key = '67c1cc1545e41a000166e9bc'
        self.api_secret = 'f7d03c97-f890-4771-a4c3-71c17e215e18'
        self.api_pass = 'Ammy*5533@sa'
        self.exchange = None

    async def init(self):
        self.exchange = ccxt.kucoinfutures({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.api_pass,
            'enableRateLimit': True,
            'timeout': 30000
        })
        print("✅ KuCoin Futures client initialized.")

    async def fetch_balance(self):
        return await self.exchange.fetch_balance()

    async def fetch_ticker(self, symbol):
        return await self.exchange.fetch_ticker(symbol)

    async def fetch_order(self, order_id, symbol=None):
        return await self.exchange.fetch_order(order_id, symbol)

    async def fetch_position(self, symbol):
        return await self.exchange.fetch_position(symbol)

    async def fetch_open_orders(self, symbol=None):
        return await self.exchange.fetch_open_orders(symbol)

    async def create_future_market_order(self, symbol, side, cost, tp, sl, leverage, tags):
        ticker = await self.fetch_ticker(symbol)
        entry_price = float(ticker['bid'] if side == 'buy' else ticker['ask'])

        takeProfit = round(entry_price * (1 + tp / 100), 4) if side == 'buy' else round(entry_price * (1 - tp / 100), 4)
        stopLoss = round(entry_price * (1 - sl / 100), 4) if side == 'buy' else round(entry_price * (1 + sl / 100), 4)

        return await self.exchange.create_order_with_take_profit_and_stop_loss(
            symbol=symbol,
            type='market',
            side=side,
            amount=cost,
            price=None,
            takeProfit=takeProfit,
            stopLoss=stopLoss,
            params={'leverage': leverage, 'tags': tags}
        )

    async def close(self):
        if self.exchange:
            await self.exchange.close()
