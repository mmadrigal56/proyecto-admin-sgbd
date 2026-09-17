/*
    Proyecto: Administración de Bases de Datos
    Semana: 4
    Módulo: 2 - Monitoreo de rendimiento
    Archivo: consultas_rendimiento.sql

    Propósito:
    Consultas administrativas reales utilizadas por el Módulo 2 para
    identificar consultas costosas, sesiones activas y bloqueos en
    la instancia de SQL Server.

    Requisito de permisos:
    Requiere que el login/usuario tenga VIEW SERVER STATE
    (ya otorgado en sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql).

    Estas mismas consultas son las que ejecuta
    app/database/queries/rendimiento.py desde Python.
*/

-- =========================================================
-- 1. Sentencias SQL de mayor consumo (Top 10 por tiempo de CPU)
-- =========================================================
-- sys.dm_exec_query_stats acumula estadísticas de todas las consultas
-- cacheadas desde que arrancó la instancia. Se limita a TOP 10 para
-- evitar una consulta de monitoreo pesada.
SELECT TOP 10
    qs.execution_count                                          AS veces_ejecutada,
    qs.total_worker_time / 1000.0                                AS cpu_total_ms,
    (qs.total_worker_time / qs.execution_count) / 1000.0         AS cpu_promedio_ms,
    qs.total_elapsed_time / 1000.0                                AS duracion_total_ms,
    (qs.total_elapsed_time / qs.execution_count) / 1000.0        AS duracion_promedio_ms,
    qs.total_logical_reads                                       AS lecturas_totales,
    (qs.total_logical_reads / qs.execution_count)                AS lecturas_promedio,
    SUBSTRING(
        st.text,
        (qs.statement_start_offset / 2) + 1,
        (
            (CASE qs.statement_end_offset
                WHEN -1 THEN DATALENGTH(st.text)
                ELSE qs.statement_end_offset
            END - qs.statement_start_offset) / 2
        ) + 1
    )                                                             AS texto_consulta
FROM sys.dm_exec_query_stats AS qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
ORDER BY qs.total_worker_time DESC;
GO

-- =========================================================
-- 2. Sesiones activas (Top 20 por consumo de CPU)
-- =========================================================
-- sys.dm_exec_sessions lista todas las sesiones conectadas a la
-- instancia. Se filtra is_user_process = 1 para excluir procesos
-- internos del sistema, y se limita a TOP 20.
SELECT TOP 20
    session_id                     AS id_sesion,
    login_name                     AS usuario,
    status                         AS estado,
    host_name                      AS equipo,
    program_name                   AS aplicacion,
    login_time                     AS hora_inicio_sesion,
    cpu_time                       AS tiempo_cpu_ms,
    memory_usage                   AS memoria_paginas_de_8kb
FROM sys.dm_exec_sessions
WHERE is_user_process = 1
ORDER BY cpu_time DESC;
GO

-- =========================================================
-- 3. Sesiones bloqueadas y bloqueadoras
-- =========================================================
-- sys.dm_exec_requests muestra las solicitudes en ejecución. Cuando
-- blocking_session_id es distinto de 0, esa sesión está siendo
-- bloqueada por la sesión indicada en esa columna.
-- Si esta consulta no devuelve filas, significa que NO hay bloqueos
-- activos en este momento (no es un error).
SELECT
    r.session_id                   AS sesion_bloqueada,
    r.blocking_session_id          AS sesion_bloqueadora,
    r.wait_type                    AS tipo_espera,
    r.wait_time / 1000.0           AS tiempo_espera_segundos,
    r.status                       AS estado,
    s.login_name                   AS usuario_bloqueado,
    r.command                      AS comando
FROM sys.dm_exec_requests AS r
JOIN sys.dm_exec_sessions AS s ON r.session_id = s.session_id
WHERE r.blocking_session_id <> 0;
GO