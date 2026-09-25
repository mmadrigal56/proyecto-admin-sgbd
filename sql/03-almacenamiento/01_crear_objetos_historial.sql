/*
    Proyecto: Administración de Bases de Datos
    Semana: 5 - Módulo 3: Gestión del almacenamiento
    Archivo: 01_crear_objetos_historial.sql

    Crea el esquema monitoreo, la tabla de historial, el procedimiento
    de captura y la vista resumen. Ejecutar como administrador.
*/

USE BD_AdminSGBD;
GO

-- Dueño dbo: permite que el usuario consultivo ejecute el procedimiento
-- sin tener INSERT sobre la tabla (encadenamiento de propiedad).
IF SCHEMA_ID(N'monitoreo') IS NULL
    EXEC (N'CREATE SCHEMA monitoreo AUTHORIZATION dbo;');
GO

IF OBJECT_ID(N'monitoreo.HistorialAlmacenamiento', N'U') IS NULL
BEGIN
    CREATE TABLE monitoreo.HistorialAlmacenamiento
    (
        id_registro            INT IDENTITY(1,1) NOT NULL,
        fecha_captura          DATETIME2(0)      NOT NULL,
        base_datos             SYSNAME           NOT NULL,
        nombre_logico          SYSNAME           NOT NULL,
        tipo_archivo           NVARCHAR(60)      NOT NULL,
        filegroup              SYSNAME           NULL,
        tamano_asignado_mb     DECIMAL(18,2)     NOT NULL,
        espacio_usado_mb       DECIMAL(18,2)     NOT NULL,
        espacio_disponible_mb  DECIMAL(18,2)     NOT NULL,
        origen                 NVARCHAR(30)      NOT NULL,
        registrado_por         SYSNAME           NOT NULL
            CONSTRAINT DF_HistAlm_registrado_por DEFAULT (ORIGINAL_LOGIN()),

        CONSTRAINT PK_HistorialAlmacenamiento PRIMARY KEY CLUSTERED (id_registro),
        CONSTRAINT CK_HistAlm_valores_no_negativos CHECK (
            tamano_asignado_mb >= 0 AND espacio_usado_mb >= 0 AND espacio_disponible_mb >= 0
        )
    );

    CREATE INDEX IX_HistAlm_fecha
        ON monitoreo.HistorialAlmacenamiento (fecha_captura);

    PRINT 'Tabla monitoreo.HistorialAlmacenamiento creada.';
END
ELSE
    PRINT 'La tabla monitoreo.HistorialAlmacenamiento ya existe (se conservan sus datos).';
GO

-- size y SpaceUsed vienen en páginas de 8 KB: MB = páginas * 8 / 1024.
CREATE OR ALTER PROCEDURE monitoreo.sp_capturar_almacenamiento
    @origen NVARCHAR(30) = N'manual'
AS
BEGIN
    SET NOCOUNT ON;

    IF @origen NOT IN (N'programado', N'manual', N'aplicacion')
        THROW 50001, N'Origen no válido. Use: programado, manual o aplicacion.', 1;

    DECLARE @fecha DATETIME2(0) = SYSDATETIME();

    DECLARE @medicion TABLE
    (
        nombre_logico     SYSNAME,
        tipo_archivo      NVARCHAR(60),
        filegroup         SYSNAME NULL,
        paginas_asignadas BIGINT,
        paginas_usadas    BIGINT NULL
    );

    INSERT INTO @medicion (nombre_logico, tipo_archivo, filegroup, paginas_asignadas, paginas_usadas)
    SELECT
        df.name,
        df.type_desc,
        fg.name,
        CAST(df.size AS BIGINT),
        CAST(FILEPROPERTY(df.name, 'SpaceUsed') AS BIGINT)
    FROM sys.database_files AS df
    LEFT JOIN sys.filegroups AS fg
        ON fg.data_space_id = df.data_space_id
    WHERE df.type IN (0, 1);

    IF EXISTS (SELECT 1 FROM @medicion WHERE paginas_usadas IS NULL)
        THROW 50002, N'No se pudo leer el espacio usado de uno o más archivos (permisos insuficientes). No se registró la medición.', 1;

    INSERT INTO monitoreo.HistorialAlmacenamiento
        (fecha_captura, base_datos, nombre_logico, tipo_archivo, filegroup,
         tamano_asignado_mb, espacio_usado_mb, espacio_disponible_mb, origen)
    SELECT
        @fecha,
        DB_NAME(),
        nombre_logico,
        tipo_archivo,
        filegroup,
        paginas_asignadas * 8 / 1024.0,
        paginas_usadas * 8 / 1024.0,
        (paginas_asignadas - paginas_usadas) * 8 / 1024.0,
        @origen
    FROM @medicion;

    SELECT
        fecha_captura, base_datos, nombre_logico, tipo_archivo, filegroup,
        tamano_asignado_mb, espacio_usado_mb, espacio_disponible_mb, origen, registrado_por
    FROM monitoreo.HistorialAlmacenamiento
    WHERE fecha_captura = @fecha
    ORDER BY tipo_archivo DESC, nombre_logico;
END;
GO

CREATE OR ALTER VIEW monitoreo.vw_resumen_historial
AS
SELECT
    fecha_captura,
    base_datos,
    MAX(origen) AS origen,
    SUM(CASE WHEN tipo_archivo = N'ROWS' THEN tamano_asignado_mb    ELSE 0 END) AS datos_asignado_mb,
    SUM(CASE WHEN tipo_archivo = N'ROWS' THEN espacio_usado_mb      ELSE 0 END) AS datos_usado_mb,
    SUM(CASE WHEN tipo_archivo = N'ROWS' THEN espacio_disponible_mb ELSE 0 END) AS datos_disponible_mb,
    SUM(CASE WHEN tipo_archivo = N'LOG'  THEN tamano_asignado_mb    ELSE 0 END) AS log_asignado_mb,
    SUM(CASE WHEN tipo_archivo = N'LOG'  THEN espacio_usado_mb      ELSE 0 END) AS log_usado_mb,
    SUM(tamano_asignado_mb) AS total_asignado_mb,
    SUM(espacio_usado_mb)   AS total_usado_mb
FROM monitoreo.HistorialAlmacenamiento
GROUP BY fecha_captura, base_datos;
GO
