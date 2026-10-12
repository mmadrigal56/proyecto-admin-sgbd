/*
    Proyecto: Administración de Bases de Datos
    Semana: 8
    Módulo: 6 - Mantenimiento preventivo
    Archivo: 03_crear_procedimientos_mantenimiento.sql

    Propósito:
    Crear los dos procedimientos que ejecutan las operaciones de
    mantenimiento REALES permitidas en este módulo:

    - mantenimiento.sp_actualizar_estadisticas: recalcula las
      estadísticas de una tabla (UPDATE STATISTICS).
    - mantenimiento.sp_reconstruir_indice: reorganiza o reconstruye
      un índice (ALTER INDEX REORGANIZE / REBUILD).

    Ambos procedimientos:
    - Verifican primero que el objeto exista (si no existe, fallan
      de forma controlada y comprensible, en vez de un error crudo
      de SQL Server). Esto es lo que permite probar el "caso fallido"
      exigido por el cronograma sin dañar nada real.
    - Registran SIEMPRE el resultado (éxito o fallo) en
      monitoreo.RegistroMantenimiento, usando encadenamiento de
      propiedad: el procedimiento y la tabla son del mismo dueño
      (dbo), por lo que no hace falta otorgar INSERT directo sobre
      la tabla al usuario administrativo.
    - Solo pueden ser ejecutados por adminsgbd_mantenimiento (ver
      los GRANT EXECUTE al final de este archivo). El usuario
      consultivo NUNCA tiene permiso para ejecutarlos.

    Ejecutar como administrador (sysadmin), después de
    02_otorgar_permisos_mantenimiento.sql.
*/

USE BD_AdminSGBD;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'mantenimiento')
BEGIN
    EXEC('CREATE SCHEMA mantenimiento');
    PRINT 'Esquema mantenimiento creado.';
END
GO

-- =========================================================
-- sp_actualizar_estadisticas
-- =========================================================
CREATE OR ALTER PROCEDURE mantenimiento.sp_actualizar_estadisticas
    @esquema NVARCHAR(128),
    @tabla   NVARCHAR(128)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @objeto_completo NVARCHAR(300) = @esquema + N'.' + @tabla;
    DECLARE @sql NVARCHAR(400);
    DECLARE @mensaje_error NVARCHAR(1000);

    -- Validación previa: si el objeto no existe, se registra un
    -- fallo controlado y comprensible (no se intenta ejecutar nada
    -- sobre un objeto inexistente).
    IF OBJECT_ID(@objeto_completo, N'U') IS NULL
    BEGIN
        SET @mensaje_error = N'La tabla ' + @objeto_completo + N' no existe en esta base de datos.';

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Actualizar estadísticas', @objeto_completo, N'Fallido', @mensaje_error);

        THROW 50001, @mensaje_error, 1;
    END

    BEGIN TRY
        SET @sql = N'UPDATE STATISTICS ' + QUOTENAME(@esquema) + N'.' + QUOTENAME(@tabla) + N' WITH FULLSCAN;';
        EXEC sp_executesql @sql;

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Actualizar estadísticas', @objeto_completo, N'Exitoso', N'UPDATE STATISTICS WITH FULLSCAN ejecutado correctamente.');
    END TRY
    BEGIN CATCH
        SET @mensaje_error = ERROR_MESSAGE();

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Actualizar estadísticas', @objeto_completo, N'Fallido', @mensaje_error);

        THROW;
    END CATCH
END
GO

-- =========================================================
-- sp_reconstruir_indice
-- =========================================================
-- @modo: 'REORGANIZE' (fragmentación leve, 5%-30%, operación en línea)
--        'REBUILD'     (fragmentación alta, > 30%)
CREATE OR ALTER PROCEDURE mantenimiento.sp_reconstruir_indice
    @esquema NVARCHAR(128),
    @tabla   NVARCHAR(128),
    @indice  NVARCHAR(128),
    @modo    NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @objeto_completo NVARCHAR(400) = @esquema + N'.' + @tabla + N' (' + @indice + N')';
    DECLARE @sql NVARCHAR(500);
    DECLARE @mensaje_error NVARCHAR(1000);

    IF OBJECT_ID(@esquema + N'.' + @tabla, N'U') IS NULL
    BEGIN
        SET @mensaje_error = N'La tabla ' + @esquema + N'.' + @tabla + N' no existe en esta base de datos.';

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Mantenimiento de índice', @objeto_completo, N'Fallido', @mensaje_error);

        THROW 50002, @mensaje_error, 1;
    END

    IF NOT EXISTS (
        SELECT 1 FROM sys.indexes
        WHERE object_id = OBJECT_ID(@esquema + N'.' + @tabla) AND name = @indice
    )
    BEGIN
        SET @mensaje_error = N'El índice ' + @indice + N' no existe sobre ' + @esquema + N'.' + @tabla + N'.';

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Mantenimiento de índice', @objeto_completo, N'Fallido', @mensaje_error);

        THROW 50003, @mensaje_error, 1;
    END

    IF @modo NOT IN (N'REORGANIZE', N'REBUILD')
    BEGIN
        SET @mensaje_error = N'Modo no válido: ' + @modo + N'. Debe ser REORGANIZE o REBUILD.';

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Mantenimiento de índice', @objeto_completo, N'Fallido', @mensaje_error);

        THROW 50004, @mensaje_error, 1;
    END

    BEGIN TRY
        SET @sql = N'ALTER INDEX ' + QUOTENAME(@indice) + N' ON ' + QUOTENAME(@esquema) + N'.' + QUOTENAME(@tabla)
                 + N' ' + @modo + N';';
        EXEC sp_executesql @sql;

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Mantenimiento de índice', @objeto_completo, N'Exitoso', @modo + N' ejecutado correctamente.');
    END TRY
    BEGIN CATCH
        SET @mensaje_error = ERROR_MESSAGE();

        INSERT INTO monitoreo.RegistroMantenimiento (operacion, objeto, resultado, detalle)
        VALUES (N'Mantenimiento de índice', @objeto_completo, N'Fallido', @mensaje_error);

        THROW;
    END CATCH
END
GO

-- =========================================================
-- Permisos: SOLO el usuario administrativo puede ejecutar estos
-- procedimientos. El consultivo nunca recibe EXECUTE sobre ellos.
-- =========================================================
GRANT EXECUTE ON mantenimiento.sp_actualizar_estadisticas TO [adminsgbd_mantenimiento];
GRANT EXECUTE ON mantenimiento.sp_reconstruir_indice     TO [adminsgbd_mantenimiento];
GO

PRINT 'Procedimientos de mantenimiento creados y permisos otorgados.';
