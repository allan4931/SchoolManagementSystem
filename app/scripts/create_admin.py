import asyncio
from app.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.core.security import hash_password


async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        admin = User(
            username="admin",
            full_name="System Administrator",
            email="admin@school.ac.zw",
            password_hash=hash_password("Admin@1234"),
            role=UserRole.ADMIN,
            is_active=True,
            is_synced=False,
        )
        session.add(admin)
        await session.commit()
        print("✅ Admin user created!")
        print("   Username: admin")
        print("   Password: Admin@1234")
        print("   Change the password after first login!")


if __name__ == "__main__":
    asyncio.run(main())
