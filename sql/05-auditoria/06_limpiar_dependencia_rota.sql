/*
    Proyecto: Administración de Bases de Datos
    Semana: 9 - Integración y pruebas
    Módulo: 5 - Auditoría
    Archivo: 06_limpiar_dependencia_rota.sql

    Propósito:
    Eliminar los objetos creados por 05_generar_dependencia_rota.sql
    para dejar la base de datos como estaba antes de la prueba.

    Ejecutar como administrador.
*/

USE BD_AdminSGBD;
GO

IF OBJECT_ID(N'dbo.vw_PruebaDependencia', N'V') IS NOT NULL
BEGIN
    DROP VIEW dbo.vw_PruebaDependencia;
    PRINT 'Vista dbo.vw_PruebaDependencia eliminada.';
END
ELSE
    PRINT 'La vista dbo.vw_PruebaDependencia no existe.';
GO

IF OBJECT_ID(N'dbo.PruebaDependencia', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.PruebaDependencia;
    PRINT 'Tabla dbo.PruebaDependencia eliminada.';
END
GO
