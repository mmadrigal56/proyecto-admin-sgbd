# Semana 03 — Resumen y continuidad

> **Nota:** este archivo se generó como borrador junto con el código. Los campos marcados con `[COMPLETAR]` deben llenarse con resultados reales después de ejecutar la aplicación contra tu instancia de SQL Server. No marcar nada como "completado" sin haberlo probado (regla de veracidad del cronograma).

## 1. Información general

- Responsable: Andrey
- Fecha de inicio: [COMPLETAR]
- Fecha de cierre: [COMPLETAR]
- Semana del cronograma: 3
- Objetivo de la semana: Implementación del módulo 1 — estado general de la instancia.

## 2. Estado recibido de la Semana 2

- Funcionalidades disponibles: conexión a SQL Server desde Python vía `pyodbc` (`app/database/connection.py`), aplicación Streamlit mínima con prueba de conexión (`app/app.py`), usuario consultivo `adminsgbd_consulta`, base de datos `BD_AdminSGBD`, `.env.example`, `requirements.txt`.
- Archivos recibidos: `app/app.py`, `app/database/connection.py`, `sql/00-configuracion/crear_base_pruebas.sql`, `sql/00-configuracion/crear_usuario_consultivo.sql`, `config/.env.example`, `docs/manuales/instalacion.md`, `test_connection.py`, `test_permissions.py`.
- Problemas o pendientes heredados: **no existe una entrada de bitácora para la Semana 2**, ni un archivo `Javi_semana2.md`, ni una carpeta `evidencias/`. El código de la Semana 2 está presente y parece correcto, pero no hay evidencia documentada de que se haya probado contra un SQL Server real. Se recomienda que el equipo lo confirme con Javi antes de la entrega final.
- Decisiones anteriores que se conservaron: Microsoft SQL Server como SGBD, Python + Streamlit + pyodbc + Plotly, separación de usuario consultivo, credenciales fuera del repositorio vía `.env`.

## 3. Trabajo realizado

### Tarea 1 — Información del servidor e instancia

- Qué se hizo: consulta de servidor, nombre de instancia, edición, versión de producto, nivel de producto y collation.
- Cómo se hizo: `SERVERPROPERTY()` y `@@SERVERNAME` en `sql/01-estado-instancia/consultas_estado_instancia.sql`, expuesta en Python como `obtener_servidor_instancia()`.
- Archivos creados o modificados: `sql/01-estado-instancia/consultas_estado_instancia.sql`, `app/database/queries/estado_instancia.py`, `app/pages/1_Estado_Instancia.py`.
- Consultas utilizadas: ver sección 1 del archivo SQL.
- Resultado obtenido: [COMPLETAR con el resultado real al ejecutar la página]

### Tarea 2 — Estado operativo

- Qué se hizo: se determina el estado operativo de forma implícita — si la consulta a `sys.dm_os_sys_info` responde, la instancia está en línea; si falla, se muestra el error real.
- Cómo se hizo: función `obtener_actividad()`.
- Resultado obtenido: [COMPLETAR]

### Tarea 3 — Inicio y uptime

- Qué se hizo: fecha/hora de inicio del servicio y tiempo de actividad en días y horas.
- Cómo se calculó: `sqlserver_start_time` de `sys.dm_os_sys_info` y `DATEDIFF` contra `GETDATE()`.
- Resultado obtenido: [COMPLETAR]

### Tarea 4 — Memoria

- Qué métrica se utilizó: memoria física en uso, memoria virtual comprometida y memoria en páginas grandes, en MB.
- Qué representa: consumo real de memoria del proceso de SQL Server (`sqlservr.exe`), no de todo el sistema operativo.
- Qué DMV, función o procedimiento se utilizó: `sys.dm_os_process_memory`.
- Limitaciones: requiere el permiso de servidor `VIEW SERVER STATE`, otorgado en `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql`. Sin ese permiso, esta sección de la página mostrará un error controlado (no un fallo silencioso).

### Tarea 5 — Bases de datos

- Qué se consultó: `sys.databases` (nombre, estado, modelo de recuperación, fecha de creación).
- Qué información se mostró: tabla con todas las bases visibles para el usuario consultivo.
- Resultado: [COMPLETAR — ¿aparece BD_AdminSGBD y las bases del sistema?]

### Tarea 6 — Integración Streamlit

- Página creada: `app/pages/1_Estado_Instancia.py` (Streamlit multipágina; aparece automáticamente en el menú lateral junto a `app.py`).
- Componentes utilizados: `st.metric`, `st.dataframe`, `st.divider`, `st.success` / `st.error` / `st.info`.
- Manejo de errores: cada sección (servidor/instancia, estado operativo, memoria, bases de datos) tiene su propio bloque `try/except` independiente, para que un fallo de permisos en una sección no oculte el resto de la información.
- Actualización de datos: botón "Actualizar información" + timestamp de última actualización al pie de la página.

