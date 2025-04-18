from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from app import create_app

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = create_app()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=eval(os.getenv("BACKEND_CORS_ORIGINS", "[]")),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to AI Email HTML Writer API",
            "version": "0.1.0",
            "status": "operational"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 