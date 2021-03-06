"""initial migration

Revision ID: 6b63b6118f42
Revises: 
Create Date: 2019-05-20 23:54:14.124521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b63b6118f42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comment', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('internal_users', 'username',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.create_index(op.f('ix_internal_users_username'), 'internal_users', ['username'], unique=True)
    op.alter_column('post', 'title',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('tag', 'title',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.create_unique_constraint(None, 'tag', ['title'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tag', type_='unique')
    op.alter_column('tag', 'title',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('post', 'title',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.drop_index(op.f('ix_internal_users_username'), table_name='internal_users')
    op.alter_column('internal_users', 'username',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('comment', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###
