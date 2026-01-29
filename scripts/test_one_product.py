"""Script simple para cargar un producto de prueba"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db
import cohere

load_dotenv()

# Setup
cohere_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(cohere_key)
db = get_db()

# 1. Leer UN producto
print("📦 Leyendo un producto...")
response = db.table('articulo').select('*').eq('estado', 'activo').limit(1).execute()

if not response.data:
    print("❌ No hay productos")
    exit(1)

producto = response.data[0]
print(f"✓ Producto: {producto['nombre']}")

#  2. Generar embedding
content = f"Producto: {producto['nombre']}, Stock: {producto['stock']}"
print(f"Generando embedding...")

embed_response = co.embed(
    texts=[content],
    model='embed-multilingual-v3.0',
    input_type='search_document'
)

embedding = embed_response.embeddings[0]
print(f"✓ Embedding generado ({len(embedding)} dimensiones)")

# 3. Guardar en documents
print("Guardando en Supabase...")
db.table('documents').insert({
    'content': content,
    'embedding': embedding,
    'metadata': {'source': 'test', 'nombre': producto['nombre']}
}).execute()

print("✅ ¡Producto cargado exitosamente!")
