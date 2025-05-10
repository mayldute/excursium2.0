from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Carrier
from app.schemas.carrier import CarrierCreate
from app.utils.security import hash_password
from app.utils.tokens import get_tokens_for_user

async def register_carrier_service(payload: CarrierCreate, db: AsyncSession, request: Request):
    user_data = payload.user

    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=409, detail="A user with this email already exists")

    new_user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        hashed_password=hash_password(user_data.password1),
    )

    db.add(new_user)
    await db.flush() 

    carrier_kwargs = {
        "user_id": new_user.id,
        "carrier_type": payload.carrier_type,
        "custom_type": payload.custom_type,
        "company_name": payload.company_name,
        "inn": payload.inn,
        "kpp": payload.kpp,
    }

    carrier = Carrier(**carrier_kwargs)
    db.add(carrier)
    await db.commit()

    tokens = get_tokens_for_user(new_user)

    return {
        "user": {
            "id": new_user.id,
            "email": new_user.email
        },
        "tokens": tokens
    }