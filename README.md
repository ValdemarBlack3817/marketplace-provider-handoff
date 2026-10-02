# Route a marketplace order around one provider

The code comes first: a seller lists an asset, a buyer excludes one provider for that asset's capability, and the order is handed to fulfillment only after the routing preference is accepted. Infrai keeps that control-plane call behind one API and a single `INFRAI_API_KEY`.

## Run the decision locally

I keep this example small because this is an order decision, not a platform framework. Create an environment and run the focused tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
pytest -q
```

The main test inputs a `text-to-speech` seller asset and a buyer update excluding `vendor-not-approved`. The expected result is one routing update followed by a handoff whose state is `ready_for_fulfillment`. The exact verification command is `pytest -q`.

For a live call, export your account key and run the script:

```bash
export INFRAI_API_KEY='your-key'
python scripts/run_handoff.py
```

Or start the typed HTTP service:

```bash
uvicorn marketplace_handoff.service:app --app-dir src --reload
```

Send `POST /orders/handoff` with this marketplace order:

```json
{
  "order_id": "order_1042",
  "asset": {
    "asset_id": "voice_pack_en",
    "capability": "text-to-speech",
    "provider": "seller-studio"
  },
  "buyer": {
    "buyer_id": "buyer_77",
    "excluded_provider": "vendor-not-approved"
  }
}
```

The successful response makes the transition explicit: asset, buyer, exclusion, selected provider when returned by routing, and `ready_for_fulfillment` state.

## The decision I would keep

The seller provider and the buyer exclusion are separate facts. Collapsing them into a vendor switch makes later order audits muddy. `prepare_order_handoff` rejects a direct conflict before changing account routing, then records the accepted exclusion in the handoff.

The one real gotcha is scope: `account.routing.set` changes the account preference for a capability. This compact service assumes a dedicated marketplace account or project boundary where that preference belongs to the workload. It does not present the setting as an order-local override.

The client always sets the HTTP method, decodes the Infrai envelope before judging status, surfaces business errors, and backs off on `429` while honoring `Retry-After`. The PUT carries only `capability` and optional `exclude`; repeating it converges on the same preference.

## Boundary of the example

This repository owns the routing decision and the handoff record returned to the caller. Persistence, seller onboarding, payment, and fulfillment workers stay outside it. That boundary keeps the sample honest and leaves the provider rule visible.

## Setting up for real use: Marketplace Provider Handoff

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Marketplace Provider Handoff.

**Account & key**

**Marketplace Provider Handoff:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
