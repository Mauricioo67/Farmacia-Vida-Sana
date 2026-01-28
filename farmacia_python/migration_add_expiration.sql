-- Migration Script: Add Expiration Date Tracking
-- Date: 2026-01-19
-- Description: Adds fecha_vencimiento column to articulo table for expiration tracking

-- Add expiration date column to articulo table
ALTER TABLE articulo 
ADD COLUMN IF NOT EXISTS fecha_vencimiento DATE;

-- Add index for faster queries on expiration dates
CREATE INDEX IF NOT EXISTS idx_articulo_fecha_vencimiento 
ON articulo(fecha_vencimiento);

-- Optional: Add comment to column
COMMENT ON COLUMN articulo.fecha_vencimiento IS 'Fecha de vencimiento del producto (opcional)';

-- Update sample data with expiration dates (optional - for testing)
-- Uncomment the following lines if you want to add sample expiration dates

/*
UPDATE articulo 
SET fecha_vencimiento = CURRENT_DATE + INTERVAL '90 days'
WHERE fecha_vencimiento IS NULL AND estado = 'activo'
LIMIT 10;

UPDATE articulo 
SET fecha_vencimiento = CURRENT_DATE + INTERVAL '7 days'
WHERE fecha_vencimiento IS NULL AND estado = 'activo'
LIMIT 3;

UPDATE articulo 
SET fecha_vencimiento = CURRENT_DATE - INTERVAL '5 days'
WHERE fecha_vencimiento IS NULL AND estado = 'activo'
LIMIT 2;
*/
