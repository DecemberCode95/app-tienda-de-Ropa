# Archivo de inicialización de PostgreSQL
# Se ejecuta automáticamente cuando se crea el contenedor por primera vez

-- Crear extensión para UUID si es necesario
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurar timezone
SET timezone = 'Europe/Madrid';

-- Mensaje de confirmación
SELECT 'Base de datos inicializada correctamente' AS status;
