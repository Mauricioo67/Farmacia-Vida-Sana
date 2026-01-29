-- seeds.sql - DATOS INICIALES Y DE PRUEBA

-- 1. Trabajador Admin (Password: 'admin')
INSERT INTO trabajador (nombre, apellidos, usuario, password, acceso, estado)
VALUES 
('Admin', 'User', 'admin', 'scrypt:32768:8:1$w2KQd2aC7GZ2B8vj$9641773489e24803b98c39d89ccf277a83d0f77626960d738bd2c76d7e60fafd4354683a9458692780e3c88019a53160bcdf2705e4c632e185ae497ff2120e3a', 'Administrador', 'activo')
ON CONFLICT (usuario) DO NOTHING;

-- 2. Categorías
INSERT INTO categoria (nombre, descripcion) VALUES
('Antibióticos', 'Medicamentos para combatir infecciones bacterianas'),
('Analgésicos', 'Medicamentos para aliviar el dolor'),
('Antiinflamatorios', 'Para reducir la inflamación'),
('Vitaminas', 'Suplementos vitamínicos y minerales'),
('Cuidado Personal', 'Productos de higiene y belleza'),
('Cardiología', 'Medicamentos para el corazón'),
('Gastroenterología', 'Para el sistema digestivo')
ON CONFLICT DO NOTHING;

-- 3. Presentaciones
INSERT INTO presentacion (nombre, descripcion) VALUES
('Caja x 10', 'Caja con 10 unidades/tiras'),
('Caja x 30', 'Caja con 30 unidades para tratamiento mensual'),
('Jarabe 120ml', 'Frasco de jarabe'),
('Inyectable', 'Ampolla inyectable'),
('Crema 50g', 'Tubo de crema tópica'),
('Unidad', 'Venta por unidad suelta')
ON CONFLICT DO NOTHING;

-- 4. Proveedor
INSERT INTO proveedor (nombre, contacto, telefono) VALUES
('FarmaDistribuidora', 'Juan Pérez', '555-1234')
ON CONFLICT DO NOTHING;

-- 5. Clientes
INSERT INTO cliente (nombre, apellidos, telefono, email) VALUES
('Cliente', 'General', '0000000', 'general@email.com'),
('Juan', 'Pérez', '77712345', 'juan.perez@email.com'),
('María', 'Gómez', '72065432', 'maria.gomez@email.com')
ON CONFLICT DO NOTHING;

-- 6. Productos (Artículos) con fechas de vencimiento
INSERT INTO articulo (codigo, nombre, descripcion, stock, precio_venta, idcategoria, idpresentacion, estado, tipo_venta, fecha_vencimiento) VALUES
('ANT001', 'Amoxicilina 500mg', 'Antibiótico de amplio espectro', 150, 5.50, (SELECT idcategoria FROM categoria WHERE nombre='Antibióticos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '180 days'),
('ANA001', 'Paracetamol 500mg', 'Para fiebre y dolor leve', 500, 2.00, (SELECT idcategoria FROM categoria WHERE nombre='Analgésicos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'TIRAS', CURRENT_DATE + INTERVAL '365 days'),
('INF001', 'Ibuprofeno 400mg', 'Antiinflamatorio no esteroideo', 300, 3.50, (SELECT idcategoria FROM categoria WHERE nombre='Antiinflamatorios' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'TIRAS', CURRENT_DATE + INTERVAL '240 days'),
('PED001', 'Ibuprofeno Jarabe', 'Para niños sabor fresa', 80, 8.50, (SELECT idcategoria FROM categoria WHERE nombre='Pediatría' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Jarabe 120ml' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '25 days'),
('ANT003', 'Cefalexina 500mg', 'Antibiótico cefalosporina', 25, 8.00, (SELECT idcategoria FROM categoria WHERE nombre='Antibióticos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE - INTERVAL '5 days');
