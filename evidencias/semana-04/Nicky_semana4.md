# Semana 04 — Resumen y continuidad

## 1. Información general

- Responsable: Nicky
- Fecha de inicio: 2026-09-17
- Fecha de cierre: 2026-09-17
- Semana del cronograma: 4
- Objetivo de la semana: Implementación del módulo 2 — monitoreo de rendimiento.

## 2. Estado recibido de la semana anterior

- Funcionalidades que ya estaban disponibles: conexión a SQL Server desde Python vía `pyodbc` (`app/database/connection.py`), módulo 1 completo (`app/pages/1_Estado_Instancia.py`, `app/database/queries/estado_instancia.py`), usuario consultivo `adminsgbd_consulta` con permiso `VIEW SERVER STATE` ya otorgado (a nivel de cada instancia local, no compartido entre integrantes).
- Archivos o módulos recibidos: todos los de la Semana 2 y 3 (ver `Andrey_semana3.md`).
- Problemas o pendientes heredados: el archivo `evidencias/semana-03/Andrey_semana3.md` sigue con los campos `[COMPLETAR]` sin llenar y el criterio de cierre marcado como "No, todavía no cumplido", pero las 8 capturas reales que Andrey subió en esa misma carpeta demuestran que el módulo sí fue probado exitosamente contra su SQL Server real (conexión, servidor/instancia, uptime, memoria, bases de datos, y manejo de error controlado con el servicio detenido). Se recomienda que Andrey actualice su `.md` con esos resultados antes de la entrega final, pero no es un bloqueante: se tomó como validado con la evidencia como respaldo.
- Decisiones anteriores que se conservaron: Microsoft SQL Server como SGBD, Python + Streamlit + pyodbc + Plotly, separación de usuario consultivo, credenciales fuera del repositorio vía `.env`, permiso `VIEW SERVER STATE` como base para consultas de monitoreo.

## 3. Trabajo realizado

### Tarea 1 — Consultas SQL de rendimiento

- Qué se hizo: consulta de las 10 sentencias SQL de mayor consumo de CPU, sesiones activas (usuario, estado, equipo, aplicación, CPU, memoria), y sesiones bloqueadas/bloqueadoras.
- Cómo se hizo: `sys.dm_exec_query_stats` + `sys.dm_exec_sql_text` para consultas costosas; `sys.dm_exec_sessions` para sesiones activas; `sys.dm_exec_requests` + `sys.dm_exec_sessions` para bloqueos.
- Archivos creados: `sql/02-rendimiento/consultas_rendimiento.sql`.
- Resultado obtenido: consultas costosas devolvió 10 filas reales (dominadas por consultas internas de SSMS, ver sección 12); sesiones activas devolvió entre 3 y 8 filas según cuántas pestañas de SSMS estuvieran abiertas; sesiones bloqueadas devolvió 0 filas en condición normal, y 1 fila durante la prueba de bloqueo controlado.

### Tarea 2 — Escenario de bloqueo controlado

- Qué se hizo: se generó un bloqueo real y reproducible entre dos sesiones de SQL Server, para poder demostrar y probar la consulta de sesiones bloqueadas.
- Cómo se hizo: tabla temporal `dbo.PruebaBloqueo`; una sesión abre una transacción con `UPDATE` sin confirmar (`BEGIN TRANSACTION` sin `COMMIT`/`ROLLBACK`), una segunda sesión intenta leer la misma fila y queda en espera; se observó el bloqueo con la consulta oficial del módulo usando el usuario `adminsgbd_consulta`; se liberó con `ROLLBACK TRANSACTION` (sin dejar cambios permanentes).
- Archivos creados: `sql/02-rendimiento/preparar_escenario_bloqueo.sql`.
- Resultado obtenido: sesión 82 bloqueada por sesión 87, tipo de espera `LCK_M_S`, estado `suspended` — capturado en evidencia.

### Tarea 3 — Capa de acceso a datos en Python

- Qué se hizo: tres funciones (`obtener_consultas_costosas`, `obtener_sesiones_activas`, `obtener_sesiones_bloqueadas`) que ejecutan las consultas del punto 1 y devuelven listas de diccionarios.
- Cómo se hizo: mismo patrón que `estado_instancia.py` de la Semana 3 (reutiliza `get_connection()`, no se modificó `connection.py`).
- Archivos creados: `app/database/queries/rendimiento.py`.
- Resultado obtenido: probado por separado desde línea de comandos contra SQL Server real — 10 consultas costosas, 8 sesiones activas, 0 sesiones bloqueadas (en condición normal, sin el escenario de prueba activo).

