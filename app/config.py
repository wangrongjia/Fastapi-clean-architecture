from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # First: Create these variables in .env file
    # Check with this:
    db_engine: str = "sqlite"  # default db; (sqlite/ postgres)

    # sqlite settings (will be read from .env file)
    sqlite_file_name: str = "database.db"

    # Postgres settings (will be read from .env file)
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str | None = None

    # DeepSeek API settings
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_timeout_seconds: float = 60.0

    # OpenRouter API settings
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-oss-120b:free"
    openrouter_claude_model: str = "anthropic/claude-3-haiku"
    openrouter_timeout_seconds: float = 60.0
    openrouter_site_url: str | None = None
    openrouter_app_name: str | None = "FastAPI Clean Architecture"

    # read env vars from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.db_engine == "sqlite":
            if not self.sqlite_file_name:
                raise ValueError(
                    "SQLITE_FILE_NAME must be set when DB_ENGINE=sqlite in .env file",
                )
            return f"sqlite:///{self.sqlite_file_name}"

        elif self.db_engine == "postgres":
            if not all([self.postgres_user, self.postgres_password, self.postgres_db]):
                raise ValueError("Postgres settings incomplete in .env file")
            return (
                f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

        else:
            message = f"Invalid or unsupported DB_ENGINE: {self.db_engine}"
            raise ValueError(message)


# Test with interactive ipynb in vscode itself (using Shift + Enter)
if __name__ == "__main__":
    settings = Settings()
    print(settings.db_engine)
    print(settings.sqlite_file_name)  # dabase.db
    print(settings.database_url)  # sqlite:///dabase.db
