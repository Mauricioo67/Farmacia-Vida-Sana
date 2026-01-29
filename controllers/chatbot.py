from flask import Blueprint, request, jsonify, session
from models.db import get_db
from models.rag import get_rag_manager
from models.jwt_auth import token_required
import os
from groq import Groq
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

def get_groq_client():
    """Inicializar cliente Groq"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)

@chatbot_bp.before_request
def require_login():
    """Verificar autenticación para rutas web del chatbot"""
    # Si la ruta empieza con /api/, delegamos la seguridad a los decoradores @token_required
    if not request.path.startswith('/chatbot/api/') and not session.get('logueado'):
        return jsonify({'error': 'No autorizado. Inicie sesión.'}), 401

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Endpoint de chat mejorado con RAG"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        db = get_db()
        
        # ============ CONTEXTO RAG ============
        
        # 1. Obtener documentación relevante (búsqueda vectorial)
        docs_context = ""
        try:
            rag = get_rag_manager()
            relevant_docs = rag.search_relevant_docs(user_message, top_k=2)
            
            if relevant_docs:
                docs_context = "\n📚 DOCUMENTACIÓN RELEVANTE:\n"
                for doc in relevant_docs:
                    content = doc.get('content', '')[:500]  # Limitar a 500 chars
                    docs_context += f"- {content}...\n"
        except Exception as e:
            print(f"Error en búsqueda RAG: {e}")
            # Continuar sin búsqueda vectorial si hay error
        
        # 2. Obtener contexto de BD (búsqueda tradicional)
        db_context = get_database_context(user_message, db)
        
        # ============ CONSTRUCCIÓN DE PROMPT ============
        
        system_prompt = f"""Eres un asistente virtual inteligente de "Farmacia Vida Sana". 
Tu rol principal es ayudar a los trabajadores/vendedores en la gestión de la farmacia.

CAPACIDADES:
1. Búsqueda de productos, stock, precios y fechas de vencimiento
2. Consultas de clientes y historial
3. Información de ventas en tiempo real
4. Alertas de productos vencidos o con bajo stock
5. Orientación sobre el sistema

CONTEXTO DE DOCUMENTACIÓN DISPONIBLE:
{docs_context}

CONTEXTO DE BASE DE DATOS ACTUAL:
{db_context}

INSTRUCCIONES DE RESPUESTA:
- Responde de forma CONCISA (máximo 4 líneas)
- Usa emojis para alertas:
  🔴 = Producto vencido
  🟡 = Vence en menos de 30 días
  ⚠️ = Stock bajo (< 10 unidades)
