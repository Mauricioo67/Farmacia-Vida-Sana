import os
import json
import requests
from config import Config

url: str = Config.SUPABASE_URL
key: str = Config.SUPABASE_KEY

class SupabaseClient:
    """Cliente simulado de Supabase para mantener compatibilidad"""
    def __init__(self, url, key):
        self.url = url
        self.key = key
    
    def table(self, name):
        return SupabaseTable(self.url, self.key, name)
    
    def rpc(self, name, params=None):
        """Atajo para RPC directamente desde el cliente"""
        return SupabaseTable(self.url, self.key, "").rpc(name, params)

    # Permitir acceso como diccionario para compatibilidad hacia atrás
    def __getitem__(self, key):
        if key == 'url': return self.url
        if key == 'key': return self.key
        if key == 'table': return self.table
        raise KeyError(key)

def get_db():
    """Obtener cliente Supabase"""
    if not url or not key:
        raise Exception("Supabase credentials not configured in .env file")
    return SupabaseClient(url, key)

class SupabaseTable:
    """Wrapper para hacer queries a Supabase via REST API"""
    def __init__(self, url, key, table_name):
        self.url = url
        self.key = key
        self.table_name = table_name
        self.select_cols = '*'
        self.filters = {}
        self.order_col = None
        self.order_desc = False
        self.limit_n = None
        self.single_row = False
        self.insert_data = None
        self.update_data = None
        self.delete_flag = False
        
    def select(self, *cols):
        if cols:
            self.select_cols = ','.join(cols)
        return self
    
    def eq(self, col, val):
        self.filters[col] = ('eq', val)
        return self
    
    def gte(self, col, val):
        self.filters[col] = ('gte', val)
        return self
    
    def lte(self, col, val):
        self.filters[col] = ('lte', val)
        return self
    
    def lt(self, col, val):
        self.filters[col] = ('lt', val)
        return self
    
    def gt(self, col, val):
        self.filters[col] = ('gt', val)
        return self
    
    def neq(self, col, val):
        self.filters[col] = ('neq', val)
        return self
    
    def order(self, col, desc=False):
        self.order_col = col
        self.order_desc = desc
        return self
    
    def limit(self, n):
        self.limit_n = n
        return self
    
    def single(self):
        self.single_row = True
        return self
    
    def insert(self, data):
        self.insert_data = data
        return self
    
    def update(self, data):
        self.update_data = data
        return self
    
    def delete(self):
        self.delete_flag = True
        return self
    
    def _build_query_string(self):
        """Construir query string para GET"""
        query_params = f'select={self.select_cols}'
        for col, (op, val) in self.filters.items():
            query_params += f'&{col}={op}.{val}'
        
        if self.order_col:
            order = 'desc' if self.order_desc else 'asc'
            query_params += f'&order={self.order_col}.{order}'
        
        if self.limit_n:
            query_params += f'&limit={self.limit_n}'
        
        return query_params
    
    def rpc(self, fn_name, params=None):
        """Ejecutar una función RPC en Supabase"""
        self.rpc_name = fn_name
        self.rpc_params = params or {}
        return self

    def execute(self):
        """Ejecutar operación (SELECT, INSERT, UPDATE, DELETE, RPC)"""
        headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'  # Forzar retorno de datos en INSERT/UPDATE/DELETE
        }
        
        try:
            # RPC (No suele necesitar Prefer)
            if hasattr(self, 'rpc_name') and self.rpc_name:
                response = requests.post(
                    f'{self.url}/rest/v1/rpc/{self.rpc_name}',
                    json=self.rpc_params,
                    headers={k:v for k,v in headers.items() if k != 'Prefer'},
                    timeout=10
                )
                response.raise_for_status()
                return SupabaseResponse(response.json())

            # INSERT
            if self.insert_data:
                response = requests.post(
                    f'{self.url}/rest/v1/{self.table_name}',
                    json=self.insert_data,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                return SupabaseResponse(data if isinstance(data, list) else [data])
            
            # DELETE
            elif self.delete_flag:
                query_params = self._build_query_string()
                response = requests.delete(
                    f'{self.url}/rest/v1/{self.table_name}?{query_params}',
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return SupabaseResponse(response.json())
            
            # UPDATE
            elif self.update_data:
                query_params = self._build_query_string()
                response = requests.patch(
                    f'{self.url}/rest/v1/{self.table_name}?{query_params}',
                    json=self.update_data,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return SupabaseResponse(response.json())
            
            # SELECT (default)
            else:
                query_params = self._build_query_string()
                response = requests.get(
                    f'{self.url}/rest/v1/{self.table_name}?{query_params}',
                    headers={k:v for k,v in headers.items() if k != 'Prefer'},
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                if isinstance(data, list):
                    if self.single_row:
                        return SupabaseResponse(data[0] if data else None)
                    return SupabaseResponse(data)
                return SupabaseResponse(data)
                
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error from Supabase: {e.response.status_code} - {e.response.text}")
            return SupabaseResponse([] if not self.insert_data and not self.update_data else None)
        except Exception as e:
            print(f"Error executing query on {self.table_name if hasattr(self, 'table_name') else 'RPC'}: {e}")
            return SupabaseResponse([] if not self.insert_data and not self.update_data else None)

class SupabaseResponse:
    """Response wrapper"""
    def __init__(self, data):
        self.data = data

def execute_sql(sql: str):
    """Ejecutar SQL usando RPC en Supabase (requiere función 'exec_sql' definida en Supabase)"""
    db = get_db()
    try:
        headers = {
            'apikey': db['key'],
            'Authorization': f'Bearer {db['key']}',
            'Content-Type': 'application/json'
        }
        response = requests.post(
            f"{db['url']}/rest/v1/rpc/exec_sql",
            json={'sql_query': sql},
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error in execute_sql: {e}")
        return False
