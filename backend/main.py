from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base

import models
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.buyer_routes import router as buyer_router
from routes.farmer_routes import router as farmer_router
import os
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Unnat Kisan API",
    description="Farmer to Buyer Agricultural Marketplace",
    version="1.0.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
os.makedirs("upload/crops", exist_ok=True)
os.makedirs("upload/payment_proofs", exist_ok=True)
os.makedirs("upload/licenses", exist_ok=True)

# Upload directory
app.mount(
    "/upload",
    StaticFiles(directory="upload"),
    name="upload"
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(buyer_router)
app.include_router(farmer_router)


@app.get("/")
def root():
    return {
        "message": "Unnat Kisan Backend is Running",
        "status": "success"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }









