from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    """

    Settings are read from environment variables.

    Why this matters:

    - Keeps secrets (e.g., DB passwords) out of code.

    - Matches how AWS deployments work (ECS passes env vars).

    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/tfl"

    tfl_base_url: str = "https://api.tfl.gov.uk"

    # Optional: TfL app_id/app_key for higher rate limits (not required for basic usage).

    tfl_app_id: str | None = None

    tfl_app_key: str | None = None


settings = Settings()
 