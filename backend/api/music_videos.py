from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.db.mongo import get_db
from backend.db.repositories import MusicVideoRepository, VideoAssetRepository
from backend.models.music_video_job import (
    MusicVideoJobCreateRequest,
    MusicVideoJobStatus,
    MusicVideoJobResponse,
    MusicVideoJobStatusResponse,
    StepSchema,
    StepStatus,
)

router = APIRouter(prefix="/api")


def _job_to_response(job: Dict[str, Any]) -> MusicVideoJobResponse:
    return MusicVideoJobResponse(
        id=job["id"],
        status=MusicVideoJobStatus(job["status"]),
        progress=job.get("progress", 0),
        title=job.get("title"),
        artist=job.get("artist"),
        style=job.get("style"),
        mood=job.get("mood"),
        aspect_ratio=job.get("aspect_ratio"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        steps=[
            StepSchema(
                name=step["name"],
                status=StepStatus(step["status"]),
                started_at=step.get("started_at"),
                finished_at=step.get("finished_at"),
                details=step.get("details", {}),
            )
            for step in job.get("steps", [])
        ],
        error=job.get("error"),
        final_video_url=job.get("final_video_url"),
        thumbnail_url=job.get("thumbnail_url"),
    )


@router.post("/music-videos", response_model=MusicVideoJobResponse)
async def create_music_video_job(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    title: str = Form(...),
    artist: Optional[str] = Form(None),
    style: str = Form("cinematic"),
    mood: str = Form("romantic"),
    aspect_ratio: str = Form("16:9"),
    duration_target_seconds: int = Form(60),
    enable_lyrics: bool = Form(True),
    enable_body_motion: bool = Form(True),
    nsfw_enabled: bool = Form(False),
):
    if not image or not image.filename:
        raise HTTPException(status_code=400, detail="Image file is required")

    if not audio or not audio.filename:
        raise HTTPException(status_code=400, detail="Audio file is required")

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image file must be an image")

    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Audio file must be an audio file")

    payload = MusicVideoJobCreateRequest(
        title=title,
        artist=artist,
        style=style,
        mood=mood,
        aspect_ratio=aspect_ratio,
        duration_target_seconds=duration_target_seconds,
        enable_lyrics=enable_lyrics,
        enable_body_motion=enable_body_motion,
        nsfw_enabled=nsfw_enabled,
    )

    db = get_db()
    repo = MusicVideoRepository(db)

    job_id = str(uuid.uuid4())
    created = await repo.create_job(payload, job_id)

    upload_dir = "/tmp/music_video_uploads"
    os.makedirs(upload_dir, exist_ok=True)

    image_path = os.path.join(upload_dir, f"{job_id}_image_{image.filename}")
    audio_path = os.path.join(upload_dir, f"{job_id}_audio_{audio.filename}")

    image_bytes = await image.read()
    audio_bytes = await audio.read()

    with open(image_path, "wb") as f:
        f.write(image_bytes)

    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    asset_repo = VideoAssetRepository(db)
    image_asset = await asset_repo.create_asset(
        job_id=job_id,
        asset_type="image",
        mime_type=image.content_type,
        storage_path=image_path,
        url=f"http://localhost:8001/files/{job_id}_image_{image.filename}",
        size_bytes=len(image_bytes),
        checksum=str(abs(hash(image_bytes))),
    )

    audio_asset = await asset_repo.create_asset(
        job_id=job_id,
        asset_type="audio",
        mime_type=audio.content_type,
        storage_path=audio_path,
        url=f"http://localhost:8001/files/{job_id}_audio_{audio.filename}",
        size_bytes=len(audio_bytes),
        checksum=str(abs(hash(audio_bytes))),
    )

    await repo.update_one(
        job_id,
        {
            "image_asset_id": image_asset["id"],
            "audio_asset_id": audio_asset["id"],
            "updated_at": datetime.utcnow(),
        },
    )

    from backend.workers.music_video_worker import enqueue_music_video_job

    await enqueue_music_video_job(job_id)

    return _job_to_response(created)


@router.get("/music-videos/{job_id}", response_model=MusicVideoJobStatusResponse)
async def get_music_video_job(job_id: str):
    db = get_db()
    repo = MusicVideoRepository(db)
    job = await repo.find_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Music video job not found")

    return MusicVideoJobStatusResponse(
        id=job["id"],
        status=MusicVideoJobStatus(job["status"]),
        progress=job.get("progress", 0),
        steps=[
            StepSchema(
                name=step["name"],
                status=StepStatus(step["status"]),
                started_at=step.get("started_at"),
                finished_at=step.get("finished_at"),
                details=step.get("details", {}),
            )
            for step in job.get("steps", [])
        ],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        final_video_url=job.get("final_video_url"),
        thumbnail_url=job.get("thumbnail_url"),
        error=job.get("error"),
    )


@router.get("/music-videos/{job_id}/result")
async def get_music_video_result(job_id: str):
    db = get_db()
    repo = MusicVideoRepository(db)
    job = await repo.find_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Music video job not found")

    return {
        "id": job["id"],
        "status": job["status"],
        "title": job["title"],
        "artist": job.get("artist"),
        "style": job.get("style"),
        "final_video_url": job.get("final_video_url"),
        "thumbnail_url": job.get("thumbnail_url"),
        "music_analysis": job.get("audio_analysis", {}),
        "storyboard": job.get("storyboard", {}),
    }


@router.get("/music-videos")
async def list_music_video_jobs(limit: int = 20, offset: int = 0):
    db = get_db()
    repo = MusicVideoRepository(db)
    jobs = await repo.find_all(limit=limit, offset=offset)
    return jobs


@router.post("/music-videos/{job_id}/cancel")
async def cancel_music_video_job(job_id: str):
    db = get_db()
    repo = MusicVideoRepository(db)
    job = await repo.find_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Music video job not found")

    await repo.mark_canceled(job_id)
    return {"message": "Music video job canceled", "job_id": job_id}


@router.get("/music-videos/accepts")
async def accepted_music_video_formats():
    return {
        "accepted_image_types": ["jpg", "png", "webp"],
        "accepted_audio_types": ["wav", "mp3", "m4a", "ogg", "flac"],
        "preferred_audio_types": ["wav", "flac"],
        "max_duration_seconds": 480,
        "max_file_size_mb": 500,
    }
