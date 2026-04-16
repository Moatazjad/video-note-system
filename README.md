<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3304/3304323.png" alt="Logo" width="150" height="150">

  <p><b>An automated system for processing YouTube videos and generating structured educational notes.</b></p>

  <p>
    <img src="https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js" alt="Next.js">
    <img src="https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-14-4169E1?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License">
  </p>

  <p>
    <a href="#-features">Features</a> •
    <a href="#-tech-stack">Tech Stack</a> •
    <a href="#-architecture--performance">Architecture</a> •
    <a href="#-getting-started">Getting Started</a> •
    <a href="#-screenshots">Screenshots</a>
  </p>
</div>

---

##  About The Project

**Video Note System** is a comprehensive solution designed to bridge the gap between passive listening and active learning. Originally developed as a Bachelor's Thesis Project for Vistula University, this system automates the tedious process of note-taking during activities where manual writing is impossible (like driving or exercising). 

### Why Video Note System?

* ✅ **Seamless YouTube Integration** - Direct URL processing with time segmentation
* ✅ **Multi-language & RTL Support** - Full support for English and Arabic text
* ✅ **Smart AI Generation** - Template-based notes (Educational, Business, Research)
* ✅ **Real-time Progress Tracking** - Live status updates and graceful task cancellation
* ✅ **Dual Format Export** - Download structured notes in Markdown or PDF
* ✅ **Production-Ready** - Built with smart retries, error handling, and resource cleanup

---

## ✨ Features

### 📹 Video & Audio Processing
* **Direct Processing** - Download and extract audio seamlessly via yt-dlp and FFmpeg.
* **Time Segmentation** - Process specific chunks of long-form video content.
* **AI Transcription** - High-accuracy speech-to-text using Groq Whisper Large-v3.

### 🧠 AI Note Generation
* **Contextual Understanding** - Powered by Groq LLaMA 3.3 70B for deep comprehension.
* **Custom Templates** - Automatically structure notes for different contexts (Education, Business, Research).
* **Language Agnostic** - Accurately generate notes in the video's native language.

### 📄 Export & Localization
* **PDF Generation** - High-quality PDF exports using ReportLab.
* **RTL Rendering** - Native Arabic font support, bidirectional text processing, and reshaping.
* **Markdown Export** - Clean, developer-friendly Markdown files.

### 🛡️ Enterprise-Grade Reliability
* **Soft Cancellation** - 7 cancellation checkpoints with graceful resource cleanup.
* **Smart Error Handling** - Exponential backoff retries for transient vs. permanent errors.
* **Race Condition Prevention** - Row-level database locking for stable task management.

---

## 🛠 Tech Stack

**Backend & AI Services**
* **Python 3.11 & FastAPI** - High-performance async backend framework.
* **Celery** - Distributed task queue for asynchronous processing.
* **Groq API** - Whisper Large-v3 (Transcription) & LLaMA 3.3 70B (Generation).
* **PostgreSQL 14 & SQLAlchemy** - Relational database and ORM.
* **Redis 7** - Fast in-memory message broker.
* **Processing Tools** - yt-dlp, FFmpeg, ReportLab, Arabic-reshaper.

**Frontend**
* **Next.js 14** - React framework using the modern App Router.
* **TypeScript** - Strict type-checking for scalable frontend architecture.
* **Tailwind CSS** - Utility-first styling for rapid UI development.
* **Axios** - Promise-based HTTP client.

---

## 📐 Architecture & Performance

### System Design

```text
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
```
## ⏱️ Performance Metrics
* **Transcription** - ~5 seconds per 10-minute audio chunk.
* **Note Generation** - ~2-3 seconds.
* **Total Processing** - ~1-2 minutes for a 10-minute video.
* **Cost** - $0 (Optimized for Groq free tier).

---

## 🚀 Getting Started

### 📋 Prerequisites
* **Python** - Version 3.11+
* **Node.js** - Version 18+
* **PostgreSQL** - Version 14+
* **Redis** - Version 7+
* **Media Tools** - FFmpeg

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/Moatazjad/video-note-system.git](https://github.com/Moatazjad/video-note-system.git)
cd video-note-system
```
### Backend Setup

```bash
cd backend
python -m venv .venv
```
### Activate virtual environment
### Windows: .venv\Scripts\activate 
### Linux/Mac: source .venv/bin/activate
```
pip install -r requirements.txt
cp .env.example .env
```

### Frontend Setup
```Bash

cd frontend
npm install
cp .env.example .env.local
```

### Start Services (3 Terminals Required)
#### Terminal 1: Backend API

```Bash

cd backend
uvicorn app.main:app --reload
```
#### Terminal 2: Celery Worker

```Bash

cd backend
celery -A app.core.celery_app worker --pool=solo -l info
```
#### Terminal 3: Frontend

```Bash

cd frontend
npm run dev
```
## 📸 Screenshots

### 🖥️ Application Views

* **Dashboard Overview**
  ![Dashboard Overview](https://github.com/user-attachments/assets/8e020ded-9a70-4ce1-8586-8705160d0cbe)

* **Real-Time Progress Tracking**
  ![Real-Time Progress Tracking](https://github.com/user-attachments/assets/7dcf4459-036a-40f3-9ab9-33b01ae0a292)

* **Generated Notes & PDF Export**

  ![Generated Notes 1](https://github.com/user-attachments/assets/484fa836-5fe2-4c8a-a8f5-67bc71297442) 
  ![Generated Notes 2](https://github.com/user-attachments/assets/6921f1d2-89d3-4949-8061-265dd703e855) 
  ![Generated Notes 3](https://github.com/user-attachments/assets/cc527f17-d008-4ce7-b4a8-22e5220e1436)

---

## 🔒 Security & Privacy

### 🛡️ System Protections
* **Environment Isolation** - Secure storage of sensitive API keys via environment variables.
* **Input Validation** - Client-side URL validation and server-side path traversal protection.
* **Secure Downloads** - Safe external linking (`noopener`, `noreferrer`).

---

## 📄 License

### 📜 Usage Rights
* **MIT License** - Distributed under the MIT License for educational purposes.

---

## 👤 Author & Acknowledgments

### 🎓 Moataz Ahmed
* **Institution** - Vistula University, Warsaw (Computer Engineering).
* **Project** - Bachelor's Thesis 2026.
* **GitHub** - [@Moatazjad](https://github.com/Moatazjad).
