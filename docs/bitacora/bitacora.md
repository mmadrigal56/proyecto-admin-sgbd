# Bitácora del proyecto

## Información general

| Campo | Valor |
|---|---|
| Proyecto | Sistema de monitoreo y administración de SGBD |
| SGBD seleccionado | Microsoft SQL Server |
| Repositorio | `proyecto-admin-sgbd` |
| Fecha de entrega | 3 de noviembre de 2026 |
| Integrantes | Juan Artavia, Javier Garita, Mariana Madrigal, Nicole Masís, Andrey Solís |

## Registro de actividades

### Semana 1 — Definición inicial del proyecto

**Periodo:** 24 al 30 de agosto de 2026  
**Responsable:** Mariana

**Actividades realizadas:**

- Se seleccionó Microsoft SQL Server como SGBD principal.
- Se creó el repositorio público `proyecto-admin-sgbd`.
- Se agregaron los integrantes como colaboradores.
- Se protegió la rama `main`.
- Se creó la rama `docs/estructura-inicial`.
- Se definió una estructura inicial de carpetas.
- Se elaboró la matriz inicial de requerimientos.
- Se clasificaron los requisitos por módulo.
- Se definió la arquitectura preliminar.
- Se creó `docs/arquitectura/arquitectura.md`.
- Se documentaron las capas de presentación, lógica y acceso a datos.

**Decisiones tomadas:**

- Utilizar Microsoft SQL Server como plataforma principal.
- Mantener `main` como rama estable.
- Trabajar las funcionalidades mediante ramas y pull requests.
- Registrar los cambios progresivamente desde las cuentas personales.
- Desarrollar una aplicación web local con Python y Streamlit.
- Utilizar `pyodbc` para conectarse con SQL Server.
- Utilizar Streamlit y Plotly para presentar indicadores y gráficos.
- Separar las operaciones consultivas de las administrativas mediante permisos apropiados.
- No almacenar credenciales reales en el repositorio.


**Resultados:**

- Repositorio disponible para el equipo.
- Matriz de requerimientos creada y publicada en la rama de documentación.
- Primeros commits identificables en el historial.
- Matriz alineada con los criterios principales del proyecto.
- Arquitectura preliminar documentada.

**Cambio respecto a la propuesta inicial:**

Inicialmente se consideró utilizar Power BI como interfaz consultiva y Python para mantenimiento. Esta alternativa se sustituyó por una aplicación web local desarrollada completamente con Python y Streamlit, debido a que facilita la integración de los seis módulos en una misma interfaz.


### Semana 3 — Módulo 1: estado general de la instancia

**Periodo:** 13 de setiembre de 2026
**Responsable:** Andrey

**Nota de continuidad:** no se encontró en el repositorio una entrada de bitácora para la Semana 2 (Javi), aunque sí existen sus archivos técnicos (`connection.py`, `app.py`, scripts de `sql/00-configuracion`, `.env.example`, pruebas de conexión y permisos). Se retomó ese trabajo tal cual está, sin modificarlo.

**Actividades realizadas:**

- Se verificó la conexión heredada de la Semana 2 (`app/database/connection.py`).
- Se identificó que el usuario consultivo `adminsgbd_consulta` no tenía permiso para leer vistas de administración dinámica (DMVs) del servidor.
- Se creó `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql` para otorgar `VIEW SERVER STATE` (permiso de solo lectura).
- Se documentaron las consultas administrativas del módulo 1 en `sql/01-estado-instancia/consultas_estado_instancia.sql`: servidor/instancia/versión, fecha de inicio y tiempo de actividad, memoria del proceso, y bases de datos administradas.
- Se creó la capa de acceso a datos `app/database/queries/estado_instancia.py`.
- Se creó la página de Streamlit `app/pages/1_Estado_Instancia.py` con tarjetas, manejo de errores por sección y fecha de actualización.
- Se creó la base de datos, el login/usuario consultivo y el entorno virtual en la máquina de Andrey (no existían localmente, solo en el repositorio como código).
- Se ejecutó la aplicación completa contra la instancia real `Espacio-Libre-para-Andrey\SQLEXPRESS` (SQL Server 2025 Express, versión 17.0.1135.8).

**Problemas encontrados**