### Tarea 4 — Integración Streamlit

- Página creada: `app/pages/2_Rendimiento.py`.
- Componentes utilizados: `st.selectbox` (ordenar consultas costosas por métrica), `st.multiselect` (filtrar sesiones activas por estado), `st.dataframe` con `column_config` para nombres y formato de columnas, `st.success` / `st.warning` para diferenciar "sin bloqueos" de "hay bloqueos".
- Manejo de errores: cada sección tiene su propio bloque `try/except` independiente, igual que el Módulo 1.
- Resultado: las tres secciones cargaron sin errores con datos reales, confirmado con capturas.

## 4. Decisiones técnicas tomadas

| Decisión | Motivo | Consecuencia para las siguientes semanas |
|---|---|---|
| Limitar consultas costosas a TOP 10 y sesiones activas a TOP 20 | Evitar consultas de monitoreo excesivamente pesadas, exigido por el cronograma | Los módulos siguientes deberían aplicar el mismo criterio de límites |
| Usar `ROLLBACK` (no `COMMIT`) en la prueba de bloqueo | No dejar cambios permanentes de una prueba en la base de datos | Ninguna — la tabla `dbo.PruebaBloqueo` puede reutilizarse para pruebas futuras si se desea |
| Generar el bloqueo con el usuario administrador (Windows), no con `adminsgbd_consulta` | El usuario consultivo no tiene permiso de escritura (`CREATE TABLE permission denied` al intentarlo) — es un error de permisos, no un bloqueo | Los módulos que necesiten *generar* actividad (no solo observarla) deben usar una conexión con más privilegios; el usuario consultivo sigue siendo suficiente para *observar* |

## 5. Cambios respecto al plan original

### Cambio 1

- Forma en que debía hacerse originalmente (X): el cronograma no especifica la ubicación local del repositorio.
- Por qué no fue posible: preferencia personal de organización de carpetas.
- Error, limitación o evidencia encontrada: no aplica.
- Solución alternativa aplicada (Y): repositorio clonado en `C:\Users\nicol\Desktop\proyecto-admin-sgbd` en lugar de `Documents`.
- Consecuencias o limitaciones de la alternativa: ninguna — es solo la ruta local de esta integrante, no afecta el repositorio ni el código.
- ¿Debe revisarse después?: No.

### Cambio 2

- Forma en que debía hacerse originalmente (X): se esperaba que el modo de autenticación mixta de SQL Server ya estuviera configurado desde la instalación (Semana 2).
- Por qué no fue posible: la instancia local de esta integrante estaba en modo "Solo autenticación de Windows" por defecto.
- Error, limitación o evidencia encontrada: `Login failed for user 'adminsgbd_consulta'. (18456)` al ejecutar `test_connection.py`, a pesar de que el login y la contraseña eran correctos.
- Solución alternativa aplicada (Y): se cambió a "Modo de autenticación de Windows y SQL Server" desde SSMS (Propiedades del servidor → Seguridad) y se reinició el servicio `MSSQL$SQLEXPRESS`.
- Consecuencias o limitaciones de la alternativa: ninguna negativa; es un paso de configuración local que cada integrante debe verificar en su propia máquina.
- ¿Debe revisarse después?: Sí — recomendar que el manual de instalación (`docs/manuales/instalacion.md`) mencione explícitamente verificar el modo de autenticación mixta, ya que no quedó documentado en la Semana 2.

## 6. Configuración actual

- SGBD y versión: Microsoft SQL Server 2025 (RTM-GDR), Express Edition, 17.0.1135.8
- Nombre de instancia usado: `Nicky\SQLEXPRESS`
- Herramientas y versiones: Python 3.11.9, SQL Server Management Studio (versión con interfaz tipo VS Code)
- Versión de Python: 3.11.9
- Versión del controlador ODBC: ODBC Driver 18 for SQL Server (64-bit)
- Versiones de dependencias relevantes: sin cambios respecto a `requirements.txt` heredado (streamlit 1.62.0, pyodbc 5.3.0, pandas 3.0.5, plotly 7.0.0)
- Variables o parámetros necesarios: mismas de `config/.env.example`, sin variables nuevas
- Permisos requeridos: `VIEW SERVER STATE` (heredado de Semana 3, reutilizado sin cambios)
- Configuraciones que no deben subirse al repositorio: `config/.env` real con contraseña

