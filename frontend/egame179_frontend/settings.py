from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings
from yarl import URL

# TEMP_DIR = Path(gettempdir())


class Settings(BaseSettings):
    """Application settings."""

    backend_host: str = "localhost"
    backend_port: int = 8000

    @property
    def backend_url(self) -> URL:
        """Assemble backend URL from settings.

        Returns:
            URL: backend URL.
        """
        return URL.build(scheme="http", host=self.backend_host, port=self.backend_port, path="/api/")

    class Config:
        env_file = ".env"
        env_prefix = "EGAME179_"
        env_file_encoding = "utf-8"


settings = Settings()
