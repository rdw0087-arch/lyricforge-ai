from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from backend.server import app


def _make_wav_bytes() -> bytes:
    return (
        b"RIFF"
        b"\x24\x00\x00\x00"
        b"WAVE"
        b"fmt "
        b"\x10\x00\x00\x00"
        b"\x01\x00\x01\x00"
        b"\x40\x00\x00\x00"
        b"\x80\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"\x02\x00\x00\x00"
        b"\x00\x00\x00\x00"
        b"data"
        b"\x04\x00\x00\x00"
        b"\x00\x00\x00\x00"
    )


def test_create_music_video_job_returns_queued_job():
    client = TestClient(app)

    class FakeRepository:
        async def create_job(self, request, job_id):
            return {
                "id": job_id,
                "status": "queued",
                "progress": 0,
                "title": request.title,
                "artist": request.artist,
                "style": request.style.value,
                "mood": request.mood,
                "aspect_ratio": request.aspect_ratio,
                "duration_target_seconds": request.duration_target_seconds,
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "steps": [
                    {"name": "audio_analysis", "status": "pending"},
                    {"name": "lyric_alignment", "status": "pending"},
                    {"name": "storyboard_generation", "status": "pending"},
                    {"name": "face_sync", "status": "pending"},
                    {"name": "clip_generation", "status": "pending"},
                    {"name": "final_render", "status": "pending"},
                ],
            }

        async def update_one(self, job_id, update):
            return update

        async def find_by_id(self, job_id):
            return None

    class FakeAssetRepository:
        async def create_asset(self, **kwargs):
            return {
                "id": "asset_123",
                "job_id": kwargs["job_id"],
                "type": kwargs["asset_type"],
                "storage_path": kwargs["storage_path"],
                "url": kwargs["url"],
            }

    with patch("backend.api.music_videos.get_db", return_value=MagicMock()), \
         patch("backend.api.music_videos.MusicVideoRepository", return_value=FakeRepository()), \
         patch("backend.api.music_videos.VideoAssetRepository", return_value=FakeAssetRepository()), \
         patch("backend.api.music_videos.enqueue_music_video_job", new=AsyncMock()):

        response = client.post(
            "/api/music-videos",
            files=[
                ("image", ("selfie.png", io.BytesIO(b"fake-png"), "image/png")),
                ("audio", ("song.wav", io.BytesIO(_make_wav_bytes()), "audio/wav")),
            ],
            data={
                "title": "Midnight Echo",
                "artist": "Nova Bloom",
                "style": "cinematic",
                "mood": "romantic",
                "aspect_ratio": "16:9",
                "duration_target_seconds": "60",
                "enable_lyrics": "true",
                "enable_body_motion": "true",
                "nsfw_enabled": "false",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"]
    assert payload["status"] == "queued"
    assert payload["title"] == "Midnight Echo"
    assert payload["artist"] == "Nova Bloom"
    assert payload["style"] == "cinematic"


def test_get_music_video_job_status():
    client = TestClient(app)

    class FakeRepository:
        async def find_by_id(self, job_id):
            return {
                "id": job_id,
                "status": "processing",
                "progress": 25,
                "title": "Test Song",
                "artist": "Tester",
                "style": "cinematic",
                "mood": "romantic",
                "aspect_ratio": "16:9",
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "steps": [
                    {"name": "audio_analysis", "status": "completed"},
                    {"name": "lyric_alignment", "status": "running"},
                    {"name": "storyboard_generation", "status": "pending"},
                ],
                "error": None,
                "final_video_url": None,
                "thumbnail_url": None,
            }

    with patch("backend.api.music_videos.get_db", return_value=MagicMock()), \
         patch("backend.api.music_videos.MusicVideoRepository", return_value=FakeRepository()):

        response = client.get("/api/music-videos/job_123")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "job_123"
    assert payload["status"] == "processing"
    assert payload["progress"] == 25