- El usuario consultivo `adminsgbd_consulta` no existía en la máquina de Andrey: cada integrante ejecuta SQL Server localmente, por lo que los scripts de la Semana 2 deben correrse una vez por máquina, no solo una vez para todo el equipo. Se resolvió ejecutando `sql/00-configuracion/crear_base_pruebas.sql` y `crear_usuario_consultivo.sql` en la instancia de Andrey.
- `pip install -r requirements.txt` falló porque `numpy==2.5.2` requiere Python 3.12+, y Andrey tiene Python 3.11.9 instalado. Se detectó que el `requirements.txt` fue generado con una versión de Python más nueva que la de al menos un integrante del equipo.

**Soluciones aplicadas**

- Se otorgó `VIEW SERVER STATE` al usuario consultivo mediante un nuevo script (`sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql`), necesario para leer las DMVs de actividad y memoria.
- Se fijó `numpy==2.2.6` en `requirements.txt` (versión compatible con Python 3.11) para desbloquear la instalación en la máquina de Andrey.

**Decisiones tomadas:**

- Se otorga `VIEW SERVER STATE` al usuario consultivo en lugar de crear un usuario adicional, porque es el permiso mínimo necesario y de solo lectura.
- El "estado operativo" se determina implícitamente: si la consulta de actividad responde, la instancia está en línea; si falla, se muestra un error explicando la causa probable (servidor caído o permisos insuficientes).

**Problemas encontrados**

- [COMPLETAR tras la prueba real: por ejemplo, error de permisos si no se ejecutó el script de otorgamiento, o driver ODBC no encontrado]

**Soluciones aplicadas**

- [COMPLETAR tras la prueba real]

**Resultados y pendientes**

- **Validado con SQL Server real.** Servidor: `Espacio-Libre-para-Andrey\SQLEXPRESS`, edición Express, versión de producto 17.0.1135.8 (RTM), collation `Modern_Spanish_CI_AS`.
- Estado operativo: en línea. Fecha de inicio: 2026-09-13 13:48:20. Tiempo de actividad: 0 días, 10 horas.
- Memoria: 145.0 MB física en uso, 439.8 MB virtual comprometida, 0.0 MB en páginas grandes.
- Bases de datos administradas detectadas: `BD_AdminSGBD`, `DB_EXTENTS`, `DB_PRUEBA`, `DB_TBS`, `LaboratorioDB`, `master`, `MiBaseDeDatos`, `model`, `msdb`, `tempdb` — todas `ONLINE`, modelo `SIMPLE`.
- Evidencias capturadas en `evidencias/semana-03/`, incluyendo la prueba de error controlado (servicio de SQL Server detenido): las 4 secciones mostraron errores claros e independientes sin caer la aplicación, y todo volvió a la normalidad al reiniciar el servicio.
- **Semana 3 cerrada.** Pendiente para el equipo: decidir si se fija `numpy==2.2.6` en `requirements.txt` para todos, o si se estandariza la versión de Python del equipo a 3.12+.

### Semana 5 — Módulo 3: gestión del almacenamiento

**Periodo:** 24 – 25 de septiembre de 2026  
**Responsable:** Juan Artavia

**Actividades realizadas**

- Se prepararon en la máquina de Juan (`Juan\SQLEXPRESS`, SQL Server 2025 Express 17.0.1000.7) la base `BD_AdminSGBD`, el usuario consultivo y el permiso `VIEW SERVER STATE` con los scripts de las semanas 2 y 3. Se verificaron los módulos 1 y 2 heredados.
- Se crearon y ejecutaron los scripts de `sql/03-almacenamiento/`: objetos del historial, permisos, carga de prueba y consultas documentadas.
- Se implementaron `app/database/queries/almacenamiento.py`, `app/services/almacenamiento.py` y `app/pages/3_Almacenamiento.py`.
- Se creó la captura periódica (`scripts/capturar_almacenamiento.py` + `.bat`) y la tarea `ProyectoSGBD_CapturaAlmacenamiento` en el Programador de tareas de Windows (cada 6 horas).
- Se generó crecimiento real con 20 000 filas: datos utilizados 4.38 → 20.69 MB (+16.31 MB); tamaño asignado total 16 → 144 MB por autocrecimiento de 64 MB en datos y log.
- Se probó el manejo de errores deteniendo el servicio `SQL Server (SQLEXPRESS)`.

**Decisiones tomadas**

