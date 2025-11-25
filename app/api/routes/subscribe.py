"""
Subscription API endpoint
"""
from fastapi import APIRouter, Request, HTTPException, Response, BackgroundTasks
from datetime import datetime
import uuid
from app.schemas import SubscribeRequest, SubscribeResponse, ErrorResponse
from app.services.rate_limit import rate_limit_service
from app.services.subscription import subscription_service
from app.services.email import email_service
from app.utils.validation import validate_email, sanitize_email, is_honeypot_filled
from app.utils.logger import logger
from app.config import settings


router = APIRouter()


def generate_correlation_id() -> str:
    """Generate unique correlation ID for request tracking"""
    return f"req_{int(datetime.utcnow().timestamp() * 1000)}_{uuid.uuid4().hex[:9]}"


@router.post(
    "/subscribe",
    response_model=SubscribeResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def subscribe(
    request: Request,
    body: SubscribeRequest,
    background_tasks: BackgroundTasks
) -> Response:
    """
    Subscribe to early access waitlist
    
    - **email**: Valid email address
    - **bot_check**: Honeypot field (should be empty)
    - **source**: Source of subscription (default: "landing_hero")
    """
    correlation_id = generate_correlation_id()
    logger.set_correlation_id(correlation_id)
    
    try:
        # Rate limiting
        allowed, remaining, reset_time = rate_limit_service.check_rate_limit(request)
        
        if not allowed:
            logger.warn("Rate limit exceeded", {
                "ip": rate_limit_service.get_client_ip(request),
                "correlation_id": correlation_id
            })
            
            response_data = ErrorResponse(
                error="Too many requests. Please try again later.",
                code="RATE_LIMIT_EXCEEDED"
            )
            
            response = Response(
                content=response_data.model_dump_json(),
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": reset_time.isoformat()
                }
            )
            return response
        
        # Honeypot check - if bot_check is filled, it's a bot
        if is_honeypot_filled(body.bot_check):
            # Silently reject (don't reveal it's a honeypot)
            logger.info("Bot detected via honeypot", {
                "correlation_id": correlation_id
            })
            return Response(
                content=SubscribeResponse(
                    success=True,
                    message="Thank you for your interest!"
                ).model_dump_json(),
                status_code=200,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": reset_time.isoformat()
                }
            )
        
        # Email validation
        if not body.email or not isinstance(body.email, str):
            logger.warn("Missing email in request", {"correlation_id": correlation_id})
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Email is required",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        # Validate email format
        if not validate_email(body.email):
            logger.warn("Invalid email format", {
                "email": body.email[:10] + "..." if len(body.email) > 10 else body.email,
                "correlation_id": correlation_id
            })
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Please enter a valid email address",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        # Sanitize email
        sanitized_email = sanitize_email(body.email)
        if not sanitized_email:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Please enter a valid email address",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        # Create subscription (sync operation, but FastAPI handles it)
        source = body.source or "landing_hero"
        result = subscription_service.create_subscription(
            email=sanitized_email,
            source=source
        )
        
        # Schedule email sending as background tasks (non-blocking)
        if result.get("success") and not result.get("is_duplicate"):
            background_tasks.add_task(email_service.send_welcome_email, sanitized_email)
            background_tasks.add_task(email_service.send_admin_notification, sanitized_email, source)
        
        logger.info("Subscription processed successfully", {
            "email": sanitized_email[:5] + "***",
            "source": source,
            "correlation_id": correlation_id,
            "is_duplicate": result.get("is_duplicate", False)
        })
        
        response_data = SubscribeResponse(
            success=True,
            message=result.get("message", "Thank you for your interest! We'll be in touch soon."),
            is_duplicate=result.get("is_duplicate", False)
        )
        
        return Response(
            content=response_data.model_dump_json(),
            status_code=200,
            media_type="application/json",
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": reset_time.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Subscription error", e, {"correlation_id": correlation_id})
        
        # Don't expose internal error details to client
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Something went wrong. Please try again later.",
                "code": "INTERNAL_ERROR"
            }
        )

