from fastapi import FastAPI, Query
from kucoin_client import KucoinFuturesClient

app = FastAPI()
client = KucoinFuturesClient()

@app.on_event("startup")
async def startup():
    await client.init()

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.get("/balance")
async def get_balance():
    return await client.fetch_balance()

@app.get("/ticker")
async def get_ticker(symbol: str = Query(..., example="BTC/USDT:USDT")):
    return await client.fetch_ticker('BTC/USDT:USDT')

@app.get("/position")
async def get_position(symbol: str = Query(...)):
    return await client.fetch_position(symbol)

@app.get("/order")
async def get_order(order_id: str, symbol: str = Query(None)):
    return await client.fetch_order(order_id, symbol)

@app.get("/open-orders")
async def open_orders(symbol: str = Query(None)):
    return await client.fetch_open_orders(symbol)

@app.post("/create-order")
async def create_order(
    symbol: str,
    side: str,
    cost: float,
    tp: float,
    sl: float,
    leverage: int,
    tags: str
):
    return await client.create_future_market_order(symbol, side, cost, tp, sl, leverage, tags)
