"""
Módulo 1 - Estado general de la instancia.

Capa de acceso a datos: ejecuta las consultas administrativas reales
definidas en sql/01-estado-instancia/consultas_estado_instancia.sql y
devuelve los resultados como estructuras simples (dict / list) para
que la capa de presentación (Streamlit) no dependa de pyodbc.

Requiere que el usuario configurado en config/.env tenga el permiso
de servidor VIEW SERVER STATE (ver
sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql).
"""

from database.connection import get_connection


_QUERY_SERVIDOR_INSTANCIA = """
    SELECT
        @@SERVERNAME AS servidor,
        ISNULL(CAST(SERVERPROPERTY('InstanceName') AS NVARCHAR(128)), 'Instancia por defecto') AS instancia,
        CAST(SERVERPROPERTY('Edition') AS NVARCHAR(128)) AS edicion,
        CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(128)) AS version_producto,
        CAST(SERVERPROPERTY('ProductLevel') AS NVARCHAR(128)) AS nivel_producto,
        CAST(SERVERPROPERTY('Collation') AS NVARCHAR(128)) AS collation_servidor
"""

_QUERY_ACTIVIDAD = """
    SELECT
        sqlserver_start_time AS fecha_inicio,
        DATEDIFF(MINUTE, sqlserver_start_time, GETDATE()) AS minutos_actividad,
        DATEDIFF(HOUR, sqlserver_start_time, GETDATE()) AS horas_actividad
    FROM sys.dm_os_sys_info
"""

_QUERY_MEMORIA = """
    SELECT
        physical_memory_in_use_kb / 1024.0 AS memoria_fisica_en_uso_mb,
        virtual_address_space_committed_kb / 1024.0 AS memoria_virtual_comprometida_mb,
        large_page_allocations_kb / 1024.0 AS memoria_paginas_grandes_mb
    FROM sys.dm_os_process_memory
"""

_QUERY_BASES_DATOS = """
    SELECT
        name AS nombre_base,
        state_desc AS estado,
        recovery_model_desc AS modelo_recuperacion,
        create_date AS fecha_creacion
    FROM sys.databases
    ORDER BY name
"""


def _fetchone_as_dict(cursor):
    """Convierte la primera fila de un cursor pyodbc en un dict."""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def _fetchall_as_dicts(cursor):
    """Convierte todas las filas de un cursor pyodbc en una lista de dicts."""
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def obtener_servidor_instancia():
    """
    Devuelve nombre de servidor, instancia, edición, versión y collation.

    Puede lanzar una excepción si falla la conexión o la consulta;
    la capa de presentación es responsable de capturarla y mostrar
    un mensaje adecuado.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_SERVIDOR_INSTANCIA)
        return _fetchone_as_dict(cursor)


def obtener_actividad():
    """Devuelve la fecha de inicio del servicio y el tiempo de actividad."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_ACTIVIDAD)
        return _fetchone_as_dict(cursor)


def obtener_memoria():
    """
    Devuelve indicadores de memoria del proceso de SQL Server, en MB.

    Requiere el permiso VIEW SERVER STATE. Si el usuario configurado
    no lo tiene, pyodbc lanzará un error de permisos que debe
    manejarse en la capa de presentación.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_MEMORIA)
        return _fetchone_as_dict(cursor)


def obtener_bases_de_datos():
    """
    Devuelve la lista de bases administradas visibles para el usuario
    consultivo configurado, con su estado y modelo de recuperación.

    Devuelve una lista vacía (no None) cuando no hay resultados, para
    que la capa de presentación pueda distinguir "sin datos" de "error".
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_BASES_DATOS)
        return _fetchall_as_dicts(cursor)
