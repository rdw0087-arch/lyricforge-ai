import asyncio
import logging

from backend.db.mongo import get_db
from backend.db.repositories import MusicVideoRepository
from backend.models.music_video_job import StepStatus
from backend.services.audio_analysis import analyze_audio_file

logger = logging.getLogger(__name__)


async def process_music_video_job(job_id: str) -> None:
    db = get_db()
    repo = MusicVideoRepository(db)

    job = await repo.find_by_id(job_id)
    if not job:
        logger.error("Music video job not found: %s", job_id)
        return

    try:
        await repo.mark_started(job_id)
        await repo.update_step_status(job_id, "audio_analysis", StepStatus.RUNNING.value)
        await repo.set_progress(job_id, 15)

        assets = await db["video_assets"].find({"job_id": job_id}).to_list(length=100)
        audio_asset = next((a for a in assets if a.get("type") == "audio"), None)

        if audio_asset is None:
            raise ValueError(f"No audio asset found for job: {job_id}")

        analysis = analyze_audio_file(audio_asset["storage_path"])

        await repo.update_audio_analysis(
            job_id,
            {
                "tempo_bpm": analysis.get("tempo_bpm"),
                "sample_rate": analysis.get("sample_rate"),
                "duration_seconds": analysis.get("duration_seconds"),
                "energy_curve": analysis.get("energy_curve"),
                "beats": analysis.get("beats"),
                "lyric_transcript": analysis.get("lyric_transcript"),
                "lyric_segments": analysis.get("lyric_segments"),
            },
        )

        await repo.update_lyric_analysis(
            job_id,
            {
                "transcript": analysis.get("lyric_transcript"),
                "lines": analysis.get("lyric_segments", []),
            },
        )

        await repo.update_step_status(job_id, "audio_analysis", StepStatus.COMPLETED.value)
        await repo.update_step_status(job_id, "lyric_alignment", StepStatus.COMPLETED.value)
        await repo.set_progress(job_id, 60)

        await repo.update_step_status(job_id, "storyboard_generation", StepStatus.RUNNING.value)
        await repo.set_progress(job_id, 80)
        await repo.update_step_status(job_id, "storyboard_generation", StepStatus.COMPLETED.value)

        await repo.update_step_status(job_id, "face_sync", StepStatus.RUNNING.value)
        await repo.set_progress(job_id, 90)
        await repo.update_step_status(job_id, "face_sync", StepStatus.COMPLETED.value)

        await repo.update_step_status(job_id, "final_render", StepStatus.RUNNING.value)
        await repo.mark_completed(job_id, final_video_url="http://localhost:8001/demo/final.mp4", thumbnail_url="http://localhost:8001/demo/thumbnail.jpg")
        await repo.update_step_status(job_id, "final_render", StepStatus.COMPLETED.value)
        await repo.set_progress(job_id, 100)

        logger.info("Music video job completed: %s", job_id)

    except Exception as exc:
        logger.exception("Music video job failed: %s", job_id)
        await repo.mark_failed(job_id, str(exc))
        await repo.update_step_status(job_id, "final_render", StepStatus.FAILED.value)


async def enqueue_music_video_job(job_id: str) -> None:
    asyncio.create_task(process_music_video_job(job_id))