## 7. Archivos importantes

| Archivo o carpeta | Propósito | Estado |
|---|---|---|
| `sql/02-rendimiento/consultas_rendimiento.sql` | Consultas documentadas del módulo 2 | Completo, validado |
| `sql/02-rendimiento/preparar_escenario_bloqueo.sql` | Genera un bloqueo real y reproducible para pruebas | Completo, validado |
| `app/database/queries/rendimiento.py` | Capa de acceso a datos del módulo 2 | Completo, validado |
| `app/pages/2_Rendimiento.py` | Página de Streamlit del módulo 2 | Completo, validado |

## 8. Consultas y operaciones administrativas

### Consultas de mayor consumo
- Ubicación: `sql/02-rendimiento/consultas_rendimiento.sql`, sección 1
- Qué información obtiene: TOP 10 sentencias SQL por tiempo de CPU, con conteo de ejecuciones, duración y lecturas
- Vistas del sistema utilizadas: `sys.dm_exec_query_stats`, `sys.dm_exec_sql_text`
- Permisos necesarios: ninguno especial además de `CONNECT`
- Resultado esperado: hasta 10 filas
- Limitaciones conocidas: refleja el caché de planes de ejecución desde que arrancó la instancia; en una instancia con poca actividad de negocio, puede estar dominada por consultas internas de SSMS o del sistema, no de la aplicación

### Sesiones activas
- Ubicación: sección 2
- Qué información obtiene: hasta 20 sesiones de usuario, ordenadas por CPU
- Vistas utilizadas: `sys.dm_exec_sessions`
- Permisos necesarios: ninguno especial
- Resultado esperado: una fila por sesión de usuario conectada
- Limitaciones conocidas: excluye procesos internos del sistema (`is_user_process = 0`)

### Sesiones bloqueadas
- Ubicación: sección 3
- Qué información obtiene: sesión bloqueada, sesión bloqueadora, tipo de espera, tiempo de espera
- Vistas utilizadas: `sys.dm_exec_requests`, `sys.dm_exec_sessions`
- Permisos necesarios: `VIEW SERVER STATE`
- Resultado esperado: 0 filas en condición normal (sin bloqueos, no es error); 1 o más filas si hay bloqueos activos
- Limitaciones conocidas: ninguna

## 9. Pruebas realizadas

| Prueba | Procedimiento | Resultado esperado | Resultado real | Estado |
|---|---|---|---|---|
| Conexión local | `python test_connection.py` | Conexión exitosa | Conexión exitosa con `Nicky\SQLEXPRESS` | Aprobada |
| Permisos heredados | `python test_permissions.py` | CONNECT y VIEW DATABASE STATE listados | Ambos confirmados | Aprobada |
| Módulo 1 (heredado) | Abrir página "Estado Instancia" | Carga sin errores con datos reales | 4 secciones cargaron correctamente | Aprobada |
| Consultas costosas | Ejecutar consulta 1 en SSMS con `adminsgbd_consulta` | Hasta 10 filas | 9 filas reales devueltas | Aprobada |
| Sesiones activas | Ejecutar consulta 2 en SSMS | Filas con sesiones reales | 3 filas devueltas | Aprobada |
| Sesiones bloqueadas (sin bloqueo) | Ejecutar consulta 3 en SSMS | 0 filas | 0 filas | Aprobada |
| Escenario de bloqueo | Dos sesiones simultáneas (Sesión A sin commit, Sesión B lee la misma fila) | Sesión B queda esperando; consulta de bloqueos detecta la relación | Bloqueo detectado: sesión 82 bloqueada por sesión 87 | Aprobada |
| Liberación del bloqueo | `ROLLBACK TRANSACTION` en Sesión A | Sesión B termina de inmediato, fila vuelve al valor original | Confirmado, valor volvió a `'inicial'` | Aprobada |
| Capa de Python | Ejecutar las 3 funciones desde línea de comandos | Listas con datos reales | 10 / 8 / 0 filas respectivamente | Aprobada |
| Página Streamlit completa | Abrir "Rendimiento" en el navegador | 3 secciones sin errores, con filtros funcionando | Confirmado con capturas | Aprobada |

## 10. Evidencias

