# Semana 8 — Resumen y continuidad

## 1. Información general

- Responsable: Andrey
- Fecha de inicio: 12 de octubre de 2026
- Fecha de cierre: 12 de octubre de 2026
- Semana del cronograma: Semana 8 — Módulo 6: mantenimiento preventivo
- Objetivo de la semana: ejecutar operaciones administrativas controladas (actualización de estadísticas, mantenimiento de índices fragmentados) y verificar su resultado.

## 2. Estado recibido de la semana anterior

- Funcionalidades que ya estaban disponibles: Módulos 1 a 5 funcionales (estado de instancia, rendimiento, almacenamiento, respaldos, auditoría), según traspaso de Javi (`Javi_semana7.md`).
- Archivos o módulos recibidos: `app/pages/1_Estado_Instancia.py` a `5_Auditoria.py`, sus respectivas capas de datos, y los scripts `sql/01` a `sql/05`.
- Problemas o pendientes heredados: las bitácoras de las Semanas 4, 6 y 7 no tienen entrada en `docs/bitacora/bitacora.md` (solo existen sus archivos de continuidad individuales). No se corrigió, solo se deja anotado como pendiente del equipo.
- Decisiones anteriores que se conservaron: separación de usuario consultivo y administrativo (ya anticipada por Javi); patrón de registrar operaciones mediante procedimientos almacenados con encadenamiento de propiedad en vez de permisos directos sobre tablas (de la Semana 5); estructura de página Streamlit con secciones independientes y manejo de errores por sección (de la Semana 3).

## 3. Trabajo realizado

### Tarea 1 — Usuario administrativo separado

- Qué se hizo: se creó un login y usuario de SQL Server dedicado a las operaciones de mantenimiento (`adminsgbd_mantenimiento`), distinto del consultivo.
- Cómo se hizo: `CREATE LOGIN`/`CREATE USER`, agregado únicamente al rol de base de datos `db_ddladmin` en `BD_AdminSGBD` (no `sysadmin`).
- Archivos creados o modificados: `sql/06-mantenimiento/01_crear_usuario_administrativo.sql`.
- Resultado obtenido: login y usuario creados y verificados; permisos suficientes para `UPDATE STATISTICS` y `ALTER INDEX`, sin acceso a otras bases ni control total de la instancia.

### Tarea 2 — Permisos de detección para el usuario consultivo

- Qué se hizo: se otorgaron al usuario consultivo los permisos de solo lectura necesarios para detectar estadísticas desactualizadas e índices fragmentados.
- Cómo se hizo: `GRANT VIEW DATABASE STATE`, `GRANT VIEW DEFINITION` y `GRANT SELECT ON SCHEMA::dbo`, todos de forma idempotente (verifican si ya existen antes de otorgar).
- Archivos creados o modificados: `sql/06-mantenimiento/02_otorgar_permisos_mantenimiento.sql`.
- Resultado obtenido: las dos consultas de detección (estadísticas e índices) funcionan correctamente a través del usuario consultivo, verificado tanto en SSMS como desde la aplicación.

### Tarea 3 — Tabla y procedimientos de mantenimiento

- Qué se hizo: se creó la tabla de historial `monitoreo.RegistroMantenimiento` y dos procedimientos almacenados que ejecutan las operaciones reales y registran siempre su resultado.
- Cómo se hizo: `mantenimiento.sp_actualizar_estadisticas(@esquema, @tabla)` ejecuta `UPDATE STATISTICS ... WITH FULLSCAN`; `mantenimiento.sp_reconstruir_indice(@esquema, @tabla, @indice, @modo)` ejecuta `ALTER INDEX ... REORGANIZE` o `REBUILD`. Ambos validan primero que el objeto exista (si no, registran un fallo controlado y lanzan un error claro) y registran éxito o fallo en `monitoreo.RegistroMantenimiento` antes de terminar. Solo `adminsgbd_mantenimiento` tiene `EXECUTE` sobre ellos.
- Archivos creados o modificados: `sql/06-mantenimiento/03_crear_procedimientos_mantenimiento.sql`.
- Resultado obtenido: ambos procedimientos probados con caso exitoso y caso fallido (ver sección 9).

