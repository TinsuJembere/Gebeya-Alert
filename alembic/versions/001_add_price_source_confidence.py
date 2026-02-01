"""add source and confidence_score to prices

Revision ID: 001_add_price_columns
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_price_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns exist before adding (for both PostgreSQL and SQLite)
    conn = op.get_bind()
    
    # Check if source column exists
    if conn.dialect.name == 'postgresql':
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prices' AND column_name = 'source'
        """))
        source_exists = result.fetchone() is not None
        
        if not source_exists:
            op.add_column('prices', sa.Column('source', sa.String(length=50), nullable=True, server_default='manual'))
        
        # Check if confidence_score column exists
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prices' AND column_name = 'confidence_score'
        """))
        confidence_exists = result.fetchone() is not None
        
        if not confidence_exists:
            op.add_column('prices', sa.Column('confidence_score', sa.Numeric(precision=3, scale=2), nullable=True, server_default='1.0'))
    else:
        # SQLite - simpler approach, will fail if column exists but that's okay
        try:
            op.add_column('prices', sa.Column('source', sa.String(length=50), nullable=True, server_default='manual'))
        except:
            pass  # Column might already exist
        
        try:
            op.add_column('prices', sa.Column('confidence_score', sa.Numeric(precision=3, scale=2), nullable=True, server_default='1.0'))
        except:
            pass  # Column might already exist
    
    # Update existing rows
    op.execute(sa.text("UPDATE prices SET source = 'manual' WHERE source IS NULL"))
    op.execute(sa.text("UPDATE prices SET confidence_score = 1.0 WHERE confidence_score IS NULL"))


def downgrade() -> None:
    # Remove columns if they exist
    conn = op.get_bind()
    
    if conn.dialect.name == 'postgresql':
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prices' AND column_name = 'source'
        """))
        if result.fetchone():
            op.drop_column('prices', 'source')
        
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prices' AND column_name = 'confidence_score'
        """))
        if result.fetchone():
            op.drop_column('prices', 'confidence_score')
    else:
        # SQLite doesn't support DROP COLUMN easily, skip for SQLite
        pass
