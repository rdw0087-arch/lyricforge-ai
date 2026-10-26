from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LumaForge"
    mongo_url: str = Field(default="mongodb://localhost:27017")
    db_name: str = Field(default="ai_video_generator")
    backend_url: str = Field(default="http://localhost:8001")
    openai_api_key: str = ""
    llm_model: str = Field(default="gpt-4o-mini")
    upload_dir: str = "/tmp/music_video_uploads"
    render_dir: str = "/tmp/music_video_renders"
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]
    allowed_audio_types: list[str] = ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/ogg", "audio/flac"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()
