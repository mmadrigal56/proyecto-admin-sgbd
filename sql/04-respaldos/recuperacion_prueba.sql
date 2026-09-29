-- Restauración de prueba de BD_AdminSGBD.
-- Ejecutar en SSMS con una cuenta administradora.
-- Crea otra base; no restaura sobre la base original.

RESTORE VERIFYONLY
FROM DISK = N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\Backup\BD_AdminSGBD_prueba.bak'
WITH CHECKSUM;
GO

RESTORE FILELISTONLY
FROM DISK = N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\Backup\BD_AdminSGBD_prueba.bak';
GO

-- Antes de ejecutar este bloque, verificar que la base de prueba no exista.
RESTORE DATABASE [BD_AdminSGBD_PruebaRestauracion]
FROM DISK = N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\Backup\BD_AdminSGBD_prueba.bak'
WITH
    MOVE N'BD_AdminSGBD'
        TO N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\DATA\BD_AdminSGBD_PruebaRestauracion.mdf',
    MOVE N'BD_AdminSGBD_log'
        TO N'C:\Program Files\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQL\DATA\BD_AdminSGBD_PruebaRestauracion_log.ldf',
    CHECKSUM,
    STATS = 10;
GO