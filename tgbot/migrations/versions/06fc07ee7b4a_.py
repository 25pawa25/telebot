"""empty message

Revision ID: 06fc07ee7b4a
Revises: 950fbc1af425
Create Date: 2022-04-11 22:01:06.292667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06fc07ee7b4a'
down_revision = '950fbc1af425'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_state', sa.Column('step', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat_state', 'step')
    # ### end Alembic commands ###