- La captura periódica se programa con el Programador de tareas de Windows: en Express, `SQL Server Agent (SQLEXPRESS)` aparece como `Stopped` / `Disabled` (`sys.dm_server_services`).
- El usuario consultivo recibe `EXECUTE` solo sobre `monitoreo.sp_capturar_almacenamiento`, no `INSERT` sobre la tabla (encadenamiento de propiedad).
- Se otorga `VIEW DEFINITION` en `BD_AdminSGBD`: sin él las tablas e índices no son visibles para el usuario consultivo.
- Umbrales: archivo ≥ 80 % de su tamaño máximo = advertencia, ≥ 90 % = crítico; disco < 20 % libre = advertencia, < 10 % = crítico.
- La página verifica la conexión una sola vez al inicio; si falla, muestra un único error y no intenta las demás secciones.
- Se agrega la carpeta `app/services/` para separar la lógica de evaluación de la presentación.

**Problemas encontrados**

- Con el servidor detenido, la primera versión de la página intentaba conectarse en cada sección (~15 s de espera cada una) y el panel de indicadores quedaba vacío mientras cargaba.
- El script de usuario consultivo se guardó por error con la contraseña local.

**Soluciones aplicadas**

- Verificación única de conexión al inicio de la página (aviso en indicadores + un solo error).
- `git restore sql/00-configuracion/crear_usuario_consultivo.sql` antes de cualquier commit; la contraseña solo vive en `config/.env` (ignorado por Git).

**Resultados y pendientes**

- Módulo 3 validado contra SQL Server real; evidencias en `evidencias/semana-05/` (24 capturas + salidas de terminal).
- 25/9: la tarea programada midió sola a las 09:55; tras una segunda carga de 20 000 filas, el historial muestra 6 mediciones en dos fechas (datos utilizados 4.38 → 32.56 MB, +28.18 MB). M3-12 completado.
- **Semana 5 cerrada.**
- Pendiente detectado: la Semana 4 no tiene entrada en esta bitácora (sí tiene `Nicky_semana4.md`).

### Semana 8 — Módulo 6: mantenimiento preventivo

**Periodo:** 12 de octubre de 2026
**Responsable:** Andrey

**Nota de continuidad:** se revisó `Javi_semana7.md` (traspaso del Módulo 5) y el cronograma maestro, sección "Semana 8". No se encontró contradicción entre ambos documentos. También se detectó que, igual que con la Semana 2, las bitácoras de las Semanas 4, 6 y 7 no tienen entrada en este archivo (aunque sí existen `Nicky_semana4.md`, `Mar_semana6.md` y `Javi_semana7.md` en `evidencias/`); queda anotado como pendiente del equipo, no se resolvió aquí.

**Actividades realizadas:**

- Se sincronizó la rama local `Andrey` con `main` (Módulos 2 a 5 ya fusionados por el equipo).
- Se creó la carpeta `sql/06-mantenimiento/` con: creación de un usuario administrativo separado (`adminsgbd_mantenimiento`, rol `db_ddladmin`, sin privilegios de sysadmin), otorgamiento de permisos de lectura al usuario consultivo (`VIEW DATABASE STATE`, `VIEW DEFINITION`, `SELECT` sobre el esquema `dbo`), tabla `monitoreo.RegistroMantenimiento`, dos procedimientos almacenados (`mantenimiento.sp_actualizar_estadisticas`, `mantenimiento.sp_reconstruir_indice`) y un script para generar un escenario de prueba real y reproducible (`dbo.PruebaMantenimiento`).
- Se agregó `get_admin_connection()` a `app/database/connection.py`, separada de `get_connection()` (consultivo), sin modificar el comportamiento de los módulos anteriores.
- Se creó `app/database/queries/mantenimiento.py` y `app/pages/6_Mantenimiento.py`: detección de estadísticas desactualizadas e índices fragmentados (usuario consultivo, solo lectura), y ejecución de mantenimiento con confirmación explícita (checkbox + botón) usando el usuario administrativo.
- Se generó el escenario de prueba real: tabla con 8000 filas, fragmentación inducida por `UPDATE` dispersos (no por `DELETE`, que con clave `IDENTITY` secuencial no fragmenta de forma confiable).
- Se validó la detección contra SQL Server real: 2 estadísticas "nunca actualizadas" y 2 índices fragmentados (93.02 % y 55.27 %, ambos con acción recomendada `REBUILD`).
- Se ejecutó una actualización de estadísticas real (caso exitoso) y una reconstrucción de índice real (caso exitoso), verificando el estado antes y después en ambos casos.
- Se probó un caso fallido controlado (actualizar estadísticas de una tabla inexistente) y se verificó que el error se muestra de forma clara y queda registrado.
- Se verificó en cada caso que la operación quedó registrada en `monitoreo.RegistroMantenimiento` con fecha, operación, objeto, usuario y resultado.

**Problemas encontrados**

