from fastapi import FastAPI

from src_auth.api.router import router as main_router
from src_auth.core.config.lifespan import lifespan
from src_auth.core.exc.handlers import register_exception_handlers

app = FastAPI(
    title="Auth API",
    docs_url="/api/auth/doc/",
    openapi_url="/api/auth/doc/openapi.json",
    description="Auth API.",
    version="0.0.1",
    lifespan=lifespan,
)
app.include_router(main_router)
register_exception_handlers(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
