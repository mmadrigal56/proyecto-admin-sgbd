/*
    Proyecto: Administración de Bases de Datos
    Semana: 3
    Módulo: 1 - Estado general de la instancia
    Archivo: consultas_estado_instancia.sql

    Propósito:
    Consultas administrativas reales utilizadas por el Módulo 1 para
    mostrar el estado general del servidor y la instancia de SQL Server.

    Requisito de permisos:
    Requiere que el login/usuario tenga VIEW SERVER STATE
    (ver otorgar_permisos_estado_instancia.sql).

    Estas mismas consultas son las que ejecuta
    app/database/queries/estado_instancia.py desde Python.
    Se dejan aquí documentadas para poder probarlas directamente
    en SSMS antes de integrarlas a la aplicación.
*/

-- =========================================================
-- 1. Servidor, instancia, tipo y versión de SQL Server
-- =========================================================
-- SERVERPROPERTY('InstanceName') devuelve NULL cuando es la instancia
-- por defecto (MSSQLSERVER), por eso se usa ISNULL para mostrar algo
-- legible en ese caso.
SELECT
    @@SERVERNAME                                   AS servidor,
    ISNULL(CAST(SERVERPROPERTY('InstanceName') AS NVARCHAR(128)), 'Instancia por defecto') AS instancia,
    CAST(SERVERPROPERTY('Edition') AS NVARCHAR(128))          AS edicion,
    CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(128))   AS version_producto,
    CAST(SERVERPROPERTY('ProductLevel') AS NVARCHAR(128))     AS nivel_producto,
    CAST(SERVERPROPERTY('Collation') AS NVARCHAR(128))        AS collation_servidor;
GO

-- =========================================================
-- 2. Fecha/hora de inicio y tiempo de actividad (uptime)
-- =========================================================
-- sys.dm_os_sys_info.sqlserver_start_time es el momento exacto en que
-- arrancó el servicio de SQL Server. El uptime se calcula en minutos
-- para que sea legible en la interfaz.
SELECT
    sqlserver_start_time                                       AS fecha_inicio,
    DATEDIFF(MINUTE, sqlserver_start_time, GETDATE())          AS minutos_actividad,
    DATEDIFF(HOUR, sqlserver_start_time, GETDATE())            AS horas_actividad
FROM sys.dm_os_sys_info;
GO

-- =========================================================
-- 3. Memoria asignada y utilizada
-- =========================================================
-- sys.dm_os_process_memory reporta la memoria del proceso de SQL Server
-- en KB. Se convierte a MB para que sea más legible.
SELECT
    physical_memory_in_use_kb / 1024.0     AS memoria_fisica_en_uso_mb,
    virtual_address_space_committed_kb / 1024.0 AS memoria_virtual_comprometida_mb,
    large_page_allocations_kb / 1024.0     AS memoria_paginas_grandes_mb
FROM sys.dm_os_process_memory;
GO

-- =========================================================
-- 4. Bases de datos administradas por la instancia
-- =========================================================
-- Lista las bases visibles para el usuario consultivo con su estado
-- y modelo de recuperación. No incluye contenido de las bases, solo
-- metadatos administrativos.
SELECT
    name                            AS nombre_base,
    state_desc                      AS estado,
    recovery_model_desc             AS modelo_recuperacion,
    create_date                     AS fecha_creacion
FROM sys.databases
ORDER BY name;
GO
