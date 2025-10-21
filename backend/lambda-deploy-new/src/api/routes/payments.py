from fastapi import APIRouter, Depends, HTTPException, status, Request
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from typing import Dict
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Stripe configuration (should be in environment variables)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')

try:
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
except ImportError:
    logger.warning("Stripe library not installed. Payment features will not work.")
    stripe = None


@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    plan: str,
    billing_period: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Create Stripe Checkout Session for subscription

    Args:
        price_id: Stripe price ID
        plan: Plan name (professional, business, enterprise)
        billing_period: monthly or annual
        user_id: Current user ID

    Returns:
        Dict with checkout_url
    """
    if not stripe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is currently unavailable"
        )

    try:
        # Get user email
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=user['email'],
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/en/dashboard.html?checkout=success",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/en/pricing.html?checkout=cancelled",
            metadata={
                'user_id': user_id,
                'plan': plan,
                'billing_period': billing_period
            }
        )

        return {
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Checkout session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Handle Stripe webhook events

    Events handled:
    - checkout.session.completed: Subscription created
    - invoice.payment_succeeded: Payment successful
    - customer.subscription.deleted: Subscription cancelled
    """
    if not stripe:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            plan = session['metadata']['plan']

            # Update user subscription in database
            cursor.execute(
                """
                UPDATE users
                SET subscription_tier = %s,
                    subscription_status = 'active',
                    stripe_customer_id = %s,
                    stripe_subscription_id = %s
                WHERE id = %s
                """,
                (plan, session['customer'], session['subscription'], user_id)
            )

            logger.info(f"Subscription activated for user {user_id}: {plan}")

        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            subscription_id = invoice['subscription']

            # Update subscription status
            cursor.execute(
                """
                UPDATE users
                SET subscription_status = 'active',
                    words_used_this_month = 0
                WHERE stripe_subscription_id = %s
                """,
                (subscription_id,)
            )

            logger.info(f"Payment succeeded for subscription {subscription_id}")

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            subscription_id = subscription['id']

            # Cancel subscription
            cursor.execute(
                """
                UPDATE users
                SET subscription_tier = 'free',
                    subscription_status = 'cancelled'
                WHERE stripe_subscription_id = %s
                """,
                (subscription_id,)
            )

            logger.info(f"Subscription cancelled: {subscription_id}")

        return {'status': 'success'}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/create-payment-intent")
async def create_payment_intent(
    amount: int,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Create Stripe Payment Intent for pay-as-you-go payments

    Args:
        amount: Amount in cents (EUR)
        user_id: Current user ID

    Returns:
        Dict with client_secret for Stripe.js
    """
    if not stripe:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        # Get user
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='eur',
            metadata={'user_id': user_id},
            receipt_email=user['email']
        )

        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment error: {str(e)}"
        )
