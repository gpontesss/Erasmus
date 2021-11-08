"""initial structure

Revision ID: 499dad92327d
Revises: 
Create Date: 2017-09-30 21:47:58.501740

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '499dad92327d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bible_versions = op.create_table(
        'bible_versions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('command', sa.String, unique=True),
        sa.Column('name', sa.String),
        sa.Column('abbr', sa.String),
        sa.Column('service', sa.String),
        sa.Column('service_version', sa.String),
    )

    op.create_table(
        'user_prefs',
        sa.Column('user_id', sa.String, primary_key=True),
        sa.Column('bible_id', sa.Integer, sa.ForeignKey('bible_versions.id')),
    )

    op.bulk_insert(
        bible_versions,
        [
            dict(
                command='kjv',
                name='King James Version',
                abbr='KJV',
                service='ApiBible',
                service_version='de4e12af7f28f599-01',
            ),
            dict(
                command='bsb',
                name='Berean Study Bible',
                abbr='BSB',
                service='ApiBible',
                service_version='bba9f40183526463-01',
            ),
            dict(
                command='trt',
                name='Translation for Translators',
                abbr='TRT',
                service='ApiBible',
                service_version='66c22495370cdfc0-01',
            ),
            dict(
                command='asv',
                name='American Standard Version',
                abbr='ASV',
                service='ApiBible',
                service_version='685d1470fe4d5c3b-01',
            ),
            dict(
                command='sbl',
                name='SBL Greek New Testament',
                abbr='SBL GNT',
                service='BibleGateway',
                service_version='SBLGNT',
            ),
            dict(
                command='niv',
                name='New International Version',
                abbr='NIV',
                service='BibleGateway',
                service_version='NIV',
            ),
            dict(
                command='csb',
                name='Christian Standard Bible',
                abbr='CSB',
                service='BibleGateway',
                service_version='CSB',
            ),
            dict(
                command='isv',
                name='International Standard Version',
                abbr='ISV',
                service='BibleGateway',
                service_version='ISV',
            ),
            dict(
                command='net',
                name='New English Translation',
                abbr='NET',
                service='BibleGateway',
                service_version='NET',
            ),
            dict(
                command='nrsv',
                name='New Revised Standard Version',
                abbr='NRSV',
                service='BibleGateway',
                service_version='NRSV',
            ),
        ],
    )


def downgrade():
    op.drop_table('user_prefs')
    op.drop_table('bible_versions')
