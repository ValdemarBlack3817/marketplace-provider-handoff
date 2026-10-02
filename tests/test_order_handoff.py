import asyncio

import pytest

from marketplace_handoff.models import BuyerRoutingUpdate, OrderRequest, SellerAsset
from marketplace_handoff.order_handoff import prepare_order_handoff


class RecordingRouting:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    async def set_provider_exclusion(
        self, capability: str, exclude: str | None
    ) -> dict[str, object]:
        self.calls.append((capability, exclude))
        return {"provider": "approved-voice-provider"}


def test_buyer_exclusion_is_applied_before_order_handoff() -> None:
    routing = RecordingRouting()
    order = OrderRequest(
        order_id="order_1042",
        asset=SellerAsset(
            asset_id="voice_pack_en",
            capability="text-to-speech",
            provider="seller-studio",
        ),
        buyer=BuyerRoutingUpdate(
            buyer_id="buyer_77", excluded_provider="vendor-not-approved"
        ),
    )

    result = asyncio.run(prepare_order_handoff(order, routing))

    assert routing.calls == [("text-to-speech", "vendor-not-approved")]
    assert result.state == "ready_for_fulfillment"
    assert result.assigned_provider == "approved-voice-provider"


def test_order_stops_when_buyer_excludes_seller_provider() -> None:
    routing = RecordingRouting()
    order = OrderRequest(
        order_id="order_1043",
        asset=SellerAsset(
            asset_id="voice_pack_en",
            capability="text-to-speech",
            provider="seller-studio",
        ),
        buyer=BuyerRoutingUpdate(
            buyer_id="buyer_78", excluded_provider="seller-studio"
        ),
    )

    with pytest.raises(ValueError, match="buyer excludes"):
        asyncio.run(prepare_order_handoff(order, routing))

    assert routing.calls == []
