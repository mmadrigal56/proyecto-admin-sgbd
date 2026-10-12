/*
    Proyecto: Administración de Bases de Datos
    Semana: 8
    Módulo: 6 - Mantenimiento preventivo
    Archivo: 02_otorgar_permisos_mantenimiento.sql

    Propósito:
    1) Dar al usuario CONSULTIVO (adminsgbd_consulta) los permisos de
       solo lectura que necesita para DETECTAR estadísticas
       desactualizadas e índices fragmentados:
       - VIEW DATABASE STATE: requerido por sys.dm_db_index_physical_stats
         y sys.dm_db_stats_properties.
       - VIEW DEFINITION: sin este permiso, sys.tables, sys.indexes y
         sys.stats NO muestran los objetos al usuario consultivo (es la
         misma lección que documentó Juan en la Semana 5 para el
         Módulo 3). Ese permiso ya se otorgó en
         sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql,
         PERO solo en la máquina donde se ejecutó ese script. Como cada
         integrante corre SQL Server en su propia instancia local (ver
         Semana 3), este archivo lo vuelve a otorgar aquí también, de
         forma idempotente, para que el Módulo 6 funcione por sí solo
         sin depender de que alguien haya corrido antes el script de
         la Semana 5 en esta máquina en particular.
    2) Crear la tabla de registro de mantenimiento, en el esquema
       monitoreo (ya usado desde la Semana 5 para el historial de
       almacenamiento).

    Decisión de diseño (lección aplicada de la Semana 5):
    El usuario consultivo NUNCA recibe INSERT directo sobre la tabla
    de registro. Solo SELECT, para poder mostrar el historial en la
    interfaz. Quien escribe en el registro es el procedimiento de
    mantenimiento (ver 03_crear_procedimientos_mantenimiento.sql),
    ejecutado por adminsgbd_mantenimiento, usando encadenamiento de
    propiedad (mismo dueño del esquema y la tabla).

    Ejecutar como administrador (sysadmin), después de
    01_crear_usuario_administrativo.sql.
*/

USE BD_AdminSGBD;
GO

-- 1) Permiso de lectura de estado de base de datos para el consultivo.
IF NOT EXISTS (
    SELECT 1
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    WHERE pr.name = N'adminsgbd_consulta'
      AND dp.permission_name = N'VIEW DATABASE STATE'
)
BEGIN
    GRANT VIEW DATABASE STATE TO [adminsgbd_consulta];
    PRINT 'Permiso VIEW DATABASE STATE otorgado a adminsgbd_consulta.';
END
ELSE
BEGIN
    PRINT 'adminsgbd_consulta ya tiene VIEW DATABASE STATE.';
END
GO

-- 1b) VIEW DEFINITION (database-wide), idempotente por si esta instancia
-- nunca corrió sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql.
IF NOT EXISTS (
    SELECT 1
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    WHERE pr.name = N'adminsgbd_consulta'
      AND dp.permission_name = N'VIEW DEFINITION'
      AND dp.class = 0 -- 0 = permiso sobre toda la base de datos
)
BEGIN
    GRANT VIEW DEFINITION TO [adminsgbd_consulta];
    PRINT 'Permiso VIEW DEFINITION otorgado a adminsgbd_consulta.';
END
ELSE
BEGIN
    PRINT 'adminsgbd_consulta ya tiene VIEW DEFINITION.';
END
GO

-- 1c) SELECT sobre el esquema dbo completo. Documentación de Microsoft:
-- sys.dm_db_stats_properties requiere, ADEMAS de VIEW DATABASE STATE,
-- permiso SELECT sobre la tabla consultada; si no lo tiene, la función
-- devuelve 0 filas para esa tabla en silencio (sin error), lo que hace
-- que la detección de estadísticas desactualizadas parezca vacía aunque
-- sí haya datos. sys.dm_db_index_physical_stats (índices fragmentados)
-- NO tiene este requisito adicional, por eso la Sección 2 del módulo
-- puede funcionar mientras la Sección 1 no. Se otorga a nivel de
-- esquema (no solo sobre la tabla de prueba) para que la detección de
-- estadísticas funcione sobre cualquier tabla futura de dbo, sin tener
-- que repetir este permiso cada vez. Sigue siendo de solo lectura.
IF NOT EXISTS (
    SELECT 1
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    WHERE pr.name = N'adminsgbd_consulta'
      AND dp.permission_name = N'SELECT'
      AND dp.class = 3 -- 3 = permiso sobre un esquema
      AND dp.major_id = SCHEMA_ID('dbo')
)
BEGIN
    GRANT SELECT ON SCHEMA::dbo TO [adminsgbd_consulta];
    PRINT 'Permiso SELECT sobre el esquema dbo otorgado a adminsgbd_consulta.';
END
ELSE
BEGIN
    PRINT 'adminsgbd_consulta ya tiene SELECT sobre el esquema dbo.';
END
GO

-- 2) Esquema monitoreo (ya debería existir desde la Semana 5; se crea
-- aquí también por si esta instancia nunca llegó a esa semana).
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'monitoreo')
BEGIN
    EXEC('CREATE SCHEMA monitoreo');
    PRINT 'Esquema monitoreo creado.';
END
ELSE
BEGIN
    PRINT 'El esquema monitoreo ya existe.';
END
GO

-- 3) Tabla de registro de mantenimiento.
IF OBJECT_ID('monitoreo.RegistroMantenimiento', 'U') IS NULL
BEGIN
    CREATE TABLE monitoreo.RegistroMantenimiento (
        id              INT IDENTITY(1,1) PRIMARY KEY,
        fecha_hora      DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
        operacion       NVARCHAR(100)   NOT NULL,
        objeto          NVARCHAR(256)   NOT NULL,
        usuario_login   NVARCHAR(128)   NOT NULL DEFAULT SUSER_SNAME(),
        resultado       NVARCHAR(20)    NOT NULL,
        detalle         NVARCHAR(1000)  NULL,

        CONSTRAINT CK_RegistroMantenimiento_Resultado
            CHECK (resultado IN (N'Exitoso', N'Fallido'))
    );

    PRINT 'Tabla monitoreo.RegistroMantenimiento creada.';
END
ELSE
BEGIN
    PRINT 'La tabla monitoreo.RegistroMantenimiento ya existe.';
END
GO

-- 4) El consultivo solo puede LEER el historial, nunca escribirlo.
IF NOT EXISTS (
    SELECT 1
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    JOIN sys.objects o ON dp.major_id = o.object_id
    WHERE pr.name = N'adminsgbd_consulta'
      AND o.name = N'RegistroMantenimiento'
      AND dp.permission_name = N'SELECT'
)
BEGIN
    GRANT SELECT ON monitoreo.RegistroMantenimiento TO [adminsgbd_consulta];
    PRINT 'Permiso SELECT otorgado a adminsgbd_consulta sobre monitoreo.RegistroMantenimiento.';
END
ELSE
BEGIN
    PRINT 'adminsgbd_consulta ya tiene SELECT sobre monitoreo.RegistroMantenimiento.';
END
GO
