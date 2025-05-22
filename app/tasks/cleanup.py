import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from app.models import User, ChangeEmail
from app.db.session import async_session_maker

# Logger for cleanup task operations
logger = logging.getLogger(__name__)

async def delete_unactivated_users() -> None:
    """Delete users who have not activated their accounts within 24 hours.

    Returns:
        None

    Raises:
        SQLAlchemyError: If a database operation fails during query or deletion.
    """
    # Open database session
    async with async_session_maker() as session:
        # Calculate cutoff time (24 hours ago)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        # Query unactivated users older than cutoff
        result = await session.execute(
            select(User).where(
                User.is_active == False,
                User.created_at < cutoff
            )
        )
        users_to_delete = result.scalars().all()

        # Delete users if any are found
        if users_to_delete:
            for user in users_to_delete:
                await session.delete(user)
            logger.info(f"Deleted {len(users_to_delete)} unactivated users")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit deletion of unactivated users: {e}")
            raise


async def delete_deleted_users() -> None:
    """Delete users marked as deleted for more than 30 days.

    Returns:
        None

    Raises:
        SQLAlchemyError: If a database operation fails during query or deletion.
    """
    # Open database session
    async with async_session_maker() as session:
        # Calculate cutoff time (30 days ago)
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        # Query deleted users older than cutoff
        result = await session.execute(
            select(User).where(
                User.is_active == False,
                User.deleted_at < cutoff
            )
        )
        users_to_delete = result.scalars().all()

        # Delete users if any are found
        if users_to_delete:
            for user in users_to_delete:
                await session.delete(user)
            logger.info(f"Deleted {len(users_to_delete)} permanently deleted users")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit deletion of deleted users: {e}")
            raise


async def delete_unchanged_emails() -> None:
    """Delete email change requests not confirmed within 1 hour.

    Returns:
        None

    Raises:
        SQLAlchemyError: If a database operation fails during query or deletion.
    """
    # Open database session
    async with async_session_maker() as session:
        # Calculate cutoff time (1 hour ago)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

        # Query expired email change requests
        result = await session.execute(
            select(ChangeEmail).where(
                ChangeEmail.expires_at < cutoff
            )
        )
        emails_to_delete = result.scalars().all()

        # Delete email requests if any are found
        if emails_to_delete:
            for email in emails_to_delete:
                await session.delete(email)
            logger.info(f"Deleted {len(emails_to_delete)} unchanged email requests")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit deletion of unchanged emails: {e}")
            raise