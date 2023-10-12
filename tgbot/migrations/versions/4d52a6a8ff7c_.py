"""empty message

Revision ID: 4d52a6a8ff7c
Revises: 06fc07ee7b4a
Create Date: 2022-04-11 22:28:29.771962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d52a6a8ff7c'
down_revision = '06fc07ee7b4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tmp_data', sa.Column('state_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tmp_data', 'chat_state', ['state_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tmp_data', type_='foreignkey')
    op.drop_column('tmp_data', 'state_id')
    # ### end Alembic commands ###