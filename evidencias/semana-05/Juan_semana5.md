# Semana 05 — Resumen y continuidad

## 1. Información general

- Responsable: Juan Artavia
- Fecha de inicio: 2026-09-24
- Fecha de cierre: pendiente (solo falta acumular mediciones en días distintos, ver sección 14)
- Semana del cronograma: 5
- Objetivo de la semana: Módulo 3 — mostrar el uso actual del almacenamiento y permitir comparar su crecimiento.

## 2. Estado recibido de la semana anterior

- Funcionalidades que ya estaban disponibles: conexión `pyodbc`, Módulo 1 (estado de la instancia) y Módulo 2 (rendimiento).
- Archivos o módulos recibidos: todo lo que estaba en `main` después del PR #8 (commit `425e1d2`).
- Problemas o pendientes heredados:
  - `Andrey_semana3.md` sigue con campos `[COMPLETAR]` (sus capturas sí prueban que funcionó).
  - La Semana 4 no tiene entrada en `docs/bitacora/bitacora.md` (sí tiene `Nicky_semana4.md`).
  - Las páginas 1 y 2 usan `use_container_width=True`, que Streamlit 1.62 marca como obsoleto. Funciona, pero conviene cambiarlo a `width="stretch"` en la Semana 9. La página 3 ya usa `width="stretch"`.
- Decisiones anteriores que se conservaron: SQL Server + Python + Streamlit + pyodbc + Plotly; usuario consultivo con permisos mínimos; credenciales en `config/.env`; patrón `app/database/queries/<modulo>.py` + `app/pages/N_<Modulo>.py`; `try/except` por sección; límites TOP N.
- Verificación del estado heredado en la máquina de Juan: se ejecutaron los scripts de las semanas 2 y 3 (la instancia local no tenía la base ni el usuario) y los módulos 1 y 2 cargaron con datos reales (`semana_05_01`, `semana_05_02`).

## 3. Trabajo realizado

### Tarea 1 — Consultas de almacenamiento actual

- Qué se hizo: resumen de la base (datos y log: asignado, utilizado, disponible, %), archivos, filegroups, espacio en disco, límite de la edición, top N tablas e índices.
- Cómo se hizo: `sys.database_files` + `FILEPROPERTY(name, 'SpaceUsed')`, `sys.filegroups`, `sys.dm_os_volume_stats`, `SERVERPROPERTY`, `sys.dm_db_partition_stats` + `sys.objects` / `sys.indexes` / `sys.schemas`.
- Archivos: `sql/03-almacenamiento/consultas_almacenamiento.sql`, `app/database/queries/almacenamiento.py`.
- Resultado real (antes de la carga): BD_AdminSGBD con 16 MB en disco; datos 4.38 MB utilizados de 8 MB; log 0.87 MB de 8 MB; filegroup `PRIMARY`; disco C: 59.9 % libre (285 GB de 476 GB); límite Express 50 GB, uso 0.0 %.

### Tarea 2 — Tabla histórica y procedimiento de captura

- Qué se hizo: esquema `monitoreo`, tabla `monitoreo.HistorialAlmacenamiento`, procedimiento `monitoreo.sp_capturar_almacenamiento @origen`, vista `monitoreo.vw_resumen_historial`.
- Cómo se hizo: el procedimiento lee el espacio real y lo inserta; no recibe cifras como parámetro. Si `FILEPROPERTY` devuelve NULL (permisos), lanza el error 50002 y no guarda nada.
- Archivos: `sql/03-almacenamiento/01_crear_objetos_historial.sql`.
- Resultado: script ejecutado sin errores (`semana_05_05`). SSMS muestra "errores" de IntelliSense al abrir el archivo porque los objetos aún no existían; no son errores de ejecución.

### Tarea 3 — Permisos del módulo

- Qué se hizo: `VIEW DEFINITION` en la base, `SELECT` sobre el esquema `monitoreo`, `EXECUTE` sobre el procedimiento.
- Archivos: `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql`.
- Resultado: la verificación muestra `CONNECT`, `VIEW DEFINITION` (toda la base), `EXECUTE` (monitoreo.sp_capturar_almacenamiento) y `SELECT` (esquema monitoreo) (`semana_05_06`).

