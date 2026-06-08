"""Stripe Checkout 支付集成"""
import stripe
from config import STRIPE_SECRET_KEY, STRIPE_SUCCESS_URL, STRIPE_CANCEL_URL

stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(product: dict, quantity: int = 1) -> str:
    """创建 Stripe Checkout Session，返回支付 URL"""
    unit_amount = int(float(product["price"]) * 100)  # 转换为分（Stripe 最小货币单位）

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "cny",
                "product_data": {
                    "name": product["name"],
                    "description": product.get("description", "")[:200],
                    "images": [product.get("image_url", "")] if product.get("image_url") else [],
                },
                "unit_amount": unit_amount,
            },
            "quantity": quantity,
        }],
        mode="payment",
        success_url=STRIPE_SUCCESS_URL,
        cancel_url=STRIPE_CANCEL_URL,
        metadata={
            "product_id": product.get("id", ""),
            "product_name": product.get("name", ""),
        },
    )
    return session.url
