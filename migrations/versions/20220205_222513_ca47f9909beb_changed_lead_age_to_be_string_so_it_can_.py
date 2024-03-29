"""changed lead.age to be string so it can work with 'deceased'.

Revision ID: ca47f9909beb
Revises: 7f137eac7926
Create Date: 2022-02-05 22:25:13.216135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca47f9909beb'
down_revision = '7f137eac7926'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lead', 'age',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=30),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lead', 'age',
               existing_type=sa.String(length=30),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
