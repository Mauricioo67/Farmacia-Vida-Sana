import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from models.db import get_db

load_dotenv()

def check_categories():
    print("=== VERIFICANDO TABLA CATEGORIA ===")
    
    try:
        db = get_db()
        
        # Intentar seleccionar de tabla 'categoria'
        response = db.table('categoria').select('*').limit(5).execute()
        
        if response.data:
            print(f"✅ Tabla 'categoria' encontrada con {len(response.data)} filas de muestra.")
            print("\nEjemplo de datos:")
            print(response.data[0])
            
            # Ver nombres claves
            keys = response.data[0].keys()
            print(f"\nColumnas detectadas: {list(keys)}")
            return True
        else:
            print("⚠️ La tabla 'categoria' parece estar vacía o no existe (si lanza error).")
            return False
            
    except Exception as e:
        print(f"❌ Error consultando tabla 'categoria': {e}")
        return False

if __name__ == "__main__":
    check_categories()
