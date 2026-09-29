# Semana 06 — Respaldos y recuperación

## 1. Información general

- Responsable: Mariana Madrigal
- Fecha: 2026-09-29
- Objetivo: implementar el módulo 4 para consultar respaldos de SQL Server y comprobar una recuperación real.

## 2. Estado recibido

- El proyecto ya tenía conexión mediante `pyodbc` y los módulos 1, 2 y 3 en Streamlit.
- Se configuró localmente `BD_AdminSGBD` y el usuario consultivo `adminsgbd_consulta`.
- Antes de las pruebas, `msdb.dbo.backupset` no tenía registros para esta base.

## 3. Trabajo realizado

### Respaldos reales

- Se creó un respaldo completo de prueba con `COPY_ONLY` y `CHECKSUM` a las 07:57:54.
- `RESTORE VERIFYONLY WITH CHECKSUM` indicó que el conjunto de respaldo era válido.
- Se creó otro respaldo completo a las 08:42:20 mediante `sql/04-respaldos/crear_respaldo.sql`.
- Ambos respaldos aparecen en `msdb.dbo.backupset` y sus rutas en `msdb.dbo.backupmediafamily`.

### Recuperación de prueba

- Se consultaron los nombres lógicos con `RESTORE FILELISTONLY`.
- Se restauró el primer respaldo como `BD_AdminSGBD_PruebaRestauracion`, usando `MOVE` para crear archivos físicos separados.
- Se comprobó que la base restaurada estaba `ONLINE` y que contenía `monitoreo.HistorialAlmacenamiento`.
- El procedimiento utilizado quedó en `sql/04-respaldos/recuperacion_prueba.sql`.

### Módulo 4 en Streamlit

- `app/database/queries/respaldos.py` consulta el historial de respaldos de la base configurada.
- `app/pages/4_Respaldos.py` muestra fecha del último respaldo, tipo, tamaño, estado, antigüedad, historial y ubicación del archivo.
- Se muestra una advertencia cuando el último respaldo tiene más de 24 horas. Este umbral es una regla de monitoreo del proyecto.
- `sql/04-respaldos/consultas_respaldos.sql` conserva la consulta SQL utilizada.

## 4. Validación

| Prueba | Resultado |
|---|---|
| Consulta inicial de `backupset` | 0 filas antes de crear respaldos |
| Primer `BACKUP DATABASE` | Completado |
| `RESTORE VERIFYONLY WITH CHECKSUM` | Conjunto de respaldo válido |
| Restauración en otra base | Completada |
| Consulta en la base restaurada | Tabla `monitoreo.HistorialAlmacenamiento` encontrada |
| Segundo respaldo | Completado; aparece como el más reciente |
| Consulta con `adminsgbd_consulta` | Lee historial y rutas de los respaldos |
| Página Streamlit | Muestra dos respaldos y los indicadores |

## 5. Evidencias

- `semana_06_01_pagina_respaldos.png`: módulo 4 con el historial y los indicadores.
- `semana_06_02_restauracion_prueba.png`: historial de restauración con la base de prueba en estado `ONLINE`.

## 6. Límites y continuidad

- `msdb` registra respaldos realizados, pero sus filas no garantizan que el archivo siga existiendo ni que una restauración futura sea exitosa.
- `is_damaged = 0` indica que SQL Server no marcó daños durante el respaldo; no sustituye una restauración de prueba.
- Los respaldos creados están en el disco local de la instancia. Para protegerse ante una falla de ese disco se requiere otra ubicación o una copia externa.
- Los scripts de recuperación contienen rutas y nombres lógicos de esta instalación; otra instancia debe ajustarlos antes de ejecutarlos.
- La aplicación usa una cuenta consultiva. La creación y restauración de respaldos se ejecutaron en SSMS con la cuenta administradora.