import uuid
from enum import Enum
from typing import List

from sqlalchemy import String, ForeignKey, Boolean, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base  


class UserTypeEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class UserRegistrationEnum(str, Enum):
    APPROVED = "A"
    DECLINED = "D"
    WAITING = "W"

class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  
        index=True,
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, index=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    user_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_type.id"))
    user_type: Mapped["UserType"] = relationship("UserType", back_populates="users")


class UserType(Base):
    __tablename__ = "user_type"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_type: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    users: Mapped[List["Users"]] = relationship("Users", back_populates="user_type")

class UserRegistration(Base):
    __tablename__ = "user_registration"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier for the registration record."
    )
    reg_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=UserRegistrationEnum.WAITING.value,
        doc="Registration status: 'W' (Waiting), 'A' (Approved), 'R' (Rejected), etc."
    )
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

    def __repr__(self) -> str:
        return f"<UserRegistration(id={self.id}, reg_status='{self.reg_status}', created_at={self.created_at})>"