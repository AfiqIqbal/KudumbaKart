"""Added email field to Order model

Revision ID: 03ab0c9be0ba
Revises: 50ead3102ae4
Create Date: 2025-04-04 11:21:41.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '03ab0c9be0ba'
down_revision = '50ead3102ae4'
branch_labels = None
depends_on = None

def upgrade():
    # Create a temp table with the new schema
    op.execute('CREATE TABLE order_new ('
               'id INTEGER NOT NULL PRIMARY KEY, '
               'user_id INTEGER NOT NULL, '
               'date_ordered DATETIME, '
               'status VARCHAR(20), '
               'total_amount FLOAT NOT NULL, '
               'shipping_address TEXT NOT NULL, '
               'phone VARCHAR(20) NOT NULL, '
               'email VARCHAR(120) NOT NULL DEFAULT "", '
               'payment_method VARCHAR(20), '
               'payment_status VARCHAR(20), '
               'FOREIGN KEY(user_id) REFERENCES user (id))')
    
    # Copy data from the old table to the new table
    op.execute('INSERT INTO order_new '
               'SELECT id, user_id, date_ordered, status, total_amount, '
               'shipping_address, phone, "", payment_method, payment_status '
               'FROM "order"')
    
    # Drop the old table
    op.execute('DROP TABLE "order"')
    
    # Rename the new table to the original name
    op.execute('ALTER TABLE order_new RENAME TO "order"')

def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('email')
