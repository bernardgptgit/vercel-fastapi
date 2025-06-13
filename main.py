from fastapi import FastAPI, Query, HTTPException
from kucoin_client import KucoinFuturesClient
import logging
from fastapi.responses import JSONResponse

app = FastAPI()
client = KucoinFuturesClient()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ticker_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



@app.on_event("startup")
async def startup():
    await client.init()

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.get("/balance")
async def get_balance():
    return await client.fetch_balance()

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


@app.get("/ticker")
async def get_ticker():
    try:
        # Initialize client
        logger.info("Initializing client connection")
        await client.init()
        
        symbol = "BTCUSDTM"
        logger.info(f"Fetching ticker for symbol: {symbol}")
        
        try:
            ticker = await client.fetch_ticker(symbol)
            logger.info(f"Successfully fetched ticker data: {ticker}")
        except Exception as fetch_error:
            logger.error(f"Failed to fetch ticker: {str(fetch_error)}", exc_info=True)
            raise HTTPException(status_code=400, detail="Ticker fetch failed")
        
        return JSONResponse(content=ticker)
        
    except Exception as e:
        logger.error(f"Unexpected error in ticker endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
        
    finally:
        try:
            logger.info("Closing client connection")
            await client.close()
        except Exception as close_error:
            logger.error(f"Error while closing client: {str(close_error)}", exc_info=True)