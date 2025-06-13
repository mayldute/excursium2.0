from typing import List

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import asc, desc

from app.models import Transport, User, Carrier, Route, TransportRoute, Schedule
from app.schemas import (
    TransportCreate,
    TransportUpdate,
    TransportResponse,
    ScheduleCreate,
    TransportFilter,
    TransportFilterResponse
)

from app.utils import (
    generate_presigned_url,
    upload_transport_photo_to_minio,
    delete_photo_from_minio
)

from app.core.constants import ALLOWED_IMAGE_TYPES

# Mapping of sort fields to model attributes
SORT_FIELD_MAP = {
    "rating": Transport.rating,
    "price": TransportRoute.min_price,
}


async def filter_transports_service(
    filters: TransportFilter, db: AsyncSession
) -> List[TransportFilterResponse]:
    """
    Filters transports based on various criteria,
        excluding transports that are busy during the requested time.

    Args:
        filters (TransportFilter): Pydantic model with filter criteria.
        db (AsyncSession): Asynchronous database session.

    Returns:
        List[TransportFilterResponse]: List of filtered transports.

    Raises:
        HTTPException: If no transports found matching the criteria (404).
    """
    sort_field = SORT_FIELD_MAP.get(filters.sort_by, Transport.rating)
    order_func = desc if filters.sort_order == "desc" else asc

    # Subquery to exclude transports with overlapping schedules
    subq = (
        select(Schedule.id_transport)
        .where(
            ~(
                (Schedule.end_time <= filters.start_time)
                | (Schedule.start_time >= filters.end_time)
            )
        )
        .subquery()
    )

    # Build main query
    query = (
        select(Transport, TransportRoute)
        .join(Transport.transport_routes)
        .join(TransportRoute.route)
        .where(
            # Filter by route IDs
            Route.id_from == filters.id_from,
            Route.id_to == filters.id_to,

            # Filter by seat count
            Transport.n_seat >= filters.n_seat,

            # Filter by price range
            TransportRoute.min_price >= filters.min_price,
            TransportRoute.max_price <= filters.max_price,

            # Exclude busy transports
            ~Transport.id.in_(select(subq.c.id_transport)),

            # Optional filters
            *(Transport.luggage == filters.luggage,)
            if filters.luggage is not None else (),
            *(Transport.wifi == filters.wifi,)
            if filters.wifi is not None else (),
            *(Transport.tv == filters.tv,)
            if filters.tv is not None else (),
            *(Transport.air_conditioning == filters.air_conditioning,)
            if filters.air_conditioning is not None else (),
            *(Transport.toilet == filters.toilet,)
            if filters.toilet is not None else (),
        )
        .order_by(order_func(sort_field))
        .options(
            joinedload(Transport.carrier),
            joinedload(Transport.transport_routes)
        )
    )

    result = await db.execute(query)
    rows = result.unique().all()

    if not rows:
        raise HTTPException(
            status_code=404, detail="No transports found matching the filters"
        )

    # Manually unpack and build response
    responses = []
    for transport, transport_route in rows:
        responses.append(
            TransportFilterResponse(
                id=transport.id,
                carrier_id=transport.carrier_id,
                brand=transport.brand,
                model=transport.model,
                n_seat=transport.n_seat,
                luggage=transport.luggage,
                wifi=transport.wifi,
                tv=transport.tv,
                air_conditioning=transport.air_conditioning,
                toilet=transport.toilet,
                photo=transport.photo,
                rating=transport.rating,
                min_price=transport_route.min_price,
                max_price=transport_route.max_price,
            )
        )

    return responses


