"""Módulo 3 - Consultas de almacenamiento (sql/03-almacenamiento/consultas_almacenamiento.sql)."""

from decimal import Decimal

from database.connection import get_connection


_QUERY_RESUMEN_BASE = """
    SELECT
        DB_NAME() AS base_datos,
        SUM(CASE WHEN type = 0 THEN CAST(size AS BIGINT) END) * 8 / 1024.0 AS datos_asignado_mb,
        SUM(CASE WHEN type = 0 THEN CAST(FILEPROPERTY(name, 'SpaceUsed') AS BIGINT) END) * 8 / 1024.0 AS datos_usado_mb,
        SUM(CASE WHEN type = 1 THEN CAST(size AS BIGINT) END) * 8 / 1024.0 AS log_asignado_mb,
        SUM(CASE WHEN type = 1 THEN CAST(FILEPROPERTY(name, 'SpaceUsed') AS BIGINT) END) * 8 / 1024.0 AS log_usado_mb
    FROM sys.database_files
    WHERE type IN (0, 1)
"""

_QUERY_ARCHIVOS = """
    SELECT
        df.file_id AS id_archivo,
        df.name AS nombre_logico,
        df.type_desc AS tipo,
        fg.name AS filegroup,
        df.physical_name AS ubicacion,
        df.state_desc AS estado,
        CAST(df.size AS BIGINT) * 8 / 1024.0 AS asignado_mb,
        CAST(FILEPROPERTY(df.name, 'SpaceUsed') AS BIGINT) * 8 / 1024.0 AS usado_mb,
        df.growth AS crecimiento_valor,
        df.is_percent_growth AS crecimiento_es_porcentaje,
        df.max_size AS tamano_maximo_paginas
    FROM sys.database_files AS df
    LEFT JOIN sys.filegroups AS fg
        ON fg.data_space_id = df.data_space_id
    ORDER BY df.type, df.file_id
"""

_QUERY_FILEGROUPS = """
    SELECT
        fg.name AS filegroup,
        fg.type_desc AS tipo,
        fg.is_default AS es_predeterminado,
        fg.is_read_only AS solo_lectura,
        COUNT(df.file_id) AS cantidad_archivos,
        ISNULL(SUM(CAST(df.size AS BIGINT)), 0) * 8 / 1024.0 AS asignado_mb,
        ISNULL(SUM(CAST(FILEPROPERTY(df.name, 'SpaceUsed') AS BIGINT)), 0) * 8 / 1024.0 AS usado_mb
    FROM sys.filegroups AS fg
    LEFT JOIN sys.database_files AS df
        ON df.data_space_id = fg.data_space_id
    GROUP BY fg.name, fg.type_desc, fg.is_default, fg.is_read_only
    ORDER BY fg.name
"""

_QUERY_VOLUMENES = """
    SELECT DISTINCT
        vs.volume_mount_point AS unidad,
        vs.logical_volume_name AS etiqueta,
        vs.total_bytes / 1048576.0 AS total_mb,
        vs.available_bytes / 1048576.0 AS disponible_mb
    FROM sys.database_files AS df
    CROSS APPLY sys.dm_os_volume_stats(DB_ID(), df.file_id) AS vs
"""

_QUERY_EDICION = """
    SELECT
        CAST(SERVERPROPERTY('Edition') AS NVARCHAR(128)) AS edicion,
        CAST(SERVERPROPERTY('EngineEdition') AS INT) AS codigo_edicion,
        CAST(SERVERPROPERTY('ProductMajorVersion') AS INT) AS version_mayor
"""

_QUERY_TABLAS_MAYOR_TAMANO = """
    SELECT TOP (?)
        s.name AS esquema,
        o.name AS tabla,
        SUM(CASE WHEN ps.index_id IN (0, 1) THEN ps.row_count ELSE 0 END) AS filas,
        SUM(ps.reserved_page_count) * 8 / 1024.0 AS reservado_mb,
        SUM(ps.used_page_count) * 8 / 1024.0 AS usado_mb,
        SUM(CASE WHEN ps.index_id IN (0, 1) THEN ps.used_page_count ELSE 0 END) * 8 / 1024.0 AS datos_mb,
        SUM(CASE WHEN ps.index_id > 1 THEN ps.used_page_count ELSE 0 END) * 8 / 1024.0 AS indices_mb
    FROM sys.dm_db_partition_stats AS ps
    JOIN sys.objects AS o ON o.object_id = ps.object_id
    JOIN sys.schemas AS s ON s.schema_id = o.schema_id
    WHERE o.type = 'U'
      AND o.is_ms_shipped = 0
    GROUP BY s.name, o.name
    ORDER BY reservado_mb DESC
"""

