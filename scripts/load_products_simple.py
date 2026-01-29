"""Cargar productos con mejor manejo de errores"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db
import cohere
import time

load_dotenv()

co = cohere.Client(os.getenv('COHERE_API_KEY'))
db = get_db()

print("=== CARGA DE PRODUCTOS A RAG ===\n")

# Leer productos
response = db.table('articulo').select('*').eq('estado', 'activo').limit(20).execute()
productos = response.data

print(f"📦 {len(productos)} productos encontrados\n")

exitos = 0
errores = 0

for i, p in enumerate(productos, 1):
    try:
        # Crear contenido
        nombre = p.get('nombre', 'Sin nombre')
        desc = p.get('descripcion', '') or 'Sin descripción'
        stock = p.get('stock', 0)
        precio = p.get('precio_venta', 0)
        venc = p.get('fecha_vencimiento', 'N/A')
        
        content = f"""Producto: {nombre}
Descripción: {desc}
Stock: {stock} unidades
Precio: Bs. {precio}
Vencimiento: {venc}"""
        
        # Generar embedding
        print(f"[{i}/{len(productos)}] {nombre[:40]}...", end=" ")
        
        embed_response = co.embed(
            texts=[content],
            model='embed-multilingual-v3.0',
            input_type='search_document'
        )
        
        # Guardar
        db.table('documents').insert({
            'content': content,
            'embedding': embed_response.embeddings[0],
            'metadata': {
                'source': 'articulo',
                'idarticulo': p.get('idarticulo'),
                'nombre': nombre
            }
        }).execute()
        
        print("✓")
        exitos += 1
        time.sleep(0.2)  # Evitar rate limit
        
    except Exception as e:
        print(f"✗ Error: {e}")
        errores += 1

print(f"\n✅ Completado: {exitos} éxitos, {errores} errores")
