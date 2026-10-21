"""EarlyCare FastAPI Application Entrypoint."""
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import router as api_router
from app.core.config import CORS_ORIGINS, MEDICAL_DISCLAIMER, PROJECT_NAME, VERSION

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("earlycare")

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Explainable Multi-Condition Health Risk Screening Platform for Students",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid input value")
        errors.append({"field": field_path, "message": msg, "type": err.get("type")})
    
    logger.warning("Validation error on %s: %s", request.url.path, errors)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Input validation failed. Please check the submitted intake fields.",
            "errors": errors
        }
    )


# General exception handler to prevent leaking internal traces
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal health screening calculation error occurred. Please verify intake parameters."
        }
    )


# Mount routers: both under /api and root for maximum client compatibility
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="")


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": PROJECT_NAME,
        "version": VERSION,
        "status": "online",
        "documentation": "/docs",
        "disclaimer": MEDICAL_DISCLAIMER
    }
