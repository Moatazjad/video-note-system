Video Note System 

An automated system for processing YouTube videos and generating structured educational notes. Supports English and Arabic content with real-time progress tracking.

Features • Tech Stack • Architecture • Getting Started • Screenshots

🎯 About The Project
Video Note System is a comprehensive solution designed to bridge the gap between passive listening and active learning. Originally developed as a Bachelor's Thesis Project for Vistula University, this system automates the tedious process of note-taking during activities where manual writing is impossible (like driving or exercising).

Why Video Note System?
✅ Seamless YouTube Integration - Direct URL processing with time segmentation
✅ Multi-language & RTL Support - Full support for English and Arabic text
✅ Smart AI Generation - Template-based notes (Educational, Business, Research)
✅ Real-time Progress Tracking - Live status updates and graceful task cancellation
✅ Dual Format Export - Download structured notes in Markdown or PDF
✅ Production-Ready - Built with smart retries, error handling, and resource cleanup

✨ Features
📹 Video & Audio Processing

Direct Processing - Download and extract audio seamlessly via yt-dlp and FFmpeg.

Time Segmentation - Process specific chunks of long-form video content.

AI Transcription - High-accuracy speech-to-text using Groq Whisper Large-v3.

🧠 AI Note Generation

Contextual Understanding - Powered by Groq LLaMA 3.3 70B for deep comprehension.

Custom Templates - Automatically structure notes for different contexts (Education, Business, Research).

Language Agnostic - Accurately generate notes in the video's native language.

📄 Export & Localization

PDF Generation - High-quality PDF exports using ReportLab.

RTL Rendering - Native Arabic font support, bidirectional text processing, and reshaping.

Markdown Export - Clean, developer-friendly Markdown files.

🛡️ Enterprise-Grade Reliability

Soft Cancellation - 7 cancellation checkpoints with graceful resource cleanup.

Smart Error Handling - Exponential backoff retries for transient vs. permanent errors.

Race Condition Prevention - Row-level database locking for stable task management.

🛠 Tech Stack
Backend & AI Services

Python 3.11 & FastAPI - High-performance async backend framework.

Celery - Distributed task queue for asynchronous processing.

Groq API - Whisper Large-v3 (Transcription) & LLaMA 3.3 70B (Generation).

PostgreSQL 14 & SQLAlchemy - Relational database and ORM.

Redis 7 - Fast in-memory message broker.

Processing Tools - yt-dlp, FFmpeg, ReportLab, Arabic-reshaper.

Frontend

Next.js 14 - React framework using the modern App Router.

TypeScript - Strict type-checking for scalable frontend architecture.

Tailwind CSS - Utility-first styling for rapid UI development.

Axios - Promise-based HTTP client.

📐 Architecture & Performance
System Design
Plaintext

┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │ HTTP │   FastAPI    │      │   Celery    │
│  Frontend   │─────▶│   Backend    │─────▶│   Worker    │
│ (TypeScript)│      │   (Python)   │      │  (Async)    │
└─────────────┘      └──────────────┘      └─────────────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌──────────────┐     ┌──────────────┐      ┌─────────────┐
│    Client    │     │ PostgreSQL   │      │   Redis     │
│   Browser    │     │  Database    │      │   Queue     │
└──────────────┘     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │  Groq API   │
                                           │ (AI Models) │
                                           └─────────────┘
Performance Metrics
Transcription: ~5 seconds per 10-minute audio chunk

Note Generation: ~2-3 seconds

Total Processing: ~1-2 minutes for a 10-minute video

Cost: $0 (Optimized for Groq free tier)

🚀 Getting Started
Prerequisites
Python 3.11+

Node.js 18+

PostgreSQL 14+

Redis 7+

FFmpeg

1. Clone the Repository
Bash

git clone https://github.com/Moatazjad/video-note-system.git
cd video-note-system
2. Backend Setup
Bash

cd backend
python -m venv .venv

# Activate virtual environment
# Windows: .venv\Scripts\activate 
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
Note: Edit .env and add your GROQ_API_KEY, DATABASE_URL, and REDIS_URL.

Bash

alembic upgrade head
3. Frontend Setup
Bash

cd frontend
npm install
cp .env.example .env.local
Note: Edit .env.local and set your NEXT_PUBLIC_API_URL.

4. Start Services (3 Terminals Required)
Terminal 1: Backend API

Bash

cd backend
uvicorn app.main:app --reload
Terminal 2: Celery Worker

Bash

cd backend
celery -A app.core.celery_app worker --pool=solo -l info
Terminal 3: Frontend

Bash

cd frontend
npm run dev
Access the application at http://localhost:3000

📸 Screenshots
(Replace these with actual images/GIFs of your project!)

Dashboard Overview
[Insert Screenshot of the Next.js UI showing the URL input area]

Real-Time Progress Tracking
<img width="2141" height="1245" alt="2" src="https://github.com/user-attachments/assets/31d58063-eedb-4906-8c33-1867c48f0075" />

Generated Notes & PDF Export
[Insert Screenshot of the dual-pane view or the generated Arabic PDF showing RTL text]

🔒 Security & Privacy
Environment Isolation - Secure storage of sensitive API keys via environment variables.

Input Validation - Client-side URL validation and server-side path traversal protection.

Secure Downloads - Safe external linking (noopener, noreferrer).

📄 License
Distributed under the MIT License - For educational purposes.

👤 Author & Acknowledgments
Moataz Jad Ahmed

Institution: Vistula University, Warsaw (Computer Engineering)

Project: Bachelor's Thesis 2026

GitHub: @Moatazjad

Special Thanks:

Groq for providing exceptional, high-speed free AI API access.

Vistula University for academic support and guidance.

The incredible open-source community behind the tools that made this possible.