### Tarea 4 — Escenario de prueba real

- Qué se hizo: una tabla desechable (`dbo.PruebaMantenimiento`) con fragmentación de índice y estadísticas desactualizadas reales, para poder probar el módulo sin depender de que la base ya tuviera algo fragmentado por casualidad.
- Cómo se hizo: 8000 filas insertadas, luego `UPDATE` dispersos (no secuenciales) que alargan una columna indexada, forzando divisiones de página reales.
- Archivos creados o modificados: `sql/06-mantenimiento/04_generar_escenario_prueba.sql`.
- Resultado obtenido: 93.02 % y 55.27 % de fragmentación reales, y 2 estadísticas "nunca actualizadas" — confirmado con `sys.dm_db_index_physical_stats` y `sys.dm_db_stats_properties`.

### Tarea 5 — Capa Python y página Streamlit

- Qué se hizo: separación clara entre detección (lectura, usuario consultivo) y ejecución (usuario administrativo, con confirmación previa).
- Cómo se hizo: `get_admin_connection()` nueva en `connection.py` (sin tocar `get_connection()`); `queries/mantenimiento.py` con funciones de detección y de ejecución; `pages/6_Mantenimiento.py` con 4 secciones (estadísticas, índices, prueba de error, historial), cada botón de ejecución detrás de un checkbox de confirmación obligatorio.
- Archivos creados o modificados: `app/database/connection.py`, `app/database/queries/mantenimiento.py`, `app/pages/6_Mantenimiento.py`.
- Resultado obtenido: validado end-to-end contra SQL Server real (ver sección 9).

## 4. Decisiones técnicas tomadas

| Decisión | Motivo | Consecuencia para las siguientes semanas |
|---|---|---|
| Usuario administrativo solo con rol `db_ddladmin`, no `sysadmin` | Mínimo permiso necesario para `UPDATE STATISTICS`/`ALTER INDEX` | Si un futuro módulo necesita otra operación administrativa (p. ej. respaldos automáticos), revisar si `db_ddladmin` alcanza o hace falta otro rol específico |
| Decisión REORGANIZE/REBUILD calculada por la consulta de detección, no por la persona usuaria | Evita que alguien elija la operación equivocada desde la interfaz | La Semana 9 (integración) debe mantener esta regla si rediseña la interfaz |
| Registro de mantenimiento escrito por los procedimientos (encadenamiento de propiedad), nunca por permiso directo de INSERT | Mismo patrón que `sp_capturar_almacenamiento` (Semana 5); minimiza permisos otorgados | Cualquier módulo futuro que necesite escribir en una tabla de auditoría/registro debería seguir este mismo patrón |
| `commit()` en `finally`, no solo en el camino exitoso | pyodbc hace `ROLLBACK` automático al salir de `with` por una excepción, lo que borraba el registro de un fallo ya guardado por el procedimiento | Cualquier función Python que llame un procedimiento con manejo de errores propio (que registra antes de lanzar) debe aplicar este mismo patrón |

## 5. Cambios respecto al plan original

### Cambio 1

- Forma en que debía hacerse originalmente (X): generar el escenario de prueba de fragmentación con `DELETE` de filas intercaladas (como se hizo para el escenario de bloqueo de la Semana 4).
- Por qué no fue posible: con una clave `IDENTITY` secuencial, `DELETE` deja huecos, pero `INSERT` sigue escribiendo al final, no en esos huecos — no genera fragmentación real y medible.
- Error, limitación o evidencia encontrada: la consulta de fragmentación mostraba porcentajes muy bajos o inconsistentes con ese enfoque inicial.
- Solución alternativa aplicada (Y): `UPDATE` de filas dispersas (no consecutivas) que alargan el valor de una columna indexada, forzando divisiones de página reales.
- Consecuencias o limitaciones de la alternativa: ninguna relevante; el resultado (93.02 % y 55.27 % de fragmentación) es representativo de un caso real.
- ¿Debe revisarse después?: No.

### Cambio 2

