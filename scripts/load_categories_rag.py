"""
Script para cargar CATEGORIAS de la farmacia a la tabla documents
usando Cohere embeddings
"""
import os
import sys
# Fix para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db
import cohere

load_dotenv()

def load_categories_to_rag():
    """Cargar categorias como documentos"""
    
    # Inicializar Cohere
    cohere_key = os.getenv('COHERE_API_KEY')
    if not cohere_key:
        print("❌ COHERE_API_KEY no configurada")
        return False
    
    co = cohere.Client(cohere_key)
    db = get_db()
    
    try:
        print("📦 Cargando categorias...")
        response = db.table('categoria').select('*').execute()
        
        categorias = response.data
        if not categorias:
            print("⚠️ No hay categorias")
            return False
            
        print(f"✓ {len(categorias)} categorias encontradas")
        
        documents_to_insert = []
        
        for i, cat in enumerate(categorias):
            # Crear texto rico para embedding
            nombre = cat.get('nombre', 'Sin nombre')
            desc = cat.get('descripcion', '') or 'Sin descripción'
            
            content_text = f"""Categoría Farmacéutica: {nombre}
Descripción: {desc}
Tipo: Clasificación de productos
"""
            
            print(f"  [{i+1}/{len(categorias)}] Procesando: {nombre}")
            
            # Embedding
            embed_response = co.embed(
                texts=[content_text],
                model='embed-multilingual-v3.0',
                input_type='search_document'
            )
            
            embedding_vector = embed_response.embeddings[0]
            
            documents_to_insert.append({
                'content': content_text,
                'embedding': embedding_vector,
                'metadata': {
                    'source': 'categoria',
                    'id': cat.get('idcategoria') or cat.get('id'),
                    'nombre': nombre,
                    'tipo': 'categoria'
                }
            })
            
            # Guardar
            db.table('documents').insert(documents_to_insert[-1]).execute()

        print(f"\n✅ ¡Carga de categorias completada!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    load_categories_to_rag()
