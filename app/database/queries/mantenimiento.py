"""
Módulo 6 - Mantenimiento preventivo.

Capa de acceso a datos. Separa claramente dos tipos de operación:

- DETECCIÓN (solo lectura): usa get_connection() (usuario consultivo).
  Nunca modifica nada.
- EJECUCIÓN de mantenimiento (destructiva/administrativa): usa
  get_admin_connection() (usuario administrativo), y siempre pasa por
  los procedimientos almacenados de
  sql/06-mantenimiento/03_crear_procedimientos_mantenimiento.sql, que
  validan el objeto, ejecutan la operación y registran el resultado
  en monitoreo.RegistroMantenimiento.

La capa de presentación (Streamlit) es responsable de pedir
confirmación explícita ANTES de llamar a cualquiera de las funciones
de ejecución de este archivo.
"""

from database.connection import get_connection, get_admin_connection


_QUERY_ESTADISTICAS_DESACTUALIZADAS = """
    SELECT
        s.name AS esquema,
        t.name AS tabla,
        st.name AS estadistica,
        STATS_DATE(st.object_id, st.stats_id) AS fecha_ultima_actualizacion,
        sp.rows AS filas_en_la_muestra,
        sp.modification_counter AS filas_modificadas_desde_entonces,
        CASE
            WHEN sp.rows IS NULL THEN NULL
            WHEN sp.rows = 0 THEN 0
            ELSE CAST(100.0 * sp.modification_counter / sp.rows AS DECIMAL(5,1))
        END AS porcentaje_modificado,
        CASE
            WHEN STATS_DATE(st.object_id, st.stats_id) IS NULL THEN 'Nunca actualizada (prioridad maxima)'
            WHEN sp.rows > 0 AND (100.0 * sp.modification_counter / sp.rows) >= 20 THEN 'Desactualizada'
            ELSE 'Al dia'
        END AS estado
    FROM sys.stats st
    JOIN sys.tables t ON st.object_id = t.object_id
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    CROSS APPLY sys.dm_db_stats_properties(st.object_id, st.stats_id) AS sp
    WHERE s.name = 'dbo'
    ORDER BY
        CASE WHEN STATS_DATE(st.object_id, st.stats_id) IS NULL THEN 0 ELSE 1 END,
        porcentaje_modificado DESC
"""

_QUERY_INDICES_FRAGMENTADOS = """
    SELECT
        s.name AS esquema,
        t.name AS tabla,
        i.name AS indice,
        ips.avg_fragmentation_in_percent AS porcentaje_fragmentacion,
        ips.page_count AS paginas,
        CASE
            WHEN ips.avg_fragmentation_in_percent >= 30 THEN 'REBUILD'
            WHEN ips.avg_fragmentation_in_percent >= 5  THEN 'REORGANIZE'
            ELSE 'Sin accion necesaria'
        END AS accion_recomendada
    FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') AS ips
    JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
    JOIN sys.tables t ON ips.object_id = t.object_id
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE i.name IS NOT NULL
      AND ips.page_count > 0
    ORDER BY porcentaje_fragmentacion DESC
"""

_QUERY_HISTORIAL_MANTENIMIENTO = """
    SELECT
        fecha_hora,
        operacion,
        objeto,
        usuario_login,
        resultado,
        detalle
    FROM monitoreo.RegistroMantenimiento
    ORDER BY fecha_hora DESC
"""


def _fetchall_as_dicts(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# Detección (solo lectura, usuario consultivo)
# ---------------------------------------------------------------------------

def obtener_estadisticas_desactualizadas():
    """Devuelve las estadísticas de dbo con más modificaciones sin recalcular."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_ESTADISTICAS_DESACTUALIZADAS)
        return _fetchall_as_dicts(cursor)


def obtener_indices_fragmentados():
    """Devuelve los índices de la base con su porcentaje de fragmentación."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_INDICES_FRAGMENTADOS)
        return _fetchall_as_dicts(cursor)


def obtener_historial_mantenimiento():
    """Devuelve el historial completo de operaciones de mantenimiento."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(_QUERY_HISTORIAL_MANTENIMIENTO)
        return _fetchall_as_dicts(cursor)


# ---------------------------------------------------------------------------
# Ejecución de mantenimiento (usuario administrativo, requiere confirmación
# previa en la interfaz)
# ---------------------------------------------------------------------------

_EXEC_ACTUALIZAR_ESTADISTICAS = (
    "EXEC mantenimiento.sp_actualizar_estadisticas @esquema = ?, @tabla = ?"
)

_EXEC_RECONSTRUIR_INDICE = (
    "EXEC mantenimiento.sp_reconstruir_indice "
    "@esquema = ?, @tabla = ?, @indice = ?, @modo = ?"
)


def ejecutar_actualizacion_estadisticas(esquema, tabla):
    """
    Ejecuta mantenimiento.sp_actualizar_estadisticas con el usuario
    administrativo. Puede lanzar una excepción (por ejemplo si la
    tabla no existe, o si las credenciales administrativas no están
    configuradas); la capa de presentación debe capturarla y mostrar
    un mensaje claro. El procedimiento ya registra el resultado
    (éxito o fallo) en monitoreo.RegistroMantenimiento antes de que
    la excepción llegue hasta aquí.

    El estilo de llamada (EXEC con parámetros nombrados "?") es el
    mismo que ya usa app/database/queries/almacenamiento.py desde la
    Semana 5 para sp_capturar_almacenamiento.

    IMPORTANTE sobre el registro de fallos: si cursor.execute() lanza
    una excepción (por ejemplo porque el procedimiento hizo THROW), el
    administrador de contexto `with` de pyodbc haría un ROLLBACK
    automático al salir del bloque, lo que borraría también el INSERT
    de "Fallido" que el procedimiento ya había hecho en
    monitoreo.RegistroMantenimiento antes de lanzar el error. Por eso
    el commit() va en un finally: así el registro del intento fallido
    se conserva SIEMPRE, incluso cuando la excepción sigue
    propagándose hacia la capa de presentación.
    """
    with get_admin_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(_EXEC_ACTUALIZAR_ESTADISTICAS, (esquema, tabla))
        finally:
            connection.commit()


def ejecutar_mantenimiento_indice(esquema, tabla, indice, modo):
    """
    Ejecuta mantenimiento.sp_reconstruir_indice con el usuario
    administrativo. modo debe ser 'REORGANIZE' o 'REBUILD'.

    Ver la nota sobre el commit() en finally en
    ejecutar_actualizacion_estadisticas: aplica igual aquí, para no
    perder el registro de un intento fallido.
    """
    with get_admin_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(_EXEC_RECONSTRUIR_INDICE, (esquema, tabla, indice, modo))
        finally:
            connection.commit()
