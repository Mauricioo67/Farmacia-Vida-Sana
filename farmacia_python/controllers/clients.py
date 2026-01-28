from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import get_db

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.before_request
def require_login():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))

@clients_bp.route('/')
def index():
    db = get_db()
    try:
        response = db.table('cliente').select('*').order('idcliente', desc=True).execute()
        clientes = response.data
    except Exception as e:
        print(f"Error fetching clients: {e}")
        clientes = []
    return render_template('clients/index.html', clientes=clientes)

@clients_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.form['nombre'],
                'apellidos': request.form['apellidos'],
                'telefono': request.form['telefono'],
                'email': request.form['email']
            }
            db = get_db()
            db.table('cliente').insert(data).execute()
            flash('Cliente registrado correctamente', 'success')
            return redirect(url_for('clients.index'))
        except Exception as e:
            flash(f"Error al crear: {e}", 'danger')
            
    return render_template('clients/form.html', cliente=None)

@clients_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.form['nombre'],
                'apellidos': request.form['apellidos'],
                'telefono': request.form['telefono'],
                'email': request.form['email']
            }
            db.table('cliente').update(data).eq('idcliente', id).execute()
            flash('Cliente actualizado correctamente', 'success')
            return redirect(url_for('clients.index'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", 'danger')

    try:
        cliente = db.table('cliente').select('*').eq('idcliente', id).single().execute().data
        return render_template('clients/form.html', cliente=cliente)
    except Exception as e:
        flash(f"Cliente no encontrado", 'danger')
        return redirect(url_for('clients.index'))

@clients_bp.route('/delete/<int:id>')
def delete(id):
    try:
        db = get_db()
        db.table('cliente').delete().eq('idcliente', id).execute()
        flash('Cliente eliminado', 'success')
    except Exception as e:
        flash(f"Error al eliminar: {e}", 'danger')
    return redirect(url_for('clients.index'))
