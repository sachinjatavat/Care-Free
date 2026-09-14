from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.database.database import engine, Base, init_db
from backend.api.state import global_state

from backend.api.dashboard import router as dashboard_router
from backend.api.patients import router as patients_router
from backend.api.beds import router as beds_router
from backend.api.simulation import router as simulation_router
from backend.api.analytics import router as analytics_router
from backend.api.decisions import router as decisions_router
from backend.api.hospitals import router as hospitals_router
from backend.api.ambulance import router as ambulance_router
from backend.api.chat import router as chat_router

# Ensure database tables exist
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Run default simulation if not initialized
    if not global_state.active_simulator:
        global_state.initialize_default_simulation()
    yield

app = FastAPI(
    title="CareFlow — Smart Hospital Bed Allocation API",
    description="Backend simulation, online allocation policy, metrics calculation, and telemetry APIs for acute care hospital bed tracking.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard_router)
app.include_router(patients_router)
app.include_router(beds_router)
app.include_router(simulation_router)
app.include_router(analytics_router)
app.include_router(decisions_router)
app.include_router(hospitals_router)
app.include_router(ambulance_router)
app.include_router(chat_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "system": "CareFlow Bed Allocation System",
        "simulator_ready": global_state.active_simulator is not None,
        "seed": global_state.active_simulator.seed if global_state.active_simulator else 20260911
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
