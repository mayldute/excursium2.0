import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import delete, false
from sqlalchemy.exc import SQLAlchemyError

from app.models import User, ChangeEmail, OAuthState
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

        # Execute mass deletion of unactivated users
        result = await session.execute(
            delete(User).where(
                User.is_active.is_(false()),
                User.created_at < cutoff
            ).returning(User.id)  # Return the IDs of deleted users for logging
        )
        users_to_delete = result.scalars().all()
        count_to_delere = len(users_to_delete)

        # Log the number of deleted users
        if count_to_delere > 0:
            logger.info(f"Deleted {count_to_delere} unactivated users")

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

        # Execute mass deletion of deleted users
        result = await session.execute(
            delete(User).where(
                User.is_active.is_(false()),
                User.deleted_at < cutoff
            ).returning(User.id)  # Return the IDs of deleted users for logging
        )
        users_to_delete = result.scalars().all()
        count_to_delere = len(users_to_delete)

        # Log the number of deleted users
        if count_to_delere > 0:
            logger.info(f"Deleted {count_to_delere} permanently deleted users")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to commit deletion of permanently deleted users: {e}"
            )
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

        # Execute mass deletion of expired email change requests
        result = await session.execute(
            delete(ChangeEmail).where(
                ChangeEmail.expires_at < cutoff
            ).returning(
                ChangeEmail.id
            )  # Return the IDs of deleted email requests for logging
        )
        emails_to_delete = result.scalars().all()
        count_to_delete = len(emails_to_delete)

        # Log the number of deleted email requests
        if count_to_delete > 0:
            logger.info(f"Deleted {count_to_delete} unchanged email requests")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(
                f"Failed to commit deletion of unchanged email requests: {e}"
            )
            raise


async def delete_oauth_state() -> None:
    """Delete OAuth states that have expired.

    Returns:
        None

    Raises:
        SQLAlchemyError: If a database operation fails during query or deletion.
    """
    # Open database session
    async with async_session_maker() as session:
        # Calculate cutoff time (1 hour ago)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)

        # Query expired email change requests
        result = await session.execute(
            delete(OAuthState).where(
                OAuthState.expires_at < cutoff
            ).returning(
                OAuthState.id
            )  # Return the IDs of deleted OAuth states for logging
        )
        states_to_delete = result.scalars().all()
        count_to_delete = len(states_to_delete)

        # Log the number of deleted states
        if count_to_delete > 0:
            logger.info(f"Deleted {count_to_delete} expired OAuth states")

        # Commit changes
        try:
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit deletion of unchanged emails: {e}")
            raise
