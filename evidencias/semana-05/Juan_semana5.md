# Semana 05 — Resumen y continuidad

> **Borrador.** El código se escribió y se revisó fuera de la instancia real (con datos de prueba simulados solo para verificar la lógica de Python y Streamlit). Los campos `[COMPLETAR]` se llenan después de ejecutar todo contra el SQL Server de Juan. Nada se marca como "Aprobada" sin evidencia (regla de veracidad del cronograma).

## 1. Información general

- Responsable: Juan Artavia
- Fecha de inicio: 2026-09-24
- Fecha de cierre: [COMPLETAR]
- Semana del cronograma: 5
- Objetivo de la semana: Módulo 3 — mostrar el uso actual del almacenamiento y permitir comparar su crecimiento.

## 2. Estado recibido de la semana anterior

- Funcionalidades que ya estaban disponibles: conexión `pyodbc` (`app/database/connection.py`), Módulo 1 (estado de la instancia) y Módulo 2 (rendimiento) validados con capturas; usuario consultivo `adminsgbd_consulta` con `VIEW SERVER STATE`.
- Archivos o módulos recibidos: todo lo que estaba en `main` después del PR #8 (commit `425e1d2`).
- Problemas o pendientes heredados:
  - `Andrey_semana3.md` sigue con campos `[COMPLETAR]` (las capturas sí prueban que funcionó).
  - La Semana 4 no tiene entrada en `docs/bitacora/bitacora.md` (sí tiene `Nicky_semana4.md`).
  - Las páginas 1 y 2 usan `use_container_width=True`, que Streamlit 1.62 marca como obsoleto (se eliminará). Funciona, pero conviene cambiarlo a `width="stretch"` en la Semana 9 (integración). La página 3 ya usa `width="stretch"`.
- Decisiones anteriores que se conservaron: SQL Server + Python + Streamlit + pyodbc + Plotly; un único usuario consultivo con permisos mínimos; credenciales en `config/.env`; patrón `app/database/queries/<modulo>.py` + `app/pages/N_<Modulo>.py`; un `try/except` independiente por sección; límites TOP N en consultas de monitoreo.

## 3. Trabajo realizado

### Tarea 1 — Consultas de almacenamiento actual

- Qué se hizo: resumen de la base (datos y log: asignado, utilizado, disponible, %), archivos de datos y registro, filegroups, espacio en disco, edición (límite de Express), top N tablas y top N índices.
- Cómo se hizo: `sys.database_files` + `FILEPROPERTY(name, 'SpaceUsed')`, `sys.filegroups`, `sys.dm_os_volume_stats`, `SERVERPROPERTY`, `sys.dm_db_partition_stats` + `sys.objects` / `sys.indexes` / `sys.schemas`.
- Archivos: `sql/03-almacenamiento/consultas_almacenamiento.sql`, `app/database/queries/almacenamiento.py`.
- Resultado obtenido: [COMPLETAR — ejecutar en SSMS como `adminsgbd_consulta` y anotar tamaño real de BD_AdminSGBD]

### Tarea 2 — Tabla histórica y procedimiento de captura

- Qué se hizo: esquema `monitoreo`; tabla `monitoreo.HistorialAlmacenamiento` (una fila por archivo y por medición); procedimiento `monitoreo.sp_capturar_almacenamiento @origen`; vista `monitoreo.vw_resumen_historial` (una fila por medición).
- Cómo se hizo: el procedimiento lee el espacio real y lo inserta; no recibe cifras como parámetro, así nadie puede registrar valores inventados. Si `FILEPROPERTY` devuelve NULL (permisos), lanza error 50002 y no guarda nada.
- Archivos: `sql/03-almacenamiento/01_crear_objetos_historial.sql`.
- Resultado obtenido: [COMPLETAR]

### Tarea 3 — Permisos del módulo

- Qué se hizo: `VIEW DEFINITION` en la base, `SELECT` sobre el esquema `monitoreo`, `EXECUTE` sobre el procedimiento de captura.
- Archivos: `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql` (incluye una consulta de verificación de permisos al final).
- Resultado obtenido: [COMPLETAR — copiar la tabla de verificación]

