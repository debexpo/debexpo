"""Switch from 200 to 32 char for md5sum field in package_files table

Revision ID: 1d81fcc4f3db
Revises: 8d6f497e959e
Create Date: 2019-02-13 15:17:51.471113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d81fcc4f3db'
down_revision = '8d6f497e959e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('package_files', schema=None) as batch_op:
        batch_op.alter_column('md5sum', type_=sa.types.String(32))
    pass


def downgrade():
    with op.batch_alter_table('package_files', schema=None) as batch_op:
        batch_op.alter_column('md5sum', type_=sa.types.String(200))
    pass
