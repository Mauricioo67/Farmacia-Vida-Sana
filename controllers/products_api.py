from flask import Blueprint, jsonify, request
from models.db import get_db

# Blueprint para API de productos (sin conflictos de nombres)
products_api_bp = Blueprint('products_api', __name__, url_prefix='/api/products')

@products_api_bp.route('', methods=['GET'])
def get_all():
    """Obtener todos los productos"""
    try:
        db = get_db()
        response = db['table']('articulo').select('*').order('idarticulo', desc=True).execute()
        productos = response.data if response.data else []
        return jsonify({'products': productos}), 200
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@products_api_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    """Obtener producto por ID"""
    try:
        db = get_db()
        response = db['table']('articulo').select('*').eq('idarticulo', id).single().execute()
        producto = response.data
        return jsonify({'product': producto}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_api_bp.route('', methods=['POST'])
def create():
    """Crear nuevo producto"""
    try:
        db = get_db()
        data = request.get_json()
        
        response = db['table']('articulo').insert({
            'codigo': data.get('codigo'),
            'nombre': data.get('nombre'),
            'descripcion': data.get('descripcion'),
            'stock': data.get('stock', 0),
            'precio_venta': data.get('precio_venta', 0),
            'idcategoria': data.get('idcategoria'),
            'idpresentacion': data.get('idpresentacion'),
            'fecha_vencimiento': data.get('fecha_vencimiento'),
            'estado': 'activo'
        }).execute()
        
        return jsonify({'message': 'Producto creado', 'data': response.data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_api_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    """Actualizar producto"""
    try:
        db = get_db()
        data = request.get_json()
        
        update_data = {}
        if 'nombre' in data:
            update_data['nombre'] = data['nombre']
        if 'descripcion' in data:
            update_data['descripcion'] = data['descripcion']
        if 'stock' in data:
            update_data['stock'] = data['stock']
        if 'precio_venta' in data:
            update_data['precio_venta'] = data['precio_venta']
        
        response = db['table']('articulo').eq('idarticulo', id).update(update_data).execute()
        
        return jsonify({'message': 'Producto actualizado', 'data': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_api_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    """Eliminar producto"""
    try:
        db = get_db()
        response = db['table']('articulo').eq('idarticulo', id).delete().execute()
        return jsonify({'message': 'Producto eliminado', 'data': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
