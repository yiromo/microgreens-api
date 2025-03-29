import asyncio
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from passlib.context import CryptContext

from core.config import settings
from database import Base
from users.models import Users, UserType, UserTypeEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_migration():
    """Initialize the database with user types and an admin user."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        existing_types_result = await session.execute(
            text("SELECT user_type FROM user_type")
        )
        existing_types = {row[0] for row in existing_types_result.fetchall()}

        roles_to_create: List[UserType] = []
        for role in UserTypeEnum:
            if role.value not in existing_types:
                roles_to_create.append(UserType(user_type=role.value))

        if roles_to_create:
            session.add_all(roles_to_create)
            await session.flush()  
            await session.commit()
            print(f"Created user types: {[role.user_type for role in roles_to_create]}")
        else:
            print("User types already exist, skipping creation.")

        superadmin_type_result = await session.execute(
            text("SELECT id FROM user_type WHERE user_type = :type"),
            {"type": UserTypeEnum.SUPERADMIN.value},
        )
        superadmin_type = superadmin_type_result.fetchone()

        if not superadmin_type:
            raise ValueError("Superadmin role not found after initialization.")
        superadmin_type_id = superadmin_type[0]

        admin_exists_result = await session.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": settings.SUPER_ADMIN_EMAIL},
        )
        admin_exists = admin_exists_result.fetchone()

        if not admin_exists:
            hashed_password = pwd_context.hash(settings.SUPER_ADMIN_PASSWORD)
            admin_user = Users(
                id=uuid.uuid4(),
                email=settings.SUPER_ADMIN_EMAIL,
                username="supadmin",
                password=hashed_password,
                is_active=True,
                is_superuser=True,
                user_type_id=superadmin_type_id,
            )
            session.add(admin_user)
            await session.commit()
            print("Admin user created with superadmin role.")
        else:
            print("Admin user already exists, skipping creation.")

    await engine.dispose()