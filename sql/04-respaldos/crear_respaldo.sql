-- Ejecutar en SSMS con una cuenta autorizada para respaldar la base.
-- Usa la carpeta predeterminada de respaldos de esta instancia.

DECLARE @carpeta nvarchar(4000) =
    CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS nvarchar(4000));

DECLARE @archivo nvarchar(4000) =
    @carpeta +
    CASE WHEN RIGHT(@carpeta, 1) IN (N'\', N'/')
         THEN N'' ELSE N'\' END +
    N'BD_AdminSGBD_' +
    CONVERT(char(8), GETDATE(), 112) + N'_' +
    REPLACE(CONVERT(char(8), GETDATE(), 108), ':', '') +
    N'.bak';

BACKUP DATABASE [BD_AdminSGBD]
TO DISK = @archivo
WITH CHECKSUM, STATS = 10;

SELECT @archivo AS archivo_creado;
GO