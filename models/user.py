from models.db import get_db
from werkzeug.security import check_password_hash

class User:
    def __init__(self, id, usuario, nombre, apellidos, rol, estado):
        self.id = id
        self.usuario = usuario
        self.nombre = nombre
        self.apellidos = apellidos
        self.rol = rol
        self.estado = estado

    @staticmethod
    def login(usuario, password):
        try:
            supabase = get_db()
            response = supabase['table']('trabajador').select('*').eq('usuario', usuario).eq('estado', 'activo').limit(1).execute()
            
            if response.data:
                user_data = response.data[0]
                # In a real scenario with PHP migration, we need to ensure the hash algorithm matches.
                # PHP password_hash uses bcrypt ($2y$). Werkzeug handles this.
                if check_password_hash(user_data['password'], password):
                    return User(
                        id=user_data['idtrabajador'],
                        usuario=user_data['usuario'],
                        nombre=user_data['nombre'],
                        apellidos=user_data['apellidos'],
                        rol=user_data['acceso'],
                        estado=user_data['estado']
                    )
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
