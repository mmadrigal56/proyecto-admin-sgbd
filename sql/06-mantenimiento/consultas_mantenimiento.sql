/*
    Proyecto: Administración de Bases de Datos
    Semana: 8
    Módulo: 6 - Mantenimiento preventivo
    Archivo: consultas_mantenimiento.sql

    Propósito:
    Consultas de SOLO LECTURA para DETECTAR qué objetos necesitan
    mantenimiento. Estas las ejecuta el usuario consultivo
    (adminsgbd_consulta); la detección nunca modifica nada.

    La ejecución real del mantenimiento (botones de la aplicación)
    usa un usuario administrativo distinto y los procedimientos de
    03_crear_procedimientos_mantenimiento.sql.

    Requisito de permisos:
    Requiere VIEW DATABASE STATE, otorgado en
    02_otorgar_permisos_mantenimiento.sql.

    Estas mismas consultas son las que ejecuta
    app/database/queries/mantenimiento.py desde Python.
*/

USE BD_AdminSGBD;
GO

-- =========================================================
-- 1. Estadísticas desactualizadas
-- =========================================================
-- Compara cuántas filas han cambiado desde el último recálculo
-- (modification_counter) contra el total de filas de la tabla.
-- Un porcentaje alto de modificaciones sin recalcular sugiere que
-- la estadística ya no refleja bien los datos reales.
--
-- Caso especial (el más urgente): si la estadística se creó cuando
-- la tabla estaba vacía y nunca se ha recalculado desde entonces,
-- SQL Server devuelve NULL en fecha, filas y modificaciones (no es
-- un error: significa literalmente "nunca actualizada"). Se trata
-- como prioridad máxima, por encima de cualquier porcentaje.
SELECT
    s.name                                                     AS esquema,
    t.name                                                      AS tabla,
    st.name                                                      AS estadistica,
    STATS_DATE(st.object_id, st.stats_id)                        AS fecha_ultima_actualizacion,
    sp.rows                                                       AS filas_en_la_muestra,
    sp.modification_counter                                       AS filas_modificadas_desde_entonces,
    CASE
        WHEN sp.rows IS NULL THEN NULL
        WHEN sp.rows = 0 THEN 0
        ELSE CAST(100.0 * sp.modification_counter / sp.rows AS DECIMAL(5,1))
    END                                                            AS porcentaje_modificado,
    CASE
        WHEN STATS_DATE(st.object_id, st.stats_id) IS NULL THEN 'Nunca actualizada (prioridad maxima)'
        WHEN sp.rows > 0 AND (100.0 * sp.modification_counter / sp.rows) >= 20 THEN 'Desactualizada'
        ELSE 'Al dia'
    END                                                            AS estado
FROM sys.stats st
JOIN sys.tables t ON st.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
CROSS APPLY sys.dm_db_stats_properties(st.object_id, st.stats_id) AS sp
WHERE s.name = 'dbo'
ORDER BY
    CASE WHEN STATS_DATE(st.object_id, st.stats_id) IS NULL THEN 0 ELSE 1 END,
    porcentaje_modificado DESC;
GO

-- =========================================================
-- 2. Índices fragmentados
-- =========================================================
-- sys.dm_db_index_physical_stats calcula la fragmentación real de
-- cada índice. Se usa el modo 'LIMITED' (el más liviano) porque es
-- suficiente para decidir si un índice necesita mantenimiento, sin
-- generar carga adicional en la instancia.
-- Guía de decisión usada por la aplicación:
--   avg_fragmentation_in_percent >= 30  -> REBUILD
--   avg_fragmentation_in_percent >= 5   -> REORGANIZE
--   avg_fragmentation_in_percent <  5   -> no necesita mantenimiento
SELECT
    s.name                              AS esquema,
    t.name                               AS tabla,
    i.name                               AS indice,
    ips.avg_fragmentation_in_percent     AS porcentaje_fragmentacion,
    ips.page_count                       AS paginas,
    CASE
        WHEN ips.avg_fragmentation_in_percent >= 30 THEN 'REBUILD'
        WHEN ips.avg_fragmentation_in_percent >= 5  THEN 'REORGANIZE'
        ELSE 'Sin accion necesaria'
    END                                   AS accion_recomendada
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') AS ips
JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
JOIN sys.tables t ON ips.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE i.name IS NOT NULL
  AND ips.page_count > 0
ORDER BY porcentaje_fragmentacion DESC;
GO

-- =========================================================
-- 3. Historial de mantenimiento
-- =========================================================
-- Registro de todas las operaciones de mantenimiento ejecutadas
-- (exitosas y fallidas), escrito por los procedimientos del
-- usuario administrativo.
SELECT
    fecha_hora,
    operacion,
    objeto,
    usuario_login,
    resultado,
    detalle
FROM monitoreo.RegistroMantenimiento
ORDER BY fecha_hora DESC;
GO
