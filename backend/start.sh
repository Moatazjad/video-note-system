#!/usr/bin/env bash
set -e

alembic upgrade head

# Render's free tier only supports one running process per service, so the
# Celery worker runs alongside the API in the same container rather than as
# a separate (paid-tier-only) background worker service.
celery -A app.core.celery_app worker --pool=solo -l info &

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
