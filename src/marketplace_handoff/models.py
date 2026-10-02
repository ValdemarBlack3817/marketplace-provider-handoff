from typing import Any

from pydantic import BaseModel, Field


class SellerAsset(BaseModel):
    asset_id: str
    capability: str
    provider: str


class BuyerRoutingUpdate(BaseModel):
    buyer_id: str
    excluded_provider: str | None = None


class OrderRequest(BaseModel):
    order_id: str
    asset: SellerAsset
    buyer: BuyerRoutingUpdate


class RoutingReceipt(BaseModel):
    capability: str
    excluded_provider: str | None
    provider: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict, exclude=True)


class OrderHandoff(BaseModel):
    order_id: str
    asset_id: str
    buyer_id: str
    capability: str
    seller_provider: str
    excluded_provider: str | None
    assigned_provider: str | None
    state: str
