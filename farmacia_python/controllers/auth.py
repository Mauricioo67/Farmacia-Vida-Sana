from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user import User
from models.jwt_auth import create_access_token, create_refresh_token, verify_token, token_required
from werkzeug.security import generate_password_hash
from models.db import get_db

auth_bp = Blueprint('auth', __name__)

# ============ RUTAS WEB (CON SESIONES PARA COMPATIBILIDAD) ============

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')
        
        user = User.login(usuario, clave)
        
        if user:
            session['logueado'] = True
            session['idtrabajador'] = user.id
            session['usuario'] = user.usuario
            session['nombre'] = f"{user.nombre} {user.apellidos}"
            session['rol'] = user.rol
            
            return redirect(url_for('main.dashboard'))
        else:
            flash('Error: El usuario o la contraseña son incorrectos.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = session.get('idtrabajador')
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        nueva_password = request.form.get('password')
        
        update_data = {
            'nombre': nombre,
            'apellidos': apellidos
        }
        
        if nueva_password:
            update_data['password'] = generate_password_hash(nueva_password)
        
        try:
            db['table']('trabajador').eq('idtrabajador', user_id).update(update_data).execute()
            session['nombre'] = f"{nombre} {apellidos}"
            flash('Perfil actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar perfil: {e}', 'danger')
            
    # Obtener datos actuales
    response = db['table']('trabajador').select('*').eq('idtrabajador', user_id).execute()
    usuario = response.data[0] if response.data else None
    
    return render_template('profile.html', usuario=usuario)

@auth_bp.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        usuario_input = request.form.get('usuario')
        try:
            db = get_db()
            response = db['table']('trabajador').select('*').eq('usuario', usuario_input).eq('estado', 'activo').execute()
            if response.data:
                user = response.data[0]
                return render_template('recover.html', step=2, 
                                       usuario_id=user['idtrabajador'], 
                                       usuario_info=f"{user['nombre']} {user['apellidos']} ({user['usuario']})")
            else:
                flash(f"Usuario no encontrado o inactivo: '{usuario_input}'", 'danger')
        except Exception as e:
            flash(f"Error de base de datos: {e}", 'danger')
            
    return render_template('recover.html', step=1)

@auth_bp.route('/recover_password', methods=['POST'])
def recover_password():
    usuario_id = request.form.get('usuario_id')
    nueva_password = request.form.get('nueva_password')
    confirmar_password = request.form.get('confirmar_password')
    
    if not nueva_password or not confirmar_password:
        flash("Complete ambos campos", 'danger')
        return redirect(url_for('auth.recover'))
        
    if nueva_password != confirmar_password:
        flash("Las contraseñas no coinciden", 'danger')
        return redirect(url_for('auth.recover'))
        
    if len(nueva_password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres", 'danger')
        return redirect(url_for('auth.recover'))
        
    try:
        password_hash = generate_password_hash(nueva_password)
        db = get_db()
        db['table']('trabajador').eq('idtrabajador', usuario_id).update({'password': password_hash}).execute()
        
        flash("✅ ¡Contraseña actualizada! Inicie sesión ahora.", 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        flash(f"Error al actualizar: {e}", 'danger')
        return redirect(url_for('auth.recover'))

# ============ API REST CON JWT (PARA REACT FRONTEND) ============

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint para login con JWT"""
    try:
        data = request.get_json()
        # Soportar ambos formatos: (usuario, clave) y (email, password)
        usuario = data.get('usuario') or data.get('email')
        clave = data.get('clave') or data.get('password')
        
        if not usuario or not clave:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        user = User.login(usuario, clave)
        
        if user:
            access_token = create_access_token(user.id, user.usuario, user.rol)
            refresh_token = create_refresh_token(user.id)
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'usuario': user.usuario,
                    'nombre': user.nombre,
                    'apellidos': user.apellidos,
                    'rol': user.rol
                }
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@auth_bp.route('/api/auth/refresh', methods=['POST'])
def api_refresh():
    """Refrescar access token usando refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token requerido'}), 400
        
        payload = verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Refresh token inválido'}), 401
        
        user_id = payload.get('user_id')
        db = get_db()
        user_data = db['table']('trabajador').select('*').eq('idtrabajador', user_id).execute()
        
        if user_data.data:
            user = user_data.data[0]
            new_access_token = create_access_token(user['idtrabajador'], user['usuario'], user['acceso'])
            
            return jsonify({
                'access_token': new_access_token
            }), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@auth_bp.route('/api/auth/validate', methods=['GET'])
@token_required
def api_validate():
    """Validar token JWT actual"""
    return jsonify({
        'valid': True,
        'user': request.user
    }), 200

@auth_bp.route('/api/auth/workers', methods=['GET'])
def api_workers():
    """Listar todos los trabajadores disponibles (para debug)"""
    try:
        db = get_db()
        response = db['table']('trabajador').select('idtrabajador,usuario,nombre,apellidos,acceso,estado').execute()
        workers = response.data if response.data else []
        return jsonify({'workers': workers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API DE RECUPERACIÓN PARA REACT ============

@auth_bp.route('/api/auth/recover/check', methods=['POST'])
def api_recover_check():
    """Verificar si un usuario existe para recuperación"""
    try:
        data = request.get_json()
        usuario_input = data.get('usuario')
        
        if not usuario_input:
            return jsonify({'error': 'Usuario requerido'}), 400
            
        db = get_db()
        response = db['table']('trabajador').select('idtrabajador, nombre, apellidos, usuario').eq('usuario', usuario_input).eq('estado', 'activo').execute()
        
        if response.data:
            user = response.data[0]
            return jsonify({
                'success': True,
                'user': {
                    'id': user['idtrabajador'],
                    'display': f"{user['nombre']} {user['apellidos']} ({user['usuario']})"
                }
            }), 200
        else:
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/recover/update', methods=['POST'])
def api_recover_update():
    """Actualizar contraseña vía API"""
    try:
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        nueva_password = data.get('nueva_password')
        
        if not usuario_id or not nueva_password:
            return jsonify({'error': 'Datos incompletos'}), 400
            
        if len(nueva_password) < 6:
            return jsonify({'error': 'Mínimo 6 caracteres'}), 400
            
        password_hash = generate_password_hash(nueva_password)
        db = get_db()
        db['table']('trabajador').eq('idtrabajador', usuario_id).update({'password': password_hash}).execute()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    """Registrar nuevo trabajador"""
    try:
        data = request.get_json()
        usuario = data.get('usuario')
        nombre = data.get('nombre')
        apellidos = data.get('apellidos')
        clave = data.get('clave')
        
        if not all([usuario, nombre, apellidos, clave]):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        if len(clave) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        # Verificar si usuario ya existe
        db = get_db()
        existing = db['table']('trabajador').select('usuario').eq('usuario', usuario).execute()
        if existing.data:
            return jsonify({'error': 'El usuario ya existe'}), 409
        
        # Hashear contraseña
        password_hash = generate_password_hash(clave)
        
        # Insertar nuevo trabajador
        new_worker = {
            'usuario': usuario,
            'nombre': nombre,
            'apellidos': apellidos,
            'password': password_hash,
            'acceso': 'Usuario',  # Rol por defecto
            'estado': 'activo'
        }
        
        response = db['table']('trabajador').insert(new_worker).execute()
        
        if response.data:
            return jsonify({
                'message': 'Registro exitoso',
                'usuario': usuario
            }), 201
        else:
            return jsonify({'error': 'Error al registrar'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500