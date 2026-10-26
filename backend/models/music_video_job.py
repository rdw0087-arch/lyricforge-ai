from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MusicVideoStyle(str, Enum):
    CINEMATIC = "cinematic"
    ANIME = "anime"
    NEON = "neon"
    DOCUMENTARY = "documentary"
    DARK = "dark"


class MusicVideoJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepSchema(BaseModel):
    name: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class MusicVideoJobCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artist: Optional[str] = None
    style: MusicVideoStyle = MusicVideoStyle.CINEMATIC
    mood: str = "romantic"
    aspect_ratio: str = "16:9"
    duration_target_seconds: int = Field(default=60, ge=15, le=480)
    enable_lyrics: bool = True
    enable_body_motion: bool = True
    nsfw_enabled: bool = False


class MusicVideoJobResponse(BaseModel):
    id: str
    status: MusicVideoJobStatus
    progress: int = 0
    title: Optional[str] = None
    artist: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    aspect_ratio: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    steps: List[StepSchema] = Field(default_factory=list)
    error: Optional[str] = None
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class MusicVideoJobStatusResponse(BaseModel):
    id: str
    status: MusicVideoJobStatus
    progress: int
    steps: List[StepSchema]
    created_at: datetime
    updated_at: datetime
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None


class MusicVideoResultResponse(BaseModel):
    id: str
    status: MusicVideoJobStatus
    title: str
    artist: Optional[str]
    style: str
    final_video_url: Optional[str]
    thumbnail_url: Optional[str]
    clips: List[Dict[str, Any]] = Field(default_factory=list)
    music_analysis: Dict[str, Any] = Field(default_factory=dict)
