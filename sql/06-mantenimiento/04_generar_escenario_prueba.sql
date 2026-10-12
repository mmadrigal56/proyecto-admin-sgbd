/*
    Proyecto: Administración de Bases de Datos
    Semana: 8
    Módulo: 6 - Mantenimiento preventivo
    Archivo: 04_generar_escenario_prueba.sql

    Propósito:
    Generar, de forma controlada, una tabla con un índice fragmentado
    y estadísticas desactualizadas, para poder probar con datos REALES
    la detección y el mantenimiento del Módulo 6 (y no depender de que
    la base ya tenga algo fragmentado por casualidad).

    Esto es equivalente, para este módulo, a lo que
    preparar_escenario_bloqueo.sql hizo para el Módulo 2 (Semana 4):
    un escenario reproducible, no datos simulados en la aplicación.

    Nota técnica importante:
    Con una clave IDENTITY secuencial, simplemente borrar filas NO
    fragmenta el índice: SQL Server sigue insertando las filas nuevas
    al final, no en los huecos dejados por el DELETE. La fragmentación
    real se produce por "page splits": cuando una fila existente crece
    de tamaño (por ejemplo, un UPDATE que alarga una columna de texto)
    y ya no cabe en su página, SQL Server mueve la mitad de la página
    a una página nueva. Si eso ocurre en filas dispersas (no
    consecutivas), el índice queda fragmentado de forma realista.
    Por eso este script actualiza filas intercaladas (id % 7, id % 11)
    en vez de borrarlas.

    Esta tabla (dbo.PruebaMantenimiento) es desechable y se recrea
    cada vez que se ejecuta este script, para obtener un resultado
    reproducible.

    Ejecutar una sola vez (o cada vez que se quiera repetir la prueba),
    con cualquier usuario con permisos de escritura sobre BD_AdminSGBD
    (no necesita ser el usuario administrativo del Módulo 6; esto es
    solo para preparar datos de prueba, no es una operación de
    mantenimiento del módulo).
*/

USE BD_AdminSGBD;
GO

IF OBJECT_ID('dbo.PruebaMantenimiento', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.PruebaMantenimiento;
    PRINT 'Tabla dbo.PruebaMantenimiento anterior eliminada (se recrea para un resultado reproducible).';
END
GO

CREATE TABLE dbo.PruebaMantenimiento (
    id      INT IDENTITY(1,1) PRIMARY KEY,
    valor   NVARCHAR(1000)
);
GO

CREATE INDEX IX_PruebaMantenimiento_valor ON dbo.PruebaMantenimiento(valor);
GO

-- 1) Insertar filas con valores cortos.
INSERT INTO dbo.PruebaMantenimiento (valor)
SELECT TOP (8000) CONCAT('v', ABS(CHECKSUM(NEWID())) % 100000)
FROM sys.all_objects a CROSS JOIN sys.all_objects b;
GO

-- 2) Alargar el valor de filas dispersas (no consecutivas). Esto obliga
--    a SQL Server a dividir páginas (page splits) por toda la tabla y
--    el índice no agrupado, generando fragmentación real y medible.
--    También incrementa el contador de modificaciones de las
--    estadísticas, lo que hace que queden desactualizadas (esperado:
--    es justo lo que la consulta 1 de consultas_mantenimiento.sql
--    debe detectar).
UPDATE dbo.PruebaMantenimiento
SET valor = CONCAT(valor, '-', REPLICATE(CAST('x' AS NVARCHAR(400)), 400))
WHERE id % 7 = 0;
GO

UPDATE dbo.PruebaMantenimiento
SET valor = CONCAT(valor, '-', REPLICATE(CAST('y' AS NVARCHAR(400)), 400))
WHERE id % 11 = 0;
GO

PRINT 'Escenario de prueba generado: dbo.PruebaMantenimiento tiene fragmentación y estadísticas desactualizadas reales.';
GO
