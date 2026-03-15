from __future__ import annotations

import logging
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException, Request, status

from app.config.settings import settings
from app.db.supabase_client import get_supabase_client
from app.services.audit_log_service import audit_log_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])

stripe.api_key = settings.STRIPE_API_KEY or ""


def _get_user_id_from_metadata(obj: dict) -> Optional[str]:
    metadata = obj.get("metadata") or {}
    if isinstance(metadata, dict):
        return metadata.get("user_id")
    return None


def _lookup_user_id_by_customer(sb, customer_id: Optional[str]) -> Optional[str]:
    if not customer_id:
        return None
    try:
        result = (
            sb.table("profiles")
            .select("id")
            .eq("stripe_customer_id", customer_id)
            .maybe_single()
            .execute()
        )
        return result.data.get("id") if result and result.data else None
    except Exception as exc:
        logger.warning("Failed to lookup user by customer id: %s", exc)
        return None


@router.post("/webhook")
async def stripe_webhook(request: Request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured.")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature.")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe payload.")

    event_type = event.get("type")
    data = (event.get("data") or {}).get("object") or {}
    sb = get_supabase_client()
    if sb is None:
        raise HTTPException(status_code=503, detail="Database not configured.")

    user_id = _get_user_id_from_metadata(data)
    if not user_id:
        user_id = _lookup_user_id_by_customer(sb, data.get("customer"))

    updates = {}
    if event_type == "checkout.session.completed":
        updates = {
            "plan_tier": "pro",
            "stripe_customer_id": data.get("customer"),
            "billing_status": data.get("payment_status") or "active",
        }
    elif event_type == "customer.subscription.deleted":
        updates = {
            "plan_tier": "free",
            "billing_status": "canceled",
            "stripe_customer_id": data.get("customer"),
        }
    elif event_type == "customer.subscription.updated":
        status_value = data.get("status") or "unknown"
        plan_tier = "pro" if status_value in {"active", "trialing"} else "free"
        updates = {
            "plan_tier": plan_tier,
            "billing_status": status_value,
            "stripe_customer_id": data.get("customer"),
        }

    if user_id and updates:
        try:
            sb.table("profiles").update(updates).eq("id", str(user_id)).execute()
        except Exception as exc:
            logger.warning("Failed to update billing for user %s: %s", user_id, exc)

    await audit_log_service.log(
        user_id=str(user_id) if user_id else None,
        action="billing_change",
        resource_type="billing",
        resource_id=str(data.get("id") or ""),
        ip_address=request.client.host if request.client else None,
        details={"event_type": event_type, "customer_id": data.get("customer")},
    )

    return {"received": True}
