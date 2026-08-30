# Sistema para el monitoreo, administración y auditoría de un SGBD

Proyecto grupal del curso EIF402 — Administración de Bases de Datos de la Universidad Nacional de Costa Rica.

## Descripción

El proyecto consiste en desarrollar una aplicación web local que permita monitorear, administrar y auditar una instancia de Microsoft SQL Server.

La aplicación obtendrá información real directamente del SGBD y la presentará mediante indicadores, tablas y gráficos que faciliten su interpretación. También permitirá ejecutar actividades básicas de mantenimiento preventivo.

## Tecnologías seleccionadas

- Microsoft SQL Server.
- Python.
- Streamlit.
- `pyodbc`.
- Plotly.
- Git y GitHub.

## Módulos

1. Estado general de la instancia.
2. Monitoreo de rendimiento.
3. Gestión del almacenamiento.
4. Respaldo y recuperación.
5. Auditoría.
6. Mantenimiento preventivo.

## Arquitectura

La solución utilizará una arquitectura modular con separación entre:

- Presentación.
- Lógica de la aplicación.
- Acceso a datos.
- Microsoft SQL Server.

La descripción completa se encuentra en [docs/arquitectura/arquitectura.md](docs/arquitectura/arquitectura.md).

## Estructura prevista

```text
proyecto-admin-sgbd/
├── app/
├── config/
├── docs/
│   ├── arquitectura/
│   ├── bitacora/
│   ├── manuales/
│   └── pruebas/
├── evidencias/
├── sql/
│   ├── 00-configuracion/
│   ├── 01-estado-instancia/
│   ├── 02-rendimiento/
│   ├── 03-almacenamiento/
│   ├── 04-respaldos/
│   ├── 05-auditoria/
│   └── 06-mantenimiento/
├── README.md
└── .gitignore
```

## Integrantes

- Juan Artavia.
- Javier Garita.
- Mariana Madrigal.
- Nicole Masís.
- Andrey Solís.
