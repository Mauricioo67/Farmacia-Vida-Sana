-- datoss.sql - Datos de prueba masivos para Farmacia (con fechas de vencimiento)

-- 0. Limpieza de Ventas Anteriores (Para evitar duplicados y errores)
DELETE FROM detalle_venta;
DELETE FROM venta;
ALTER SEQUENCE venta_idventa_seq RESTART WITH 1;

-- 0.1 Trabajadores Iniciales
-- Limpiar trabajadores anteriores si es necesario (Opcional, ten cuidado si ya hay datos reales)
-- DELETE FROM trabajador WHERE usuario != 'admin'; 

INSERT INTO trabajador (usuario, password, nombre, apellidos, acceso, estado) VALUES
('mauricio2', 'scrypt:32768:8:1$OxCcmfCcL3H67vEw$d9fd39e3ec66e743fcd22f3e8b4e4d58849b28b76df4775d7fc263388c4be4206814b4bf', 'Mauricio', 'Gómez', 'vendedor', 'activo')
ON CONFLICT (usuario) DO UPDATE SET password = EXCLUDED.password;

-- 1. Categorías
INSERT INTO categoria (nombre, descripcion) VALUES
('Antibióticos', 'Medicamentos para combatir infecciones bacterianas'),
('Analgésicos', 'Medicamentos para aliviar el dolor'),
('Antiinflamatorios', 'Para reducir la inflamación'),
('Vitaminas', 'Suplementos vitamínicos y minerales'),
('Cuidado Personal', 'Productos de higiene y belleza'),
('Cardiología', 'Medicamentos para el corazón'),
('Pediatría', 'Medicamentos para niños'),
('Gastroenterología', 'Para el sistema digestivo')
ON CONFLICT DO NOTHING;

-- 2. Presentaciones
INSERT INTO presentacion (nombre, descripcion) VALUES
('Caja x 10', 'Caja con 10 unidades/tiras'),
('Caja x 30', 'Caja con 30 unidades para tratamiento mensual'),
('Jarabe 120ml', 'Frasco de jarabe'),
('Inyectable', 'Ampolla inyectable'),
('Crema 50g', 'Tubo de crema tópica'),
('Unidad', 'Venta por unidad suelta')
ON CONFLICT DO NOTHING;

