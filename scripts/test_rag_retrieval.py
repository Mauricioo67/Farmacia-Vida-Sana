import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from models.rag import get_rag_manager

load_dotenv()

def test_rag():
    print("=== TEST DE RECUPERACIÓN RAG (COHERE) ===")
    
    try:
        rag = get_rag_manager()
        
        # Test query
        query = "categorias"
        print(f"\n🔎 Buscando: '{query}'")
        
        results = rag.search_relevant_docs(query, top_k=3)
        
        if results:
            print(f"\n✅ Se encontraron {len(results)} resultados:")
            for i, doc in enumerate(results):
                content = doc.get('content', '')[:100].replace('\n', ' ')
                similarity = doc.get('similarity', 'N/A')
                print(f"  {i+1}. [Sim: {similarity}] {content}...")
        else:
            print("\n❌ No se encontraron resultados. Verifique:")
            print("  1. Que la tabla 'documents' tenga contenido")
            print("  2. Que la función RPC 'search_documents' exista")
            print("  3. Que las dimensiones de embedding coincidan (Code: Cohere/1024 vs DB)")

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