- Forma en que debía hacerse originalmente (X): asumir que `VIEW DATABASE STATE` era el único permiso adicional necesario para el usuario consultivo (además de `VIEW SERVER STATE` de la Semana 3).
- Por qué no fue posible: la Sección 1 (estadísticas desactualizadas) seguía sin mostrar resultados aun con ese permiso otorgado.
- Error, limitación o evidencia encontrada: la app mostraba "No se encontraron estadísticas en el esquema dbo." mientras SSMS (como administrador) sí encontraba datos reales. Investigado: `sys.dm_db_stats_properties` exige además `SELECT` sobre la tabla y `VIEW DEFINITION` a nivel de base, que esta máquina nunca había recibido (se otorgó en la Semana 5, pero solo en la máquina de Juan).
- Solución alternativa aplicada (Y): se agregaron `GRANT VIEW DEFINITION` y `GRANT SELECT ON SCHEMA::dbo` al script de permisos del módulo, de forma idempotente.
- Consecuencias o limitaciones de la alternativa: ninguna; además hace que el Módulo 6 no dependa de que alguien haya corrido antes el script de permisos de la Semana 5 en esa máquina específica.
- ¿Debe revisarse después?: No, pero vale la pena que el equipo revise si todas las máquinas tienen `VIEW DEFINITION` otorgado, por si otro módulo futuro también lo necesita.

## 6. Configuración actual

- SGBD y versión: Microsoft SQL Server 2025 Express (misma instancia de la Semana 3).
- Nombre de instancia usado: `ANDREY-PC\SQLEXPRESS`.
- Herramientas y versiones: Python 3.11.9, Streamlit, pyodbc, SSMS.
- Versión de Python: 3.11.9.
- Versión del controlador ODBC: ODBC Driver 18 for SQL Server.
- Versiones de dependencias relevantes: sin cambios respecto a la Semana 3/5 (`numpy==2.2.6` ya fijado).
- Variables o parámetros necesarios: en `config/.env` (local, no versionado) se agregaron `DB_ADMIN_USER=adminsgbd_mantenimiento` y `DB_ADMIN_PASSWORD=<contraseña local>`.
- Permisos requeridos: usuario consultivo — `VIEW SERVER STATE` (Semana 3), `VIEW DATABASE STATE`, `VIEW DEFINITION`, `SELECT` sobre el esquema `dbo` y sobre `monitoreo.RegistroMantenimiento`; usuario administrativo — rol `db_ddladmin` en `BD_AdminSGBD`, `EXECUTE` sobre los dos procedimientos de mantenimiento.
- Configuraciones que no deben subirse al repositorio: las contraseñas reales de `adminsgbd_consulta` y `adminsgbd_mantenimiento` (solo en `config/.env`, ignorado por Git).

No se colocan contraseñas, llaves ni credenciales reales en este archivo.

## 7. Archivos importantes

| Archivo o carpeta | Propósito | Estado |
|---|---|---|
| `sql/06-mantenimiento/01_crear_usuario_administrativo.sql` | Crea el login/usuario administrativo separado | Completo |
| `sql/06-mantenimiento/02_otorgar_permisos_mantenimiento.sql` | Permisos de detección para el consultivo + tabla de registro | Completo |
| `sql/06-mantenimiento/03_crear_procedimientos_mantenimiento.sql` | Procedimientos de actualización de estadísticas y mantenimiento de índices | Completo |
| `sql/06-mantenimiento/04_generar_escenario_prueba.sql` | Genera `dbo.PruebaMantenimiento` con fragmentación/estadísticas reales para pruebas | Completo |
| `sql/06-mantenimiento/consultas_mantenimiento.sql` | Consultas de detección documentadas, para probar en SSMS | Completo |
| `app/database/connection.py` | Agrega `get_admin_connection()` sin modificar `get_connection()` | Completo |
| `app/database/queries/mantenimiento.py` | Capa de acceso a datos (detección y ejecución) | Completo |
| `app/pages/6_Mantenimiento.py` | Interfaz Streamlit del módulo | Completo |
| `evidencias/semana-08/` | 10 capturas de pantalla con la validación real, incluidos los problemas encontrados | Completo |

