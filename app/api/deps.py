import hmac
import hashlib
import logging
from typing import Optional
from fastapi import Header, HTTPException, Request

from core.config import settings

logger = logging.getLogger(__name__)


async def verify_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature")
) -> bool:
    """
    Verify webhook signature if WEBHOOK_SECRET is configured.
    Adapt this to match your self-service platform's signature mechanism.
    
    Args:
        request: FastAPI request object
        x_webhook_signature: Signature header from webhook
        
    Returns:
        True if verification passes or is disabled
        
    Raises:
        HTTPException: If signature verification fails
    """
    # If no webhook secret is configured, skip verification
    if not settings.WEBHOOK_SECRET:
        logger.debug("Webhook signature verification disabled (no secret configured)")
        return True
    
    # If secret is configured but no signature provided, reject
    if not x_webhook_signature:
        logger.warning("Webhook signature missing but secret is configured")
        raise HTTPException(status_code=401, detail="Missing webhook signature")
    
    try:
        # Get request body
        body = await request.body()
        
        # Calculate expected signature
        expected_signature = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison)
        if not hmac.compare_digest(expected_signature, x_webhook_signature):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        logger.debug("Webhook signature verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        raise HTTPException(status_code=401, detail="Signature verification failed")
