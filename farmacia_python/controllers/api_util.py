from flask import Blueprint, jsonify
from models.db import get_db

api_util_bp = Blueprint('api_util', __name__, url_prefix='/api/util')

@api_util_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        db = get_db()
        response = db['table']('categoria').select('*').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_util_bp.route('/presentations', methods=['GET'])
def get_presentations():
    try:
        db = get_db()
        response = db['table']('presentacion').select('*').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_util_bp.route('/clients', methods=['GET'])
def get_clients():
    try:
        db = get_db()
        response = db['table']('cliente').select('*').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