### Tarea 4 — Captura periódica

- Qué se hizo: `scripts/capturar_almacenamiento.py` ejecuta el procedimiento con el usuario consultivo y escribe una línea en `logs/captura_almacenamiento.log`; `scripts/capturar_almacenamiento.bat` lo lanza con el Python del `.venv`; tarea `ProyectoSGBD_CapturaAlmacenamiento` en el Programador de tareas de Windows cada 6 horas (ver `docs/manuales/instalacion.md`, sección 11.1).
- Resultado obtenido: [COMPLETAR — cuántas mediciones reales, en qué fechas]

### Tarea 5 — Carga de prueba

- Qué se hizo: `sql/03-almacenamiento/03_generar_carga_prueba.sql` crea `prueba.CargaAlmacenamiento` (con índice no agrupado) e inserta 20 000 filas reales por ejecución (~12 MB).
- Por qué: BD_AdminSGBD está casi vacía; sin carga no hay tablas grandes que mostrar ni crecimiento que comparar. Son filas reales en SQL Server; las métricas se siguen leyendo del motor, no se simulan.
- Resultado obtenido: [COMPLETAR]

### Tarea 6 — Integración Streamlit

- Página: `app/pages/3_Almacenamiento.py`. Lógica de evaluación separada en `app/services/almacenamiento.py`.
- Secciones: indicadores de advertencia (arriba), tamaño de la base con gráfico apilado utilizado/disponible y límite de la edición, archivos, filegroups, disco, objetos de mayor tamaño (pestañas Tablas / Índices, control deslizante 5–30), historial con gráfico temporal Plotly, resumen de crecimiento y botón "Registrar una medición ahora".
- Manejo de errores: `try/except` por sección; si una sección falla, el panel de indicadores lo avisa en vez de decir "sin riesgos". Lista vacía se muestra como información, no como error.
- Resultado: [COMPLETAR con capturas]

## 4. Decisiones técnicas tomadas

| Decisión | Motivo | Consecuencia para las siguientes semanas |
|---|---|---|
| Captura periódica con el Programador de tareas de Windows | SQL Server Express no incluye SQL Server Agent | Cada integrante que quiera historial en su máquina debe crear la tarea. Mar (respaldos) y Andrey (mantenimiento) tampoco tendrán Agent para programar trabajos |
| `EXECUTE` sobre el procedimiento en vez de `INSERT` sobre la tabla | Mínimo privilegio: el usuario solo puede agregar mediciones que calcula SQL Server. Funciona por encadenamiento de propiedad (esquema, tabla y procedimiento son de `dbo`) | El usuario consultivo sigue sin poder escribir en tablas. Andrey puede usar el mismo patrón en el módulo 6 si le sirve |
| `VIEW DEFINITION` en `BD_AdminSGBD` | Sin él, la visibilidad de metadatos oculta tablas e índices (la sección saldría vacía sin error) | Javi (auditoría) probablemente lo necesite también; ya estará otorgado |
| Umbrales 80 % / 90 % contra el tamaño MÁXIMO del archivo; disco 20 % / 10 % libre | Un archivo con autocrecimiento lleno no es un riesgo; lo es acercarse al límite o quedarse sin disco | Documentado en la página |
| Límite de Express según versión: 10 GB (≤ 2022) / 50 GB (2025) | SQL Server 2025 Express subió el límite a 50 GB por base | Se calcula con `SERVERPROPERTY('EngineEdition')` y `ProductMajorVersion` |
| Nueva carpeta `app/services/` | Separar la lógica (umbrales, cálculos) de la presentación, como prevé la estructura base | Los módulos siguientes pueden poner su lógica ahí |
| El módulo mide la base de la conexión (`DB_NAME`) | `FILEPROPERTY` y `sys.database_files` solo funcionan en la base actual, y el usuario consultivo solo existe en `BD_AdminSGBD` | Para medir otra base habría que crear el usuario ahí y cambiar `DB_NAME` en `.env` |

