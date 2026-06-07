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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup():
        Base.metadata.create_all(bind=engine)

    @app.get("/", tags=["system"])
    def root():
        return {
            "message": "Welcome to TransactAI API",
            "status": "running"
        }

    @app.get("/health", tags=["system"])
    def health_check():
        return {"status": "ok"}

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

    @app.get("/cors-test", tags=["system"])
    def cors_test():
        return {
            "origins": settings.cors_origins
        }

    include_feature_routers(app)

    return app


app = create_app()