## 4. Decisiones técnicas tomadas

| Decisión | Motivo | Consecuencia para las siguientes semanas |
|---|---|---|
| Otorgar `VIEW SERVER STATE` al usuario consultivo existente, en vez de crear un segundo usuario | Es el permiso mínimo necesario y es de solo lectura | Los módulos 2 y 3 (rendimiento, almacenamiento) probablemente necesiten este mismo permiso — ya está disponible, no hay que volver a pedirlo |
| Estado operativo determinado de forma implícita (si responde = en línea) | SQL Server no expone un "estado" simple vía DMV accesible a un usuario consultivo sin permisos adicionales de `xp_servicecontrol` | Documentar esta limitación en el manual técnico para que el profesor no espere un semáforo de servicio de Windows |

## 5. Cambios respecto al plan original

### Cambio 1

- Forma en que debía hacerse originalmente (X): el cronograma no especifica el mecanismo exacto de permisos.
- Por qué no fue posible: el usuario consultivo de la Semana 2 solo tenía permisos mínimos de conexión, insuficientes para las DMVs del Módulo 1.
- Error, limitación o evidencia encontrada: [COMPLETAR con el mensaje de error real si lo tuviste antes de otorgar el permiso]
- Solución alternativa aplicada (Y): script `otorgar_permisos_estado_instancia.sql` que agrega `VIEW SERVER STATE`.
- Consecuencias o limitaciones de la alternativa: ninguna negativa; es un permiso de solo lectura acorde a las reglas del proyecto.
- ¿Debe revisarse después?: No.

## 6. Configuración actual

- SGBD y versión: [COMPLETAR — ejecutar la página y copiar edición/versión reales]
- Nombre de instancia usado: [COMPLETAR]
- Herramientas y versiones: según `docs/manuales/instalacion.md` (Python 3.14, SQL Server 2025 Express, ODBC Driver 17/18)
- Versión de Python: [COMPLETAR con la tuya]
- Versión del controlador ODBC: [COMPLETAR con la tuya]
- Versiones de dependencias relevantes: sin cambios respecto a `requirements.txt` de la Semana 2
- Variables o parámetros necesarios: mismas de `config/.env.example` (no se agregaron variables nuevas)
- Permisos requeridos: `VIEW SERVER STATE` (nuevo, agregado esta semana)
- Configuraciones que no deben subirse al repositorio: `config/.env` real con contraseñas

## 7. Archivos importantes

| Archivo o carpeta | Propósito | Estado |
|---|---|---|
| `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql` | Otorga VIEW SERVER STATE al usuario consultivo | Implementado, pendiente de validación |
| `sql/01-estado-instancia/consultas_estado_instancia.sql` | Consultas documentadas del módulo 1 | Implementado, pendiente de validación |
| `app/database/queries/estado_instancia.py` | Capa de acceso a datos del módulo 1 | Implementado, pendiente de validación |
| `app/pages/1_Estado_Instancia.py` | Página de Streamlit del módulo 1 | Implementado, pendiente de validación |

## 8. Consultas y operaciones administrativas

### Servidor e instancia
- Ubicación: `sql/01-estado-instancia/consultas_estado_instancia.sql`, sección 1
- Qué información obtiene: nombre de servidor, instancia, edición, versión, collation
- Vistas o tablas del sistema utilizadas: `SERVERPROPERTY()`, `@@SERVERNAME`
- Permisos necesarios: ninguno especial (disponible para cualquier login conectado)
- Resultado esperado: una fila con los datos del servidor
- Limitaciones conocidas: ninguna

### Actividad (inicio/uptime)
- Ubicación: sección 2 del mismo archivo
- Qué información obtiene: fecha de inicio del servicio y minutos/horas de actividad
- Vistas utilizadas: `sys.dm_os_sys_info`
- Permisos necesarios: `VIEW SERVER STATE`
- Resultado esperado: una fila
- Limitaciones conocidas: se reinicia a cero si el servicio de SQL Server se reinicia

### Memoria
- Ubicación: sección 3
- Qué información obtiene: memoria física en uso, virtual comprometida, páginas grandes (MB)
- Vistas utilizadas: `sys.dm_os_process_memory`
- Permisos necesarios: `VIEW SERVER STATE`
- Resultado esperado: una fila
- Limitaciones conocidas: refleja memoria del proceso `sqlservr.exe`, no del sistema operativo completo

### Bases de datos administradas
- Ubicación: sección 4
- Qué información obtiene: nombre, estado, modelo de recuperación y fecha de creación de cada base
- Vistas utilizadas: `sys.databases`
- Permisos necesarios: ninguno especial (metadatos visibles por defecto)
- Resultado esperado: una fila por base de datos
- Limitaciones conocidas: no muestra tamaño ni contenido (eso corresponde al módulo 3)

## 9. Pruebas realizadas

