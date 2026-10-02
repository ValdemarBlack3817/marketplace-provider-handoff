from typing import Protocol

from .models import OrderHandoff, OrderRequest, RoutingReceipt


class RoutingPort(Protocol):
    async def set_provider_exclusion(
        self, capability: str, exclude: str | None
    ) -> dict[str, object]:
        raise AssertionError("structural typing declaration")


async def prepare_order_handoff(
    order: OrderRequest, routing: RoutingPort
) -> OrderHandoff:
    if order.buyer.excluded_provider == order.asset.provider:
        raise ValueError("buyer excludes the provider attached to this seller asset")

    data = await routing.set_provider_exclusion(
        order.asset.capability, order.buyer.excluded_provider
    )
    receipt = RoutingReceipt(
        capability=order.asset.capability,
        excluded_provider=order.buyer.excluded_provider,
        provider=data.get("provider") if isinstance(data.get("provider"), str) else None,
        raw=data,
    )
    return OrderHandoff(
        order_id=order.order_id,
        asset_id=order.asset.asset_id,
        buyer_id=order.buyer.buyer_id,
        capability=receipt.capability,
        seller_provider=order.asset.provider,
        excluded_provider=receipt.excluded_provider,
        assigned_provider=receipt.provider,
        state="ready_for_fulfillment",
    )
