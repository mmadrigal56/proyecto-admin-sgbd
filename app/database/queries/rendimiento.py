"""
Módulo 2 - Monitoreo de rendimiento.

Capa de acceso a datos: ejecuta las consultas administrativas reales
definidas en sql/02-rendimiento/consultas_rendimiento.sql y devuelve
los resultados como estructuras simples (dict / list) para que la
capa de presentación (Streamlit) no dependa de pyodbc.

Requiere que el usuario configurado en config/.env tenga el permiso
de servidor VIEW SERVER STATE (ya otorgado en la Semana 3, ver
sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql).
"""

from database.connection import get_connection


_QUERY_CONSULTAS_COSTOSAS = """
    SELECT TOP 10
        qs.execution_count AS veces_ejecutada,
        qs.total_worker_time / 1000.0 AS cpu_total_ms,
        (qs.total_worker_time / qs.execution_count) / 1000.0 AS cpu_promedio_ms,
        qs.total_elapsed_time / 1000.0 AS duracion_total_ms,
        (qs.total_elapsed_time / qs.execution_count) / 1000.0 AS duracion_promedio_ms,
        qs.total_logical_reads AS lecturas_totales,
        (qs.total_logical_reads / qs.execution_count) AS lecturas_promedio,
        SUBSTRING(
            st.text,
            (qs.statement_start_offset / 2) + 1,
            (
                (CASE qs.statement_end_offset
                    WHEN -1 THEN DATALENGTH(st.text)
                    ELSE qs.statement_end_offset
                END - qs.statement_start_offset) / 2
            ) + 1
        ) AS texto_consulta
    FROM sys.dm_exec_query_stats AS qs
    CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
    ORDER BY qs.total_worker_time DESC
"""

_QUERY_SESIONES_ACTIVAS = """
    SELECT TOP 20
        session_id AS id_sesion,
        login_name AS usuario,
        status AS estado,
        host_name AS equipo,
        program_name AS aplicacion,
        login_time AS hora_inicio_sesion,
        cpu_time AS tiempo_cpu_ms,
        memory_usage AS memoria_paginas_de_8kb
    FROM sys.dm_exec_sessions
    WHERE is_user_process = 1
    ORDER BY cpu_time DESC
"""

_QUERY_SESIONES_BLOQUEADAS = """
    SELECT
        r.session_id AS sesion_bloqueada,
        r.blocking_session_id AS sesion_bloqueadora,
        r.wait_type AS tipo_espera,
        r.wait_time / 1000.0 AS tiempo_espera_segundos,
        r.status AS estado,
        s.login_name AS usuario_bloqueado,
        r.command AS comando
    FROM sys.dm_exec_requests AS r
    JOIN sys.dm_exec_sessions AS s ON r.session_id = s.session_id
    WHERE r.blocking_session_id <> 0
"""


def _fetchall_as_dicts(cursor):
    """Convierte todas las filas de un cursor pyodbc en una lista de dicts."""
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def obtener_consultas_costosas():
    """
    Devuelve las 10 sentencias SQL de mayor consumo, ordenadas por
    tiempo total de CPU.

    Devuelve una lista vacía (no None) cuando no hay datos en el
    caché de planes, para que la capa de presentación distinga
    "sin datos todavía" de "error".
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_CONSULTAS_COSTOSAS)
        return _fetchall_as_dicts(cursor)


def obtener_sesiones_activas():
    """Devuelve hasta 20 sesiones de usuario activas, ordenadas por CPU."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_SESIONES_ACTIVAS)
        return _fetchall_as_dicts(cursor)


def obtener_sesiones_bloqueadas():
    """
    Devuelve las sesiones actualmente bloqueadas y su bloqueadora.

    Una lista vacía significa que NO hay bloqueos en este momento
    (condición normal, no un error). La capa de presentación debe
    interpretar la lista vacía como "sin bloqueos", no como fallo.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_SESIONES_BLOQUEADAS)
        return _fetchall_as_dicts(cursor)