_QUERY_INDICES_MAYOR_TAMANO = """
    SELECT TOP (?)
        s.name AS esquema,
        o.name AS tabla,
        ISNULL(i.name, N'(heap - sin índice agrupado)') AS indice,
        i.type_desc AS tipo_indice,
        SUM(ps.row_count) AS filas,
        SUM(ps.reserved_page_count) * 8 / 1024.0 AS reservado_mb,
        SUM(ps.used_page_count) * 8 / 1024.0 AS usado_mb
    FROM sys.dm_db_partition_stats AS ps
    JOIN sys.indexes AS i ON i.object_id = ps.object_id AND i.index_id = ps.index_id
    JOIN sys.objects AS o ON o.object_id = ps.object_id
    JOIN sys.schemas AS s ON s.schema_id = o.schema_id
    WHERE o.type = 'U'
      AND o.is_ms_shipped = 0
    GROUP BY s.name, o.name, i.name, i.type_desc
    ORDER BY reservado_mb DESC
"""

_QUERY_HISTORIAL = """
    SELECT TOP (?)
        fecha_captura,
        origen,
        datos_asignado_mb,
        datos_usado_mb,
        datos_disponible_mb,
        log_asignado_mb,
        log_usado_mb,
        total_asignado_mb,
        total_usado_mb
    FROM monitoreo.vw_resumen_historial
    WHERE base_datos = DB_NAME()
    ORDER BY fecha_captura DESC
"""

_EXEC_CAPTURAR = "EXEC monitoreo.sp_capturar_almacenamiento @origen = ?"


def _normalizar(valor):
    """Convierte Decimal a float para pandas y Plotly."""
    if isinstance(valor, Decimal):
        return float(valor)
    return valor


def _fila_a_dict(columns, row):
    return {col: _normalizar(val) for col, val in zip(columns, row)}


def _fetchall_as_dicts(cursor):
    """Convierte todas las filas de un cursor pyodbc en una lista de dicts."""
    columns = [column[0] for column in cursor.description]
    return [_fila_a_dict(columns, row) for row in cursor.fetchall()]


def _fetchone_as_dict(cursor):
    """Convierte la primera fila de un cursor pyodbc en un dict."""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return _fila_a_dict(columns, row)


def _ejecutar(query, params=(), una_fila=False):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        if una_fila:
            return _fetchone_as_dict(cursor)
        return _fetchall_as_dicts(cursor)


def obtener_resumen_base():
    """Espacio asignado y utilizado (MB) de datos y registro de la base actual."""
    return _ejecutar(_QUERY_RESUMEN_BASE, una_fila=True)


def obtener_archivos():
    """Archivos de datos y de registro: nombre, ubicación, tamaño y crecimiento."""
    return _ejecutar(_QUERY_ARCHIVOS)


def obtener_filegroups():
    """Filegroups de la base con su espacio asignado y utilizado."""
    return _ejecutar(_QUERY_FILEGROUPS)


def obtener_volumenes():
    """Unidades de disco donde residen los archivos de la base (requiere VIEW SERVER STATE)."""
    return _ejecutar(_QUERY_VOLUMENES)


def obtener_edicion():
    """Edición y versión mayor de SQL Server (para el límite de tamaño de Express)."""
    return _ejecutar(_QUERY_EDICION, una_fila=True)


def obtener_tablas_mayor_tamano(limite=10):
    """Tablas de usuario ordenadas de mayor a menor espacio reservado."""
    return _ejecutar(_QUERY_TABLAS_MAYOR_TAMANO, (int(limite),))


def obtener_indices_mayor_tamano(limite=10):
    """Índices (y heaps) ordenados de mayor a menor espacio reservado."""
    return _ejecutar(_QUERY_INDICES_MAYOR_TAMANO, (int(limite),))


def obtener_historial(limite=200):
    """Últimas mediciones registradas en monitoreo.HistorialAlmacenamiento, de la más reciente a la más antigua."""
    return _ejecutar(_QUERY_HISTORIAL, (int(limite),))


def registrar_medicion(origen="aplicacion"):
    """Ejecuta monitoreo.sp_capturar_almacenamiento y devuelve las filas registradas (una por archivo)."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_EXEC_CAPTURAR, (origen,))
        filas = _fetchall_as_dicts(cursor)
        connection.commit()
        return filas
