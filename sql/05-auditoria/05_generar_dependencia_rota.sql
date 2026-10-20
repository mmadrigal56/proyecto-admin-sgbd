/*
    Proyecto: Administración de Bases de Datos
    Semana: 9 - Integración y pruebas
    Módulo: 5 - Auditoría
    Archivo: 05_generar_dependencia_rota.sql

    Propósito:
    Generar un objeto problemático real para probar la pestaña
    "Objetos Problemáticos" de la página de Auditoría. Se crea una tabla,
    una vista que depende de ella y luego se borra la tabla, de modo que
    la vista queda con una dependencia rota.

    Resultado esperado en la aplicación:
    la vista dbo.vw_PruebaDependencia aparece como objeto con dependencia
    rota, con MissingDependency = PruebaDependencia.

    Ejecutar como administrador. Para dejar la base como estaba, ejecutar
    después 06_limpiar_dependencia_rota.sql.
*/

USE BD_AdminSGBD;
GO

IF OBJECT_ID(N'dbo.vw_PruebaDependencia', N'V') IS NOT NULL
    DROP VIEW dbo.vw_PruebaDependencia;
GO

IF OBJECT_ID(N'dbo.PruebaDependencia', N'U') IS NOT NULL
    DROP TABLE dbo.PruebaDependencia;
GO

CREATE TABLE dbo.PruebaDependencia (id INT NOT NULL);
GO

-- Sin SCHEMABINDING, para que SQL Server permita borrar la tabla.
CREATE VIEW dbo.vw_PruebaDependencia
AS
SELECT id FROM dbo.PruebaDependencia;
GO

DROP TABLE dbo.PruebaDependencia;
GO

PRINT 'Dependencia rota generada: dbo.vw_PruebaDependencia apunta a una tabla que ya no existe.';
GO
