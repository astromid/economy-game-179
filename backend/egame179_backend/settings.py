from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())


class Settings(BaseSettings):
    """Application settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    workers_count: int = 1  # quantity of workers for uvicorn
    reload: bool = False  # enable uvicorn reloading
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "egame179_backend"
    db_pass: str = ""
    db_base: str = "egame179"
    db_echo: bool = False

    @property
    def db_url(self) -> URL:
        """Assemble database URL from settings.

        Returns:
            URL: database URL.
        """
        return URL.build(
            scheme="mysql+aiomysql",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "EGAME179_BACKEND_"
        env_file_encoding = "utf-8"


settings = Settings()
