from pydantic import BaseModel
from typing import Optional

class IdBase(BaseModel):
    id: str

class DateBase(BaseModel):
    created_at: str
    updated_at: Optional[str]

class ReadBase(IdBase, DateBase):
    pass

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