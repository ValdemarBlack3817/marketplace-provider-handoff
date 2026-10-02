import asyncio

import httpx

from marketplace_handoff.infrai_client import InfraiRoutingClient


def test_routing_boundary_sends_only_documented_fields() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/v1/account/routing/set"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.content == b'{"capability":"text-to-speech","exclude":["vendor-a"]}'
        return httpx.Response(
            200,
            json={
                "ok": True,
                "data": {"provider": "vendor-b"},
                "error": None,
                "metadata": {},
            },
        )

    client = InfraiRoutingClient("test-key", transport=httpx.MockTransport(handler))
    data = asyncio.run(client.set_provider_exclusion("text-to-speech", "vendor-a"))

    assert data == {"provider": "vendor-b"}
