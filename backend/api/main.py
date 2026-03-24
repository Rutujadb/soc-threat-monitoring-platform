import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import Base, engine
from api.routes import alerts, cases, ingest, metrics, rules_api
from detection.engine import DetectionEngine

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def create_app() -> FastAPI:
    app = FastAPI(title="SOC Threat Monitoring API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.repo_root = REPO_ROOT
    app.state.detection_engine = DetectionEngine(REPO_ROOT / "rules")

    @app.on_event("startup")
    def _startup():
        if os.environ.get("TESTING") == "1":
            return
        Base.metadata.create_all(bind=engine)

    app.include_router(ingest.router)
    app.include_router(alerts.router)
    app.include_router(cases.router)
    app.include_router(metrics.router)
    app.include_router(rules_api.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
