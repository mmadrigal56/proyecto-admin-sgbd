/*
    Proyecto: Administración de Bases de Datos
    Semana: 9 - Integración y pruebas
    Módulo: 5 - Auditoría
    Archivo: 00_otorgar_permisos_auditoria.sql

    Permisos de SOLO LECTURA de metadatos que necesita el usuario
    consultivo para que la página de Auditoría muestre información
    completa y no falle:
      - VIEW ANY DEFINITION (servidor): ver todos los logins y roles
        de servidor. Sin él, SQL Server oculta lo que el usuario no
        posee y la lista sale incompleta, sin dar error.
      - SELECT sobre sys.sql_expression_dependencies (base): consulta
        de objetos con dependencias rotas.
    No permite leer datos de tablas ni modificar nada.

    Ejecutar como administrador, una vez por máquina.
*/

USE master;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'adminsgbd_consulta')
BEGIN
    GRANT VIEW ANY DEFINITION TO [adminsgbd_consulta];
    PRINT 'VIEW ANY DEFINITION otorgado a adminsgbd_consulta.';
END
ELSE
    PRINT 'El login adminsgbd_consulta no existe. Ejecutar primero sql/00-configuracion/crear_usuario_consultivo.sql.';
GO

USE BD_AdminSGBD;
GO

IF DATABASE_PRINCIPAL_ID(N'adminsgbd_consulta') IS NOT NULL
BEGIN
    GRANT SELECT ON sys.sql_expression_dependencies TO [adminsgbd_consulta];
    PRINT 'SELECT sobre sys.sql_expression_dependencies otorgado a adminsgbd_consulta.';
END
ELSE
    PRINT 'El usuario adminsgbd_consulta no existe en BD_AdminSGBD.';
GO
