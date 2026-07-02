from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseForge"
    database_url: str = "sqlite:///./pulseforge.db"

    # --- Gemini ---
    gemini_api_key: str = ""

    # --- Gmail SMTP (email) ---
    # The Gmail address you want to send FROM (e.g. pulseforge.team@gmail.com)
    gmail_sender_email: str = ""
    # A Gmail App Password (16 chars) — NOT your regular Gmail password.
    # Generate one at: myaccount.google.com → Security → App Passwords
    gmail_app_password: str = ""

    # --- Vapi.ai (voice assistant) ---
    vapi_api_key: str = ""
    vapi_assistant_id: str = ""
    vapi_phone_number_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
