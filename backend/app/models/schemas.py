from pydantic import BaseModel, Field, HttpUrl, model_validator, computed_field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime


class VideoProcessRequest(BaseModel):
    url: HttpUrl = Field(..., description="YouTube or video URL")
    start_time: Optional[float] = Field(None, ge=0)
    end_time: Optional[float] = Field(None, ge=0)
    language: Literal["en", "ar"] = Field(default="en")
    template_type: Literal["educational", "business", "research"] = Field(default="educational")

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("end_time must be greater than start_time")
        return self


class VideoStatusResponse(BaseModel):
    id: int
    url: str
    status: str
    progress: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    language: str
    template_type: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class VideoResultResponse(BaseModel):
    id: int
    url: str
    status: str
    transcript: Optional[str] = None
    notes: Optional[str] = None
    detected_language: Optional[str] = None
    transcript_source: Optional[str] = None
    topics: Optional[List[Dict[str, Any]]] = None
    duration: Optional[float] = None
    created_at: datetime

    @computed_field
    @property
    def markdown_url(self) -> Optional[str]:
        if self.status != "completed":
            return None
        return f"/api/v1/export/{self.id}/markdown"

    @computed_field
    @property
    def pdf_url(self) -> Optional[str]:
        if self.status != "completed":
            return None
        return f"/api/v1/export/{self.id}/pdf"

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]


class TranslateRequest(BaseModel):
    target_language: Literal["en", "ar"]


class TranslateResponse(BaseModel):
    language: str
    content: str