- `sys.dm_db_stats_properties` requiere, además de `VIEW DATABASE STATE`, permiso `SELECT` sobre la tabla consultada; sin él, la función devuelve 0 filas en silencio (sin error), lo que hacía parecer vacía la detección de estadísticas aunque sí había datos. `sys.dm_db_index_physical_stats` no tiene este requisito adicional, por lo que la Sección 2 (índices) funcionaba mientras la Sección 1 (estadísticas) no — eso ayudó a aislar la causa.
- El usuario consultivo de la máquina de Andrey no tenía `VIEW DEFINITION` otorgado: ese permiso se otorgó en la Semana 5 en la máquina de Juan, pero cada integrante corre SQL Server localmente (misma lección de la Semana 3), así que nunca se propagó a esta máquina.
- Generar fragmentación con `DELETE` sobre una clave `IDENTITY` secuencial no funciona: SQL Server sigue insertando al final, no en los huecos. Se corrigió usando `UPDATE` dispersos que alargan el valor de una columna indexada, forzando divisiones de página reales.
- El `commit()` de pyodbc, ejecutado solo en el camino exitoso, hacía que un `ROLLBACK` automático (al salir del bloque `with` por una excepción) borrara también el `INSERT` de "Fallido" que el procedimiento ya había hecho antes de lanzar el error. El primer intento de la prueba de error controlado no quedó registrado en el historial por esta razón.
- Al correr `python -m streamlit run app/app.py` sin haber activado antes el entorno virtual, se usó por error el Python del sistema (sin `streamlit` instalado).

**Soluciones aplicadas**

- Se agregó `GRANT SELECT ON SCHEMA::dbo` al usuario consultivo (además de `VIEW DATABASE STATE` y `VIEW DEFINITION`, ambos otorgados de forma idempotente) en `02_otorgar_permisos_mantenimiento.sql`, documentando la causa exacta para que el resto del equipo no repita el mismo diagnóstico.
- Se corrigió `04_generar_escenario_prueba.sql` para fragmentar con `UPDATE` dispersos sobre una columna indexada, en vez de `DELETE`.
- Se movió el `connection.commit()` a un bloque `finally` en `ejecutar_actualizacion_estadisticas()` y `ejecutar_mantenimiento_indice()`, para que el registro de un intento fallido se conserve siempre, incluso cuando la excepción sigue propagándose hacia Streamlit.
- Se activó el entorno virtual (`.\.venv\Scripts\Activate.ps1`) antes de levantar la aplicación.

**Decisiones tomadas:**

- El usuario administrativo (`adminsgbd_mantenimiento`) se agrega solo al rol `db_ddladmin` de `BD_AdminSGBD`, no a `sysadmin`: es el permiso mínimo necesario para `UPDATE STATISTICS` y `ALTER INDEX`, sin darle control total de la instancia ni acceso a otras bases.
- La detección (qué necesita mantenimiento) siempre corre con el usuario consultivo, de solo lectura; la ejecución (el cambio real) siempre corre con el usuario administrativo, y solo después de que la persona marque una casilla de confirmación explícita. Ningún botón ejecuta nada sin ese paso.
- El registro de mantenimiento (`monitoreo.RegistroMantenimiento`) lo escriben los procedimientos almacenados, no la aplicación directamente, usando encadenamiento de propiedad — el usuario administrativo nunca recibe `INSERT` directo sobre la tabla, y el consultivo solo tiene `SELECT` sobre ella (mismo patrón que `sp_capturar_almacenamiento` en la Semana 5).
- La decisión entre `REORGANIZE` y `REBUILD` la calcula la consulta de detección según el porcentaje de fragmentación (≥30 % `REBUILD`, 5–30 % `REORGANIZE`), no la persona que usa la aplicación, para evitar elegir la operación equivocada.

**Resultados y pendientes**

- **Validado con SQL Server real**, instancia `ANDREY-PC\SQLEXPRESS`.
- Estadísticas: antes — 2 estadísticas de `dbo.PruebaMantenimiento` "nunca actualizadas"; después de ejecutar la actualización — ambas con fecha real y `0` filas modificadas (estado "Al día").
- Índices: antes — `IX_PruebaMantenimiento_valor` con 93.02 % de fragmentación (`REBUILD`), `PK__PruebaMa...` con 55.27 %; después de reconstruir el primero — `0 %` de fragmentación, acción recomendada "Sin acción necesaria".
- Caso fallido: intento de actualizar estadísticas de `dbo.TablaQueNoExiste` mostró el error `La tabla dbo.TablaQueNoExiste no existe en esta base de datos.` de forma clara (sin romper la aplicación) y quedó registrado en el historial con `resultado = Fallido`.
- Historial de mantenimiento (`monitoreo.RegistroMantenimiento`) verificado con 6 operaciones reales: 4 actualizaciones de estadísticas exitosas, 1 reconstrucción de índice exitosa, 1 actualización fallida controlada.
- Evidencias capturadas en `evidencias/semana-08/` (10 capturas), incluyendo la detección del problema de permisos y del problema del `commit()`, no solo el resultado final.
- **Semana 8 cerrada.** Pendiente para el equipo: las bitácoras de las Semanas 4, 6 y 7 siguen sin entrada en este archivo.