## 5. Cambios respecto al plan original

### Cambio 1

- Forma en que debía hacerse originalmente (X): "crear un procedimiento o script que capture mediciones periódicas" — lo normal en SQL Server es un trabajo de SQL Server Agent.
- Por qué no fue posible: la edición Express no incluye SQL Server Agent.
- Error, limitación o evidencia encontrada: [COMPLETAR — p. ej. captura de SSMS sin el nodo "SQL Server Agent" o con "Agent XPs disabled"]
- Solución alternativa aplicada (Y): procedimiento almacenado + script Python + Programador de tareas de Windows.
- Consecuencias o limitaciones: las mediciones solo se toman con la computadora encendida y la sesión iniciada (se ejecutan al encender si se perdió una). El historial es local a cada máquina.
- ¿Debe revisarse después?: No.

## 6. Configuración actual

- SGBD y versión: [COMPLETAR]
- Nombre de instancia usado: [COMPLETAR]
- Versión de Python: [COMPLETAR]
- Versión del controlador ODBC: [COMPLETAR]
- Dependencias: sin cambios en `requirements.txt` (se usan pandas, plotly y streamlit ya incluidos).
- Variables o parámetros necesarios: los mismos de `config/.env.example`, sin variables nuevas.
- Permisos requeridos: `VIEW SERVER STATE` (heredado) + `VIEW DEFINITION`, `SELECT ON SCHEMA::monitoreo`, `EXECUTE ON monitoreo.sp_capturar_almacenamiento` (nuevos).
- Configuraciones que no deben subirse: `config/.env`, `logs/`.

## 7. Archivos importantes

| Archivo o carpeta | Propósito | Estado |
|---|---|---|
| `sql/03-almacenamiento/01_crear_objetos_historial.sql` | Esquema, tabla de historial, procedimiento y vista | Implementado, pendiente de validación |
| `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql` | Permisos del módulo + verificación | Implementado, pendiente de validación |
| `sql/03-almacenamiento/03_generar_carga_prueba.sql` | Carga real de prueba para mostrar crecimiento | Implementado, pendiente de validación |
| `sql/03-almacenamiento/consultas_almacenamiento.sql` | Consultas documentadas del módulo | Implementado, pendiente de validación |
| `app/database/queries/almacenamiento.py` | Capa de acceso a datos | Implementado, pendiente de validación |
| `app/services/almacenamiento.py` | Umbrales y cálculos | Implementado, lógica probada con datos simulados |
| `app/pages/3_Almacenamiento.py` | Página de Streamlit | Implementado, pendiente de validación |
| `scripts/capturar_almacenamiento.py` / `.bat` | Captura periódica | Implementado, pendiente de validación |

## 8. Consultas y operaciones administrativas

| Consulta | Vistas / funciones | Permiso | Limitación |
|---|---|---|---|
| Resumen de la base | `sys.database_files`, `FILEPROPERTY` | `VIEW DEFINITION` (si no, espacio usado = NULL) | Solo la base actual |
| Archivos | `sys.database_files`, `sys.filegroups` | ídem | — |
| Filegroups | `sys.filegroups`, `sys.database_files` | ídem | El log no pertenece a ningún filegroup |
| Disco | `sys.dm_os_volume_stats` | `VIEW SERVER STATE` | — |
| Tablas / índices más grandes | `sys.dm_db_partition_stats`, `sys.objects`, `sys.indexes` | `VIEW DATABASE STATE` (implícito por `VIEW SERVER STATE`) + `VIEW DEFINITION` | TOP N (5–30) |
| Historial | `monitoreo.vw_resumen_historial` | `SELECT` en `monitoreo` | Últimas 200 mediciones |
| Registrar medición | `monitoreo.sp_capturar_almacenamiento` | `EXECUTE` en el procedimiento | Única escritura del módulo; solo agrega filas |

## 9. Pruebas realizadas

