import os
from models.db import get_db
from config import Config
import json

# Intentar importaciones opcionales de LangChain; si no están disponibles,
# marcamos que RAG no está disponible pero no rompemos la importación del módulo.
try:
    from langchain.document_loaders import DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import SupabaseVectorStore
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except Exception:
    DirectoryLoader = None
    RecursiveCharacterTextSplitter = None
    OpenAIEmbeddings = None
    SupabaseVectorStore = None
    ChatOpenAI = None
    RetrievalQA = None
    LANGCHAIN_AVAILABLE = False

class RAGManager:
    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no está instalado. Instala 'langchain' y 'langchain-openai' para habilitar RAG.")

        self.api_key = Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada")

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key, model="text-embedding-3-small")
        self.db = get_db()
        self.knowledge_base_path = "docs/knowledge_base"
    
    def index_documents(self):
        """Indexar documentos de la base de conocimiento"""
        try:
            # Cargar documentos
            loader = DirectoryLoader(
                self.knowledge_base_path,
                glob="**/*.md",
                show_progress=True
            )
            docs = loader.load()
            
            # Dividir documentos en chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = splitter.split_documents(docs)
            
            # Generar embeddings
            for i, doc in enumerate(split_docs):
                try:
                    embedding_vector = self.embeddings.embed_query(doc.page_content)
                    
                    # Guardar en Supabase
                    self.db.table('documents').insert({
                        'content': doc.page_content,
                        'embedding': embedding_vector,
                        'metadata': {
                            'source': doc.metadata.get('source', 'unknown'),
                            'page': i
                        }
                    }).execute()
                    
                    if (i + 1) % 10 == 0:
                        print(f"✓ Indexados {i + 1}/{len(split_docs)} documentos")
                
                except Exception as e:
                    print(f"Error indexando documento {i}: {e}")
                    continue
            
            print(f"✅ Indexación completada: {len(split_docs)} documentos")
            return True
            
        except Exception as e:
            print(f"Error en indexación: {e}")
            return False
    
    def search_relevant_docs(self, query, top_k=3):
        """Búsqueda vectorial de documentos relevantes"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.embeddings.embed_query(query)
            
            # Búsqueda en Supabase con pgvector
            results = self.db.rpc(
                'search_documents',
                {
                    'query_embedding': query_embedding,
                    'similarity_threshold': 0.6,
                    'match_count': top_k
                }
            ).execute()
            
            return results.data if results.data else []
            
        except Exception as e:
            print(f"Error en búsqueda vectorial: {e}")
            return []
    
    def get_context_from_db(self, query):
        """Obtener contexto relevante de la BD directamente"""
        context = ""
        
        try:
            from datetime import datetime, timedelta
            query_lower = query.lower()
            hoy = datetime.now()
            hoy_str = hoy.strftime('%Y-%m-%d')
            en_30_dias = (hoy + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Buscar productos si es una consulta de productos
            if any(word in query_lower for word in ['producto', 'medicamento', 'stock', 'precio', 'vence', 'vencimiento']):
                productos = self.db.table('articulo').select(
                    'nombre, stock, precio_venta, fecha_vencimiento'
                ).eq('estado', 'activo').limit(10).execute()
                
                if productos.data:
                    context += "📦 PRODUCTOS DISPONIBLES:\n"
                    for p in productos.data:
                        venc = p.get('fecha_vencimiento', 'N/A')
                        context += f"- {p['nombre']}: {p['stock']} un., Bs. {p['precio_venta']} (Vence: {venc})\n"
            
            # Alertas Críticas (Stock < 5)
            bajo_stock = self.db.table('articulo').select('nombre, stock').lt('stock', 5).eq('estado', 'activo').execute()
            if bajo_stock.data:
                context += f"\n⚠️ ALERTA STOCK CRÍTICO:\n"
                for p in bajo_stock.data[:3]:
                    context += f"- {p['nombre']}: solo {p['stock']} unidades!\n"

            # Próximos a vencer (30 días)
            proximos_vencer = self.db.table('articulo').select(
                'nombre, fecha_vencimiento'
            ).gte('fecha_vencimiento', hoy_str).lte('fecha_vencimiento', en_30_dias).eq('estado', 'activo').execute()
            
            if proximos_vencer.data:
                context += f"\n🟡 PRÓXIMOS A VENCER (30 días):\n"
                for p in proximos_vencer.data[:3]:
                    context += f"- {p['nombre']}: {p['fecha_vencimiento']}\n"
            
            # Información de ventas si es consulta de ventas
            if any(word in query_lower for word in ['venta', 'vendido', 'total', 'cuanto']):
                ventas = self.db.table('venta').select('total_venta').gte(
                    'fecha_hora', hoy_str
                ).execute()
                
                if ventas.data:
                    total = sum(float(v['total_venta']) for v in ventas.data)
                    context += f"\n💰 VENTAS DE HOY:\n"
                    context += f"- Total: Bs. {total:.2f}\n"
                    context += f"- Transacciones: {len(ventas.data)}\n"
            
        except Exception as e:
            print(f"Error obteniendo contexto de BD en RAG: {e}")
        
        return context
    
    def build_system_prompt(self, query, docs_context="", db_context=""):
        """Construir prompt mejorado con contexto"""
        return f"""Eres un asistente virtual inteligente de "Farmacia Vida Sana". 
