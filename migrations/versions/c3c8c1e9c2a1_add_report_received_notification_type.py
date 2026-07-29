"""add report received notification type

Revision ID: c3c8c1e9c2a1
Revises: a47c40f911e5
Create Date: 2026-07-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3c8c1e9c2a1'
down_revision = 'a47c40f911e5'
branch_labels = None
depends_on = None


def upgrade():
    # MySQL needs the enum definition updated in place so the new
    # REPORT_RECEIVED value is valid for future inserts.
    op.execute(
        "ALTER TABLE notifications "
        "MODIFY type ENUM('REPORT_RECEIVED', 'HOTSPOT', 'STATUS_UPDATE') NOT NULL"
    )


def downgrade():
    op.execute(
        "ALTER TABLE notifications "
        "MODIFY type ENUM('HOTSPOT', 'STATUS_UPDATE') NOT NULL"
    )