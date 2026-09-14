/*
    Proyecto: Administración de Bases de Datos
    Semana: 2
    Archivo: crear_usuario_consultivo.sql

    Propósito:
    Crear el login y usuario utilizados por la aplicación
    para las consultas iniciales de administración.

    IMPORTANTE:
    La contraseña utilizada durante la ejecución NO debe
    almacenarse en GitHub ni en este archivo.
*/

USE master;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.server_principals
    WHERE name = N'adminsgbd_consulta'
)
BEGIN
    CREATE LOGIN [adminsgbd_consulta]
    WITH PASSWORD = N'CAMBIAR_ESTA_CONTRASEÑA';
    
    PRINT 'Login adminsgbd_consulta creado correctamente.';
END
ELSE
BEGIN
    PRINT 'El login adminsgbd_consulta ya existe.';
END
GO

USE BD_AdminSGBD;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_principals
    WHERE name = N'adminsgbd_consulta'
)
BEGIN
    CREATE USER [adminsgbd_consulta]
    FOR LOGIN [adminsgbd_consulta];

    PRINT 'Usuario adminsgbd_consulta creado correctamente.';
END
ELSE
BEGIN
    PRINT 'El usuario adminsgbd_consulta ya existe.';
END
GO
