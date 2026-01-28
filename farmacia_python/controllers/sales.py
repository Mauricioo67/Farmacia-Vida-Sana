from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
from models.db import get_db
import json
from datetime import datetime
from models.jwt_auth import token_required
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from flask import make_response

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.before_request
def require_login():
    if not session.get('logueado'):
        return redirect(url_for('auth.login'))

@sales_bp.route('/')
def index():
    db = get_db()
    try:
        # Fetch sales with related info
        # Note: Supabase-py join syntax can be tricky. 
        # For simplicity, we fetch sales and then maybe enrich or just show basic info.
        # Ideally: .select('*, cliente(nombre, apellidos), trabajador(nombre)')
        response = db['table']('venta').select('*, cliente(nombre, apellidos), trabajador(usuario)').order('idventa', desc=True).execute()
        ventas = response.data
    except Exception as e:
        print(f"Error serving sales: {e}")
        ventas = []
    return render_template('sales/index.html', ventas=ventas)

@sales_bp.route('/create', methods=['GET'])
def create():
    db = get_db()
    # Get products for the search/dropdown
    productos = db['table']('articulo').select('*').eq('estado', 'activo').gt('stock', 0).execute().data
    clientes = db['table']('cliente').select('*').execute().data

    # Detectar el QR dinámicamente
    qr_filename = 'qr_pago.png' # Default
    static_img_path = os.path.join('static', 'img')
    for ext in ['.png', '.jpg', '.jpeg']:
        if os.path.exists(os.path.join(static_img_path, f'qr_pago{ext}')):
            qr_filename = f'qr_pago{ext}'
            break
            
    return render_template('sales/create.html', productos=productos, clientes=clientes, qr_filename=qr_filename)

