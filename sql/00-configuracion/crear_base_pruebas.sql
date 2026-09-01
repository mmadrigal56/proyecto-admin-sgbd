/*
Proyecto: Administración de Bases de Datos
Semana: 2
Archivo: crear_base_pruebas.sql

```
Propósito:
Crear la base de datos utilizada para las pruebas iniciales
de la aplicación de administración de SQL Server.
```

*/

USE master;
GO

IF DB_ID(N'BD_AdminSGBD') IS NULL
BEGIN
CREATE DATABASE BD_AdminSGBD;
PRINT 'Base de datos BD_AdminSGBD creada correctamente.';
END
ELSE
BEGIN
PRINT 'La base de datos BD_AdminSGBD ya existe.';
END
GO
