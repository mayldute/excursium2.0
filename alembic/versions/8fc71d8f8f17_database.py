"""database

Revision ID: 8fc71d8f8f17
Revises: 
Create Date: 2025-04-05 09:43:36.531713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fc71d8f8f17'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('region', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('middle_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('is_staff', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_subscribed', sa.Boolean(), nullable=True),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('carriers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('carrier_type', sa.Enum('GP', 'LP', 'EC', 'PJC', 'NJC', 'LLC', 'IE', 'UE', 'FD', 'EST', 'OTH', name='legaltypeenum'), nullable=True),
    sa.Column('company_name', sa.String(length=255), nullable=False),
    sa.Column('inn', sa.String(length=12), nullable=True),
    sa.Column('kpp', sa.String(length=9), nullable=True),
    sa.Column('ogrn', sa.String(length=13), nullable=True),
    sa.Column('current_account', sa.String(length=20), nullable=True),
    sa.Column('corresp_account', sa.String(length=20), nullable=True),
    sa.Column('bik', sa.String(length=9), nullable=True),
    sa.Column('oktmo', sa.String(length=11), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_carriers_id'), 'carriers', ['id'], unique=False)
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_type', sa.Enum('IND', 'LEG', name='clienttypeenum'), nullable=False),
    sa.Column('legal_type', sa.Enum('GP', 'LP', 'EC', 'PJC', 'NJC', 'LLC', 'IE', 'UE', 'FD', 'EST', 'OTH', name='legaltypeenum'), nullable=True),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('inn', sa.String(length=12), nullable=True),
    sa.Column('kpp', sa.String(length=9), nullable=True),
    sa.Column('ogrn', sa.String(length=13), nullable=True),
    sa.Column('current_account', sa.String(length=20), nullable=True),
    sa.Column('corresp_account', sa.String(length=20), nullable=True),
    sa.Column('bik', sa.String(length=9), nullable=True),
    sa.Column('oktmo', sa.String(length=11), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
    op.create_table('routes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_from', sa.Integer(), nullable=False),
    sa.Column('id_to', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_from'], ['cities.id'], ),
    sa.ForeignKeyConstraint(['id_to'], ['cities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)
    op.create_table('docs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doc_type', sa.Enum('LC', 'ME', 'IS', 'CT', name='doctypeenum'), nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('carrier_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_docs_id'), 'docs', ['id'], unique=False)
    op.create_table('transports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('brand', sa.String(length=50), nullable=True),
    sa.Column('model', sa.String(length=50), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('n_desk', sa.Integer(), nullable=True),
    sa.Column('n_seat', sa.Integer(), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('luggage', sa.Boolean(), nullable=True),
    sa.Column('wifi', sa.Boolean(), nullable=True),
    sa.Column('tv', sa.Boolean(), nullable=True),
    sa.Column('air_conditioning', sa.Boolean(), nullable=True),
    sa.Column('toilet', sa.Boolean(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('carrier_id', sa.Integer(), nullable=True),
    sa.Column('route_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
    sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_transports_id'), 'transports', ['id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'CONFIRMD', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'ARCHIVED', name='orderstatusenum'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('passenger_type', sa.Enum('CHILDREN', 'ADULT', 'MIXED', 'CORPORATE', name='passendertypeenum'), nullable=False),
    sa.Column('notification_sent', sa.Boolean(), nullable=True),
    sa.Column('payment_status', sa.String(length=50), nullable=False),
    sa.Column('payment_method', sa.String(length=50), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('id_client', sa.Integer(), nullable=True),
    sa.Column('id_carrier', sa.Integer(), nullable=True),
    sa.Column('id_transport', sa.Integer(), nullable=True),
    sa.Column('id_route', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_carrier'], ['carriers.id'], ),
    sa.ForeignKeyConstraint(['id_client'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['id_route'], ['routes.id'], ),
    sa.ForeignKeyConstraint(['id_transport'], ['transports.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_table('schedules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trip_start', sa.DateTime(), nullable=True),
    sa.Column('trip_end', sa.DateTime(), nullable=True),
    sa.Column('id_transport', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_transport'], ['transports.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schedules_id'), 'schedules', ['id'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=255), nullable=False),
    sa.Column('answer', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('carrier_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_table('extra_services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extra_services_id'), 'extra_services', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_extra_services_id'), table_name='extra_services')
    op.drop_table('extra_services')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_schedules_id'), table_name='schedules')
    op.drop_table('schedules')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_transports_id'), table_name='transports')
    op.drop_table('transports')
    op.drop_index(op.f('ix_docs_id'), table_name='docs')
    op.drop_table('docs')
    op.drop_index(op.f('ix_routes_id'), table_name='routes')
    op.drop_table('routes')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_table('clients')
    op.drop_index(op.f('ix_carriers_id'), table_name='carriers')
    op.drop_table('carriers')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_cities_id'), table_name='cities')
    op.drop_table('cities')
    # ### end Alembic commands ###
