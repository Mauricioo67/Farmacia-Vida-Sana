import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db

load_dotenv()

db = get_db()

# Verificar tabla documents
try:
    result = db.table('documents').select('*').limit(1).execute()
    print(f"✓ Tabla documents existe")
    print(f"Columns: {result.data[0].keys() if result.data else 'vacía'}")
except Exception as e:
    print(f"Error: {e}")
