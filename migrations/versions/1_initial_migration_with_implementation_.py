"""Initial migration with implementation_details field

Revision ID: 1
Revises: 
Create Date: 2025-03-20 12:55:38.146587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create Project table
    # pylint: disable=no-member
    op.create_table('project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('implementation_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create Sprint table
    op.create_table('sprint',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create Task table
    op.create_table('task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprint.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create Issue table
    op.create_table('issue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprint.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order of creation
    # pylint: disable=no-member
    op.drop_table('issue')
    op.drop_table('task')
    op.drop_table('sprint')
    op.drop_table('project')