async def get_transport_by_id_service(
    transport_id: int, db: AsyncSession
) -> TransportFilterResponse:
    """Retrieves a transport by its ID.

    Args:
        transport_id (int): ID of the transport to retrieve.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Transport: Transport instance if found.

    Raises:
        HTTPException: If transport does not exist (404).
    """
    result = await db.execute(
        select(Transport, TransportRoute)
        .join(Transport.transport_routes)
        .where(Transport.id == transport_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Transport not found")

    transport, transport_route = row

    return TransportFilterResponse(
        id=transport.id,
        carrier_id=transport.carrier_id,
        brand=transport.brand,
        model=transport.model,
        n_seat=transport.n_seat,
        luggage=transport.luggage,
        wifi=transport.wifi,
        tv=transport.tv,
        air_conditioning=transport.air_conditioning,
        toilet=transport.toilet,
        photo=transport.photo,
        rating=transport.rating,
        min_price=transport_route.min_price,
        max_price=transport_route.max_price,
    )


async def get_transport_and_validate_user(
    transport_id: int, current_user: User, db: AsyncSession
) -> Transport:
    """Gets transport by ID and checks that
        the current user owns the associated carrier.

    Args:
        transport_id (int): ID of the transport to retrieve.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Transport: Transport instance if found and user is authorized.

    Raises:
        HTTPException: If transport does not exist (404) or
            user does not own the carrier (403).
    """
    # Get transport and associated carrier in one query
    result = await db.execute(
        select(Transport)
        .options(selectinload(Transport.carrier))
        .where(Transport.id == transport_id)
    )
    transport = result.scalar_one_or_none()

    # Check existence of transport and ownership of carrier
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    if transport.carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return transport


async def save_entity(entity: Transport, db: AsyncSession) -> None:
    """Saves a transport instance to the database and refreshes its state.

    Args:
        entity (Transport): Transport instance to save.
        db (AsyncSession): Asynchronous database session.
    """
    # Add entity to session, commit changes and refresh data
    db.add(entity)
    await db.commit()
    await db.refresh(entity)


async def create_transport_service(
    payload: TransportCreate, current_user: User, db: AsyncSession
) -> TransportResponse:
    """Creates a new transport for the current user's carrier.

    Args:
        payload (TransportCreate):
            Pydantic model with data for creating transport.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        TransportResponse: Pydantic model with created transport data.

    Raises:
        HTTPException: If user does not own a carrier (403).
    """
    # Get carrier ID for current user
    result = await db.execute(
        select(Carrier.id).where(Carrier.user_id == current_user.id)
    )
    carrier_id = result.scalar_one_or_none()

    # Ensure user has a registered carrier
    if not carrier_id:
        raise HTTPException(
            status_code=403, detail="Access denied: user does not own a carrier"
        )

    # Create new transport instance from payload data
    transport = Transport(
        name=payload.name,
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        n_seat=payload.n_seat,
        photo="transport_photos/default_bus.jpg",  # Set default photo
        luggage=payload.luggage,
        wifi=payload.wifi,
        tv=payload.tv,
        air_conditioning=payload.air_conditioning,
        toilet=payload.toilet,
        carrier_id=carrier_id
    )

    # Save transport to database
    await save_entity(transport, db)

    # Return transport as Pydantic model
    return TransportResponse.model_validate(transport)


async def get_transports_by_carrier_id_service(
    carrier_id: int, current_user: User, db: AsyncSession
) -> List[TransportResponse]:
    """Gets a list of all transports for the specified carrier.

    Args:
        carrier_id (int): Carrier ID to get transports for.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        List[TransportResponse]: List of Pydantic models with transport data.

    Raises:
        HTTPException: If carrier not found (404),
            user does not own carrier (403), or no transports found (404).
    """
    # Get carrier with user data for ownership check
    result = await db.execute(
        select(Carrier)
        .options(selectinload(Carrier.user))
        .where(Carrier.id == carrier_id)
    )
    carrier = result.scalar_one_or_none()

    # Check existence of carrier and ownership
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    if carrier.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get all transports for carrier
    result = await db.execute(
        select(Transport).where(Transport.carrier_id == carrier_id)
    )
    transports = result.scalars().all()

    # Check if transports exist
    if not transports:
        raise HTTPException(
            status_code=404, detail="No transports found for this carrier"
        )

    # Add presigned URLs for transport photos
    for transport in transports:
        transport.photo = generate_presigned_url(transport.photo)

    # Convert to Pydantic models
    return [
        TransportResponse.model_validate(transport) for transport in transports
    ]


async def update_transport_service(
    transport_id: int,
    payload: TransportUpdate,
    current_user: User,
    db: AsyncSession
) -> TransportResponse:
    """Updates an existing transport by ID if user owns the carrier.

    Args:
        transport_id (int): ID of the transport to update.
        payload (TransportUpdate): Pydantic model with update data.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        TransportResponse: Pydantic model with updated transport data.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Update fields from payload
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(transport, key, value)

    # Save updated transport
    await save_entity(transport, db)

    # Return updated transport as Pydantic model
    return TransportResponse.model_validate(transport)


async def delete_transport_service(
    transport_id: int, current_user: User, db: AsyncSession
) -> dict:
    """Deletes a transport by ID if user owns the carrier.

    Args:
        transport_id (int): ID of the transport to delete.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message about successful deletion and deleted transport ID.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Delete transport from database
    await db.delete(transport)
    await db.commit()

    # Return success message
    return {
        'message': 'Transport successfully deleted',
        'transport_id': transport_id
    }


async def upload_transport_photo_service(
    transport_id: int,
    file: UploadFile,
    current_user: User,
    db: AsyncSession
) -> dict:
    """Uploads a transport photo to MinIO and updates the transport profile.

    Args:
        transport_id (int): ID of the transport to update photo for.
        file (UploadFile): Photo file to upload.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Dictionary with uploaded photo URL.

    Raises:
        HTTPException:
        If file not provided (400), file type not supported (400),
            transport not found (404), user does not own carrier (403),
                or upload failed (500).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Check uploaded file
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: JPEG, PNG, WEBP."
        )

    # Upload new photo to MinIO
    photo_url = await upload_transport_photo_to_minio(file, transport.id)
    if not photo_url:
        raise HTTPException(status_code=500, detail="Failed to upload photo")

    # Delete previous photo if not default
    if (
        transport.photo
        and transport.photo != "transport_photos/default_bus.jpg"
    ):
        delete_photo_from_minio(transport.photo)

    # Update transport photo URL
    transport.photo = photo_url
    await save_entity(transport, db)

    # Return new photo URL
    return {"photo_url": photo_url}


async def add_route_to_transport_service(
    transport_id: int,
    id_from: int, id_to: int,
    min_price: float, max_price: float,
    current_user: User, db: AsyncSession
) -> TransportRoute:
    """Adds a route to the transport.

    Args:
        transport_id (int): ID of the transport to add route to.
        id_from (int): ID of the starting point.
        id_to (int): ID of the destination point.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Transport: Updated transport instance with new route.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403) or route already exists (400).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Find the route by its starting and destination point IDs
    route_result = await db.execute(
        select(Route).where(Route.id_from == id_from, Route.id_to == id_to)
    )
    route = route_result.scalar_one_or_none()

    # If route does not exist, create a new one
    if not route:
        route = Route(id_from=id_from, id_to=id_to)
        db.add(route)
        await db.commit()
        await db.refresh(route)

    # Check if the route is already assigned to the transport
    existing_result = await db.execute(
        select(TransportRoute).where(
            TransportRoute.transport_id == transport.id,
            TransportRoute.route_id == route.id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This route is already assigned to the transport"
        )

    # Create a new TransportRoute instance
    transport_route = TransportRoute(
        transport_id=transport.id,
        route_id=route.id,
        min_price=min_price,
        max_price=max_price
    )

    db.add(transport_route)
    await db.commit()
    return transport_route


async def get_transport_routes_service(
    transport_id: int, current_user: User, db: AsyncSession
) -> List[TransportRoute]:
    """Gets all routes associated with a transport.

    Args:
        transport_id (int): ID of the transport to get routes for.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        List[TransportRoute]: List of TransportRoute instances.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403) or no routes found (404).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Get all routes for the transport
    result = await db.execute(
        select(TransportRoute)
        .where(TransportRoute.transport_id == transport.id)
    )
    routes = result.scalars().all()

    # Check if routes exist
    if not routes:
        raise HTTPException(
            status_code=404, detail="No routes found for this transport"
        )

    return routes


async def delete_transport_route_service(
    transport_id: int, route_id: int, current_user: User, db: AsyncSession
) -> dict:
    """Deletes a route from a transport.

    Args:
        transport_id (int): ID of the transport to delete route from.
        route_id (int): ID of the route to delete.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message about successful deletion and deleted route ID.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403) or route not found (404).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Find the TransportRoute instance to delete
    result = await db.execute(select(TransportRoute).where(
        TransportRoute.transport_id == transport.id,
        TransportRoute.route_id == route_id
    ))
    transport_route = result.scalar_one_or_none()

    # Check if the route exists
    if not transport_route:
        raise HTTPException(
            status_code=404, detail="Route not found for this transport"
        )

    # Delete the route
    await db.delete(transport_route)
    await db.commit()

    return {'message': 'Route successfully deleted', 'route_id': route_id}


async def add_transport_schedule_service(
    payload: ScheduleCreate, current_user: User, db: AsyncSession
) -> Schedule:
    """Adds a new schedule for a transport.

    Args:
        payload (ScheduleCreate): Pydantic model with schedule data.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Schedule: Created schedule instance.

    Raises:
        HTTPException:
        If transport not found (404), user does not own the carrier (403),
            or schedule with these times already exists (400).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        payload.transport_id, current_user, db
    )

    # Create a new schedule instance
    schedule = Schedule(
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason,
        id_transport=transport.id
    )

    # Check if a schedule with the same times already exists for this transport
    result = await db.execute(select(Schedule).where(
        Schedule.id_transport == payload.transport_id,
        Schedule.start_time == payload.start_time,
        Schedule.end_time == payload.end_time
    ))

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Schedule with these times already exists for this transport"
        )

    db.add(schedule)
    await db.commit()

    return schedule


async def get_transport_schedules_service(
    transport_id: int, current_user: User, db: AsyncSession
) -> List[Schedule]:
    """Gets all schedules for a transport.

    Args:
        transport_id (int): ID of the transport to get schedules for.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        List[Schedule]: List of Schedule instances.

    Raises:
        HTTPException: If transport not found (404) or
            user does not own the carrier (403) or no schedules found (404).
    """
    # Get and check ownership of transport
    transport = await get_transport_and_validate_user(
        transport_id, current_user, db
    )

    # Get all schedules for the transport
    result = await db.execute(
        select(Schedule).where(Schedule.id_transport == transport.id)
    )
    schedules = result.scalars().all()

    # Check if schedules exist
    if not schedules:
        raise HTTPException(
            status_code=404, detail="No schedules found for this transport"
        )

    return schedules


async def delete_transport_schedules_service(
    schedule_id: int, current_user: User, db: AsyncSession
) -> dict:
    """Deletes a schedule by ID.

    Args:
        schedule_id (int): ID of the schedule to delete.
        current_user (User): The currently authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message about successful deletion and deleted schedule ID.

    Raises:
        HTTPException: If schedule not found (404) or
            user does not own the carrier (403).
    """
    # Get the schedule by ID
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()

    # Check if the schedule exists
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Check ownership of the transport associated with the schedule
    await get_transport_and_validate_user(
        schedule.id_transport, current_user, db
    )

    # Delete the schedule
    await db.delete(schedule)
    await db.commit()

    return {
        'message': 'Schedule successfully deleted',
        'schedule_id': schedule_id
    }
