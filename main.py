import requests
from fastapi import FastAPI, HTTPException, status, Depends, Query
import ccxt
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()

# Configuration
API_KEY_KUCOIN = '67c1cc1545e41a000166e9bc'
API_SECRET_KUCOIN = 'f7d03c97-f890-4771-a4c3-71c17e215e18'
API_PASS_KUCOIN = 'Ammy*5533@sa'


kucoin_futures = ccxt.kucoinfutures({
        'apiKey': API_KEY_KUCOIN,
        'secret': API_SECRET_KUCOIN,
        'password': API_PASS_KUCOIN,
        'enableRateLimit': True,
        'timeout': 30000,
    })

class OrderRequest(BaseModel):
    leverage: float = 20
    price: float
    side: str = None
    cost: float = 10
    symbol: str
    type: str = "market"
    tp: float
    sl: float


class OrderStatusRequest(BaseModel):
    symbol: str = None
    orderID: str = None

@app.get("/ticker")
def fetch_ticker(symbol: str, params: dict):

    try:

        ticker = kucoin_futures.fetch_ticker(
            symbol=symbol,
            params=params or {}
        )
        ticker['bid'] = float(ticker['bid']) if ticker['bid'] is not None else None
        ticker['ask'] = float(ticker['ask']) if ticker['ask'] is not None else None
        ticker['last'] = float(ticker['last']) if ticker['last'] is not None else None

        return ticker


    except ccxt.BaseError as e:
        print(f"Failed to create order ")

        raise

@app.post("/fetch_open_orders_details")
def fetch_open_orders_details():

    try:
        return kucoin_futures.fetch_open_orders()
    except Exception as e:
        print("Unexpected error during fetch order:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/fetch_order_details")
def fetch_order(orderID: str, symbol: str):
    try:
        return kucoin_futures.fetch_order(orderID, symbol)
    except Exception as e:
        print(f"Failed to fetch order {orderID}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/fetch_positions_for_symbol")
def fetch_positions_for_symbol(order_status: OrderStatusRequest):

    try:
        return kucoin_futures.fetch_positions_for_symbol(order_status.symbol)
    except Exception as e:
        print("Failed to fetch order %s: %s", str(e))
        raise


@app.post("/fetch_orders_by_status")
def validate_status(status: str):
    valid_statuses = ['open', 'closed', 'canceled']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {valid_statuses}")
    return status


@app.post("/fetch_orders_by_status")
async def fetch_orders_by_status(
        status: str = Depends(validate_status),
        symbol: str = Query(..., example="BTC/USDT"),
        since: Optional[int] = Query(None, description="Timestamp in milliseconds"),
        limit: Optional[int] = Query(20, ge=1, le=100)
):
    """
    Fetch orders by status from KuCoin Futures.
    Status: 'open', 'closed', 'canceled'
    """
    try:
        params = {}
        if since:
            params['since'] = since
        if limit:
            params['limit'] = limit

        # Standard CCXT method (adjust if KuCoin uses a custom endpoint)
        orders = kucoin_futures.fetch_orders(symbol=symbol, since=since, limit=limit, params=params)

        # Filter by status if not already done by the exchange
        filtered_orders = [order for order in orders if order['status'] == status]
        return filtered_orders

    except ccxt.NetworkError as e:
        raise HTTPException(status_code=502, detail=f"Network error: {str(e)}")
    except ccxt.ExchangeError as e:
        raise HTTPException(status_code=400, detail=f"Exchange error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/place-tp-sl-market-order")
def create_market_futures_order(order_request: OrderRequest):

    try:

        ticker = fetch_ticker(order_request.symbol, {})
        entry_price = float(ticker['bid'] if order_request.side == 'buy' else ticker['ask'])

        if order_request.side == 'buy':
            takeProfitPrice = round(entry_price * (1 + order_request.tp / 100), 4)
            stopLossPrice = round(entry_price * (1 - order_request.sl / 100), 4)

        else:
            takeProfitPrice = round(entry_price * (1 + order_request.tp / 100), 4)
            stopLossPrice = round(entry_price * (1 - order_request.sl / 100), 4)

        return kucoin_futures.create_order_with_take_profit_and_stop_loss(
                symbol=order_request.symbol,
                type='market',
                side=order_request.side,
                amount=order_request.cost,
                price=None,
                takeProfit=takeProfitPrice,
                stopLoss=stopLossPrice,
                params={'leverage': order_request.leverage, 'remark': '1222'}
        )

    except ccxt.BaseError as e:
        print("Failed to create order:", str(e))
        raise HTTPException(status_code=400, detail=f"Kucoin error: {str(e)}")

    except Exception as e:
        print("Unexpected error during order creation:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.post("/place-tp-sl-limit-order")
def create_limit_futures_order(order_request: OrderRequest):

    try:

        ticker = fetch_ticker(order_request.symbol, {})
        entry_price = float(ticker['bid'] if order_request.side == 'buy' else ticker['ask'])
        amount = round(order_request.cost / entry_price, 4)

        if order_request.side == 'buy':
            takeProfitPrice = round(entry_price * (1 + order_request.tp / 100), 4)
            stopLossPrice = round(entry_price * (1 - order_request.sl / 100), 4)

        else:
            takeProfitPrice = round(entry_price * (1 + order_request.sl / 100), 4)
            stopLossPrice = round(entry_price * (1 - order_request.tp / 100), 4)

        return kucoin_futures.create_order_with_take_profit_and_stop_loss(
                symbol=order_request.symbol,
                type='limit',
                side=order_request.side,
                amount=amount,
                price=entry_price,
                takeProfit=takeProfitPrice,
                stopLoss=stopLossPrice,
                params={'leverage': order_request.leverage, 'remark': '1222'}
        )

    except ccxt.BaseError as e:
        print("Failed to create order:", str(e))
        raise HTTPException(status_code=400, detail=f"Kucoin error: {str(e)}")

    except Exception as e:
        print("Unexpected error during order creation:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/webhook-wunder")
def webhook(signal: str):
    url = "https://wtalerts.com/bot/custom"
    
    response = requests.post(url, json={"code": signal})
    print(response.status_code, response.text)

@app.get("/")
async def health_check():
    return {"status": "API is running"}

exchange = ccxt.kucoinfutures({
  "apiKey": "67c1cc1545e41a000166e9bc",
  "secret": "f7d03c97-f890-4771-a4c3-71c17e215e18",
  "password": "Ammy*5533@sa",
  "enableRateLimit": True,
  "timeout": 30000   
})
       
@app.get("/balance") 
def fetch_balance():
  print("⏳ Fetching balance from KuCoin Futures...")
  try:
    balance = exchange.fetch_balance()
    print("✅ Balance fetched successfully.")
    return balance
  except Exception as e:
    print("❌ Error fetching balance:", e)
    return None


