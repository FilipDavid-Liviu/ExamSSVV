from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.repository import InMemoryRepository, seed_data
from backend.services import FarmService
from backend.routers import web_router

app = FastAPI(title="Agricultural Crop Rotation Management System")

# Mount static files for CSS
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Initialize Data Access
repo = InMemoryRepository()
seed_data(repo)

# Initialize Service
service = FarmService(repo)

# Inject service into application state
app.state.farm_service = service

# Include routers
app.include_router(web_router)
