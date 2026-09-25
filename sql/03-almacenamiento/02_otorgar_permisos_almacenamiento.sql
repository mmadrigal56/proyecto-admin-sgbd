/*
    Proyecto: Administración de Bases de Datos
    Semana: 5 - Módulo 3: Gestión del almacenamiento
    Archivo: 02_otorgar_permisos_almacenamiento.sql

    Permisos del usuario consultivo para el módulo 3.
    Ejecutar como administrador, después de 01_crear_objetos_historial.sql.
*/

USE BD_AdminSGBD;
GO

IF DATABASE_PRINCIPAL_ID(N'adminsgbd_consulta') IS NULL
BEGIN
    PRINT 'El usuario adminsgbd_consulta no existe en BD_AdminSGBD. Ejecutar primero sql/00-configuracion/crear_usuario_consultivo.sql.';
END
ELSE
BEGIN
    -- Sin VIEW DEFINITION las tablas e índices no son visibles en los catálogos.
    GRANT VIEW DEFINITION TO [adminsgbd_consulta];
    GRANT SELECT ON SCHEMA::monitoreo TO [adminsgbd_consulta];
    GRANT EXECUTE ON OBJECT::monitoreo.sp_capturar_almacenamiento TO [adminsgbd_consulta];
    PRINT 'Permisos del módulo 3 otorgados a adminsgbd_consulta.';
END
GO

SELECT
    pr.name              AS usuario,
    pe.permission_name   AS permiso,
    pe.state_desc        AS estado,
    CASE pe.class
        WHEN 0 THEN N'(toda la base)'
        WHEN 3 THEN N'esquema ' + SCHEMA_NAME(pe.major_id)
        WHEN 1 THEN OBJECT_SCHEMA_NAME(pe.major_id) + N'.' + OBJECT_NAME(pe.major_id)
    END                  AS sobre
FROM sys.database_permissions AS pe
JOIN sys.database_principals AS pr
    ON pr.principal_id = pe.grantee_principal_id
WHERE pr.name = N'adminsgbd_consulta'
ORDER BY pe.class_desc, pe.permission_name;
GO