## 8. Consultas y operaciones administrativas

- Nombre o ubicación: `consultas_mantenimiento.sql`, consulta 1 (estadísticas desactualizadas).
  - Qué información obtiene o modifica: fecha de última actualización, filas modificadas desde entonces, y un estado ("Nunca actualizada", "Desactualizada", "Al día") por cada estadística del esquema `dbo`.
  - Vistas o tablas del sistema utilizadas: `sys.stats`, `sys.dm_db_stats_properties`, `sys.tables`, `sys.schemas`.
  - Permisos necesarios: `VIEW DATABASE STATE`, `VIEW DEFINITION`, `SELECT` sobre el esquema `dbo`.
  - Resultado esperado: lista de estadísticas ordenada por prioridad (nunca actualizadas primero).
  - Limitaciones conocidas: solo cubre el esquema `dbo`.

- Nombre o ubicación: `consultas_mantenimiento.sql`, consulta 2 (índices fragmentados).
  - Qué información obtiene o modifica: porcentaje de fragmentación de cada índice y la acción recomendada (`REORGANIZE`/`REBUILD`/ninguna).
  - Vistas o tablas del sistema utilizadas: `sys.dm_db_index_physical_stats` (modo `LIMITED`), `sys.indexes`, `sys.tables`, `sys.schemas`.
  - Permisos necesarios: `VIEW DATABASE STATE`.
  - Resultado esperado: lista de índices ordenada por mayor fragmentación.
  - Limitaciones conocidas: ninguna relevante detectada.

- Nombre o ubicación: `mantenimiento.sp_actualizar_estadisticas`.
  - Qué información obtiene o modifica: ejecuta `UPDATE STATISTICS <tabla> WITH FULLSCAN` sobre la tabla indicada.
  - Vistas o tablas del sistema utilizadas: valida existencia con `OBJECT_ID`; registra en `monitoreo.RegistroMantenimiento`.
  - Permisos necesarios: `EXECUTE` (solo `adminsgbd_mantenimiento`); internamente requiere permisos de `db_ddladmin`.
  - Resultado esperado: estadísticas recalculadas; registro de éxito o fallo.
  - Limitaciones conocidas: actualiza TODAS las estadísticas de la tabla, no una estadística específica.

- Nombre o ubicación: `mantenimiento.sp_reconstruir_indice`.
  - Qué información obtiene o modifica: ejecuta `ALTER INDEX <indice> ON <tabla> REORGANIZE` o `REBUILD`, según el parámetro `@modo`.
  - Vistas o tablas del sistema utilizadas: valida existencia de tabla e índice con `OBJECT_ID`/`sys.indexes`; registra en `monitoreo.RegistroMantenimiento`.
  - Permisos necesarios: `EXECUTE` (solo `adminsgbd_mantenimiento`); internamente requiere permisos de `db_ddladmin`.
  - Resultado esperado: índice reorganizado o reconstruido; registro de éxito o fallo.
  - Limitaciones conocidas: `REBUILD` en SQL Server Express no soporta `ONLINE` (no es un problema para este proyecto, solo para producción con alta concurrencia).

## 9. Pruebas realizadas

