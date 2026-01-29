from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import get_db

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.before_request
def require_login():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))

@categories_bp.route('/')
def index():
    db = get_db()
    try:
        response = db.table('categoria').select('*').order('idcategoria', desc=True).execute()
        categorias = response.data
    except Exception as e:
        print(f"Error fetching categories: {e}")
        categorias = []
    return render_template('categories/index.html', categorias=categorias)

@categories_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        
        try:
            db = get_db()
            db.table('categoria').insert({
                'nombre': nombre,
                'descripcion': descripcion,
                'condicion': 1
            }).execute()
            flash('Categoría creada correctamente', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            flash(f'Error al crear categoría: {e}', 'danger')
            
    return render_template('categories/form.html')

@categories_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        
        try:
            db.table('categoria').update({
                'nombre': nombre,
                'descripcion': descripcion
            }).eq('idcategoria', id).execute()
            flash('Categoría actualizada correctamente', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            flash(f'Error al actualizar: {e}', 'danger')
            
    # GET
    try:
        categoria = db.table('categoria').select('*').eq('idcategoria', id).single().execute().data
    except:
        flash('Categoría no encontrada', 'danger')
        return redirect(url_for('categories.index'))
        
    return render_template('categories/form.html', categoria=categoria)

@categories_bp.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    try:
        # Check dependencies first (optional but recommended)
        # For now, simplistic delete
        db.table('categoria').delete().eq('idcategoria', id).execute()
        flash('Categoría eliminada', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'danger')
    return redirect(url_for('categories.index'))
