-- Add missing columns to prices table
-- Run this script directly on your PostgreSQL database

-- Add source column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'prices' AND column_name = 'source'
    ) THEN
        ALTER TABLE prices ADD COLUMN source VARCHAR(50) DEFAULT 'manual';
    END IF;
END $$;

-- Add confidence_score column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'prices' AND column_name = 'confidence_score'
    ) THEN
        ALTER TABLE prices ADD COLUMN confidence_score NUMERIC(3, 2) DEFAULT 1.0;
    END IF;
END $$;

-- Update existing rows with default values
UPDATE prices SET source = 'manual' WHERE source IS NULL;
UPDATE prices SET confidence_score = 1.0 WHERE confidence_score IS NULL;

-- Verify columns were added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'prices' 
ORDER BY ordinal_position;
