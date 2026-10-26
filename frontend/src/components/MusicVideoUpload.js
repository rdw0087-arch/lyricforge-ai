import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const MusicVideoUpload = () => {
  const [title, setTitle] = useState('Midnight Echo');
  const [artist, setArtist] = useState('Nova Bloom');
  const [style, setStyle] = useState('cinematic');
  const [mood, setMood] = useState('romantic');
  const [duration, setDuration] = useState(60);
  const [imageFile, setImageFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!job || !job.id) return;

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API}/music-videos/${job.id}`);
        const nextJob = response.data;
        setJob(nextJob);

        if (nextJob.status === 'completed' || nextJob.status === 'failed' || nextJob.status === 'canceled') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [job]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!imageFile || !audioFile) {
      setError('Please upload both a selfie image and a song file.');
      return;
    }

    setIsUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('audio', audioFile);
    formData.append('title', title);
    formData.append('artist', artist);
    formData.append('style', style);
    formData.append('mood', mood);
    formData.append('duration_target_seconds', String(duration));
    formData.append('enable_lyrics', 'true');
    formData.append('enable_body_motion', 'true');

    try {
      const response = await axios.post(`${API}/music-videos`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setJob(response.data);
    } catch (err) {
      console.error(err);
      setError('Unable to create the music video job.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-semibold mb-4">Create Music Video</h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium mb-2">Song Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Artist</label>
          <input
            type="text"
            value={artist}
            onChange={(e) => setArtist(e.target.value)}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Style</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="cinematic">Cinematic</option>
              <option value="anime">Anime</option>
              <option value="neon">Neon</option>
              <option value="documentary">Documentary</option>
              <option value="dark">Dark</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Mood</label>
            <input
              type="text"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
          <input
            type="range"
            min="30"
            max="180"
            step="10"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="text-sm text-gray-400 mt-2">{duration}s target</div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Selfie Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files[0])}
              className="w-full text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-600 file:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Song File</label>
            <input
              type="file"
              accept=".wav,.mp3,.m4a,.ogg,.flac,audio/*"
              onChange={(e) => setAudioFile(e.target.files[0])}
              className="w-full text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-600 file:text-white"
            />
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-900/40 border border-red-700 text-red-200 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isUploading}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold"
        >
          {isUploading ? 'Generating Music Video...' : 'Generate Music Video'}
        </button>
      </form>

      {job && (
        <div className="mt-6 p-4 rounded-lg bg-gray-900 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-400">Job status</div>
            <div className="text-sm font-medium capitalize text-purple-300">{job.status}</div>
          </div>

          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2.5 rounded-full"
              style={{ width: `${job.progress || 0}%` }}
            />
          </div>

          <div className="mt-3 text-sm text-gray-400">
            {job.status === 'queued' && 'Your music video is waiting in the queue.'}
            {job.status === 'processing' && 'Analyzing the audio and preparing your scenes...'}
            {job.status === 'completed' && 'Your music video is ready.'}
            {job.status === 'failed' && 'The generation failed. Please try again.'}
            {job.status === 'canceled' && 'This job was canceled.'}
          </div>
        </div>
      )}
    </div>
  );
};

export default MusicVideoUpload;
