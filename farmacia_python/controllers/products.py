from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db import get_db

products_bp = Blueprint('products', __name__)

@products_bp.before_request
def require_login_web():
    """Require login solo para rutas web, no para API"""
    if request.path.startswith('/api/'):
        return  # API endpoints no requieren login (pueden usar JWT)
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))

# ============ RUTAS WEB ============

@products_bp.route('/')
def index():
    db = get_db()
    
    # Query with Joins using Supabase (Simulated Join or explicit view)
    # Supabase allows joins if foreign keys are set up.
    # For now, we will fetch raw or use a view if available.
    # Since we are migrating, let's assume simple fetch for now and we might need to handle joins manually or via proper relations.
    # We'll try to fetch basic article info first. 
    try:
        # We need to Select * from articulo. 
        # Ideally we join with categoria and presentacion.
        # select('*, categoria(nombre), presentacion(nombre)')
        response = db['table']('articulo').select('*').order('idarticulo', desc=True).execute()
        articulos = response.data
    except Exception as e:
        print(f"Error fetching products: {e}")
        articulos = []

    return render_template('products/index.html', articulos=articulos)

@products_bp.route('/create', methods=['GET', 'POST'])
def create():
    db = get_db()
    if request.method == 'POST':
        try:
            data = {
                'codigo': request.form.get('codigo'),
                'nombre': request.form.get('nombre'),
                'descripcion': request.form.get('descripcion'),
                'idcategoria': request.form.get('idcategoria'),
                'idpresentacion': request.form.get('idpresentacion'),
                'stock': request.form.get('stock'),
                'precio_venta': request.form.get('precio_venta'),
                'estado': request.form.get('estado', 'activo'),
                'idcategoria': request.form['idcategoria'],
                'idpresentacion': request.form['idpresentacion'],
                'stock': request.form['stock'],
                'precio_venta': request.form['precio_venta'],
                'estado': request.form['estado'],
                'tipo_venta': request.form['tipo_venta']
            }
            db['table']('articulo').insert(data).execute()
            flash('Producto creado correctamente', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            flash(f"Error al crear: {e}", 'danger')

    # Load foreign keys for dropdowns
    categorias = db['table']('categoria').select('*').execute().data
    presentaciones = db['table']('presentacion').select('*').execute().data
    return render_template('products/form.html', categorias=categorias, presentaciones=presentaciones, articulo=None)

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        try:
            data = {
                'codigo': request.form['codigo'],
                'nombre': request.form['nombre'],
                'descripcion': request.form['descripcion'],
                'idcategoria': request.form['idcategoria'],
                'idpresentacion': request.form['idpresentacion'],
                'stock': request.form['stock'],
                'precio_venta': request.form['precio_venta'],
                'estado': request.form['estado'],
                'tipo_venta': request.form['tipo_venta']
            }
            db['table']('articulo').eq('idarticulo', id).update(data).execute()
            flash('Producto actualizado correctamente', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", 'danger')

    # Get article and foreign keys
    try:
        articulo = db['table']('articulo').select('*').eq('idarticulo', id).single().execute().data
        categorias = db['table']('categoria').select('*').execute().data
        presentaciones = db['table']('presentacion').select('*').execute().data
        return render_template('products/form.html', categorias=categorias, presentaciones=presentaciones, articulo=articulo)
    except Exception as e:
        flash(f"Producto no encontrado: {e}", 'danger')
        return redirect(url_for('products.index'))

@products_bp.route('/delete/<int:id>')
def delete(id):
    try:
        db = get_db()
        # Check logic: soft delete usually better, but user asked for delete. 
        # Using soft delete (estado=inactivo) is safer, but let's do real delete for CRUD request unless specified.
        # Actually in PHP code it seemed to be a delete.
        db.table('articulo').delete().eq('idarticulo', id).execute()
        flash('Producto eliminado', 'success')
    except Exception as e:
        flash(f"Error al eliminar: {e}", 'danger')
    return redirect(url_for('products.index'))