### Semana 9 — Integración y pruebas

**Periodo:** 20 de octubre de 2026
**Responsable:** Nicky

**Nota de continuidad:** se revisó `Andrey_semana8.md` (traspaso del Módulo 6) y el cronograma maestro, sección "Semana 9 — Nicky: integración y pruebas". Se respetó lo indicado por Andrey: no se modificaron los procedimientos de mantenimiento ni la decisión REBUILD/REORGANIZE.

**Actividades realizadas:**

- Se creó la rama `semana9/integracion` a partir de `main`.
- Se integraron los seis módulos en una sola aplicación: `app/app.py` usa `st.navigation` con 7 páginas (Inicio + 6 módulos) y se agregó `app/inicio.py` con la prueba de conexión y la lista de módulos.
- Se unificó el diseño: encabezado "Módulo N — Nombre" con descripción, botón "Actualizar información" y hora de actualización; formato de fecha AAAA-MM-DD; tablas sin columna de índice; encabezados de tablas en español; `width="stretch"` en lugar de `use_container_width`.
- Se revisaron las consultas y el manejo de conexiones: el historial de mantenimiento se limitó a las 50 operaciones más recientes; no se encontraron fugas de conexiones.
- Se ejecutaron las 9 pruebas planificadas (conexión correcta e incorrecta, consultas sin resultados, permisos insuficientes, servidor detenido, bloqueo real, objeto problemático, mantenimiento exitoso y fallido), todas aprobadas, con 26 evidencias.
- Se redactaron el informe de pruebas, la lista de defectos y `Nicky_semana9.md`.

**Decisiones tomadas:**

- Se usó `st.navigation` en lugar del descubrimiento automático de `pages/` para controlar el nombre y el orden del menú.
- Para simular una conexión incorrecta se usó una variable de entorno, sin tocar `config/.env` ni probar una contraseña errónea, para no bloquear el login.
- No se cambiaron los textos del Módulo 6 como "Sin accion necesaria", porque la lógica los compara y cambiarlos implica tocar consulta y lógica a la vez.

**Problemas encontrados:**

- Auditoría mostraba un error de consulta como lista vacía (D-11) y no veía todos los logins por falta de permiso de metadatos (D-10).
- La consulta de dependencias rotas devolvía falsos positivos (D-15).
- En el Módulo 6, la casilla de confirmación quedaba marcada después de ejecutar un mantenimiento (D-17).

**Soluciones aplicadas:**

- Auditoría ahora muestra el error en pantalla (D-11) y se agregó `sql/05-auditoria/00_otorgar_permisos_auditoria.sql` con `VIEW ANY DEFINITION` (D-10).
- La consulta de dependencias se reescribió para detectar solo dependencias realmente rotas (D-15).
- La casilla de confirmación se desmarca sola después de cada ejecución (D-17).

**Resultados y pendientes:**

- **Probado con SQL Server real**, instancia `Nicky\SQLEXPRESS`: 9 de 9 pruebas aprobadas; evidencias en `evidencias/semana-09/` (26 capturas), con `informe_pruebas.md`, `lista_defectos.md` y `Nicky_semana9.md`.
- Los defectos corregidos tienen un commit cada uno en la rama `semana9/integracion` (detalle en `lista_defectos.md`).
- Pendientes menores: valores sin tildes en el Módulo 6 (por la lógica que los compara) y cierre explícito de conexiones como recomendación.
- **Semana 9 cerrada**; la rama `semana9/integracion` es el release candidate, en el Pull Request #13 pendiente de revisión del equipo.



## Formato para futuras entradas

### Semana # — Nombre de la etapa

**Periodo:**  
**Responsable:**

**Actividades realizadas**

-

**Decisiones tomadas**

-

**Problemas encontrados**

-

**Soluciones aplicadas**

-

**Resultados y pendientes**

-