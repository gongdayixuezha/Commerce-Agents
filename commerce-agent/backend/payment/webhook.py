"""Stripe Webhook 处理"""
from fastapi import APIRouter, Request, HTTPException
import stripe
from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

stripe.api_key = STRIPE_SECRET_KEY
router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """接收 Stripe Webhook 事件"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 处理支付完成事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"[Payment] Completed: {session.get('metadata', {}).get('product_name', 'Unknown')} "
              f"- ¥{session.get('amount_total', 0) / 100:.2f}")

    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        print(f"[Payment] Expired: {session.get('id', '')}")

    return {"status": "ok"}