- Ubicación de las capturas: `evidencias/semana-04/`
- `semana_04_01.png`: consulta de sesiones bloqueadas detectando el bloqueo real (sesión 82 bloqueada por 87)
- `semana_04_02.png`: Sesión B tras el `ROLLBACK`, mostrando la fila con el valor original
- `semana_04_03.png`: página principal, conexión exitosa
- `semana_04_04.png`: Módulo 1 (Estado Instancia) funcionando
- `semana_04_05.png`: Módulo 2 (Rendimiento), sección de consultas de mayor consumo
- `semana_04_06.png`: tabla completa de consultas de mayor consumo
- `semana_04_07.png`: sesiones activas con filtro por estado
- `semana_04_08.png`: sesiones bloqueadas, mensaje de "sin bloqueos"

## 11. Problemas encontrados

### Problema 1

- Descripción: fallo de login del usuario `adminsgbd_consulta` al probar la conexión desde Python
- Mensaje de error exacto: `pyodbc.InterfaceError: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Login failed for user 'adminsgbd_consulta'. (18456)...")`
- Causa identificada: la instancia local estaba en modo "Solo autenticación de Windows"
- Solución aplicada: cambio a modo de autenticación mixta + reinicio del servicio `MSSQL$SQLEXPRESS`
- Estado actual: resuelto

### Problema 2

- Descripción: el archivo `config/.env` no reflejaba los cambios guardados desde el Bloc de notas
- Mensaje de error exacto: no aplica (no fue un error de SQL Server, sino que Python seguía leyendo el valor de la plantilla `CAMBIAR_POR_LA_CONTRASENA_LOCAL`)
- Causa identificada: el Bloc de notas no guardó el archivo correctamente al usar `Ctrl+S`
- Solución aplicada: corrección directa del archivo vía PowerShell (`-replace` + `Set-Content`), evitando el Bloc de notas para archivos de configuración sensibles
- Estado actual: resuelto

## 12. Tareas no completadas

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Actualizar `Andrey_semana3.md` con resultados reales | No es responsabilidad de esta integrante | Coordinar con Andrey antes de la entrega final | Media |
| Enriquecer "consultas de mayor consumo" con actividad propia de la aplicación | La instancia tiene poca actividad de negocio real todavía; los resultados actuales están dominados por consultas internas de SSMS | Generar actividad real de la aplicación (usarla más, o correr consultas de prueba) antes de la presentación final, para que la tabla muestre algo más representativo | Baja |

## 13. Instrucciones para la siguiente persona y su IA

- Qué debe revisar primero: este archivo completo, y ejecutar `streamlit run app/app.py` para confirmar que los módulos 1 y 2 cargan sin errores antes de construir el Módulo 3.
- Qué no debe modificar sin consultar: `app/database/connection.py`, la estructura de `app/database/queries/`, y el permiso `VIEW SERVER STATE` (el Módulo 3 de almacenamiento probablemente también lo necesite).
- Qué archivos debe abrir: `sql/02-rendimiento/*.sql`, `app/database/queries/rendimiento.py`, `app/pages/2_Rendimiento.py`.
- Qué pruebas debe repetir: correr la app y confirmar que "Rendimiento" carga sin errores antes de empezar el Módulo 3.
- Qué decisiones debe respetar: cada integrante corre su propia instancia local de SQL Server Express (`localhost\SQLEXPRESS` o el nombre de su equipo); verificar el modo de autenticación mixta antes de reportar un error de login como un problema de código.
- Qué pendiente tiene mayor prioridad: ninguno bloqueante — la Semana 4 se cumple completamente.

## 14. Estado del criterio de cierre

- Criterio de cierre de la semana: el módulo debe identificar consultas costosas, mostrar sesiones y diferenciar correctamente entre ausencia de bloqueos y error de consulta.
- ¿Se cumplió completamente?: Sí.
- Evidencia: sección 10 (8 capturas en `evidencias/semana-04/`).
- Si no se cumplió, explicación precisa: no aplica.

## 15. Resumen breve para el equipo

Se implementó completamente el Módulo 2 (rendimiento): consultas SQL documentadas para identificar sentencias costosas, sesiones activas y bloqueos; capa de acceso a datos en Python siguiendo el patrón de la Semana 3; y página de Streamlit con filtros y ordenamiento. Se generó y documentó un escenario de bloqueo real y reproducible, con evidencia de detección y liberación correctas. En el camino se resolvieron dos problemas de configuración local (modo de autenticación de SQL Server, y un archivo `.env` que no se guardaba bien desde el Bloc de notas) que probablemente afecten a otros integrantes del equipo al configurar sus propias máquinas, por lo que quedaron documentados en la sección 11. El siguiente paso es que Juan revise este archivo antes de empezar el Módulo 3 (almacenamiento).
