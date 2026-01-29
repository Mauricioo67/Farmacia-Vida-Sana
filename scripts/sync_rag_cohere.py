import os
import time
from supabase import create_client, Client
import cohere
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, COHERE_API_KEY]):
    print("❌ Error: Faltan variables de entorno (SUPABASE_URL, SUPABASE_KEY, COHERE_API_KEY)")
    exit(1)

# Inicializar clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
co = cohere.Client(COHERE_API_KEY)

def get_products():
    """Obtener productos activos"""
    print("📦 Buscando productos...")
    response = supabase.table('articulo').select(
        'idarticulo, nombre, descripcion, stock, precio_venta, fecha_vencimiento, categoria(nombre), presentacion(nombre)'
    ).eq('estado', 'activo').execute()
    return response.data

def format_product_doc(p):
    """Formatear producto a texto para embedding"""
    cat = p.get('categoria', {}).get('nombre') if p.get('categoria') else 'General'
    pres = p.get('presentacion', {}).get('nombre') if p.get('presentacion') else 'Unidad'
    
    # Texto rico para búsqueda semántica
    content = (
        f"PRODUCTO: {p['nombre']}\n"
        f"CATEGORÍA: {cat}\n"
        f"PRESENTACIÓN: {pres}\n"
        f"DESCRIPCIÓN: {p['descripcion'] or 'Sin descripción'}\n"
        f"PRECIO: {p['precio_venta']} Bs\n"
        f"STOCK ACTUAL: {p['stock']}\n"
        f"VENCIMIENTO: {p['fecha_vencimiento']}"
    )
    
    metadata = {
        "type": "product",
        "id": p['idarticulo'],
        "name": p['nombre'],
        "stock": p['stock'],
        "price": p['precio_venta']
    }
    return content, metadata

def sync_products():
    products = get_products()
    print(f"✅ Encontrados {len(products)} productos.")
    
    docs_to_insert = []
    texts_to_embed = []
    
    for p in products:
        content, metadata = format_product_doc(p)
        docs_to_insert.append({"content": content, "metadata": metadata})
        texts_to_embed.append(content)
    
    if not docs_to_insert:
        return

    print("🧠 Generando embeddings con Cohere (embed-multilingual-v3.0)...")
    
    # Batch processing podría ser necesario si son muchos, pero para <1000 items está bien
    # Cohere rate limit podría aplicar.
    
    batch_size = 90 # Cohere max batch size usually around 96
    
    total_indexed = 0
    
    for i in range(0, len(texts_to_embed), batch_size):
        batch_texts = texts_to_embed[i:i+batch_size]
        batch_docs = docs_to_insert[i:i+batch_size]
        
        try:
            response = co.embed(
                texts=batch_texts,
                model='embed-multilingual-v3.0',
                input_type='search_document'
            )
            embeddings = response.embeddings
            
            # Preparar records
            records = []
            for j, doc in enumerate(batch_docs):
                records.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "embedding": embeddings[j]
                })
            
            # Insertar en Supabase
            print(f"💾 Guardando batch {i}-{i+len(batch_texts)} en Supabase...")
            supabase.table('documents').insert(records).execute()
            total_indexed += len(records)
            
            # Rate limit guard
            time.sleep(1) 
            
        except Exception as e:
            print(f"❌ Error en batch {i}: {e}")

    print(f"✨ Sincronización completada. {total_indexed} documentos indexados.")

if __name__ == "__main__":
    print("🚀 Iniciando sincronización de RAG...")
    # Limpiar documentos antiguos de productos (opcional, para evitar duplicados puros)
    # supabase.table('documents').delete().eq('metadata->>type', 'product').execute()
    # Por seguridad, el usuario debería truncar o manejar esto.
    
    sync_products()