Tu rol es ayudar a los trabajadores durante la gestión de la farmacia.

CONTEXTO DE DOCUMENTACIÓN:
{docs_context}

CONTEXTO DE BASE DE DATOS:
{db_context}

INSTRUCCIONES:
1. Responde de forma CONCISA (máximo 4 líneas)
2. Usa emojis para alertas (🔴 vencido, 🟡 próximo a vencer, ⚠️ bajo stock)
3. Basa tu respuesta en el contexto proporcionado
4. Si no tienes información, di "No tengo datos sobre eso"
5. Para datos médicos, recomienda consultar con farmacéutico

Pregunta del usuario: {query}"""


# Función para crear tabla de embeddings en Supabase
def create_embeddings_table():
    """Crear tabla de documentos si no existe
    
    Nota: Esta función requiere ejecutar el SQL directamente en Supabase SQL Editor.
    El SQL está disponible en el código comentado abajo.
    Por ahora, solo verifica que podamos conectar a Supabase.
    """
    db = get_db()
    try:
        # Intenta consultar la tabla; si existe, retorna True
        result = db.table('documents').select('id').limit(1).execute()
        print("✅ Tabla de embeddings ya existe")
        return True
    except Exception as e:
        # La tabla probablemente no existe - necesita ser creada vía SQL directo
        print(f"⚠️ Tabla de embeddings no existe (crear con SQL en Supabase SQL Editor)")
        print("""
        Ejecuta el siguiente SQL en Supabase SQL Editor:
        
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(1536),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS documents_embedding_idx 
        ON documents USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        
        CREATE OR REPLACE FUNCTION search_documents(
            query_embedding vector(1536),
            similarity_threshold float,
            match_count int
        )
        RETURNS TABLE(id int, content text, similarity float, metadata jsonb)
        LANGUAGE sql
        AS $$
        SELECT
            d.id,
            d.content,
            1 - (d.embedding <=> query_embedding) as similarity,
            d.metadata
        FROM documents d
        WHERE 1 - (d.embedding <=> query_embedding) > similarity_threshold
        ORDER BY d.embedding <=> query_embedding
        LIMIT match_count;
        $$;
        """)
        return False


# Instancia global
rag_manager = None

def get_rag_manager():
    """Obtener instancia del RAG manager"""
    global rag_manager
    if rag_manager is None:
        rag_manager = RAGManager()
    return rag_manager
