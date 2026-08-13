from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes import router, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    initialize_database()
    yield
    # Any cleanup / shutdown logic goes here if needed


app = FastAPI(title="Eligibility Engine", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {"code": str(exc.status_code), "message": str(exc.detail)},
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "error": {"code": "VALIDATION_ERROR", "message": str(exc)},
        },
    )