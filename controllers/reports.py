from flask import Blueprint, render_template, request, redirect, url_for, session
from models.db import get_db
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.before_request
def require_login():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))

@reports_bp.route('/')
def index():
    """Main reports dashboard"""
    return render_template('reports/index.html')

@reports_bp.route('/sales')
def sales():
    """Sales report with date range filter"""
    db = get_db()
    
    # Get date range from query params, default to last 30 days
    date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
    date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    try:
        # Fetch sales within date range
        response = db['table']('venta').select(
            '*, cliente(nombre, apellidos), trabajador(usuario)'
        ).gte('fecha_hora', f'{date_from} 00:00:00').lte('fecha_hora', f'{date_to} 23:59:59').order('fecha_hora', desc=True).execute()
        
        ventas = response.data
        
        # Calculate totals
        total_ventas = len(ventas)
        total_monto = sum(float(v['total_venta']) for v in ventas)
        
    except Exception as e:
        print(f"Error fetching sales report: {e}")
        ventas = []
        total_ventas = 0
        total_monto = 0
    
    return render_template('reports/sales.html', 
                         ventas=ventas, 
                         date_from=date_from, 
                         date_to=date_to,
                         total_ventas=total_ventas,
                         total_monto=total_monto)

@reports_bp.route('/inventory')
def inventory():
    """Inventory report showing current stock levels"""
    db = get_db()
    
    try:
        # Fetch all products with category info
        response = db['table']('articulo').select(
            '*, categoria(nombre)'
        ).order('nombre').execute()
        
        productos = response.data
        
        # Calculate statistics
        total_productos = len(productos)
        productos_bajo_stock = sum(1 for p in productos if p['stock'] < 10)
        productos_sin_stock = sum(1 for p in productos if p['stock'] == 0)
        
    except Exception as e:
        print(f"Error fetching inventory report: {e}")
        productos = []
        total_productos = 0
        productos_bajo_stock = 0
        productos_sin_stock = 0
    
    return render_template('reports/inventory.html',
                         productos=productos,
                         total_productos=total_productos,
                         productos_bajo_stock=productos_bajo_stock,
                         productos_sin_stock=productos_sin_stock)
