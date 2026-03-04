from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import Boolean


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (
        CheckConstraint(
            'progress >= 0 AND progress <= 100',
            name='check_progress_range'
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)

    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    language = Column(String(5), default="en")
    template_type = Column(String(32), default="educational")

    status = Column(String(32), default="pending", index=True)
    progress = Column(Integer, default=0)
    current_step = Column(String(64), nullable=True)

    is_cancelled = Column(Boolean, default=False, nullable=False)

    video_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    markdown_path = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    processed_content = relationship(
        "ProcessedContent",
        back_populates="video",
        uselist=False,
        cascade="all, delete-orphan"
    )


class ProcessedContent(Base):
    __tablename__ = "processed_contents"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(
        Integer,
        ForeignKey("videos.id"),
        unique=True,
        nullable=False,
        index=True
    )

    transcript = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    detected_language = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    video = relationship("Video", back_populates="processed_content")
