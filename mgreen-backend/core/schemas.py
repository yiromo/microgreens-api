from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class IdBase(BaseModel):
    id: str = Field(..., description="UUID as a string")

    @field_validator("id", mode="before")
    def coerce_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

class DateBase(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class ReadBase(IdBase, DateBase):
    class Config:
        from_attributes = True

class StatusBase(BaseModel):
    is_active: bool = True
    is_deleted: bool = False

class MetadataBase(BaseModel):
    version: int = 1
    source: Optional[str] = None
    tags: Optional[list[str]] = None

class AuditBase(BaseModel):
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    notes: Optional[str] = None

class ExtendedBase(ReadBase, StatusBase, MetadataBase, AuditBase):
    pass