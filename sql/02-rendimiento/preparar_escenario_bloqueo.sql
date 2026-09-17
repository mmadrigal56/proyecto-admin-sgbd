/*
    Proyecto: Administración de Bases de Datos
    Semana: 4
    Módulo: 2 - Monitoreo de rendimiento
    Archivo: preparar_escenario_bloqueo.sql

    Propósito:
    Generar de forma controlada un bloqueo real en SQL Server, para
    poder demostrar y capturar evidencia de la consulta de sesiones
    bloqueadas/bloqueadoras (sql/02-rendimiento/consultas_rendimiento.sql,
    sección 3), y para probar que la aplicación distingue correctamente
    entre "sin bloqueos" y "hay un bloqueo".

    Este archivo NO se ejecuta completo de una sola vez. Contiene dos
    bloques separados (SESIÓN A y SESIÓN B) que deben ejecutarse en dos
    pestañas de consulta distintas de SSMS, abiertas al mismo tiempo.

    Tabla utilizada: se usa la tabla del sistema sys.objects únicamente
    como ejemplo neutral; si el proyecto ya tiene una tabla propia de
    pruebas, se puede sustituir aquí. Por ahora se crea una tabla mínima
    y desechable solo para este propósito.
*/

-- =========================================================
-- Preparación (ejecutar una sola vez, en cualquier pestaña,
-- antes de abrir las dos sesiones)
-- =========================================================
USE BD_AdminSGBD;
GO

IF OBJECT_ID('dbo.PruebaBloqueo', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.PruebaBloqueo (
        id INT PRIMARY KEY,
        valor NVARCHAR(50)
    );

    INSERT INTO dbo.PruebaBloqueo (id, valor) VALUES (1, 'inicial');

    PRINT 'Tabla dbo.PruebaBloqueo creada con una fila de prueba.';
END
ELSE
BEGIN
    PRINT 'La tabla dbo.PruebaBloqueo ya existe.';
END
GO


-- =========================================================
-- SESIÓN A — ejecutar en la PRIMERA pestaña de consulta
-- =========================================================
-- Abre una transacción y modifica la fila, pero NO la termina
-- (no hay COMMIT ni ROLLBACK todavía). Esto mantiene un bloqueo
-- de escritura activo sobre esa fila hasta que se cierre la
-- transacción manualmente (ver instrucciones al final).

USE BD_AdminSGBD;
GO

BEGIN TRANSACTION;

UPDATE dbo.PruebaBloqueo
SET valor = 'modificado por sesion A'
WHERE id = 1;

-- NO ejecutar COMMIT ni ROLLBACK todavía.
-- Dejar esta pestaña tal cual, con la transacción abierta.


-- =========================================================
-- SESIÓN B — ejecutar en una SEGUNDA pestaña de consulta,
-- mientras la Sesión A sigue con su transacción abierta
-- =========================================================
-- Intenta leer la misma fila. Como la Sesión A tiene un bloqueo
-- de escritura sobre ella y no lo ha liberado, esta consulta se
-- queda esperando (no da error, simplemente no termina de
-- ejecutarse hasta que la Sesión A haga COMMIT o ROLLBACK).

USE BD_AdminSGBD;
GO

SELECT *
FROM dbo.PruebaBloqueo
WHERE id = 1;


-- =========================================================
-- Para liberar el bloqueo cuando ya se haya capturado la evidencia
-- =========================================================
-- Volver a la pestaña de la SESIÓN A y ejecutar:
--
--     ROLLBACK TRANSACTION;
--
-- Esto libera el bloqueo, la Sesión B termina de ejecutarse
-- inmediatamente, y la fila queda como estaba antes de la prueba
-- (por eso se usa ROLLBACK y no COMMIT: no queremos dejar el
-- cambio de prueba guardado permanentemente).