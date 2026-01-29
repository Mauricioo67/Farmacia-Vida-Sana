import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from models.db import execute_sql

load_dotenv()

def fix_schema():
    print("=== ACTUALIZANDO ESQUEMA DE BASE DE DATOS ===")
    
    # SQL para redefinir la función con vector(1024)
    # Nota: Usamos vector(1024) por Cohere.
    # DROP FUNCTION es importante para eliminar la firma anterior.
    sql = """
    DROP FUNCTION IF EXISTS search_documents;
    
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
    """
    
    print("\nEjecutando SQL...")
    try:
        success = execute_sql(sql)
        if success:
            print("✅ Función search_documents actualizada correctamente a vector(1024)")
        else:
            print("❌ Falló la ejecución del SQL. Puede que 'exec_sql' no esté habilitado en Supabase.")
            print("   Por favor ejecuta el SQL manualmente en Supabase SQL Editor.")
            print("\nSQL NECESARIO:\n" + sql)
    except Exception as e:
        print(f"❌ Error intentando ejecutar SQL: {e}")

if __name__ == "__main__":
    fix_schema()
