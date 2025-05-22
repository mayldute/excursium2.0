from typing import NamedTuple
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.get_db import get_db
from app.dependencies.user import get_current_user
from app.models import User

class CommonContext(NamedTuple):
    db: AsyncSession
    current_user: User

def get_common_context(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommonContext:
    return CommonContext(db=db, current_user=current_user)