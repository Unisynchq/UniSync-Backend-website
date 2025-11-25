"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from app.config import settings
from app.middleware.cors import setup_cors
from app.api.routes import subscribe
from app.utils.logger import logger
from app.schemas import HealthResponse


# Initialize FastAPI app
app = FastAPI(
    title="UniSync Backend API",
    description="Backend API for UniSync - Feedback Management Platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with correlation ID"""
    import uuid
    correlation_id = f"req_{int(datetime.utcnow().timestamp() * 1000)}_{uuid.uuid4().hex[:9]}"
    logger.set_correlation_id(correlation_id)
    
    start_time = datetime.utcnow()
    
    logger.info("Request received", {
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params),
        "correlation_id": correlation_id
    })
    
    response = await call_next(request)
    
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info("Request completed", {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": f"{process_time:.3f}s",
        "correlation_id": correlation_id
    })
    
    return response


# Setup CORS (after other middleware to ensure proper execution order)
setup_cors(app)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error("Unhandled exception", exc, {
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong. Please try again later.",
            "code": "INTERNAL_ERROR"
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.ENVIRONMENT
    )


# Include API routes
app.include_router(
    subscribe.router,
    prefix=settings.API_PREFIX,
    tags=["subscriptions"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("UniSync Backend API starting", {
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    })


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("UniSync Backend API shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

