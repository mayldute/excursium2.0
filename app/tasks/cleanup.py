from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select
from app.models import User
from app.db.session import async_session_maker

async def delete_unactivated_users():
    async with async_session_maker() as session:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        result = await session.execute(
            select(User).where(
                User.is_active == False,
                User.created_at < cutoff
            )
        )
        users_to_delete = result.scalars().all()

        for user in users_to_delete:
            await session.delete(user)

        await session.commit()