| Prueba | Procedimiento | Resultado esperado | Resultado real | Estado |
|---|---|---|---|---|
| Detección de estadísticas desactualizadas | Ejecutar consulta 1 en SSMS y desde la app, contra `dbo.PruebaMantenimiento` | Mostrar ambas estadísticas como nunca actualizadas | 2 estadísticas detectadas, estado "Nunca actualizada (prioridad maxima)" | Aprobada |
| Detección de índices fragmentados | Ejecutar consulta 2 en SSMS y desde la app | Mostrar los índices con su % de fragmentación y acción recomendada | `IX_PruebaMantenimiento_valor` 93.02 % (REBUILD), `PK__PruebaMa...` 55.27 % (REBUILD) | Aprobada |
| Actualización de estadísticas (caso exitoso) | Confirmar y ejecutar desde la Sección 1 sobre `dbo.PruebaMantenimiento` | Estadísticas actualizadas; estado pasa a "Al día", 0 filas modificadas | Confirmado con fecha real y `0.0` en `porcentaje_modificado`; registrado en el historial | Aprobada |
| Mantenimiento de índice (caso exitoso) | Confirmar y ejecutar REBUILD sobre `IX_PruebaMantenimiento_valor` | Fragmentación baja a un valor cercano a 0 % | Fragmentación pasó de 93.02 % a 0 %; registrado en el historial | Aprobada |
| Ejecución sin confirmar la casilla | Hacer clic en el botón de ejecución sin marcar la casilla | La app rechaza la ejecución con un mensaje claro | Mensaje de error mostrado, ninguna operación ejecutada | Aprobada |
| Caso fallido controlado | Botón "Probar caso fallido controlado" (tabla inexistente) | Error claro, sin romper la app, registrado como "Fallido" | Error `La tabla dbo.TablaQueNoExiste no existe en esta base de datos.` mostrado correctamente; registrado en el historial tras corregir el bug del `commit()` | Aprobada |
| Separación de credenciales | Revisar que `6_Mantenimiento.py`, `mantenimiento.py` y el repositorio no contengan contraseñas reales | Ninguna credencial expuesta | Confirmado: solo nombres de usuario en el código; contraseñas únicamente en `config/.env` local | Aprobada |

Evidencias en `evidencias/semana-08/` (10 capturas, numeradas en orden cronológico, incluyendo los dos problemas encontrados y su corrección).

## 10. Problemas encontrados

### Problema 1

- Descripción: la Sección 1 (estadísticas) de la app mostraba "No se encontraron estadísticas en el esquema dbo." aunque sí había datos reales.
- Mensaje de error exacto: ninguno (la consulta simplemente devolvía 0 filas, sin lanzar error).
- Causa identificada: `sys.dm_db_stats_properties` exige `SELECT` sobre la tabla y `VIEW DEFINITION` a nivel de base, que esta máquina nunca había recibido (otorgado en la Semana 5 solo en la máquina de Juan).
- Solución aplicada: se agregó el otorgamiento de `VIEW DEFINITION` y `SELECT ON SCHEMA::dbo` al script de permisos del módulo, de forma idempotente.
- Estado actual: resuelto y verificado.

### Problema 2

- Descripción: el historial no registraba un intento de mantenimiento fallido, aunque el procedimiento sí lo insertaba antes de lanzar el error.
- Mensaje de error exacto: no aplica (el error de SQL Server sí se mostraba bien; lo que faltaba era el registro en el historial).
- Causa identificada: pyodbc hace `ROLLBACK` automático al salir del bloque `with` por una excepción no capturada, deshaciendo también el `INSERT` del procedimiento.
- Solución aplicada: se movió `connection.commit()` a un bloque `finally` en ambas funciones de ejecución.
- Estado actual: resuelto y verificado (ver `semana_08_09` y `semana_08_10` en evidencias, que documentan el problema y la corrección).

### Problema 3

- Descripción: generar fragmentación de índice con `DELETE` sobre filas intercaladas (como en el escenario de bloqueo de la Semana 4) no funcionó.
- Mensaje de error exacto: no aplica (no fue un error, sino un resultado técnico distinto al esperado).
- Causa identificada: clave `IDENTITY` secuencial — los `INSERT` posteriores siguen escribiendo al final, no en los huecos dejados por `DELETE`.
- Solución aplicada: se cambió a `UPDATE` de filas dispersas que alargan una columna indexada, forzando divisiones de página reales.
- Estado actual: resuelto y verificado (93.02 % y 55.27 % de fragmentación real obtenidos).

## 11. Tareas no completadas

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Entradas de bitácora de las Semanas 4, 6 y 7 | No era responsabilidad de esta semana; se detectó pero no se corrigió | Que Nicky, Mar y Javi (o quien el equipo designe) agreguen sus entradas a `docs/bitacora/bitacora.md` | Media |

## 12. Deuda técnica y riesgos

