from fastapi import FastAPI, Query, HTTPException
import ccxt
from fastapi.responses import JSONResponse
import ccxt
import requests

exchange = ccxt.kucoinfutures({
  "apiKey": "67c1cc1545e41a000166e9bc",
  "secret": "f7d03c97-f890-4771-a4c3-71c17e215e18",
  "password": "Ammy*5533@sa",
  "enableRateLimit": True,
  "timeout": 30000   
})

app = FastAPI()


# @app.on_event("startup")
# async def startup():
#     await client.init()

# @app.on_event("shutdown")
# async def shutdown():
#     await client.close()


# @app.get("/position")
# async def get_position(symbol: str = Query(...)):
#     return await client.fetch_position(symbol)

# @app.get("/order")
# async def get_order(order_id: str, symbol: str = Query(None)):
#     return await client.fetch_order(order_id, symbol)

# @app.get("/open-orders")
# async def open_orders(symbol: str = Query(None)):
#     return await client.fetch_open_orders(symbol)

# @app.post("/create-order")
# async def create_order(
#     symbol: str,
#     side: str,
#     cost: float,
#     tp: float,
#     sl: float,
#     leverage: int,
#     tags: str
# ):
#     return await client.create_future_market_order(symbol, side, cost, tp, sl, leverage, tags)

@app.get("/ticker")
def fetch_ticker(symbol: str = Query(...)):
  try:
    ticker = exchange.fetchTicker(symbol)
    ticker['bid'] = float(ticker['bid']) if ticker['bid'] is not None else None
    ticker['ask'] = float(ticker['ask']) if ticker['ask'] is not None else None
    ticker['last'] = float(ticker['last']) if ticker['last'] is not None else None
    return ticker
  except Exception as e:
    print("❌ Error fetching ticker:", e)
    return None


# @app.get("/balance")
# async def get_balance():
#     try:
#         # Initialize client with timeout
#         logger.info("Initializing client connection")
#         try:
#             await client.init()
#         except Exception as init_error:
#             logger.error(f"Client initialization failed: {str(init_error)}", exc_info=True)
#             raise HTTPException(
#                 status_code=503,
#                 detail="Service temporarily unavailable"
#             )

#         logger.info(f"Fetching balance")

#         try:
#             ticker = await client.fetch_balance()
#             logger.info(f"balance data retrieved successfully")
#             return JSONResponse(content=ticker)
#         except Exception as fetch_error:
#             logger.error(f"balance fetch failed for : {str(fetch_error)}", exc_info=True)
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Could not retrieve balance data "
#             )

#     except HTTPException:
#         # Re-raise already handled HTTP exceptions
#         raise
#     except Exception as e:
#         logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error"
#         )
#     finally:
#         try:
#             if 'client' in locals() and hasattr(client, 'close'):
#                 logger.info("Closing client connection")
#                 await client.close()
#         except Exception as close_error:
#             logger.error(f"Error closing client: {str(close_error)}", exc_info=True)