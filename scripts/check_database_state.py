import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.db import get_db

load_dotenv()

def check_db():
    try:
        db = get_db()
        
        # Check 'articulo' table
        print("Checking 'articulo' table...")
        response_art = db.table('articulo').select('idarticulo').execute()
        count_art = len(response_art.data)
        print(f"Products in 'articulo' table: {count_art}")
        
        # Check 'documents' table
        print("\nChecking 'documents' table...")
        response_doc = db.table('documents').select('id, content, embedding').limit(1).execute()
        
        # Get total count (approximation by fetching up to 1000 IDs if needed, or just assume >0 from limit 1)
        # Since I can't count easily without fetching, I'll just rely on the first row check for structure.
        # But wait, I want to know total. I'll do a separate header count if I could, but I can't.
        # I'll just fetch all IDs again to get count.
        ids_response = db.table('documents').select('id').execute()
        count_doc = len(ids_response.data)
        print(f"Entries in 'documents' table: {count_doc}")
        
        if count_doc > 0:
            first_doc = response_doc.data[0]
            print("\nSample document check:")
            doc_id = first_doc.get('id')
            print(f"ID: {doc_id} (Type: {type(doc_id)})")

            
            emb = first_doc.get('embedding')
            if emb:
                   # Convert to string to avoid garbage in async output if necessary, or just print len
                   print(f"VECTOR_DIMENSION:{len(emb)}")
            else:
                   print("Embedding found: NO (None)")
                   
        # Check specific for categories
        print("\nChecking for 'categoria' documents...")
        # Fetch ID and metadata for all documents (or large limit)
        all_docs = db.table('documents').select('id, metadata').execute()
        
        cat_docs = 0
        prod_docs = 0
        
        if all_docs.data:
            for d in all_docs.data:
                meta = d.get('metadata')
                if meta:
                    tipo = meta.get('type') or meta.get('source')
                    if tipo == 'categoria':
                        cat_docs += 1
                    elif tipo == 'producto' or tipo == 'articulo':
                        prod_docs += 1
                        
        print(f"  - Product Documents: {prod_docs}")
        print(f"  - Category Documents: {cat_docs}")
        
        if cat_docs > 0:
            print("✅ Category data verified in DB")
        else:
            print("⚠️ No category data found!")

            
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db()
