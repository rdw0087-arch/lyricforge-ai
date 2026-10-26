# LumaForge

LumaForge is an AI-powered music-video generation app that turns a selfie and a song into a lyric-aware, beat-synced short-form music video.

## Features
- Upload a selfie image and a song file
- Create a generation job and track progress
- Analyze beat structure and lyrics
- Blueprint a storyboard from the song mood and lyrics
- Render a short MVP music video

## Stack
- Backend: FastAPI + MongoDB + Pydantic
- Frontend: React + Axios
- ML/audio: librosa + Whisper

## Local development

### 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

### 2) Start the backend

```bash
source .venv/bin/activate
uvicorn backend.server:app --host 0.0.0.0 --port 8001 --reload
```

### 3) Start the frontend

```bash
cd frontend
npm start
```

## Environment variables

Create a `.env` file in the repo root with:

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=ai_video_generator
```

For the frontend, set:

```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Notes
This repo is the initial milestone for the 60-second MVP. The workload is structured to support future expansion into face sync, body motion, and long-form music-video generation.
