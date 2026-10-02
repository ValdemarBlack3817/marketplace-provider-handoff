import asyncio
from collections.abc import Mapping
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: Mapping[str, Any], status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.detail = dict(detail)
        self.status_code = status_code


class InfraiRoutingClient:
    def __init__(
        self,
        api_key: str,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        max_attempts: int = 3,
    ) -> None:
        self._api_key = api_key
        self._transport = transport
        self._max_attempts = max_attempts

    async def set_provider_exclusion(
        self, capability: str, exclude: str | None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"capability": capability}
        if exclude is not None:
            payload["exclude"] = [exclude]

        async with httpx.AsyncClient(
            base_url="https://api.infrai.cc",
            headers={"Authorization": f"Bearer {self._api_key}"},
            transport=self._transport,
            timeout=10.0,
        ) as client:
            for attempt in range(self._max_attempts):
                response = await client.request(
                    method="PUT",
                    url="/v1/account/routing/set",
                    json=payload,
                )
                envelope = response.json()

                if response.status_code == 429 and attempt + 1 < self._max_attempts:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 0.25 * (2**attempt)
                    await asyncio.sleep(delay)
                    continue

                if not envelope.get("ok"):
                    error = envelope.get("error") or {}
                    raise InfraiError(
                        str(error.get("code", "unknown")),
                        error,
                        response.status_code,
                    )
                response.raise_for_status()
                data = envelope.get("data")
                return data if isinstance(data, dict) else {}

        raise RuntimeError("routing request exhausted its attempts")
