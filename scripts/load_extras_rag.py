"""
Script para cargar PROVEEDORES y CLIENTES a RAG
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db
import cohere

load_dotenv()

def load_extras():
    cohere_key = os.getenv('COHERE_API_KEY')
    if not cohere_key:
        print("❌ COHERE_API_KEY no configurada")
        return

    co = cohere.Client(cohere_key)
    db = get_db()

    # 1. Cargar Proveedores
    try:
        print("\n📦 Cargando Proveedores...")
        proveedores = db.table('proveedor').select('*').execute().data
        if proveedores:
            for p in proveedores:
                nombre = p.get('nombre', 'Sin nombre')
                contacto = p.get('contacto', '')
                telefono = p.get('telefono', '')
                
                content = f"""Proveedor: {nombre}
Contacto: {contacto}
Teléfono: {telefono}
Tipo: Proveedor de medicamentos"""
                
                embed = co.embed(texts=[content], model='embed-multilingual-v3.0', input_type='search_document').embeddings[0]
                
                db.table('documents').insert({
                    'content': content,
                    'embedding': embed,
                    'metadata': {'type': 'proveedor', 'id': p.get('idproveedor'), 'nombre': nombre}
                }).execute()
                print(f"  ✓ Proveedor indexado: {nombre}")
        else:
            print("⚠️ No se encontraron proveedores")

    except Exception as e:
        print(f"❌ Error proveedores: {e}")

    # 2. Cargar Clientes (Opcional, puede ser mucho volumen pero útil para "Quién es Juan Pérez")
    try:
        print("\n📦 Cargando Clientes (Top 50 activos)...")
        clientes = db.table('cliente').select('*').limit(50).execute().data
        if clientes:
            for c in clientes:
                nombre = c.get('nombre', 'Sin nombre')
                tipo_doc = c.get('tipo_documento', '')
                num_doc = c.get('num_documento', '')
                tel = c.get('telefono', '')
                
                content = f"""Cliente: {nombre}
Documento: {tipo_doc} {num_doc}
Teléfono: {tel}
Tipo: Cliente registrado"""
                
                embed = co.embed(texts=[content], model='embed-multilingual-v3.0', input_type='search_document').embeddings[0]
                
                db.table('documents').insert({
                    'content': content,
                    'embedding': embed,
                    'metadata': {'type': 'cliente', 'id': c.get('idcliente'), 'nombre': nombre}
                }).execute()
                print(f"  ✓ Cliente indexado: {nombre}")
        else:
            print("⚠️ No se encontraron clientes")

    except Exception as e:
        print(f"❌ Error clientes: {e}")

if __name__ == "__main__":
    load_extras()
