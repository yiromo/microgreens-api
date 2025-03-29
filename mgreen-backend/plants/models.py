from sqlalchemy import String, ForeignKey, Boolean, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base  
import uuid
from enum import Enum
from typing import List


class Plants(Base):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        index=True,
    )
    name: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(),
        doc="Timestamp when the registration record was created."
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.now(),
        doc="Timestamp when the registration record was last updated."
    )

    plant_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plants_classifications.id"))
    plant_type: Mapped["PlantsClassifications"] = relationship("PlantsClassifications", back_populates="plants")


class PlantsClassifications(Base):
    __tablename__ = "plants_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        index=True,
    )
    
    name: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(),
        doc="Timestamp when the registration record was created."
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.now(),
        doc="Timestamp when the registration record was last updated."
    )

    plants: Mapped[List["Plants"]] = relationship("Plants", back_populates="plant_type")
