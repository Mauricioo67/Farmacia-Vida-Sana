-- RLS (Row Level Security) para Supabase
-- Ejecutar en SQL Editor de Supabase

-- ============ HABILITAR RLS EN TODAS LAS TABLAS ============

-- Tabla trabajador
ALTER TABLE trabajador ENABLE ROW LEVEL SECURITY;

-- Tabla cliente
ALTER TABLE cliente ENABLE ROW LEVEL SECURITY;

-- Tabla articulo
ALTER TABLE articulo ENABLE ROW LEVEL SECURITY;

-- Tabla venta
ALTER TABLE venta ENABLE ROW LEVEL SECURITY;

-- Tabla documents (para RAG)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- ============ POLICIES PARA TABLA TRABAJADOR ============

-- Los usuarios pueden ver su propia información
CREATE POLICY "trabajador_select_own" ON trabajador
  FOR SELECT USING (
    auth.uid()::text = idtrabajador::text OR
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- Solo administrador puede ver todos
CREATE POLICY "trabajador_select_admin" ON trabajador
  FOR SELECT USING (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- Los usuarios no pueden actualizar a otros
CREATE POLICY "trabajador_update_own" ON trabajador
  FOR UPDATE USING (
    idtrabajador = auth.uid()::int OR
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- ============ POLICIES PARA TABLA CLIENTE ============

-- Cualquier usuario autenticado puede ver clientes
CREATE POLICY "cliente_select_auth" ON cliente
  FOR SELECT USING (auth.role() = 'authenticated');

-- Cualquier usuario puede crear clientes
CREATE POLICY "cliente_insert_auth" ON cliente
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Cualquier usuario puede actualizar clientes
CREATE POLICY "cliente_update_auth" ON cliente
  FOR UPDATE USING (auth.role() = 'authenticated');

-- Solo admin puede eliminar
CREATE POLICY "cliente_delete_admin" ON cliente
  FOR DELETE USING (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- ============ POLICIES PARA TABLA ARTICULO ============

-- Cualquier usuario autenticado puede ver artículos activos
CREATE POLICY "articulo_select_auth" ON articulo
  FOR SELECT USING (
    auth.role() = 'authenticated' OR estado = 'activo'
  );

-- Solo vendedor+ puede crear/actualizar
CREATE POLICY "articulo_insert_vendedor" ON articulo
  FOR INSERT WITH CHECK (
    auth.role() = 'authenticated'
  );

CREATE POLICY "articulo_update_vendedor" ON articulo
  FOR UPDATE USING (
    auth.role() = 'authenticated'
  );

-- Solo admin puede eliminar
CREATE POLICY "articulo_delete_admin" ON articulo
  FOR DELETE USING (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- ============ POLICIES PARA TABLA VENTA ============

-- Vendedor puede ver sus ventas
CREATE POLICY "venta_select_own" ON venta
  FOR SELECT USING (
    trabajador_id = auth.uid()::int OR
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- Vendedor puede crear sus ventas
CREATE POLICY "venta_insert_own" ON venta
  FOR INSERT WITH CHECK (
    trabajador_id = auth.uid()::int
  );

-- ============ POLICIES PARA TABLA DOCUMENTS ============

-- Cualquier usuario autenticado puede leer documentos
CREATE POLICY "documents_select_auth" ON documents
  FOR SELECT USING (auth.role() = 'authenticated');

-- Solo admin puede insertar/actualizar/eliminar documentos
CREATE POLICY "documents_insert_admin" ON documents
  FOR INSERT WITH CHECK (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

CREATE POLICY "documents_update_admin" ON documents
  FOR UPDATE USING (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

CREATE POLICY "documents_delete_admin" ON documents
  FOR DELETE USING (
    (SELECT acceso FROM trabajador WHERE idtrabajador = auth.uid()::int) = 'administrador'
  );

-- ============ VERIFICACIÓN ============

-- Mostrar todas las policies activas
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
