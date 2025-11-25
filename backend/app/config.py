from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GCS_BUCKET: str
    GCP_SERVICE_ACCOUNT_JSON: str = ""  # path to service account JSON file
    PROJECT_ID: str = ""
    SECRET_KEY: str = "changeme"
    ALLOW_ORIGINS: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