| Prueba | Procedimiento | Resultado esperado | Resultado real | Estado |
|---|---|---|---|---|
| Conexión heredada | Ejecutar `python test_connection.py` | Conexión exitosa | [COMPLETAR] | Pendiente |
| Permisos VIEW SERVER STATE | Ejecutar `otorgar_permisos_estado_instancia.sql`, luego `python test_permissions.py` | VIEW SERVER STATE listado | [COMPLETAR] | Pendiente |
| Servidor e instancia | Abrir la página "Estado Instancia" en Streamlit | Se muestran servidor, instancia, edición y versión | [COMPLETAR] | Pendiente |
| Uptime | Ídem | Se muestra fecha de inicio y tiempo de actividad coherente | [COMPLETAR] | Pendiente |
| Memoria | Ídem | Se muestran los tres indicadores de memoria en MB | [COMPLETAR] | Pendiente |
| Bases de datos | Ídem | Aparece BD_AdminSGBD y las bases del sistema | [COMPLETAR] | Pendiente |
| Error controlado | Detener temporalmente el servicio de SQL Server y recargar la página | Mensajes de error claros en cada sección, sin que la app se caiga | [COMPLETAR] | Pendiente |

## 10. Evidencias

- Ubicación de las capturas: `evidencias/semana-03/` (crear solo cuando existan capturas reales; no se creó vacía por regla del cronograma)
- Evidencia de conexión: [COMPLETAR]
- Evidencia del dashboard: [COMPLETAR]
- Evidencia de consultas: [COMPLETAR]
- Evidencia de pruebas: [COMPLETAR]

## 11. Problemas encontrados

### Problema 1

- Descripción: [COMPLETAR si aplica]
- Mensaje de error exacto: [COMPLETAR]
- Causa identificada: [COMPLETAR]
- Solución aplicada: [COMPLETAR]
- Estado actual: [COMPLETAR]

## 12. Tareas no completadas

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Validación contra SQL Server real | El código se generó junto con la IA sin acceso a la instancia real de Andrey | Ejecutar la app localmente, corregir cualquier error de tipos/permisos y actualizar este documento | Alta |
| Cerrar el registro de la Semana 2 | No hay `Javi_semana2.md` ni entrada de bitácora de Javi | Coordinar con Javi para completar esa documentación antes de la entrega final | Media |
| Evidencias | No se han capturado pantallas | Ejecutar la app y guardar capturas en `evidencias/semana-03/` | Alta |

## 13. Instrucciones para la siguiente persona y su IA

- Qué debe revisar primero: este archivo (`Andrey_semana3.md`) completo, y confirmar que las pruebas de la sección 9 quedaron en estado "Aprobada" antes de construir el Módulo 2 sobre esta base.
- Qué no debe modificar sin consultar: `app/database/connection.py` (Semana 2) y la estructura de `app/database/queries/` (para mantener el mismo patrón en los módulos siguientes).
- Qué archivos debe abrir: `sql/01-estado-instancia/*.sql`, `app/database/queries/estado_instancia.py`, `app/pages/1_Estado_Instancia.py`.
- Qué pruebas debe repetir: correr la app (`streamlit run app/app.py`) y confirmar que la página "Estado Instancia" carga sin errores antes de empezar el Módulo 2.
- Qué decisiones debe respetar: uso de `VIEW SERVER STATE` como permiso base para consultas de monitoreo (Nicky probablemente necesite el mismo permiso para el Módulo 2, ya está otorgado).
- Qué pendiente tiene mayor prioridad: validar este módulo contra SQL Server real y completar los campos `[COMPLETAR]` de este documento.

## 14. Estado del criterio de cierre

- Criterio de cierre de la semana: todos los datos deben ser reales y el módulo debe satisfacer cada criterio del módulo 1 de la rúbrica.
- ¿Se cumplió completamente?: **No, todavía no** — el código está implementado pero no validado contra una instancia real.
- Evidencia: pendiente (sección 10).
- Si no se cumplió, explicación precisa: el trabajo se generó como apoyo técnico antes de la prueba local; falta que Andrey ejecute la aplicación contra su SQL Server, confirme los resultados y complete los campos `[COMPLETAR]` de este archivo.

## 15. Resumen breve para el equipo

Se implementó el código completo del Módulo 1 (consultas SQL documentadas, capa de acceso a datos en Python y página de Streamlit), reutilizando sin modificar la conexión de la Semana 2. Se detectó y resolvió una dependencia de permisos: el usuario consultivo necesitaba `VIEW SERVER STATE` para leer las DMVs de actividad y memoria, y se agregó un script para otorgarlo. También se detectó que la Semana 2 no dejó bitácora ni archivo de continuidad propio, aunque el código sí está presente; se recomienda cerrarlo con Javi antes de la entrega final. El siguiente paso inmediato es que Andrey ejecute todo localmente contra su SQL Server, capture evidencias y complete los campos pendientes de este documento antes de entregárselo a Nicky para la Semana 4.