@sales_bp.route('/store', methods=['POST'])
def store():
    try:
        data = request.get_json()
        idcliente = data.get('idcliente')
        items = data.get('items')
        
        if not items:
            return jsonify({'success': False, 'message': 'No hay items en la venta'})

        db = get_db()
        total_venta = sum(float(item['subtotal']) for item in items)
        
        # 1. Create Sale
        venta_data = {
            'idcliente': idcliente,
            'idtrabajador': session.get('idtrabajador'),
            'total_venta': total_venta,
            'estado': 'completada'
        }
        res_venta = db['table']('venta').insert(venta_data).execute()
        if not res_venta.data:
            raise Exception("No se pudo registrar la venta")
            
        idventa = res_venta.data[0]['idventa']
        
        # 2. Create Details and Update Stock
        for item in items:
            detalle_data = {
                'idventa': idventa,
                'idarticulo': item['idarticulo'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio'],
                'subtotal': item['subtotal']
            }
            db['table']('detalle_venta').insert(detalle_data).execute()
            
            # Decrease Stock
            # Note: Concurrency might be an issue here in prod, but for this migration let's do read-modify-write or rpc if available.
            # Simple approach: rpc or direct update. Let's do direct update for now.
            curr_prod = db['table']('articulo').select('stock').eq('idarticulo', item['idarticulo']).single().execute()
            new_stock = curr_prod.data['stock'] - int(item['cantidad'])
            db['table']('articulo').update({'stock': new_stock}).eq('idarticulo', item['idarticulo']).execute()
            
        return jsonify({'success': True, 'message': 'Venta registrada correctamente', 'redirect': url_for('sales.index')})
        
    except Exception as e:
        print(f"Error processing sale: {e}")
        return jsonify({'success': False, 'message': str(e)})

@sales_bp.route('/api/store', methods=['POST'])
@token_required
def api_store(current_user):
    try:
        data = request.get_json()
        idcliente = data.get('idcliente')
        items = data.get('items')
        
        if not items:
            return jsonify({'success': False, 'message': 'No hay items en la venta'}), 400

        db = get_db()
        total_venta = sum(float(item['subtotal']) for item in items)
        
        # 1. Create Sale
        venta_data = {
            'idcliente': idcliente,
            'idtrabajador': current_user['idtrabajador'],
            'total_venta': total_venta,
            'estado': 'completada'
        }
        res_venta = db['table']('venta').insert(venta_data).execute()
        if not res_venta.data:
            raise Exception("No se pudo registrar la venta")
            
        idventa = res_venta.data[0]['idventa']
        
        # 2. Create Details and Update Stock
        for item in items:
            detalle_data = {
                'idventa': idventa,
                'idarticulo': item['idarticulo'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio'],
                'subtotal': item['subtotal']
            }
            db['table']('detalle_venta').insert(detalle_data).execute()
            
            # Decrease Stock
            curr_prod = db['table']('articulo').select('stock').eq('idarticulo', item['idarticulo']).single().execute()
            if curr_prod.data:
                new_stock = curr_prod.data['stock'] - int(item['cantidad'])
                db['table']('articulo').update({'stock': new_stock}).eq('idarticulo', item['idarticulo']).execute()
            
        return jsonify({
            'success': True, 
            'message': 'Venta registrada correctamente', 
            'idventa': idventa
        }), 201
        
    except Exception as e:
        print(f"Error processing sales API: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@sales_bp.route('/invoice_pdf/<int:id>')
def invoice_pdf(id):
    db = get_db()
    
    try:
        venta = db['table']('venta').select('*, cliente(nombre, apellidos, telefono), trabajador(usuario)').eq('idventa', id).single().execute().data
        detalles = db['table']('detalle_venta').select('*, articulo(nombre, codigo)').eq('idventa', id).execute().data
    except Exception as e:
        flash(f"Error al obtener venta: {e}", "danger")
        return redirect(url_for('sales.index'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    # Estilos Personalizados
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=2)
    sub_header = ParagraphStyle('SubHeader', parent=styles['Normal'], fontSize=9, alignment=1, spaceAfter=1)
    
    # 1. ENCABEZADO REALISTA
    elements.append(Paragraph("FARMACIA VIDA SANA", header_style))
    elements.append(Paragraph("Av. Principal #123, Zona Central", sub_header))
    elements.append(Paragraph("Tel: (555) 123-4567 | NIT: 849302019", sub_header))
    elements.append(Paragraph("Santa Cruz - Bolivia", sub_header))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"RECIBO DE VENTA #{str(venta['idventa']).zfill(6)}", styles['Heading2']))
    elements.append(Paragraph(f"Fecha de Emisión: {venta['fecha_hora'][:16]}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # 2. DATOS DEL CLIENTE
    cliente_nombre = f"{venta['cliente']['nombre']} {venta['cliente']['apellidos']}"
    cliente_tel = venta['cliente'].get('telefono', 'S/T')
    
    # Usamos una tabla invisible para alinear datos del cliente
    info_data = [
        [f"Cliente: {cliente_nombre}", f"Vendedor: {venta['trabajador']['usuario']}"],
        [f"Teléfono: {cliente_tel}", "Condición: Contado"]
    ]
    info_table = Table(info_data, colWidths=[300, 200])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # 3. DETALLE DE PRODUCTOS
    data = [['CANT', 'CÓDIGO', 'DESCRIPCIÓN', 'P.UNIT (Bs.)', 'SUBTOTAL (Bs.)']]
    for d in detalles:
        data.append([
            str(d['cantidad']),
            d['articulo']['codigo'],
            d['articulo']['nombre'][:35], # Truncar nombre largo
            f"{d['precio_unitario']:.2f}",
            f"{d['subtotal']:.2f}"
        ])
    
    # Totales
    data.append(['', '', '', 'TOTAL Bs.:', f"{venta['total_venta']:.2f}"])

    col_widths = [40, 70, 250, 80, 80]
    table = Table(data, colWidths=col_widths)
    
    # Estilo profesional de tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        # Cuerpo
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'), # Centrar todo por defecto
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Izquierda descripcion
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'), # Derecha precios
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        # Fila Total
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (-2, -1), (-2, -1), 'RIGHT'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 40))

    # 4. PIE DE PÁGINA / DISCLAIMER
    elements.append(Paragraph("GRACIAS POR SU PREFERENCIA", ParagraphStyle('FooterCenter', parent=styles['Normal'], alignment=1)))
    elements.append(Spacer(1, 5))
    disclaimer = "Nota: No se aceptan cambios ni devoluciones pasadas las 24 horas. Medicamentos refrigerados no tienen devolución."
    elements.append(Paragraph(disclaimer, ParagraphStyle('Disclaimer', parent=styles['Italic'], fontSize=8, alignment=1)))

    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=recibo_farmacia_{id}.pdf'
    return response

@sales_bp.route('/invoice/<int:id>')
def invoice(id):
    # Logic to show invoice/ticket
    db = get_db()
    venta = db['table']('venta').select('*, cliente(*), trabajador(*)').eq('idventa', id).single().execute().data
    detalles = db['table']('detalle_venta').select('*, articulo(nombre, codigo)').eq('idventa', id).execute().data
    return render_template('sales/invoice.html', venta=venta, detalles=detalles)
