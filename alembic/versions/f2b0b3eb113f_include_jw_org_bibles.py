"""include jw.org bibles

Revision ID: f2b0b3eb113f
Revises: 85d51f96a1cd
Create Date: 2021-11-09 14:49:43.966485

"""
import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f2b0b3eb113f'
down_revision = '85d51f96a1cd'
branch_labels = None
depends_on = None

bible_versions = table(
    'bible_versions',
    column('id', sa.Integer),
    column('command', sa.String),
    column('name', sa.String),
    column('abbr', sa.String),
    column('service', sa.String),
    column('service_version', sa.String),
    column('rtl', sa.Boolean),
    column('books', sa.BigInteger),
)


def upgrade():
    op.bulk_insert(
        bible_versions,
        [
            dict(
                command='nwt84',
                name='New World Translation of the Holy Scriptures with References (1984)',
                abbr='NWT84',
                service='JWOrg',
                service_version='en/wol/b/r1/lp-e/Rbi8',
                books=3,
            ),
            dict(
                command='nwt13',
                name='New World Translation of the Holy Scriptures, revised 2013',
                abbr='NWT13',
                service='JWOrg',
                service_version='en/wol/b/r1/lp-e/nwt',
                books=3,
            ),
        ],
    )


def downgrade():
    op.execute(
        bible_versions.delete().where(
            (bible_versions.c.command == op.inline_literal('nwt84'))
            | (bible_versions.c.command == op.inline_literal('nwt13'))
        )
    )
