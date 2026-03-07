from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.ask import router as ask_router
from api.routers.health import router as health_router
from api.routers.ingest import router as ingest_router
from api.routers.phd import router as phd_router


app = FastAPI(
	title="Floramigo API",
	version="0.1.0",
	description="Sensor-aware Floramigo chatbot API adapted from the floramigo-plant-care-main reference project.",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(phd_router)
