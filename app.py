from fastapi import FastAPI
import uvicorn
from src.api.v1.api import api_router

app = FastAPI(title='API - Nasa Challenge')
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True)
