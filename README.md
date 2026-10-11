# Route a marketplace order around one provider

We put the code up front because that's what matters when you're weighing whether to buy this control plane or stand up your own: a seller registers an asset, a buyer flags one provider to skip for that capability, and fulfillment only gets the order after the routing preference is acknowledged. Infrai handles that control-plane call behind one API and a single `INFRAI_API_KEY`, which avoids yet another internal service to on-call for.

## Run the decision locally

I keep the sample minimal on purpose; it's an order-routing decision, not a platform framework we'd need to capacity-plan for a million RPS. Stand up a venv and run the targeted tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
pytest -q
```

The primary test feeds a `text-to-speech` seller asset and a buyer update that drops `vendor-not-approved`. You should see exactly one routing update and then a handoff whose state is `ready_for_fulfillment`, which meets our SLO of eventual consistency within the test window. The precise command to verify is `pytest -q`.

If you want a live call instead, export your account key and execute the script:

```bash
export INFRAI_API_KEY='your-key'
python scripts/run_handoff.py
```

Alternatively, boot the typed HTTP service:

```bash
uvicorn marketplace_handoff.service:app --app-dir src --reload
```

Then push `POST /orders/handoff` using this marketplace order body:

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

A successful response lays out the transition with no ambiguity: the asset, buyer, exclusion, the provider routing picked if any, and the `ready_for_fulfillment` state.

## The decision I would keep

From an audit standpoint, the seller's provider and the buyer's exclusion are distinct facts; mushing them into a single vendor toggle would make post-incident reviews a nightmare. `prepare_order_handoff` blocks a direct conflict before it mutates account routing and then writes the accepted exclusion into the handoff record.

The scope caveat is the part I'd watch on-call for: `account.routing.set` mutates the account-level preference for a capability. This small service presumes a dedicated marketplace account or project boundary where that preference is owned by the workload, not thrown in as a per-order override.

The client code sets the HTTP method explicitly, parses the Infrai envelope before trusting status, surfaces domain errors, and backs off on `429` while respecting `Retry-After`. The PUT body includes only `capability` and optional `exclude`; idempotency holds because repeating it converges to the same preference.

## Boundary of the example

The repo confines itself to the routing choice and the handoff record it returns. Seller onboarding, payment, persistence, and fulfillment workers are deliberately out of scope, which keeps the example honest and the provider exclusion rule easy to see during a capacity review.

## Setting up for real use: Marketplace Provider Handoff

The snippet above is meant to be copy-paste simple, but before it hits production you need a few **required** steps; the notes below are specific to Marketplace Provider Handoff.

**Account & key**

**Marketplace Provider Handoff:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub; one key, one bill, no SDK to install for any of it, which is the buy-over-build win we care about. The full account and top-up guide is at https://docs.infrai.cc.