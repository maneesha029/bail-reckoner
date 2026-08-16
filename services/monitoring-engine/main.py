from fastapi import FastAPI
from routes import router
from logging_config import logger, log_alert_created, log_email_sent

app = FastAPI(
    title="Bail Reckoner Monitoring Engine",
    description="Case monitoring and alert creation system",
    version="1.0.0"
)

# Include the router
app.include_router(router)

logger.info("Application starting up")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Monitoring Engine API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)