### Tarea 4 — Captura periódica

- Qué se hizo: `scripts/capturar_almacenamiento.py` ejecuta el procedimiento con el usuario consultivo y escribe en `logs/captura_almacenamiento.log`; `scripts/capturar_almacenamiento.bat` lo lanza con el Python del `.venv`; tarea `ProyectoSGBD_CapturaAlmacenamiento` cada 6 horas con `StartWhenAvailable`.
- Resultado: la tarea se ejecutó sola a las 21:55:18 con resultado `0x0`; próxima ejecución 25/9 03:55 (`semana_05_18`). Log con líneas `OK` (`semana_05_salidas_terminal.txt`).

### Tarea 5 — Carga de prueba y crecimiento

- Qué se hizo: `03_generar_carga_prueba.sql` insertó 20 000 filas reales en `prueba.CargaAlmacenamiento` (`semana_05_12`).
- Resultado real:

| | Antes (21:42) | Después (21:50) | Cambio |
|---|---|---|---|
| Datos utilizados | 4.38 MB | 20.69 MB | +16.31 MB |
| Datos asignados | 8 MB | 72 MB | +64 MB (autocrecimiento) |
| Log asignado | 8 MB | 72 MB | +64 MB (autocrecimiento) |
| Total en disco | 16 MB | 144 MB | +128 MB |

- Objetos: `prueba.CargaAlmacenamiento` 20 000 filas, 16.20 MB reservados (índice agrupado `PK_CargaAlmacenamiento` 11.63 MB + `IX_Carga_codigo` 4.57 MB) (`semana_05_16`, `semana_05_17`).

### Tarea 6 — Integración Streamlit

- Página: `app/pages/3_Almacenamiento.py`; lógica en `app/services/almacenamiento.py`.
- Secciones: indicadores de advertencia, tamaño de la base con gráfico utilizado/disponible y límite de la edición, archivos, filegroups, disco, objetos de mayor tamaño (Tablas / Índices), historial con gráfico temporal, resumen de crecimiento y botón "Registrar una medición ahora".
- Resultado: todas las secciones cargaron con datos reales (`semana_05_07` a `semana_05_15`).

## 4. Decisiones técnicas tomadas

| Decisión | Motivo | Consecuencia para las siguientes semanas |
|---|---|---|
| Captura periódica con el Programador de tareas de Windows | En Express, `SQL Server Agent (SQLEXPRESS)` está `Stopped` / `Disabled` (`semana_05_20`) | Mar (respaldos) y Andrey (mantenimiento) tampoco tendrán Agent para programar trabajos |
| `EXECUTE` sobre el procedimiento en vez de `INSERT` sobre la tabla | Mínimo privilegio; funciona por encadenamiento de propiedad (todo es de `dbo`) | El usuario consultivo sigue sin poder escribir en tablas |
| `VIEW DEFINITION` en `BD_AdminSGBD` | Sin él, la visibilidad de metadatos oculta tablas e índices | Javi (auditoría) probablemente lo necesite; ya estará otorgado |
| Umbrales 80 / 90 % contra el tamaño máximo del archivo; disco 20 / 10 % libre | Un archivo lleno con autocrecimiento ilimitado no es un riesgo | Documentado en la página |
| Límite de Express según versión: 10 GB (≤ 2022) / 50 GB (2025) | SQL Server 2025 Express subió el límite a 50 GB | Se calcula con `EngineEdition` y `ProductMajorVersion` |
| Verificación de conexión única al inicio de la página | Con el servidor caído, cada sección esperaba ~15 s y el panel quedaba vacío | Patrón recomendable para las demás páginas en la Semana 9 |
| Carpeta `app/services/` | Separar lógica de presentación, como prevé la estructura base | Los módulos siguientes pueden usarla |
| El módulo mide la base de la conexión (`DB_NAME`) | `FILEPROPERTY` y `sys.database_files` solo funcionan en la base actual | Para medir otra base hay que crear el usuario ahí y cambiar `DB_NAME` |

