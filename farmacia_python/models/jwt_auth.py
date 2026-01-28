import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config

def create_access_token(user_id, usuario, rol):
    """Crear token JWT de acceso"""
    payload = {
        'user_id': user_id,
        'usuario': usuario,
        'rol': rol,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        'type': 'access'
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def create_refresh_token(user_id):
    """Crear token JWT de refresco"""
    payload = {
        'user_id': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + Config.JWT_REFRESH_TOKEN_EXPIRES,
        'type': 'refresh'
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def verify_token(token):
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para proteger rutas que requieren JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar si token viene en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token expirado o inválido'}), 401
        
        # Pasar información del usuario a la función
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para proteger rutas que requieren rol admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token expirado o inválido'}), 401
        
        if payload.get('rol') != 'administrador':
            return jsonify({'error': 'Acceso denegado: se requiere rol administrador'}), 403
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated
