/*
    Proyecto: Administración de Bases de Datos
    Semana: 5 - Módulo 3: Gestión del almacenamiento
    Archivo: consultas_almacenamiento.sql

    Consultas del módulo 3 (las mismas que usa
    app/database/queries/almacenamiento.py).
*/

USE BD_AdminSGBD;
GO

-- 1. Resumen de la base: asignado / utilizado / disponible
SELECT
    DB_NAME()                                                                          AS base_datos,
    SUM(CASE WHEN type = 0 THEN CAST(size AS BIGINT) END) * 8 / 1024.0                  AS datos_asignado_mb,
    SUM(CASE WHEN type = 0 THEN CAST(FILEPROPERTY(name, 'SpaceUsed') AS BIGINT) END) * 8 / 1024.0 AS datos_usado_mb,
    SUM(CASE WHEN type = 1 THEN CAST(size AS BIGINT) END) * 8 / 1024.0                  AS log_asignado_mb,
    SUM(CASE WHEN type = 1 THEN CAST(FILEPROPERTY(name, 'SpaceUsed') AS BIGINT) END) * 8 / 1024.0 AS log_usado_mb
FROM sys.database_files
WHERE type IN (0, 1);
GO

-- 2. Archivos de datos y de registro
SELECT
    df.file_id                                               AS id_archivo,
    df.name                                                  AS nombre_logico,
    df.type_desc                                             AS tipo,
    fg.name                                                  AS filegroup,
    df.physical_name                                         AS ubicacion,
    df.state_desc                                            AS estado,
    CAST(df.size AS BIGINT) * 8 / 1024.0                     AS asignado_mb,
    CAST(FILEPROPERTY(df.name, 'SpaceUsed') AS BIGINT) * 8 / 1024.0 AS usado_mb,
    df.growth                                                AS crecimiento_valor,
    df.is_percent_growth                                     AS crecimiento_es_porcentaje,
    df.max_size                                              AS tamano_maximo_paginas
FROM sys.database_files AS df
LEFT JOIN sys.filegroups AS fg
    ON fg.data_space_id = df.data_space_id
ORDER BY df.type, df.file_id;
GO

-- 3. Filegroups
SELECT
    fg.name                                                               AS filegroup,
    fg.type_desc                                                          AS tipo,
    fg.is_default                                                         AS es_predeterminado,
    fg.is_read_only                                                       AS solo_lectura,
    COUNT(df.file_id)                                                     AS cantidad_archivos,
    ISNULL(SUM(CAST(df.size AS BIGINT)), 0) * 8 / 1024.0                   AS asignado_mb,
    ISNULL(SUM(CAST(FILEPROPERTY(df.name, 'SpaceUsed') AS BIGINT)), 0) * 8 / 1024.0 AS usado_mb
FROM sys.filegroups AS fg
LEFT JOIN sys.database_files AS df
    ON df.data_space_id = fg.data_space_id
GROUP BY fg.name, fg.type_desc, fg.is_default, fg.is_read_only
ORDER BY fg.name;
GO

-- 4. Espacio del disco donde están los archivos
SELECT DISTINCT
    vs.volume_mount_point                  AS unidad,
    vs.logical_volume_name                 AS etiqueta,
    vs.total_bytes     / 1048576.0         AS total_mb,
    vs.available_bytes / 1048576.0         AS disponible_mb
FROM sys.database_files AS df
CROSS APPLY sys.dm_os_volume_stats(DB_ID(), df.file_id) AS vs;
GO

-- 5. Edición (para el límite de tamaño de Express)
SELECT
    CAST(SERVERPROPERTY('Edition') AS NVARCHAR(128))            AS edicion,
    CAST(SERVERPROPERTY('EngineEdition') AS INT)                AS codigo_edicion,
    CAST(SERVERPROPERTY('ProductMajorVersion') AS INT)          AS version_mayor;
GO

-- 6. Top 10 tablas de mayor tamaño
SELECT TOP (10)
    s.name                                                                        AS esquema,
    o.name                                                                        AS tabla,
    SUM(CASE WHEN ps.index_id IN (0, 1) THEN ps.row_count ELSE 0 END)             AS filas,
    SUM(ps.reserved_page_count) * 8 / 1024.0                                      AS reservado_mb,
    SUM(ps.used_page_count) * 8 / 1024.0                                          AS usado_mb,
    SUM(CASE WHEN ps.index_id IN (0, 1) THEN ps.used_page_count ELSE 0 END) * 8 / 1024.0 AS datos_mb,
    SUM(CASE WHEN ps.index_id > 1       THEN ps.used_page_count ELSE 0 END) * 8 / 1024.0 AS indices_mb
FROM sys.dm_db_partition_stats AS ps
JOIN sys.objects AS o ON o.object_id = ps.object_id
JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.type = 'U'
  AND o.is_ms_shipped = 0
GROUP BY s.name, o.name
ORDER BY reservado_mb DESC;
GO

-- 7. Top 10 índices de mayor tamaño
SELECT TOP (10)
    s.name                                         AS esquema,
    o.name                                         AS tabla,
    ISNULL(i.name, N'(heap - sin índice agrupado)') AS indice,
    i.type_desc                                    AS tipo_indice,
    SUM(ps.row_count)                              AS filas,
    SUM(ps.reserved_page_count) * 8 / 1024.0       AS reservado_mb,
    SUM(ps.used_page_count) * 8 / 1024.0           AS usado_mb
FROM sys.dm_db_partition_stats AS ps
JOIN sys.indexes AS i ON i.object_id = ps.object_id AND i.index_id = ps.index_id
JOIN sys.objects AS o ON o.object_id = ps.object_id
JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.type = 'U'
  AND o.is_ms_shipped = 0
GROUP BY s.name, o.name, i.name, i.type_desc
ORDER BY reservado_mb DESC;
GO

-- 8. Historial de crecimiento (últimas 200 mediciones)
SELECT TOP (200)
    fecha_captura, origen,
    datos_asignado_mb, datos_usado_mb, datos_disponible_mb,
    log_asignado_mb, log_usado_mb,
    total_asignado_mb, total_usado_mb
FROM monitoreo.vw_resumen_historial
WHERE base_datos = DB_NAME()
ORDER BY fecha_captura DESC;
GO

-- 9. Registrar una medición manualmente
-- EXEC monitoreo.sp_capturar_almacenamiento @origen = 'manual';