## 5. Cambios respecto al plan original

### Cambio 1

- Forma en que debía hacerse originalmente (X): capturar mediciones periódicas con un trabajo de SQL Server Agent.
- Por qué no fue posible: la edición Express no permite usar SQL Server Agent.
- Evidencia: `sys.dm_server_services` → `SQL Server Agent (SQLEXPRESS)` = `Stopped`, `Disabled` (`semana_05_20`).
- Solución alternativa aplicada (Y): procedimiento almacenado + script Python + Programador de tareas de Windows.
- Consecuencias: solo mide con la computadora encendida (si se perdió una ejecución, corre al encender). El historial es local a cada máquina.
- ¿Debe revisarse después?: No.

## 6. Configuración actual

- SGBD y versión: Microsoft SQL Server 2025 (RTM) 17.0.1000.7, Express Edition (64-bit)
- Instancia: `Juan\SQLEXPRESS` (en `.env`: `localhost\SQLEXPRESS`)
- Python: 3.12.7 (entorno `.venv`)
- Controlador ODBC: ODBC Driver 18 for SQL Server
- Dependencias: sin cambios en `requirements.txt` (streamlit 1.62.0)
- Variables: las mismas de `config/.env.example`
- Permisos: `VIEW SERVER STATE` (heredado) + `VIEW DEFINITION`, `SELECT ON SCHEMA::monitoreo`, `EXECUTE ON monitoreo.sp_capturar_almacenamiento`
- No subir: `config/.env`, `logs/`

## 7. Archivos importantes

| Archivo o carpeta | Propósito | Estado |
|---|---|---|
| `sql/03-almacenamiento/01_crear_objetos_historial.sql` | Esquema, tabla, procedimiento y vista | Completo, validado |
| `sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql` | Permisos del módulo | Completo, validado |
| `sql/03-almacenamiento/03_generar_carga_prueba.sql` | Carga real de prueba | Completo, validado |
| `sql/03-almacenamiento/consultas_almacenamiento.sql` | Consultas documentadas | Completo |
| `app/database/queries/almacenamiento.py` | Acceso a datos | Completo, validado |
| `app/services/almacenamiento.py` | Umbrales y cálculos | Completo, validado |
| `app/pages/3_Almacenamiento.py` | Página de Streamlit | Completo, validado |
| `scripts/capturar_almacenamiento.py` / `.bat` | Captura periódica | Completo, validado |

## 8. Consultas y operaciones administrativas

| Consulta | Vistas / funciones | Permiso | Limitación |
|---|---|---|---|
| Resumen de la base | `sys.database_files`, `FILEPROPERTY` | `VIEW DEFINITION` | Solo la base actual |
| Archivos | `sys.database_files`, `sys.filegroups` | ídem | — |
| Filegroups | `sys.filegroups`, `sys.database_files` | ídem | El log no pertenece a ningún filegroup |
| Disco | `sys.dm_os_volume_stats` | `VIEW SERVER STATE` | — |
| Tablas / índices más grandes | `sys.dm_db_partition_stats`, `sys.objects`, `sys.indexes` | `VIEW SERVER STATE` + `VIEW DEFINITION` | TOP N (5–30) |
| Historial | `monitoreo.vw_resumen_historial` | `SELECT` en `monitoreo` | Últimas 200 mediciones |
| Registrar medición | `monitoreo.sp_capturar_almacenamiento` | `EXECUTE` | Única escritura del módulo; solo agrega filas |

## 9. Pruebas realizadas

