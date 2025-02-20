from typing import Optional, List

from fastapi import Body, Cookie, File, Form, Header, Path, Query,FastAPI
from setuptools import Require

from bybit_api import send_request
import json
app = FastAPI(
    title="Bybit P2P API",
    description="API documentation for Bybit P2P services",
    version="1.0",
    docs_url="/swagger",
    redoc_url="/redoc"
)


@app.post("/p2p/info")
def get_p2p_info():
    return send_request("POST", "/v5/p2p/user/personal/info", body={})


@app.get("/server-time")
def get_time():
    return send_request("GET", "/v5/time")

@app.get("/wallet-balance")
def get_wallet_balance():
    return send_request("POST", "/v5/account/wallet-balance")


#POST
@app.post("/p2p/adslist")
def get_p2p_adslist(
        itemId: str = Query(None, description="Ad's ID"),
        status: str = Query(None, description="1 - Sold Out, 2 - Available"),
        side: str = Query(None, description="0 - Buy, 1 - Sell"),
        tokenId: str = Query(None, description="Token ID (e.g., USDT, ETH, BTC)"),
        page: str = Query(None, description="Page number, default is 1"),
        size: str = Query(None, description="Page size, default is 10"),
        currency_id: str = Query(None, description="Currency ID (e.g., HKD, USD, EUR)")
):
    body = {
        "itemId": itemId,
        "status": status,
        "side": side,
        "tokenId": tokenId,
        "page": page,
        "size": size,
        "currency_id": currency_id
    }
    # Remove None values
    body = {k: v for k, v in body.items() if v is not None}

    return send_request("POST", "/v5/p2p/item/personal/list", body)

@app.post("/p2p/order-info")
def get_p2p_order_info(orderId: str = Body(..., embed=True, description="Order ID")):

    body = {"orderId": orderId}
    return send_request("POST", "/v5/p2p/order/info", body)

@app.post("/p2p/order/simplify-list")
def get_p2p_order_simplify_list(
    page: int = Body(..., description="Page number to query"),
    size: int = Body(..., description="Rows to query per page"),
    status: Optional[int] = Body(None, description="Order status"),
    beginTime: Optional[str] = Body(None, description="Begin time"),
    endTime: Optional[str] = Body(None, description="End time"),
    tokenId: Optional[str] = Body(None, description="Token ID"),
    side: Optional[List[int]] = Body(None, description="Side (list of integers)")
):

    body = {
        "status": status,
        "beginTime": beginTime,
        "endTime": endTime,
        "tokenId": tokenId,
        "side": side,
        "page": page,
        "size": size
    }

    # Remove None values
    body = {k: v for k, v in body.items() if v is not None}

    return send_request("POST", "/v5/p2p/order/simplifyList", body)

@app.post("/p2p/pending")
def get_p2p_pending():
    return send_request("POST", "/v5/p2p/order/pending/simplifyList", body={})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
