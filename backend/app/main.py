"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import get_settings
from app.schemas.errors import ErrorCode, ErrorResponse, fallback_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"🔮 {settings.app_name} v{settings.app_version} ({settings.env})")
    print(f"   CORS origins: {settings.cors_origins}")
    print(f"   Mock AI: {settings.use_mock_ai}")
    yield
    print("👋 Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="shushu-hub API",
        description="Unified API for multiple Chinese divination (術數) systems.",
        version=settings.app_version,
        lifespan=lifespan,
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="ui")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {}
        safe_errors = []
        for err in exc.errors():
            ctx = err.get("ctx")
            if isinstance(ctx, dict):
                err = {k: v for k, v in err.items() if k != "ctx"}
                err["ctx_type"] = type(ctx).__name__ if ctx else None
            safe_errors.append(err)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error_code=ErrorCode.INVALID_DATETIME,
                message=first_error.get("msg", fallback_message(ErrorCode.INVALID_DATETIME)),
                details={"errors": safe_errors},
            ).model_dump(mode="json"),
        )

    return app


app = create_app()
