from __future__ import annotations

import os
from typing import Any, Dict

import axios


API_BASE = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")


class MusicVideoClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or API_BASE).rstrip("/")
        self.client = axios.create({
            "baseURL": self.base_url,
            "timeout": 30000,
        })

    async def create_job(self, form_data: FormData):
        response = await self.client.post("/api/music-videos", form_data, {
            headers: {"Content-Type": "multipart/form-data"},
        })
        return response.data

    async def get_job(self, job_id: str):
        response = await self.client.get(f"/api/music-videos/{job_id}")
        return response.data

    async def list_jobs(self):
        response = await self.client.get("/api/music-videos")
        return response.data

    async def cancel_job(self, job_id: str):
        response = await self.client.post(f"/api/music-videos/{job_id}/cancel")
        return response.data


api = MusicVideoClient()


def createMusicVideoJob(formData):
    return api.create_job(formData)


def getMusicVideoJob(jobId):
    return api.get_job(jobId)


def listMusicVideoJobs():
    return api.list_jobs()


def cancelMusicVideoJob(jobId):
    return api.cancel_job(jobId)
