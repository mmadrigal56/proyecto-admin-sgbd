/*
    Proyecto: Administración de Bases de Datos
    Semana: 8
    Módulo: 6 - Mantenimiento preventivo
    Archivo: 01_crear_usuario_administrativo.sql

    Propósito:
    Crear un login y usuario ADMINISTRATIVO separado del usuario
    consultivo (adminsgbd_consulta). Este usuario es el único que
    podrá ejecutar operaciones de mantenimiento reales (actualizar
    estadísticas, reconstruir/reorganizar índices).

    Decisión de diseño (documentada también en Andrey_semana8.md):
    Este usuario NO es sysadmin. Se agrega únicamente al rol de base
    de datos db_ddladmin en BD_AdminSGBD, que le permite ejecutar
    operaciones DDL (ALTER INDEX, UPDATE STATISTICS) pero no le da
    control total del servidor ni acceso a otras bases de datos.
    Esto cumple con la regla del cronograma de separar el acceso
    consultivo del administrativo, usando el mínimo permiso necesario.

    IMPORTANTE:
    - La contraseña real NUNCA debe quedar en este archivo ni en
      GitHub. Cámbiala en la ventana de SSMS antes de ejecutar, y
      usa una distinta a la del usuario consultivo.
    - Ejecutar como administrador (sysadmin), una sola vez por máquina
      (igual que adminsgbd_consulta en la Semana 2: cada integrante
      tiene su propia instancia local).
*/

USE master;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.server_principals
    WHERE name = N'adminsgbd_mantenimiento'
)
BEGIN
    CREATE LOGIN [adminsgbd_mantenimiento]
    WITH PASSWORD = N'CAMBIAR_ESTA_CONTRASEÑA';

    PRINT 'Login adminsgbd_mantenimiento creado correctamente.';
END
ELSE
BEGIN
    PRINT 'El login adminsgbd_mantenimiento ya existe.';
END
GO

USE BD_AdminSGBD;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_principals
    WHERE name = N'adminsgbd_mantenimiento'
)
BEGIN
    CREATE USER [adminsgbd_mantenimiento]
    FOR LOGIN [adminsgbd_mantenimiento];

    PRINT 'Usuario adminsgbd_mantenimiento creado correctamente.';
END
ELSE
BEGIN
    PRINT 'El usuario adminsgbd_mantenimiento ya existe.';
END
GO

-- Rol mínimo necesario para poder actualizar estadísticas y
-- reconstruir/reorganizar índices sobre los objetos de esta base.
IF NOT EXISTS (
    SELECT 1
    FROM sys.database_role_members drm
    JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON drm.member_principal_id = m.principal_id
    WHERE r.name = N'db_ddladmin' AND m.name = N'adminsgbd_mantenimiento'
)
BEGIN
    ALTER ROLE db_ddladmin ADD MEMBER [adminsgbd_mantenimiento];
    PRINT 'adminsgbd_mantenimiento agregado al rol db_ddladmin.';
END
ELSE
BEGIN
    PRINT 'adminsgbd_mantenimiento ya pertenece al rol db_ddladmin.';
END
GO
