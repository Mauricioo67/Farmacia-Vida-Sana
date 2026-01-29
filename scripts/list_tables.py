import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from models.db import get_db

load_dotenv()

def list_tables():
    print("=== INSPECCIONANDO TABLAS DISPONIBLES ===")
    
    # Intento de listar tablas via information_schema (si es posible con este cliente)
    # Si no, probaremos nombres comunes.
    
    known_tables = [
        'articulo', 'categoria', 'cliente', 'compra', 'detalle_compra', 
        'detalle_venta', 'usuario', 'venta', 'ingreso', 'proveedor', 'laboratorio', 'presentacion'
    ]
    
    db = get_db()
    
    for table in known_tables:
        try:
            # Intentar leer 1 fila
            resp = db.table(table).select('*').limit(1).execute()
            count = len(resp.data) if resp.data else 0
            if resp.data is not None: # Si no error, existe
                status = "✅ Existe"
                # Intentar contar (aproximado o si wrapper soporta)
                print(f"{status.ljust(15)} {table} (Accesible)")
            
        except Exception:
            print(f"❌ No existe    {table}")

if __name__ == "__main__":
    list_tables()
