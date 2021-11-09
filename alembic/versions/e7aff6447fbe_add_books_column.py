"""Add books column

Revision ID: e7aff6447fbe
Revises: 7cdaa5513f2d
Create Date: 2017-10-08 15:22:12.019617

"""
import sqlalchemy as sa
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e7aff6447fbe'
down_revision = '7cdaa5513f2d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bible_versions', sa.Column('books', sa.BigInteger, nullable=True))
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

    op.execute(
        bible_versions.update()
        .where(
            (bible_versions.c.command == op.inline_literal('asv'))
            | (bible_versions.c.command == op.inline_literal('kjv'))
            | (bible_versions.c.command == op.inline_literal('niv'))
            | (bible_versions.c.command == op.inline_literal('csb'))
            | (bible_versions.c.command == op.inline_literal('net'))
            | (bible_versions.c.command == op.inline_literal('isv'))
            | (bible_versions.c.command == op.inline_literal('trt'))
            | (bible_versions.c.command == op.inline_literal('bsb'))
        )
        .values({'books': 3})
    )
    op.execute(
        bible_versions.update()
        .where(bible_versions.c.command == op.inline_literal('sbl'))
        .values({'books': 2})
    )
    op.execute(
        bible_versions.update()
        .where(bible_versions.c.command == op.inline_literal('nrsv'))
        .values({'books': 1048575})
    )
    op.alter_column('bible_versions', 'books', nullable=False)


def downgrade():
    op.drop_column('bible_versions', 'books')
