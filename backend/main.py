from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import Base, engine
from utils.router_loader import include_feature_routers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup Event
    @app.on_event("startup")
    def startup():
        Base.metadata.create_all(bind=engine)

    # Root Endpoint
    @app.get("/", tags=["system"])
    def root():
        return {
            "message": "Welcome to TransactAI API",
            "status": "running"
        }

    # Health Check
    @app.get("/health", tags=["system"])
    def health_check():
        return {
            "status": "ok"
        }

    # Database Test
    @app.get("/db-test", tags=["system"])
    def db_test():
        try:
            conn = engine.connect()
            conn.close()

            return {
                "database": "connected",
                "status": "success"
            }

        except Exception as e:
            return {
                "database": "failed",
                "error": str(e)
            }

    # Load Feature Routers
    include_feature_routers(app)

    return app


app = create_app()