/*
    Proyecto: Administración de Bases de Datos
    Semana: 5 - Módulo 3: Gestión del almacenamiento
    Archivo: 03_generar_carga_prueba.sql

    Inserta filas reales en una tabla de prueba para generar crecimiento
    medible (~12 MB por ejecución). Ejecutar como administrador.
*/

USE BD_AdminSGBD;
GO

IF SCHEMA_ID(N'prueba') IS NULL
    EXEC (N'CREATE SCHEMA prueba AUTHORIZATION dbo;');
GO

IF OBJECT_ID(N'prueba.CargaAlmacenamiento', N'U') IS NULL
BEGIN
    CREATE TABLE prueba.CargaAlmacenamiento
    (
        id           INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_CargaAlmacenamiento PRIMARY KEY CLUSTERED,
        fecha_carga  DATETIME2(0)  NOT NULL CONSTRAINT DF_Carga_fecha DEFAULT (SYSDATETIME()),
        codigo       CHAR(10)      NOT NULL,
        descripcion  NVARCHAR(200) NOT NULL,
        relleno      CHAR(400)     NOT NULL
    );

    CREATE NONCLUSTERED INDEX IX_Carga_codigo
        ON prueba.CargaAlmacenamiento (codigo)
        INCLUDE (descripcion);

    PRINT 'Tabla prueba.CargaAlmacenamiento creada.';
END
GO

DECLARE @lotes INT = 20;   -- 1 lote = 1000 filas
DECLARE @i INT = 0;

WHILE @i < @lotes
BEGIN
    INSERT INTO prueba.CargaAlmacenamiento (codigo, descripcion, relleno)
    SELECT TOP (1000)
        RIGHT(REPLICATE('0', 10) + CAST(ABS(CAST(CHECKSUM(NEWID()) AS BIGINT)) % 1000000000 AS VARCHAR(10)), 10),
        N'Registro de carga de prueba del módulo 3, lote ' + CAST(@i + 1 AS NVARCHAR(10)),
        REPLICATE('x', 400)
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b;

    SET @i += 1;
END;

SELECT
    COUNT(*)          AS filas_totales_en_tabla,
    MIN(fecha_carga)  AS primera_carga,
    MAX(fecha_carga)  AS ultima_carga
FROM prueba.CargaAlmacenamiento;
GO