| Prueba | Procedimiento | Resultado esperado | Resultado real | Estado |
|---|---|---|---|---|
| Lógica de la página con datos simulados | `streamlit.testing` (AppTest) con una conexión falsa, fuera del repositorio | Sin excepciones; advertencias correctas; secciones vacías como "info" | Sin excepciones; archivo al 95 % de su máximo → crítico; disco 8 % libre → crítico; crecimiento % → advertencia; servidor caído → 7 errores controlados y aviso de indicadores incompletos | Aprobada (solo lógica, no SQL real) |
| Script de captura con datos simulados | Éxito y error forzado | Código 0 / 1 y línea en el log | 0 con "OK", 1 con "ERROR" | Aprobada (solo lógica) |
| Crear objetos | Ejecutar `01_...sql` como admin | Mensajes de creación sin errores | [COMPLETAR] | Pendiente |
| Permisos | Ejecutar `02_...sql` como admin | Tabla de verificación con los 3 permisos | [COMPLETAR] | Pendiente |
| Consultas en SSMS como `adminsgbd_consulta` | `consultas_almacenamiento.sql` | Valores coherentes con Propiedades → Archivos de SSMS | [COMPLETAR] | Pendiente |
| Captura manual | `python scripts/capturar_almacenamiento.py` | "OK" en consola y en el log | [COMPLETAR] | Pendiente |
| Carga + crecimiento | Captura → `03_...sql` → captura | Datos utilizados aumentan ~12 MB | [COMPLETAR] | Pendiente |
| Tarea programada | `Start-ScheduledTask`, luego revisar el log | Nueva línea con origen programado | [COMPLETAR] | Pendiente |
| Página completa | Abrir "Almacenamiento" | Todas las secciones sin errores | [COMPLETAR] | Pendiente |
| Error controlado | Detener `MSSQL$SQLEXPRESS` y recargar | Errores claros por sección, sin caída | [COMPLETAR] | Pendiente |
| Varias mediciones en días distintos | Dejar la tarea funcionando | Gráfico temporal con ≥ 3 puntos en fechas distintas | [COMPLETAR] | Pendiente |

## 10. Evidencias

- Ubicación: `evidencias/semana-05/`
- [COMPLETAR lista de capturas `semana_05_XX.png`]

## 11. Problemas encontrados

- [COMPLETAR si aparecen durante la prueba real]

## 12. Tareas no completadas

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Validación contra SQL Server real | El código se preparó fuera de la instancia | Ejecutar la guía y completar este archivo | Alta |
| Mediciones en fechas distintas | Requiere que pase el tiempo | Dejar la tarea programada activa y generar carga en días distintos | Alta |

## 13. Instrucciones para la siguiente persona y su IA

- Qué revisar primero: este archivo; ejecutar `streamlit run app/app.py` y confirmar que las páginas 1, 2 y 3 cargan.
- Qué no modificar sin consultar: `monitoreo.HistorialAlmacenamiento` (contiene el historial real) y los permisos del usuario consultivo.
- Para Mar (respaldos): `msdb.dbo.backupset` necesita permisos en `msdb` que el usuario consultivo no tiene; no hay SQL Server Agent en Express, así que respaldos programados también tendrían que ir por el Programador de tareas. El espacio en disco de esta página es útil para justificar dónde guardar respaldos.
- Qué pendiente tiene mayor prioridad: [COMPLETAR]

## 14. Estado del criterio de cierre

- Criterio: el módulo debe mostrar almacenamiento real y contar con un mecanismo documentado para registrar y comparar crecimiento.
- ¿Se cumplió completamente?: [COMPLETAR — "No, todavía no" hasta tener capturas]
- Evidencia: [COMPLETAR]

## 15. Resumen breve para el equipo

[COMPLETAR al cerrar. Borrador: se implementó el Módulo 3 (almacenamiento) con consultas a `sys.database_files`, `FILEPROPERTY`, `sys.filegroups`, `sys.dm_os_volume_stats` y `sys.dm_db_partition_stats`, una tabla propia de historial alimentada por un procedimiento almacenado y una tarea programada de Windows (Express no tiene SQL Server Agent), y una página de Streamlit con indicadores de advertencia y gráfico temporal de crecimiento.]
