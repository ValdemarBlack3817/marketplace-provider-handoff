import os

from fastapi import FastAPI, HTTPException

from .infrai_client import InfraiError, InfraiRoutingClient
from .models import OrderHandoff, OrderRequest
from .order_handoff import prepare_order_handoff

app = FastAPI(title="Marketplace provider handoff")


@app.post("/orders/handoff", response_model=OrderHandoff)
async def handoff_order(order: OrderRequest) -> OrderHandoff:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="INFRAI_API_KEY is required")

    try:
        return await prepare_order_handoff(order, InfraiRoutingClient(api_key))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InfraiError as exc:
        status_code = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=status_code,
            detail={"code": exc.code, "error": exc.detail},
        ) from exc
