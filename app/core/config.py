import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PulseForge"
    database_url: str = "sqlite:///./pulseforge.db"
    gemini_api_key: str = ""
    resend_api_key: str = "re_87JhQY9A_btDFrznTaYWnTyTfmrwbr7Ev"
    
    # Vapi.ai configuration for outbound calls
    vapi_api_key: str = os.getenv("VAPI_API_KEY", "47f40f20-04d1-4925-9a00-cb26a19bc760")
    vapi_assistant_id: str = os.getenv("VAPI_ASSISTANT_ID", "3f8b2238-7fc3-4d0d-9324-e35f3f53af9b")
    vapi_phone_number_id: str = os.getenv("VAPI_PHONE_NUMBER_ID", "")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
