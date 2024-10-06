from fastapi import FastAPI
import uvicorn
from src.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='API - Nasa Challenge')
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere para uma lista específica de origens se necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True)
