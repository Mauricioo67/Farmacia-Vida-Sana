"""
Script para cargar productos de la farmacia a la tabla documents
usando Cohere embeddings (gratis)
"""
import os
import sys
# Fix para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db
import cohere

load_dotenv()

def load_products_to_rag():
    """Cargar productos como documentos en la base de conocimiento"""
    
    # Inicializar Cohere
    cohere_key = os.getenv('COHERE_API_KEY')
    if not cohere_key:
        print("❌ COHERE_API_KEY no configurada en .env")
        return False
    
    co = cohere.Client(cohere_key)
    db = get_db()
    
    try:
        # 1. Leer productos activos
        print("📦 Cargando productos...")
        response = db.table('articulo').select(
            'idarticulo, nombre, descripcion, stock, precio_venta, fecha_vencimiento, estado'
        ).eq('estado', 'activo').execute()
        
        productos = response.data
        if not productos:
            print("⚠️ No se encontraron productos activos")
            return False
        
        print(f"✓ {len(productos)} productos encontrados")
        
        # 2. Convertir cada producto en texto y generar embeddings
        documents_to_insert = []
        
        for i, producto in enumerate(productos):
            # Crear descripción del producto
            desc = producto.get('descripcion', '') or 'Sin descripción'
            vencimiento = producto.get('fecha_vencimiento', 'N/A')
            
            content_text = f"""Producto: {producto['nombre']}
Descripción: {desc}
Stock disponible: {producto['stock']} unidades
Precio: Bs. {producto['precio_venta']}
Fecha de vencimiento: {vencimiento}
Estado: {producto['estado']}"""
            
            # Generar embedding con Cohere
            print(f"  [{i+1}/{len(productos)}] Generando embedding para: {producto['nombre'][:30]}...")
            
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
                    'source': 'articulo',
                    'idarticulo': producto['idarticulo'],
                    'nombre': producto['nombre'],
                    'tipo': 'producto'
                }
            })
            
            # Insertar en lotes de 10
            if len(documents_to_insert) >= 10 or i == len(productos) - 1:
                print(f"  💾 Guardando lote en Supabase...")
                for doc in documents_to_insert:
                    db.table('documents').insert(doc).execute()
                documents_to_insert = []
        
        print(f"\n✅ ¡Carga completada! {len(productos)} productos indexados en RAG")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== CARGA DE PRODUCTOS A RAG ===\n")
    success = load_products_to_rag()
    sys.exit(0 if success else 1)
