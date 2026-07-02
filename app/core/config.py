from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseForge"
    database_url: str = "sqlite:///./pulseforge.db"

    # --- Gemini ---
    gemini_api_key: str = ""

    # --- SMTP (email) ---
    smtp_email: str = ""
    smtp_password: str = ""
    smtp_host: str = ""
    smtp_port: int = 587

    # --- Vapi.ai (voice assistant) ---
    vapi_api_key: str = ""
    vapi_assistant_id: str = ""
    vapi_phone_number_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
