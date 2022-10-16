import uvicorn

from egame179_backend.settings import Settings


def main() -> None:
    """Entrypoint of the application."""
    settings = Settings()
    uvicorn.run(
        "egame179_backend.app.app:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
