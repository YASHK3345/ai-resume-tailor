from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import User
from auth.auth import get_current_user_dependency
from database import get_database
import stripe
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/subscription", tags=["subscription"])

# Initialize Stripe (will be configured when user provides keys)
# stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.get("/pricing")
async def get_pricing_plans():
    """Get available pricing plans"""
    
    plans = {
        "free": {
            "name": "Free",
            "price": 0,
            "currency": "USD",
            "interval": "month",
            "features": [
                "3 CV templates",
                "Basic AI suggestions",
                "PDF export",
                "5 AI optimizations per month"
            ],
            "limitations": [
                "Limited templates",
                "Watermark on exports",
                "Limited AI features"
            ]
        },
        "pro": {
            "name": "Pro",
            "price": 9.99,
            "currency": "USD",
            "interval": "month",
            "features": [
                "20+ premium templates",
                "Unlimited AI optimizations",
                "Advanced ATS analysis",
                "All export formats (PDF, Word, HTML)",
                "No watermarks",
                "Priority support",
                "Custom colors and fonts",
                "LinkedIn import"
            ],
            "stripe_price_id": "price_1234567890"  # This would be set in production
        }
    }
    
    return {"plans": plans}

@router.get("/current")
async def get_current_subscription(
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current user subscription details"""
    
    return {
        "tier": current_user.subscription_tier,
        "expires_at": current_user.subscription_expires_at,
        "is_active": current_user.subscription_tier == "pro" and 
                     (current_user.subscription_expires_at is None or 
                      current_user.subscription_expires_at > datetime.utcnow())
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,  # "pro"
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create Stripe checkout session for subscription"""
    
    if plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan selected"
        )
    
    try:
        # This is a placeholder - would need actual Stripe integration
        # For now, return a mock response
        return {
            "message": "Stripe integration not configured. Please contact support.",
            "checkout_url": "#",
            "session_id": "mock_session_id"
        }
        
        # Actual Stripe implementation would be:
        # checkout_session = stripe.checkout.Session.create(
        #     payment_method_types=['card'],
        #     line_items=[
        #         {
        #             'price': 'price_1234567890',  # Pro plan price ID
        #             'quantity': 1,
        #         },
        #     ],
        #     mode='subscription',
        #     success_url='http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}',
        #     cancel_url='http://localhost:3000/pricing',
        #     client_reference_id=current_user.id,
        # )
        # 
        # return {
        #     "checkout_url": checkout_session.url,
        #     "session_id": checkout_session.id
        # }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(
    # request: Request,
    db: AsyncIOMotorClient = Depends(get_database)
):
    """Handle Stripe webhooks"""
    
    # This would handle Stripe webhook events
    # For now, return a placeholder response
    return {"message": "Webhook received"}
    
    # Actual implementation would be:
    # payload = await request.body()
    # sig_header = request.headers.get('stripe-signature')
    # endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    # 
    # try:
    #     event = stripe.Webhook.construct_event(
    #         payload, sig_header, endpoint_secret
    #     )
    # except ValueError:
    #     raise HTTPException(status_code=400, detail="Invalid payload")
    # except stripe.error.SignatureVerificationError:
    #     raise HTTPException(status_code=400, detail="Invalid signature")
    # 
    # # Handle different event types
    # if event['type'] == 'checkout.session.completed':
    #     session = event['data']['object']
    #     # Update user subscription
    #     await handle_successful_payment(session, db)
    # 
    # return {"status": "success"}

@router.post("/cancel")
async def cancel_subscription(
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Cancel user subscription"""
    
    try:
        # Update user subscription in database
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "subscription_tier": "free",
                    "subscription_expires_at": None
                }
            }
        )
        
        return {"message": "Subscription cancelled successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )