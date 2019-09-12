"""Add a field on table package_files to hold file's sha256 checksum

Revision ID: 8d6f497e959e
Revises:
Create Date: 2019-02-13 13:33:36.249795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d6f497e959e'
down_revision = '7cceb63f746e'
branch_labels = None
depends_on = None

# SQlite does not support ALTER TABLE with ALTER COLUMN.
# Hence we must:
#   - create a new table with the correct schema
#   - copy over the data
#   - swap the names
#   - remove the old table
#
# https://www.sqlitetutorial.net/sqlite-alter-table/

# Alembic has a feature that take care of that automatically.
#
# https://alembic.sqlalchemy.org/en/latest/batch.html#batch-mode-with-autogenerate


def upgrade():
    op.add_column('package_files', sa.Column('sha256sum', sa.types.String(64),
                  nullable=False, server_default=''))
    with op.batch_alter_table('package_files', schema=None) as batch_op:
        batch_op.alter_column('sha256sum', server_default=None)
    pass


def downgrade():
    with op.batch_alter_table('package_files', schema=None) as batch_op:
        batch_op.drop_column('sha256sum')
    pass
