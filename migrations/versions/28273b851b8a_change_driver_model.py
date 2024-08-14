"""change driver model

Revision ID: 28273b851b8a
Revises: 00c40565a7e8
Create Date: 2024-08-14 15:20:09.347593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28273b851b8a'
down_revision = '00c40565a7e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('drivers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(), nullable=False))
        batch_op.alter_column('contact_info',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.create_unique_constraint(None, ['contact_info'])
        batch_op.create_unique_constraint(None, ['email'])

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.drop_column('buyer_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('buyer_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['buyer_id'], ['id'])
        batch_op.drop_column('user_id')

    with op.batch_alter_table('drivers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('contact_info',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.drop_column('email')

    # ### end Alembic commands ###