- Soluciones temporales utilizadas: ninguna — todo lo construido esta semana quedó en su forma final, no hay atajos pendientes de reemplazar.
- Consultas que deben optimizarse: ninguna identificada; el volumen de datos de prueba es pequeño.
- Permisos que deben revisarse: confirmar que todas las máquinas del equipo tengan `VIEW DEFINITION` otorgado al usuario consultivo (no solo la de Juan y ahora la de Andrey), por si algún módulo futuro también lo necesita.
- Riesgos de seguridad: ninguno nuevo — las credenciales administrativas siguen fuera del repositorio, y el usuario administrativo tiene el permiso mínimo necesario (no es sysadmin).
- Riesgos para la demostración: la tabla `dbo.PruebaMantenimiento` es desechable y se recrea cada vez que se corre `04_generar_escenario_prueba.sql`; si se corre de nuevo antes de la presentación, los porcentajes de fragmentación pueden salir ligeramente distintos (sigue siendo representativo, solo cambian los números exactos).
- Dependencias de una versión o equipo específico: la demostración en vivo requiere que `dbo.PruebaMantenimiento` exista con fragmentación real; si se presenta desde otra máquina, hay que correr primero los 4 scripts de `sql/06-mantenimiento/` en esa instancia.

## 13. Instrucciones para la siguiente persona y su IA

- Qué debe revisar primero: este archivo completo, y el cronograma maestro sección "Semana 9 — Nicky: integración y pruebas".
- Qué no debe modificar sin consultar: los procedimientos `mantenimiento.sp_actualizar_estadisticas` y `mantenimiento.sp_reconstruir_indice` (la validación de existencia y el registro en `finally` son intencionales, no simplificar).
- Qué archivos debe abrir: `app/pages/6_Mantenimiento.py` (para integrarlo al menú general), `sql/06-mantenimiento/` completo.
- Qué pruebas debe repetir: "Probar mantenimiento exitoso" y "Probar mantenimiento fallido" (ya listadas en el cronograma para la Semana 9), usando `dbo.PruebaMantenimiento` o recreándola con `04_generar_escenario_prueba.sql`.
- Qué decisiones debe respetar: la separación entre usuario consultivo (detección) y administrativo (ejecución); la confirmación explícita obligatoria antes de cualquier operación destructiva; nunca otorgar `sysadmin` al usuario administrativo.
- Qué pendiente tiene mayor prioridad: ninguno bloqueante para integración; el único pendiente (entradas de bitácora faltantes) es documental, no funcional.

## 14. Estado del criterio de cierre

- Criterio de cierre de la semana: demostrar una operación administrativa real, comprobar su resultado y explicar sus permisos y riesgos.
- ¿Se cumplió completamente?: Sí.
- Evidencia: `evidencias/semana-08/semana_08_04_estadisticas_antes_despues.png` (actualización de estadísticas, antes/después) y `semana_08_07_indice_reconstruido.png` (reconstrucción de índice, 93.02 % → 0 %), más el historial completo en `semana_08_10_historial_completo_final.png`. Permisos y riesgos documentados en las secciones 6 y 12 de este archivo.
- Si no se cumplió, explicación precisa: no aplica.

## 15. Resumen breve para el equipo

El Módulo 6 (mantenimiento preventivo) quedó funcionando y validado contra SQL Server real: detecta estadísticas desactualizadas e índices fragmentados con el usuario consultivo (solo lectura), y permite actualizar estadísticas o reconstruir/reorganizar índices con un usuario administrativo separado, solo después de una confirmación explícita. Se probaron un caso exitoso y un caso fallido de cada operación, y toda operación (exitosa o fallida) queda registrada con fecha, objeto, usuario y resultado. En el camino se encontraron y corrigieron tres problemas reales: permisos de SQL Server incompletos para la detección de estadísticas, un bug donde el registro de un fallo se perdía por un rollback automático de pyodbc, y un enfoque inicial de generación de fragmentación que no funcionaba con claves secuenciales. El siguiente paso (Semana 9, Nicky) es integrar este módulo al menú general de la aplicación junto con los demás.
