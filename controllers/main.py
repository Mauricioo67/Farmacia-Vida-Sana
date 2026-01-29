from flask import Blueprint, render_template, session, redirect, url_for, request
from models.db import get_db
from datetime import date, datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.before_request
def require_login():
    if request.endpoint != 'auth.login' and not session.get('logueado'):
        return redirect(url_for('auth.login'))

@main_bp.route('/')
def dashboard():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))
        
    db = get_db()
    
    # Fetch stats
    try:
        # Productos
        res_prod = db['table']('articulo').select('*').execute()
        count_prod = len(res_prod.data) if res_prod.data else 0
        
        # Clientes
        res_client = db['table']('cliente').select('*').execute()
        count_client = len(res_client.data) if res_client.data else 0
        
        # Ventas Hoy (Cantidad y Monto)
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        res_sales = db['table']('venta').select('total_venta').gte('fecha_hora', today).execute()
        sales_today_data = res_sales.data if res_sales.data else []
        count_sales = len(sales_today_data)
        total_sales_today = sum(float(v['total_venta']) for v in sales_today_data if v['total_venta'])
        
        # Stock Bajo
        res_stock = db['table']('articulo').select('*').lte('stock', 10).execute()
        count_stock = len(res_stock.data) if res_stock.data else 0
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        count_prod = 0
        count_client = 0
        count_sales = 0
        count_stock = 0

    stats = [
        {
            'icon': 'bi-box-seam',
            'title': 'Productos',
            'value': count_prod,
            'gradient': 'linear-gradient(135deg, #4FD1C5 0%, #38B2AC 100%)'
        },
        {
            'icon': 'bi-people',
            'title': 'Clientes',
            'value': count_client,
            'gradient': 'linear-gradient(135deg, #4299E1 0%, #3182CE 100%)'
        },
        {
            'icon': 'bi-cart-check',
            'title': 'Ventas Hoy',
            'value': f"Bs. {total_sales_today:.2f}",
            'gradient': 'linear-gradient(135deg, #9F7AEA 0%, #805AD5 100%)'
        },
        {
            'icon': 'bi-exclamation-triangle',
            'title': 'Stock Bajo',
            'value': count_stock,
            'gradient': 'linear-gradient(135deg, #F56565 0%, #E53E3E 100%)'
        }
    ]

    # Datos para el gráfico (Últimos 7 días) - OPTIMIZADO: Una sola query
    try:
        from datetime import datetime, timedelta
        chart_labels = []
        chart_values = []
        
        # Fecha de inicio (hace 6 días)
        start_date = (datetime.now() - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        # Obtener todas las ventas de la semana en una sola llamada
        res_week = db.table('venta').select('total_venta, fecha_hora').gte('fecha_hora', start_date_str).execute()
        all_sales = res_week.data if res_week.data else []
        
        # Procesar datos por día
        for i in range(6, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            day_name = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'][day.weekday()]
            
            # Filtrar ventas de este día específico en memoria
            total_day = sum(
                float(v['total_venta']) 
                for v in all_sales 
                if v['fecha_hora'].startswith(day_str) and v.get('total_venta') is not None
            )
            
            chart_labels.append(day_name)
            chart_values.append(total_day)
    except Exception as e:
        print(f"Error calculando gráfico optimizado: {e}")
        chart_labels = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        chart_values = [0, 0, 0, 0, 0, 0, 0]
    
    return render_template('index.html', stats=stats, chart_labels=chart_labels, chart_values=chart_values)
