from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseForge"
    database_url: str = "sqlite:///./pulseforge.db"

    # --- Gemini ---
    gemini_api_key: str = ""

    # --- Resend (email) ---
    resend_api_key: str = ""
    # The verified sender address in your Resend account.
    # Free plan: use 'onboarding@resend.dev' to send ONLY to your own Resend account email.
    # Production: use 'noreply@yourdomain.com' after verifying a domain in Resend.
    resend_from_email: str = "onboarding@resend.dev"

    # --- Vapi.ai (voice assistant) ---
    vapi_api_key: str = ""
    vapi_assistant_id: str = ""
    vapi_phone_number_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
