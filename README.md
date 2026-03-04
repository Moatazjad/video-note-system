\# Video Note System



\*\*Bachelor's Thesis Project\*\*  

Computer Engineering, Vistula University, Warsaw  

\*\*Author:\*\* Moataz Jad Ahmed  

\*\*Year:\*\* 2026



---



\## Project Overview



An automated system for processing YouTube videos and generating structured educational notes. Supports English and Arabic content with real-time progress tracking and multi-format export.



\### Problem Statement

Taking notes while driving or during activities that prevent manual note-taking is challenging. This system automates the process by:

\- Downloading YouTube videos

\- Extracting and transcribing audio

\- Generating structured notes using AI

\- Exporting to Markdown and PDF formats



---



\## Key Features



\- YouTube Integration - Direct URL processing with time segmentation

\- Multi-language Support - English and Arabic with RTL rendering

\- AI-Powered Transcription - Groq Whisper Large-v3

\- Smart Note Generation - Template-based (Educational, Business, Research)

\- Real-time Progress - Live status updates and cancellation

\- Dual Export - Markdown + PDF with Arabic font support

\- Production-Ready - Error handling, retries, resource cleanup



---



\## Architecture



\### System Design

```

┌─────────────┐      ┌──────────────┐      ┌─────────────┐

│   Next.js   │ HTTP │   FastAPI    │      │   Celery    │

│  Frontend   │─────▶│   Backend    │─────▶│   Worker    │

│ (TypeScript)│      │   (Python)   │      │  (Async)    │

└─────────────┘      └──────────────┘      └─────────────┘

&nbsp;                           │                      │

&nbsp;                           ▼                      ▼

&nbsp;                    ┌──────────────┐      ┌─────────────┐

&nbsp;                    │ PostgreSQL   │      │   Redis     │

&nbsp;                    │  Database    │      │   Queue     │

&nbsp;                    └──────────────┘      └─────────────┘

&nbsp;                                                 │

&nbsp;                                                 ▼

&nbsp;                                         ┌─────────────┐

&nbsp;                                         │ Groq API    │

&nbsp;                                         │ (AI Models) │

&nbsp;                                         └─────────────┘

```



\### Tech Stack



\*\*Frontend:\*\*

\- Next.js 14 (App Router)

\- TypeScript (strict mode)

\- React Hooks

\- Tailwind CSS

\- Axios



\*\*Backend:\*\*

\- FastAPI (async)

\- Celery (task queue)

\- PostgreSQL (persistence)

\- Redis (message broker)

\- SQLAlchemy (ORM)

\- Alembic (migrations)



\*\*AI Services:\*\*

\- Groq Whisper Large-v3 (transcription)

\- Groq LLaMA 3.3 70B (note generation)



\*\*Processing:\*\*

\- yt-dlp (video download)

\- FFmpeg (audio extraction)

\- ReportLab (PDF generation)

\- Arabic-reshaper \& python-bidi (RTL support)



---



\## Project Structure

```

Video-Note-System/

├── backend/

│   ├── app/

│   │   ├── api/              # FastAPI routes

│   │   ├── core/             # Config, database, Celery

│   │   ├── models/           # SQLAlchemy models

│   │   ├── services/         # Business logic layer

│   │   └── tasks/            # Celery tasks

│   ├── alembic/              # Database migrations

│   ├── requirements.txt

│   └── .env.example

├── frontend/

│   ├── src/

│   │   ├── app/              # Next.js pages

│   │   ├── components/       # React components

│   │   ├── hooks/            # Custom hooks

│   │   ├── lib/              # API client, utilities

│   │   └── types/            # TypeScript definitions

│   ├── package.json

│   └── .env.example

└── README.md

```



---



\## Setup Instructions



\### Prerequisites

\- Python 3.11+

\- Node.js 18+

\- PostgreSQL 14+

\- Redis 7+

\- FFmpeg



\### 1. Clone Repository

```bash

git clone https://github.com/Moatazjad/video-note-system.git

cd video-note-system

```



\### 2. Backend Setup

```bash

cd backend



\# Create virtual environment

python -m venv .venv

.venv\\Scripts\\activate  # Windows

source .venv/bin/activate  # Linux/Mac



\# Install dependencies

pip install -r requirements.txt



\# Configure environment

cp .env.example .env

\# Edit .env and add:

\# - GROQ\_API\_KEY (get from https://console.groq.com)

\# - DATABASE\_URL

\# - REDIS\_URL



\# Run database migrations

alembic upgrade head

```



\### 3. Frontend Setup

```bash

cd frontend



\# Install dependencies

npm install



\# Configure environment

cp .env.example .env.local

\# Edit .env.local and set NEXT\_PUBLIC\_API\_URL

```



\### 4. Start Services



\*\*Terminal 1 - Backend:\*\*

```bash

cd backend

uvicorn app.main:app --reload

```



\*\*Terminal 2 - Celery Worker:\*\*

```bash

cd backend

celery -A app.core.celery\_app worker --pool=solo -l info

```



\*\*Terminal 3 - Frontend:\*\*

```bash

cd frontend

npm run dev

```



\*\*Access:\*\* http://localhost:3000



---



\## Academic Contributions



\### Key Implementation Patterns



1\. \*\*Soft Cancellation Architecture\*\*

&nbsp;  - Database-driven state management

&nbsp;  - 7 cancellation checkpoints

&nbsp;  - Graceful resource cleanup



2\. \*\*Production Error Handling\*\*

&nbsp;  - Smart retry with exponential backoff

&nbsp;  - Transient vs permanent error distinction

&nbsp;  - Row-level locking for race conditions



3\. \*\*Frontend Architecture\*\*

&nbsp;  - Separation of concerns (Hook + Components)

&nbsp;  - Stable service interfaces

&nbsp;  - Type-safe state machines



4\. \*\*Multi-language Support\*\*

&nbsp;  - RTL rendering for Arabic

&nbsp;  - Font family registration for PDF

&nbsp;  - Bidirectional text processing



---



\## Performance Metrics



\- \*\*Transcription:\*\* ~5 seconds per 10-minute audio chunk

\- \*\*Note Generation:\*\* ~2-3 seconds

\- \*\*Total Processing:\*\* ~1-2 minutes for 10-minute video

\- \*\*Cost:\*\* $0 (using Groq free tier)



---



\## Security \& Privacy



\- Environment variables for sensitive data

\- Path validation against directory traversal

\- Client-side URL validation

\- Secure download links (noopener, noreferrer)



---



\## License



MIT License - For educational purposes



---



\## Author



\*\*Moataz Jad Ahmed\*\*  

Vistula University, Warsaw  

Computer Engineering  

Bachelor's Thesis 2026



---



\## Acknowledgments



\- Groq - For free AI API access

\- Vistula University - Academic support

\- Open Source Community - Technologies used

