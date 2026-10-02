import asyncio
import os

from marketplace_handoff.infrai_client import InfraiRoutingClient
from marketplace_handoff.models import BuyerRoutingUpdate, OrderRequest, SellerAsset
from marketplace_handoff.order_handoff import prepare_order_handoff


async def main() -> None:
    api_key = os.environ["INFRAI_API_KEY"]
    order = OrderRequest(
        order_id="order_1042",
        asset=SellerAsset(
            asset_id="voice_pack_en",
            capability="text-to-speech",
            provider="seller-studio",
        ),
        buyer=BuyerRoutingUpdate(
            buyer_id="buyer_77",
            excluded_provider="vendor-not-approved",
        ),
    )
    handoff = await prepare_order_handoff(order, InfraiRoutingClient(api_key))
    print(handoff.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
