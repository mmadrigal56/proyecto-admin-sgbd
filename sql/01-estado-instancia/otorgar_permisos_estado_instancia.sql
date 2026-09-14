/*
    Proyecto: Administración de Bases de Datos
    Semana: 3
    Módulo: 1 - Estado general de la instancia
    Archivo: otorgar_permisos_estado_instancia.sql

    Propósito:
    El usuario consultivo "adminsgbd_consulta" (creado en la Semana 2)
    solo tenía permisos mínimos de conexión. Las consultas del Módulo 1
    necesitan leer vistas de administración dinámica (DMVs) del servidor
    (sys.dm_os_sys_info, sys.dm_os_process_memory), y esas vistas requieren
    el permiso de servidor VIEW SERVER STATE.

    Este permiso es de SOLO LECTURA: permite ver información de estado
    del servidor, pero no permite modificar nada ni ejecutar operaciones
    administrativas. No es un permiso destructivo.

    Ejecutar este script como administrador (sysadmin), una sola vez.
*/

USE master;
GO

IF EXISTS (
    SELECT 1
    FROM sys.server_principals
    WHERE name = N'adminsgbd_consulta'
)
BEGIN
    GRANT VIEW SERVER STATE TO [adminsgbd_consulta];
    PRINT 'Permiso VIEW SERVER STATE otorgado a adminsgbd_consulta.';
END
ELSE
BEGIN
    PRINT 'El login adminsgbd_consulta no existe. Ejecutar primero sql/00-configuracion/crear_usuario_consultivo.sql.';
END
GO