| Prueba | Resultado real | Estado |
|---|---|---|
| Conexión (`test_connection.py`) | Conexión exitosa a `Juan\SQLEXPRESS`, base `BD_AdminSGBD` | Aprobada |
| Permisos (`test_permissions.py`) | `CONNECT`, `VIEW DATABASE STATE` | Aprobada |
| Módulos 1 y 2 heredados | Cargan con datos reales | Aprobada |
| Crear objetos y permisos | Sin errores; 4 permisos verificados | Aprobada |
| Captura manual con usuario consultivo | `OK`: 4.38/8.00 MB datos, 0.87/8.00 MB log | Aprobada |
| Página completa | Todas las secciones con datos reales | Aprobada |
| Carga + crecimiento | +16.31 MB utilizados; +128 MB asignados | Aprobada |
| Tarea programada | Ejecución automática 21:55:18, resultado `0x0` | Aprobada |
| Error controlado (servicio detenido) | Aviso en indicadores + un único error claro; la app no se cae (`semana_05_22`) | Aprobada |
| Recuperación | Al reiniciar el servicio todo vuelve a la normalidad (`semana_05_23`) | Aprobada |
| Mediciones en días distintos | Todas las mediciones son del 24/9 | Pendiente |

## 10. Evidencias

`evidencias/semana-05/`: `semana_05_01` a `semana_05_23` + `semana_05_salidas_terminal.txt`. No se incluyen capturas donde se ve la contraseña del usuario consultivo.

## 11. Problemas encontrados

### Problema 1

- Descripción: con el servidor detenido, la primera versión intentaba conectarse en cada sección y el panel de indicadores quedaba vacío mientras cargaba (~2 min).
- Causa: cada sección esperaba el tiempo de espera del login (~15 s).
- Solución: verificación única de conexión al inicio (`semana_05_21` antes, `semana_05_22` después).
- Estado: resuelto.

### Problema 2

- Descripción: el script `crear_usuario_consultivo.sql` se guardó con la contraseña local.
- Solución: `git restore` antes de cualquier commit; la contraseña solo está en `config/.env`.
- Estado: resuelto; nunca llegó al repositorio.

### Nota

- La medición de las 21:42:08 figura como `programado` aunque se ejecutó a mano, porque el script siempre usa ese origen. Las de las 21:54:41 y 21:55:18 sí son de la tarea.

## 12. Tareas no completadas

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Mediciones en fechas distintas (M3-12) | Requiere que pase el tiempo | Dejar la tarea activa unos días (opcional: otra carga de prueba otro día) | Alta |

## 13. Instrucciones para la siguiente persona y su IA

- Revisar primero: este archivo; ejecutar `streamlit run app/app.py` y confirmar que las páginas 1, 2 y 3 cargan.
- En cada máquina nueva, ejecutar en orden: `sql/00-configuracion/*`, `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql`, `sql/03-almacenamiento/01_...` y `02_...`.
- No modificar sin consultar: `monitoreo.HistorialAlmacenamiento` y los permisos del usuario consultivo.
- Para Mar (respaldos): `msdb.dbo.backupset` necesita permisos en `msdb` que el usuario consultivo no tiene; en Express no hay SQL Server Agent para respaldos programados. La sección de disco de esta página sirve para justificar dónde guardar respaldos.

## 14. Estado del criterio de cierre

- Criterio: el módulo debe mostrar almacenamiento real y contar con un mecanismo documentado para registrar y comparar crecimiento.
- ¿Se cumplió completamente?: Casi. El almacenamiento real y el mecanismo de registro y comparación están probados. Falta que el gráfico tenga mediciones de días distintos (M3-12), lo que depende solo de que la tarea siga ejecutándose.
- Evidencia: sección 10.

## 15. Resumen breve para el equipo

Se implementó y validó contra SQL Server real el Módulo 3 (almacenamiento): tamaño asignado, utilizado y disponible de datos y log, archivos, filegroups, disco, límite de la edición y objetos de mayor tamaño, con indicadores de advertencia. El crecimiento se registra en una tabla propia mediante un procedimiento que el usuario consultivo puede ejecutar sin permisos de escritura, y se captura cada 6 horas con el Programador de tareas de Windows, porque SQL Server Agent está deshabilitado en Express. Se demostró crecimiento real (+16.31 MB de datos, +128 MB asignados por autocrecimiento) y el manejo de errores con el servidor detenido. Solo falta acumular mediciones en días distintos.
