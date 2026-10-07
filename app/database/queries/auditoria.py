"""Consultas del módulo 5: auditoría de la base de datos."""

from database.connection import get_connection

_QUERY_LOGINS = """
    SELECT 
        name AS LoginName,
        type_desc AS LoginType,
        is_disabled AS IsDisabled,
        create_date AS CreateDate
    FROM sys.server_principals
    WHERE type IN ('S', 'U', 'G') AND name NOT LIKE '##%##'
    ORDER BY name;
"""

_QUERY_USERS = """
    SELECT 
        name AS UserName,
        type_desc AS UserType,
        authentication_type_desc AS AuthType,
        create_date AS CreateDate
    FROM sys.database_principals
    WHERE type IN ('S', 'U', 'G') AND name NOT IN ('sys', 'INFORMATION_SCHEMA')
    ORDER BY name;
"""

_QUERY_SERVER_ROLES = """
    SELECT 
        r.name AS RoleName,
        m.name AS MemberName
    FROM sys.server_role_members srm
    JOIN sys.server_principals r ON srm.role_principal_id = r.principal_id
    JOIN sys.server_principals m ON srm.member_principal_id = m.principal_id
    ORDER BY r.name, m.name;
"""

_QUERY_DB_ROLES = """
    SELECT 
        r.name AS RoleName,
        m.name AS MemberName
    FROM sys.database_role_members drm
    JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON drm.member_principal_id = m.principal_id
    ORDER BY r.name, m.name;
"""

_QUERY_PERMISOS = """
    SELECT 
        dp.class_desc AS ObjectType,
        ISNULL(OBJECT_NAME(dp.major_id), 'N/A') AS ObjectName,
        dp.permission_name AS Permission,
        dp.state_desc AS State,
        pr.name AS GranteeName,
        pr.type_desc AS GranteeType
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    WHERE dp.major_id >= 0
    ORDER BY GranteeName, ObjectName;
"""

_QUERY_DEPENDENCIAS = """
    SELECT 
        obj.name AS ObjectName,
        obj.type_desc AS ObjectType,
        sed.referenced_entity_name AS MissingDependency
    FROM sys.sql_expression_dependencies sed
    LEFT JOIN sys.objects obj ON sed.referencing_id = obj.object_id
    WHERE OBJECT_ID(sed.referenced_entity_name) IS NULL 
      AND sed.is_ambiguous = 0
    ORDER BY ObjectName;
"""


def _ejecutar_consulta(query):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            columnas = [columna[0] for columna in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    except Exception as e:
        print(f"Error ejecutando consulta de auditoría: {e}")
        return []

def obtener_logins():
    return _ejecutar_consulta(_QUERY_LOGINS)

def obtener_usuarios():
    return _ejecutar_consulta(_QUERY_USERS)

def obtener_roles_servidor():
    return _ejecutar_consulta(_QUERY_SERVER_ROLES)

def obtener_roles_bd():
    return _ejecutar_consulta(_QUERY_DB_ROLES)

def obtener_permisos():
    return _ejecutar_consulta(_QUERY_PERMISOS)

def obtener_objetos_problematicos():
    return _ejecutar_consulta(_QUERY_DEPENDENCIAS)
