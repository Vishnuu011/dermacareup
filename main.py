from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import time
from src.database.base import Base
from src.database.sessionmaker import engine
from src.logger.custom_logger import logger
from src.routers.authRouters import auth_router
from src.routers.paymentRoutes import payment_router
from src.exceptions.custom_exception import CustomException
# Import all models to register them with Base metadata
from src.models.DatabaseModels import (
    OrganizationModel,
    UserModel,
    SubscriptionsModel,
    PaymentsModel,
    PatientModel,
    ScanModel,
    DetectionModel,
    RecommendationModel,
    ReportModel,
    ScanUsageModel
)


""""
This is the main application file for the FastAPI project. It sets up the FastAPI application, including middleware, routers, and exception handlers.
The application includes a lifespan event handler for logging startup and shutdown times, as well as middleware for logging requests and handling CORS.
The application also includes exception handlers for custom application exceptions and generic exceptions, providing structured error responses and logging of errors. 
Finally, a health check endpoint is defined to verify that the application is running correctly.
"""




@asynccontextmanager
async def lifespan(app: FastAPI):

    """
    Lifespan event handler for the FastAPI application.
    This function is executed during the startup and shutdown phases of the application.
    """
    logger.info("Starting up the application...")
    start_time = time.time()
    yield
    end_time = time.time()
    logger.info(f"Application shutdown completed in {end_time - start_time:.2f} seconds.")
    
app = FastAPI(
    title="Blog API",
    description="A simple blog API built with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)


@app.on_event("startup")
async def startup():
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(payment_router)



@app.middleware("http")
async def log_requests(request, call_next):

    


    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
   
    return response


@app.exception_handler(CustomException)
async def app_http_exception_handler(request: Request, exc: CustomException):


   
    logger.error(f"Error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):

    

    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

@app.get("/")
async def health_check():    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)