- Basa respuestas en contexto proporcionado
- Para datos médicos, recomienda consultar farmacéutico
- Sé amable y profesional"""
        
        # ============ HISTORIAL DE CONVERSACIÓN ============
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Agregar historial (últimos 6 mensajes)
        for msg in conversation_history[-6:]:
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        # Mensaje actual
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # ============ LLAMADA A GROQ ============
        
        client = get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=400
        )
        
        ai_response = chat_completion.choices[0].message.content
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'has_rag': len(docs_context) > 0
        })
        
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return jsonify({
            'success': False,
            'error': 'Error procesando el mensaje. Intenta de nuevo.'
        }), 500


def get_database_context(query, db):
    """Extraer contexto relevante de la BD basado en la consulta"""
    context = "INFORMACIÓN DISPONIBLE EN BD:"
    query_lower = query.lower()
    
    try:
        # ===== CONTEXTO DE PRODUCTOS =====
        if any(word in query_lower for word in ['producto', 'medicamento', 'stock', 'precio', 'vence', 'vencimiento']):
            try:
                productos = db.table('articulo').select(
                    'nombre, stock, precio_venta, fecha_vencimiento'
                ).eq('estado', 'activo').order('fecha_vencimiento').limit(10).execute().data
                
                if productos:
                    context += "\n📦 PRODUCTOS ACTIVOS:\n"
                    for p in productos[:5]:
                        stock_alert = "⚠️" if p['stock'] < 10 else "✓"
                        venc = p.get('fecha_vencimiento', 'N/A')
                        context += f"  {stock_alert} {p['nombre']}: {p['stock']} unidades @ Bs.{p['precio_venta']}\n"
            except Exception as e:
                print(f"Error en contexto productos: {e}")
        
        # ===== CONTEXTO DE VENTAS =====
        if any(word in query_lower for word in ['venta', 'vendido', 'cuanto', 'total', 'resumen']):
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                ventas = db.table('venta').select('total_venta').gte(
                    'fecha_hora', today
                ).execute().data
                
                if ventas:
                    total = sum(float(v['total_venta']) for v in ventas if v['total_venta'])
                    context += f"\n💰 VENTAS DE HOY:\n  Total: Bs.{total:.2f} ({len(ventas)} transacciones)\n"
                else:
                    context += "\n💰 Sin ventas hoy aún\n"
            except Exception as e:
                print(f"Error en contexto ventas: {e}")

        # ===== CONTEXTO DE CATEGORIAS =====
        if any(word in query_lower for word in ['categoria', 'categoría', 'tipo', 'clases', 'grupos']):
            try:
                cats = db.table('categoria').select('nombre, descripcion').limit(10).execute().data
                if cats:
                    context += "\n🗂️ CATEGORÍAS DISPONIBLES:\n"
                    for c in cats:
                        context += f"  - {c['nombre']}: {c.get('descripcion', '')}\n"
            except Exception as e:
                print(f"Error en contexto categorias: {e}")
        
        # ===== ALERTAS CRÍTICAS =====
        try:
            hoy = datetime.now().strftime('%Y-%m-%d')
            vencidos = db.table('articulo').select(
                'nombre'
            ).lt('fecha_vencimiento', hoy).eq('estado', 'activo').execute().data
            
            if vencidos:
                context += f"\n🔴 PRODUCTOS VENCIDOS ({len(vencidos)}):\n"
                for v in vencidos[:3]:
                    context += f"  - {v['nombre']}\n"
        except Exception as e:
            print(f"Error en alertas: {e}")
        
    except Exception as e:
        print(f"Error general en contexto BD: {e}")
    
    return context


@chatbot_bp.route('/index', methods=['POST'])
def index_documents():
    """Indexar documentos de conocimiento (admin only)"""
    try:
        # Verificar autenticación (aquí normalmente verificarías role=admin)
        if not session.get('logueado'):
            return jsonify({'error': 'No autorizado'}), 401
        
        rag = get_rag_manager()
        success = rag.index_documents()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Documentos indexados exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error indexando documentos'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/api/chat', methods=['POST'])
@token_required
def api_chat():
    """Endpoint API REST con JWT (para React frontend)"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        db = get_db()
        
        # Mismo flujo que el chat normal
        docs_context = ""
        try:
            rag = get_rag_manager()
            relevant_docs = rag.search_relevant_docs(user_message, top_k=2)
            
            if relevant_docs:
                docs_context = "📚 DOCUMENTACIÓN:\n"
                for doc in relevant_docs:
                    content = doc.get('content', '')[:300]
                    docs_context += f"- {content}...\n"
        except Exception as e:
            print(f"RAG error: {e}")
        
        db_context = get_database_context(user_message, db)
        
        system_prompt = f"""Eres un asistente IA para Farmacia Vida Sana.
Documentación: {docs_context}
BD: {db_context}"""
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-6:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        client = get_groq_client()
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=400
        )
        
        return jsonify({
            'success': True,
            'response': response.choices[0].message.content
        })
        
    except Exception as e:
        print(f"API Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@chatbot_bp.route('/n8n-chat', methods=['POST'])
def n8n_chat():
    """Proxy para enviar mensajes al workflow de n8n"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        # URL del Webhook de n8n (configurada en .env)
        n8n_url = os.getenv('N8N_WEBHOOK_URL')
        
        print(f"🔹 Enviando a n8n ({n8n_url}): {message}")
        
        if not n8n_url:
            print("❌ Error: N8N_WEBHOOK_URL falta")
            return jsonify({'error': 'N8N_WEBHOOK_URL no configurada'}), 500
            
        import requests
        # Enviar al webhook de n8n
        response = requests.post(n8n_url, json={'chatInput': message})
        
        print(f"🔹 Status n8n: {response.status_code}")
        print(f"🔹 Respuesta n8n raw: {response.text}")
        
        if response.status_code == 200:
            try:
                return jsonify(response.json())
            except Exception as json_err:
                print(f"❌ Error parseando JSON de n8n: {json_err}")
                # Fallback si n8n devuelve texto plano
                return jsonify({'response': response.text})
        else:
            return jsonify({'error': 'Error en n8n', 'details': response.text}), response.status_code
            
    except Exception as e:
        print(f"Error Proxy n8n: {e}")
        return jsonify({'error': str(e)}), 500

