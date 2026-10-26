from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.models.music_video_job import (
    MusicVideoJobCreateRequest,
    MusicVideoJobStatus,
    StepStatus,
)


class BaseMongoRepository:
    collection_name: str = ""

    def __init__(self, db: AsyncIOMotorDatabase):
        if not self.collection_name:
            raise ValueError("collection_name must be set")
        self.collection = db[self.collection_name]

    async def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        if not item_id:
            return None
        try:
            doc = await self.collection.find_one({"id": item_id})
        except Exception:
            try:
                doc = await self.collection.find_one({"_id": ObjectId(item_id)})
            except Exception:
                return None
        return doc

    async def find_all(
        self,
        limit: int = 20,
        offset: int = 0,
        sort_field: str = "created_at",
        sort_dir: int = -1,
    ) -> List[Dict[str, Any]]:
        cursor = (
            self.collection.find()
            .sort(sort_field, sort_dir)
            .skip(offset)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def update_one(self, item_id: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = await self.collection.update_one({"id": item_id}, {"$set": update})
        if result.matched_count == 0:
            return None
        return await self.find_by_id(item_id)

    async def delete_one(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"id": item_id})
        return result.deleted_count > 0


class MusicVideoRepository(BaseMongoRepository):
    collection_name = "music_videos"

    async def create_job(self, request: MusicVideoJobCreateRequest, job_id: str) -> Dict[str, Any]:
        now = datetime.utcnow()

        job_document = {
            "id": job_id,
            "user_id": "anonymous",
            "status": MusicVideoJobStatus.QUEUED.value,
            "progress": 0,
            "title": request.title,
            "artist": request.artist,
            "style": request.style.value,
            "mood": request.mood,
            "aspect_ratio": request.aspect_ratio,
            "duration_target_seconds": request.duration_target_seconds,
            "enable_lyrics": request.enable_lyrics,
            "enable_body_motion": request.enable_body_motion,
            "nsfw_enabled": request.nsfw_enabled,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "finished_at": None,
            "error": None,
            "image_asset_id": None,
            "audio_asset_id": None,
            "output_video_id": None,
            "thumbnail_id": None,
            "final_video_url": None,
            "thumbnail_url": None,
            "steps": [
                {"name": "audio_analysis", "status": StepStatus.PENDING.value},
                {"name": "lyric_alignment", "status": StepStatus.PENDING.value},
                {"name": "storyboard_generation", "status": StepStatus.PENDING.value},
                {"name": "face_sync", "status": StepStatus.PENDING.value},
                {"name": "clip_generation", "status": StepStatus.PENDING.value},
                {"name": "final_render", "status": StepStatus.PENDING.value},
            ],
            "audio_analysis": {
                "tempo_bpm": None,
                "key": None,
                "energy_curve": [],
                "segments": [],
            },
            "lyric_analysis": {
                "transcript": None,
                "lines": [],
            },
            "storyboard": {
                "shots": [],
                "scene_summary": None,
            },
        }
        return await self.insert_one(job_document)

    async def update_step_status(self, job_id: str, step_name: str, status: str) -> Optional[Dict[str, Any]]:
        job = await self.find_by_id(job_id)
        if not job:
            return None

        for step in job.get("steps", []):
            if step["name"] == step_name:
                step["status"] = status

        update = {"steps": job["steps"], "updated_at": datetime.utcnow()}
        return await self.update_one(job_id, update)

    async def set_progress(self, job_id: str, progress: int) -> Optional[Dict[str, Any]]:
        return await self.update_one(job_id, {"progress": progress, "updated_at": datetime.utcnow()})

    async def mark_started(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.update_one(
            job_id,
            {
                "status": MusicVideoJobStatus.PROCESSING.value,
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )

    async def mark_completed(
        self,
        job_id: str,
        final_video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return await self.update_one(
            job_id,
            {
                "status": MusicVideoJobStatus.COMPLETED.value,
                "finished_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "final_video_url": final_video_url,
                "thumbnail_url": thumbnail_url,
            },
        )

    async def mark_failed(self, job_id: str, error_message: str) -> Optional[Dict[str, Any]]:
        return await self.update_one(
            job_id,
            {
                "status": MusicVideoJobStatus.FAILED.value,
                "error": error_message,
                "finished_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )

    async def mark_canceled(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.update_one(
            job_id,
            {
                "status": MusicVideoJobStatus.CANCELED.value,
                "updated_at": datetime.utcnow(),
            },
        )

    async def update_audio_analysis(self, job_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.update_one(job_id, {"audio_analysis": data, "updated_at": datetime.utcnow()})

    async def update_lyric_analysis(self, job_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.update_one(job_id, {"lyric_analysis": data, "updated_at": datetime.utcnow()})

    async def update_storyboard(self, job_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.update_one(job_id, {"storyboard": data, "updated_at": datetime.utcnow()})


class VideoAssetRepository(BaseMongoRepository):
    collection_name = "video_assets"

    async def create_asset(
        self,
        job_id: str,
        asset_type: str,
        mime_type: str,
        storage_path: str,
        url: str,
        size_bytes: int,
        checksum: str,
    ) -> Dict[str, Any]:
        asset = {
            "id": f"asset_{asset_type}_{job_id[:8]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "job_id": job_id,
            "type": asset_type,
            "mime_type": mime_type,
            "storage_path": storage_path,
            "url": url,
            "size_bytes": size_bytes,
            "checksum": checksum,
            "created_at": datetime.utcnow(),
        }
        return await self.insert_one(asset)

    async def find_by_job_id(self, job_id: str) -> List[Dict[str, Any]]:
        return await self.collection.find({"job_id": job_id}).to_list(length=100)
