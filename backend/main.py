from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Myntra AI Discovery Engine API",
    description="API for the Myntra AI-Powered Discovery Engine",
    version="1.0.0",
)

# Configure CORS for the frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Myntra AI Discovery Engine API"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
