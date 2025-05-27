from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Transport, User, Carrier
from app.schemas import TransportCreate

async def get_owned_client_or_403(carrier_id: int, current_user: User, db: AsyncSession) -> Carrier:
    """Fetch a client by ID and verify user ownership.

    Args:
        client_id (int): The ID of the client to fetch.
        current_user (User): The authenticated user making the request.
        db (AsyncSession): The database session for querying.

    Returns:
        Client: The client object if found and owned by the user.

    Raises:
        HTTPException: If the client is not found or the user does not have ownership (status code 403).
    """
    carrier = await db.get(Carrier, carrier_id)

    if not carrier or carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return carrier

async def create_transport_service(payload: TransportCreate, curernt_user: User, db: AsyncSession):
    carrier_id = await db.execute(select(Carrier.id).where(Carrier.user_id == curernt_user.id))
    carrier_id = carrier_id.scalar_one_or_none()

    carrier = await get_owned_client_or_403(carrier_id, curernt_user, db)
    
    transport = Transport(
        name=payload.name,
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        n_desk=payload.n_desk,
        n_seat=payload.n_seat,
        photo="transport_photos/default_bus.jpg",
        luggage=payload.luggage,
        wifi=payload.wifi,
        tv=payload.tv,
        air_conditioning=payload.air_conditioning,
        toilet=payload.toilet,
        carrier_id=carrier.id
    )

    db.add(transport)
    await db.commit()

    return {'message': 'Transport created successfully', 'transport_id': transport.id}

    