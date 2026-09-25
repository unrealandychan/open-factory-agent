"""FastAPI application entrypoint for Open Factory Agent."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from open_factory import __version__
from open_factory.api.dependencies import cron_engine
from open_factory.api.routes import compat, runs, schedules, system, workflows


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cron_engine.start()
    yield
    # Shutdown
    cron_engine.stop()


app = FastAPI(
    title="Open Factory Agent API",
    description="Clean Code & DDD-architected local-first workflow automation platform",
    version=__version__,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(compat.router)
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")

# Mount frontend build if available
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    from open_factory.infrastructure.config import HOST, PORT

    uvicorn.run("open_factory.api.main:app", host=HOST, port=PORT, reload=True)