-- 3. Productos (Artículos) con fechas de vencimiento
INSERT INTO articulo (codigo, nombre, descripcion, stock, precio_venta, idcategoria, idpresentacion, estado, tipo_venta, fecha_vencimiento) VALUES
-- Productos con vencimiento normal (más de 30 días)
('ANT001', 'Amoxicilina 500mg', 'Antibiótico de amplio espectro', 150, 5.50, (SELECT idcategoria FROM categoria WHERE nombre='Antibióticos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '180 days'),
('ANA001', 'Paracetamol 500mg', 'Para fiebre y dolor leve', 500, 2.00, (SELECT idcategoria FROM categoria WHERE nombre='Analgésicos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'TIRAS', CURRENT_DATE + INTERVAL '365 days'),
('INF001', 'Ibuprofeno 400mg', 'Antiinflamatorio no esteroideo', 300, 3.50, (SELECT idcategoria FROM categoria WHERE nombre='Antiinflamatorios' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'TIRAS', CURRENT_DATE + INTERVAL '240 days'),
('VIT001', 'Vitamina C 1g', 'Refuerzo sistema inmune', 100, 4.00, (SELECT idcategoria FROM categoria WHERE nombre='Vitaminas' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'UNIDADES', CURRENT_DATE + INTERVAL '120 days'),
('GAS001', 'Omeprazol 20mg', 'Protector gástrico', 200, 3.00, (SELECT idcategoria FROM categoria WHERE nombre='Gastroenterología' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 30' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '300 days'),
('CAR001', 'Losartán 50mg', 'Para la presión arterial', 120, 6.00, (SELECT idcategoria FROM categoria WHERE nombre='Cardiología' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 30' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '270 days'),

-- Productos por vencer (8-30 días)
('PED001', 'Ibuprofeno Jarabe', 'Para niños sabor fresa', 80, 8.50, (SELECT idcategoria FROM categoria WHERE nombre='Pediatría' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Jarabe 120ml' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '25 days'),
('CUI001', 'Protector Solar FPS50', 'Protección alta 100ml', 40, 15.00, (SELECT idcategoria FROM categoria WHERE nombre='Cuidado Personal' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Unidad' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '15 days'),

-- Productos que vencen pronto (1-7 días)
('ANT002', 'Azitromicina 500mg', 'Antibiótico 3 tabletas', 60, 12.00, (SELECT idcategoria FROM categoria WHERE nombre='Antibióticos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '5 days'),
('ANA002', 'Diclofenaco Gel', 'Para dolores musculares', 45, 7.50, (SELECT idcategoria FROM categoria WHERE nombre='Analgésicos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Crema 50g' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE + INTERVAL '3 days'),

-- Productos vencidos (para pruebas)
('ANT003', 'Cefalexina 500mg', 'Antibiótico cefalosporina', 25, 8.00, (SELECT idcategoria FROM categoria WHERE nombre='Antibióticos' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 10' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE - INTERVAL '5 days'),
('VIT002', 'Complejo B', 'Vitaminas del complejo B', 30, 5.50, (SELECT idcategoria FROM categoria WHERE nombre='Vitaminas' LIMIT 1), (SELECT idpresentacion FROM presentacion WHERE nombre='Caja x 30' LIMIT 1), 'activo', 'COMPLETO', CURRENT_DATE - INTERVAL '10 days');

-- 4. Clientes
INSERT INTO cliente (nombre, apellidos, telefono, email) VALUES
('Juan', 'Pérez', '77712345', 'juan.perez@email.com'),
('María', 'Gómez', '72065432', 'maria.gomez@email.com'),
('Carlos', 'López', '60598765', 'carlos.lopez@email.com'),
('Ana', 'Martínez', '71234567', 'ana.martinez@email.com'),
('Pedro', 'Sánchez', '78901234', 'pedro.sanchez@email.com'),
('Lucía', 'Fernández', '76543210', 'lucia.fernandez@email.com'),
('Miguel', 'Torres', '68765432', 'miguel.torres@email.com'),
('Sofía', 'Ramírez', '70123456', 'sofia.ramirez@email.com');

-- 5. Ventas de prueba (Históricas)
INSERT INTO venta (idventa, idcliente, idtrabajador, fecha_hora, total_venta, estado) VALUES
(1, (SELECT idcliente FROM cliente WHERE nombre='Juan' LIMIT 1), (SELECT idtrabajador FROM trabajador WHERE usuario='admin' LIMIT 1), NOW() - INTERVAL '3 days', 15.50, 'completada'),
(2, (SELECT idcliente FROM cliente WHERE nombre='María' LIMIT 1), (SELECT idtrabajador FROM trabajador WHERE usuario='admin' LIMIT 1), NOW() - INTERVAL '2 days', 45.00, 'completada'),
(3, (SELECT idcliente FROM cliente WHERE nombre='Carlos' LIMIT 1), (SELECT idtrabajador FROM trabajador WHERE usuario='admin' LIMIT 1), NOW() - INTERVAL '1 day', 8.50, 'completada')
ON CONFLICT (idventa) DO NOTHING;

-- 6. Detalle Venta
INSERT INTO detalle_venta (idventa, idarticulo, cantidad, precio_unitario, subtotal) VALUES
-- Venta 1: Juan (Total 15.50)
(1, (SELECT idarticulo FROM articulo WHERE nombre='Amoxicilina 500mg' LIMIT 1), 1, 5.50, 5.50),
(1, (SELECT idarticulo FROM articulo WHERE nombre='Paracetamol 500mg' LIMIT 1), 5, 2.00, 10.00),

-- Venta 2: María (Total 45.00)
(2, (SELECT idarticulo FROM articulo WHERE nombre='Protector Solar FPS50' LIMIT 1), 2, 15.00, 30.00),
(2, (SELECT idarticulo FROM articulo WHERE nombre='Azitromicina 500mg' LIMIT 1), 1, 15.00, 15.00),

-- Venta 3: Carlos (Total 8.50)
(3, (SELECT idarticulo FROM articulo WHERE nombre='Ibuprofeno Jarabe' LIMIT 1), 1, 8.50, 8.50);

-- Ajustar secuencia para que las nuevas ventas empiecen desde el ID correcto
SELECT setval('venta_idventa_seq', (SELECT MAX(idventa) FROM venta));
