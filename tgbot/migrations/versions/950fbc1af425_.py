"""empty message

Revision ID: 950fbc1af425
Revises: 6be1dbdb0011
Create Date: 2022-04-10 22:57:46.911511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '950fbc1af425'
down_revision = '6be1dbdb0011'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_state',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('state', sa.Enum('DEFAULT_STATE', 'USER_CREATE_STATE', 'PROJECT_CREATE_STATE', name='chatstate'), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('chat_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_state')
    # ### end Alembic commands ###
