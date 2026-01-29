-- migration_rag_cohere.sql
-- Ejecutar en Supabase SQL Editor para adaptar a Cohere (1024 dimensiones)

-- 1. Eliminar función anterior (depende del tipo de dato antiguo)
DROP FUNCTION IF EXISTS search_documents;

-- 2. Modificar columna vector a 1024 dimensiones
-- Nota: Esto borrará los datos existentes en la columna si no son compatibles.
-- Si la tabla está vacía o se va a repoblar, mejor truncar.
TRUNCATE TABLE documents;
ALTER TABLE documents ALTER COLUMN embedding TYPE vector(1024);

-- 3. Recrear índice (recomendado borrar y crear)
DROP INDEX IF EXISTS documents_embedding_idx;
CREATE INDEX documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Recrear función de búsqueda con 1024 dims
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(1024),
    similarity_threshold float,
    match_count int
)
RETURNS TABLE(id int, content text, similarity float, metadata jsonb)
LANGUAGE sql
AS $$
SELECT
    d.id,
    d.content,
    1 - (d.embedding <=> query_embedding) as similarity,
    d.metadata
FROM documents d
WHERE 1 - (d.embedding <=> query_embedding) > similarity_threshold
ORDER BY d.embedding <=> query_embedding
LIMIT match_count;
$$;
