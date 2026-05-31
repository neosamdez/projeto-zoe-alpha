"""sprint_28_fase2_rma_kpi_inventory_deliveries_discard

Revision ID: b3f7a1c2d4e5
Revises: cd1826eb6e07
Create Date: 2026-05-29 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3f7a1c2d4e5'
down_revision: Union[str, Sequence[str], None] = 'cd1826eb6e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('technicians', sa.Column('bp_code', sa.String(length=50), nullable=True))
    op.add_column('technicians', sa.Column('occupation', sa.String(length=100), nullable=True))

    op.add_column('service_orders', sa.Column('defect_code', sa.String(length=10), nullable=True))
    op.add_column('service_orders', sa.Column('grms_number', sa.String(length=50), nullable=True))
    op.add_column('service_orders', sa.Column('scheduled_date', sa.Date(), nullable=True))
    op.add_column('service_orders', sa.Column('scheduled_shift', sa.String(length=10), nullable=True))
    op.add_column('service_orders', sa.Column('route_car', sa.String(length=20), nullable=True))
    op.add_column('service_orders', sa.Column('route_technicians', sa.Text(), nullable=True))

    op.add_column('products', sa.Column('category', sa.String(length=20), nullable=False, server_default='VD'))
    op.add_column('products', sa.Column('samsung_part_code', sa.String(length=50), nullable=True))

    op.create_table('defect_codes',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=False),
        sa.Column('most_used_part', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_defect_tenant_code'),
    )
    op.create_index(op.f('ix_defect_codes_id'), 'defect_codes', ['id'], unique=False)
    op.create_index(op.f('ix_defect_codes_tenant_id'), 'defect_codes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_defect_codes_code'), 'defect_codes', ['code'], unique=False)

    op.create_table('rma_requests',
        sa.Column('protocol', sa.String(length=50), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=True),
        sa.Column('product_id', sa.UUID(), nullable=True),
        sa.Column('delivery_code', sa.String(length=50), nullable=True),
        sa.Column('samsung_nf', sa.String(length=50), nullable=True),
        sa.Column('return_code', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('deadline_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('deadline_date', sa.Date(), nullable=True),
        sa.Column('inspection_photos', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['service_orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'protocol', name='uq_rma_tenant_protocol'),
    )
    op.create_index(op.f('ix_rma_requests_id'), 'rma_requests', ['id'], unique=False)
    op.create_index(op.f('ix_rma_requests_tenant_id'), 'rma_requests', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_rma_requests_protocol'), 'rma_requests', ['protocol'], unique=True)
    op.create_index(op.f('ix_rma_requests_order_id'), 'rma_requests', ['order_id'], unique=False)
    op.create_index(op.f('ix_rma_requests_product_id'), 'rma_requests', ['product_id'], unique=False)

    op.create_table('rma_inspections',
        sa.Column('rma_request_id', sa.UUID(), nullable=False),
        sa.Column('defect_code', sa.String(length=10), nullable=False),
        sa.Column('defect_description', sa.String(length=255), nullable=False),
        sa.Column('inspector_id', sa.UUID(), nullable=True),
        sa.Column('photos_url', sa.Text(), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rma_request_id'], ['rma_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rma_inspections_id'), 'rma_inspections', ['id'], unique=False)
    op.create_index(op.f('ix_rma_inspections_tenant_id'), 'rma_inspections', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_rma_inspections_rma_request_id'), 'rma_inspections', ['rma_request_id'], unique=False)
    op.create_index(op.f('ix_rma_inspections_inspector_id'), 'rma_inspections', ['inspector_id'], unique=False)

    op.create_table('returned_parts',
        sa.Column('rma_request_id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=True),
        sa.Column('part_code', sa.String(length=50), nullable=False),
        sa.Column('delivery_code', sa.String(length=50), nullable=True),
        sa.Column('samsung_nf', sa.String(length=50), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('return_reason', sa.String(length=10), nullable=False),
        sa.Column('devolution_deadline', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('devolution_date', sa.Date(), nullable=True),
        sa.Column('return_nf', sa.String(length=50), nullable=True),
        sa.Column('technician_signature', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('stock_signature', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rma_request_id'], ['rma_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['service_orders.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_returned_parts_id'), 'returned_parts', ['id'], unique=False)
    op.create_index(op.f('ix_returned_parts_tenant_id'), 'returned_parts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_returned_parts_rma_request_id'), 'returned_parts', ['rma_request_id'], unique=False)
    op.create_index(op.f('ix_returned_parts_order_id'), 'returned_parts', ['order_id'], unique=False)

    op.create_table('kpi_metrics',
        sa.Column('technician_id', sa.UUID(), nullable=True),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('nps_score', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('first_visit_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('waiting_time_avg', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('oow_hq_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('ow_repair_approved', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('ltp_mx_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('crrr_mx_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('eco_repair_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('ssr_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('gd_ta_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('atendimento_10min', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('meta_vendas', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('total_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bonus_tier', sa.String(length=20), nullable=True),
        sa.Column('bonus_value', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['technician_id'], ['technicians.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'technician_id', 'month', 'year', name='uq_kpi_tenant_tech_month'),
    )
    op.create_index(op.f('ix_kpi_metrics_id'), 'kpi_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_kpi_metrics_tenant_id'), 'kpi_metrics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_kpi_metrics_technician_id'), 'kpi_metrics', ['technician_id'], unique=False)

    op.create_table('inventory_movements',
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_inventory_movements_id'), 'inventory_movements', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_movements_tenant_id'), 'inventory_movements', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_inventory_movements_product_id'), 'inventory_movements', ['product_id'], unique=False)

    op.create_table('delivery_pendings',
        sa.Column('delivery_number', sa.String(length=50), nullable=False),
        sa.Column('pending_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('received_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_delivery_pendings_id'), 'delivery_pendings', ['id'], unique=False)
    op.create_index(op.f('ix_delivery_pendings_tenant_id'), 'delivery_pendings', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_delivery_pendings_delivery_number'), 'delivery_pendings', ['delivery_number'], unique=False)

    op.create_table('discard_records',
        sa.Column('serial', sa.String(length=100), nullable=False),
        sa.Column('product_type', sa.String(length=30), nullable=False),
        sa.Column('discard_type', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('term_document', sa.Text(), nullable=True),
        sa.Column('authorized_by', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['authorized_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_discard_records_id'), 'discard_records', ['id'], unique=False)
    op.create_index(op.f('ix_discard_records_tenant_id'), 'discard_records', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_discard_records_serial'), 'discard_records', ['serial'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_discard_records_serial'), table_name='discard_records')
    op.drop_index(op.f('ix_discard_records_tenant_id'), table_name='discard_records')
    op.drop_index(op.f('ix_discard_records_id'), table_name='discard_records')
    op.drop_table('discard_records')

    op.drop_index(op.f('ix_delivery_pendings_delivery_number'), table_name='delivery_pendings')
    op.drop_index(op.f('ix_delivery_pendings_tenant_id'), table_name='delivery_pendings')
    op.drop_index(op.f('ix_delivery_pendings_id'), table_name='delivery_pendings')
    op.drop_table('delivery_pendings')

    op.drop_index(op.f('ix_inventory_movements_product_id'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_tenant_id'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_id'), table_name='inventory_movements')
    op.drop_table('inventory_movements')

    op.drop_index(op.f('ix_kpi_metrics_technician_id'), table_name='kpi_metrics')
    op.drop_index(op.f('ix_kpi_metrics_tenant_id'), table_name='kpi_metrics')
    op.drop_index(op.f('ix_kpi_metrics_id'), table_name='kpi_metrics')
    op.drop_table('kpi_metrics')

    op.drop_index(op.f('ix_returned_parts_order_id'), table_name='returned_parts')
    op.drop_index(op.f('ix_returned_parts_rma_request_id'), table_name='returned_parts')
    op.drop_index(op.f('ix_returned_parts_tenant_id'), table_name='returned_parts')
    op.drop_index(op.f('ix_returned_parts_id'), table_name='returned_parts')
    op.drop_table('returned_parts')

    op.drop_index(op.f('ix_rma_inspections_inspector_id'), table_name='rma_inspections')
    op.drop_index(op.f('ix_rma_inspections_rma_request_id'), table_name='rma_inspections')
    op.drop_index(op.f('ix_rma_inspections_tenant_id'), table_name='rma_inspections')
    op.drop_index(op.f('ix_rma_inspections_id'), table_name='rma_inspections')
    op.drop_table('rma_inspections')

    op.drop_index(op.f('ix_rma_requests_product_id'), table_name='rma_requests')
    op.drop_index(op.f('ix_rma_requests_order_id'), table_name='rma_requests')
    op.drop_index(op.f('ix_rma_requests_protocol'), table_name='rma_requests')
    op.drop_index(op.f('ix_rma_requests_tenant_id'), table_name='rma_requests')
    op.drop_index(op.f('ix_rma_requests_id'), table_name='rma_requests')
    op.drop_table('rma_requests')

    op.drop_index(op.f('ix_defect_codes_code'), table_name='defect_codes')
    op.drop_index(op.f('ix_defect_codes_tenant_id'), table_name='defect_codes')
    op.drop_index(op.f('ix_defect_codes_id'), table_name='defect_codes')
    op.drop_table('defect_codes')

    op.drop_column('products', 'samsung_part_code')
    op.drop_column('products', 'category')

    op.drop_column('service_orders', 'route_technicians')
    op.drop_column('service_orders', 'route_car')
    op.drop_column('service_orders', 'scheduled_shift')
    op.drop_column('service_orders', 'scheduled_date')
    op.drop_column('service_orders', 'grms_number')
    op.drop_column('service_orders', 'defect_code')

    op.drop_column('technicians', 'occupation')
    op.drop_column('technicians', 'bp_code')
