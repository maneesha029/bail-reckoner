from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routes import router, limiter
from database import init_db
from config import HTTPS_ENFORCED

app = FastAPI(title="Trust & Access Layer")

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if HTTPS_ENFORCED:
    app.add_middleware(HTTPSRedirectMiddleware)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router)
