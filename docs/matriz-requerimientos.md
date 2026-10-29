# Matriz de requerimientos

## Información general

| Campo | Valor |
|---|---|
| Proyecto | Sistema de monitoreo y administración de SGBD |
| Repositorio | `proyecto-admin-sgbd` |
| SGBD seleccionado | Microsoft SQL Server |
| Interfaz | Aplicación web local desarrollada con Python y Streamlit |
| Arquitectura | SQL Server, consultas administrativas y aplicación modular en Python |
| Estado del documento | Versión final de entrega |
| Última actualización | 28 de octubre de 2026 (semana 10) |

## Estados utilizados

| Estado | Significado |
|---|---|
| Pendiente | Todavía no se ha iniciado |
| En proceso | Se está trabajando en el requerimiento |
| Bloqueado | Depende de una decisión, permiso o recurso |
| Completado | Fue implementado y verificado |
| Parcial | Implementado en parte; la limitación se explica en la columna de evidencia |

## Organización funcional de la solución

Para organizar el desarrollo, el equipo decidió dividir la solución en seis módulos funcionales. Esta división constituye una decisión de diseño del equipo y permite separar las consultas y operaciones administrativas de acuerdo con su propósito.

Los módulos definidos son:

1. Estado general de la instancia.
2. Rendimiento.
3. Almacenamiento.
4. Respaldos.
5. Auditoría.
6. Mantenimiento preventivo.

## Integración general

| ID | Requerimiento | Solución definida | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| IG-01 | La solución debe iniciar correctamente | Aplicación web local desarrollada con Streamlit | La solución se ejecuta sin errores graves | Completado | `semana_09_05`; informe de pruebas, prueba 1 |
| IG-02 | Conectarse directamente con el SGBD | Conector de Microsoft SQL Server | Se ejecuta una consulta real desde la solución | Completado | `test_connection.py`; `semana_09_05` |
| IG-03 | Integrar los seis módulos requeridos | Navegación organizada entre los módulos | Se puede acceder a todos los módulos | Completado | `app/app.py` (`st.navigation`); `Nicky_semana9.md` |
| IG-04 | Utilizar información real | Consultas administrativas ejecutadas sobre SQL Server | Los resultados proceden de la instancia configurada | Completado | Consultas a DMV y catálogo en `app/database/queries/`; evidencias de las semanas 3 a 9 |
| IG-07 | Separar las operaciones consultivas y administrativas | Conexiones o usuarios con permisos diferentes según la operación | Las consultas utilizan permisos limitados y el mantenimiento solo utiliza los permisos administrativos necesarios | Completado | `get_connection()` / `get_admin_connection()`; `Andrey_semana8.md`; manual técnico §5 |

## Módulo 1: estado general de la instancia

| ID | Requerimiento | Presentación propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M1-01 | Consultar el nombre del servidor | Tarjeta | Coincide con el servidor conectado | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-02 | Consultar el identificador de la instancia | Tarjeta | Muestra la instancia real de SQL Server | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-03 | Mostrar el tipo de SGBD | Tarjeta | Identifica Microsoft SQL Server | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-04 | Mostrar la versión del SGBD | Tarjeta o campo informativo | Presenta la versión instalada | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-05 | Consultar el estado de la instancia | Indicador | Refleja el estado real de la instancia | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-06 | Obtener la fecha y hora de inicio | Tarjeta | El dato procede de SQL Server | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-07 | Calcular el tiempo de actividad | Indicador | Se calcula a partir del inicio de la instancia | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-08 | Obtener la memoria asignada | Tarjeta o gráfico | Muestra el valor con una unidad comprensible | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-09 | Obtener la memoria utilizada o una métrica equivalente | Tarjeta o gráfico | La métrica está documentada y utiliza datos reales | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-10 | Listar las bases de datos administradas | Tabla | Presenta las bases accesibles para el usuario consultivo | Completado | `evidencias/semana-03/`; `semana_09_05` |
| M1-11 | Permitir seleccionar, configurar o cambiar la instancia monitoreada | Parámetros o configuración de conexión | Se puede cambiar la conexión sin modificar el código fuente principal | Completado | Parámetros en `config/.env`, sin cambiar el código |

## Módulo 2: rendimiento

| ID | Requerimiento | Presentación propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M2-01 | Consultar las sentencias SQL de mayor consumo | Tabla ordenada | Identifica las consultas más costosas según una métrica definida | Completado | `evidencias/semana-04/` |
| M2-02 | Mostrar la duración de las consultas | Tabla o indicador | Permite consultar duración total, promedio o acumulada | Completado | `evidencias/semana-04/` |
| M2-03 | Consultar las sesiones activas | Tabla | Muestra identificador, usuario, estado y aplicación cuando estén disponibles | Completado | `evidencias/semana-04/` |
| M2-04 | Consultar las sesiones bloqueadas | Tabla y alerta | Identifica la sesión bloqueada y la sesión bloqueadora | Completado | `evidencias/semana-04/`; `semana_09_17` |
| M2-05 | Informar cuando no existen bloqueos | Mensaje informativo | La ausencia de bloqueos se presenta claramente | Completado | `evidencias/semana-04/`; `semana_09_18` |
| M2-06 | Consultar procesos o sesiones con mayor consumo | Tabla ordenada | Los resultados se ordenan según la métrica seleccionada | Completado | `evidencias/semana-04/` |
| M2-07 | Mostrar unidades comprensibles | Etiquetas del dashboard | CPU, tiempo, memoria y lecturas se presentan con unidades identificadas | Completado | `evidencias/semana-04/` |

## Módulo 3: almacenamiento

| ID | Requerimiento | Presentación propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M3-01 | Consultar los filegroups de la base de datos | Tabla o gráfico | Se muestran los filegroups existentes | Completado | `evidencias/semana-05/` |
| M3-02 | Obtener el espacio total asignado | Tarjeta o tabla | Presenta el tamaño asignado con una unidad comprensible | Completado | `evidencias/semana-05/` |
| M3-03 | Obtener el espacio utilizado | Tarjeta o gráfico | El valor se calcula utilizando información real de SQL Server | Completado | `evidencias/semana-05/` |
| M3-04 | Obtener el espacio disponible | Tarjeta o gráfico | Se diferencia claramente del espacio total y utilizado | Completado | `evidencias/semana-05/` |
| M3-05 | Calcular el porcentaje de utilización | Indicador | El porcentaje coincide con los valores de espacio utilizado y disponible | Completado | `evidencias/semana-05/` |
| M3-06 | Consultar el tamaño total de la base de datos | Tarjeta | Muestra el tamaño actual de los archivos de datos y de registro | Completado | `evidencias/semana-05/` |
| M3-07 | Consultar los archivos de datos y de registro | Tabla | Muestra nombre lógico, tipo, ubicación y tamaño | Completado | `evidencias/semana-05/` |
| M3-08 | Identificar las tablas de mayor tamaño | Tabla ordenada | Presenta primero las tablas con mayor consumo | Completado | `evidencias/semana-05/` |
| M3-09 | Identificar los índices de mayor tamaño | Tabla ordenada | Presenta primero los índices con mayor consumo | Completado | `evidencias/semana-05/` |
| M3-10 | Registrar mediciones históricas del almacenamiento | Tabla propia de historial | Guarda fecha, espacio total, utilizado y disponible | Completado | `evidencias/semana-05/` |
| M3-11 | Automatizar o facilitar el registro de mediciones | Procedimiento o script | Puede ejecutarse periódicamente sin modificar manualmente los valores | Completado | `evidencias/semana-05/` |
| M3-12 | Mostrar el crecimiento histórico | Gráfico temporal | Utiliza varias mediciones reales almacenadas en fechas diferentes | Completado | `evidencias/semana-05/` |

## Módulo 4: respaldos

| ID | Requerimiento | Presentación propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M4-01 | Consultar el respaldo exitoso más reciente | Tarjeta | Muestra la fecha y hora del último respaldo registrado correctamente | Completado | `evidencias/semana-06/semana_06_01_pagina_respaldos.png` |
| M4-02 | Consultar el tipo de respaldo | Tarjeta o tabla | Distingue entre respaldo completo, diferencial y del registro de transacciones | Completado | `evidencias/semana-06/semana_06_01_pagina_respaldos.png` |
| M4-03 | Consultar el historial de respaldos | Tabla | Presenta varios respaldos reales registrados por SQL Server | Completado | `semana_06_01` (dos respaldos reales); `semana_06_02` (restauración de prueba) |
| M4-04 | Mostrar el estado del respaldo | Indicador o columna | Permite reconocer si el respaldo finalizó correctamente o presentó errores | Completado | `evidencias/semana-06/semana_06_01_pagina_respaldos.png` |
| M4-05 | Interpretar administrativamente el estado de los respaldos | Indicador, color o mensaje | Explica si la información representa una condición adecuada o un posible riesgo | Completado | `evidencias/semana-06/semana_06_01_pagina_respaldos.png` |

## Módulo 5: auditoría

| ID | Requerimiento | Presentación propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M5-01 | Consultar los logins registrados en la instancia | Tabla | Muestra información administrativa relevante sin exponer datos sensibles | Completado | `semana_09_02` (logins completos tras D-10) |
| M5-02 | Consultar los usuarios de las bases de datos | Tabla y filtro | Permite identificar los usuarios existentes en la base seleccionada | Completado | Pestaña "Logins y Usuarios"; informe de pruebas |
| M5-03 | Consultar los roles de servidor | Tabla | Muestra los roles y sus integrantes | Completado | Pestaña "Roles y Miembros" |
| M5-04 | Consultar los roles de base de datos | Tabla | Muestra los roles y usuarios asignados | Completado | Pestaña "Roles y Miembros" |
| M5-05 | Consultar los permisos otorgados directamente | Tabla filtrable | Identifica el usuario, permiso, estado y objeto relacionado | Completado | Pestaña "Permisos" con filtros por usuario/rol y permiso |
| M5-06 | Consultar los permisos obtenidos mediante roles | Tabla filtrable | Permite identificar el rol del cual procede cada permiso | Parcial | Los permisos de cada rol y los integrantes de cada rol se ven en pestañas separadas; no hay una vista única usuario → rol → permiso, y los permisos implícitos de los roles fijos no aparecen |
| M5-07 | Evitar resultados duplicados o confusos | Consultas organizadas | Cada relación entre usuario, rol y permiso puede interpretarse correctamente | Completado | Consultas separadas por tipo de relación; `DISTINCT` en dependencias |
| M5-08 | Detectar objetos con dependencias problemáticas | Tabla y alerta | Muestra objetos con referencias que no pueden resolverse correctamente | Completado | `semana_09_16`; sin falsos positivos tras D-15 (`semana_09_03`) |

## Módulo 6: mantenimiento preventivo

| ID | Requerimiento | Solución propuesta | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|---|
| M6-01 | Consultar objetos que podrían requerir mantenimiento | Aplicación Python y consultas SQL | Presenta una lista real de objetos seleccionables | Completado | `evidencias/semana-08/semana_08_02`, `semana_08_05` |
| M6-02 | Actualizar las estadísticas de un objeto seleccionado | Acción administrativa desde Python | La operación se ejecuta sobre el objeto indicado | Completado | `semana_08_04` (antes/después); `semana_09_11`, `semana_09_12` |
| M6-03 | Permitir actualizar estadísticas de forma controlada | Selección de base, esquema y objeto | No se ejecutan operaciones generales accidentalmente | Completado | Selección de tabla e índice con confirmación obligatoria; la base es la de `DB_NAME` y el esquema es `dbo` |
| M6-04 | Actualizar o validar la definición de módulos SQL | Acción administrativa equivalente | La operación utiliza un mecanismo válido de SQL Server y documenta su efecto | Pendiente | No implementado: el Módulo 6 actualiza estadísticas e índices, pero no actualiza ni valida la definición de módulos SQL (`sp_refreshsqlmodule`). Los módulos con dependencias rotas se detectan en el Módulo 5 |
| M6-05 | Manejar operaciones exitosas | Mensaje de resultado | La aplicación confirma qué operación terminó correctamente | Completado | `semana_08_07`; `semana_09_15` |
| M6-06 | Manejar operaciones fallidas | Mensaje de error | La aplicación presenta un error comprensible sin exponer datos sensibles | Completado | `semana_09_09`, `semana_09_10` |

## Requerimientos no funcionales

| ID | Requerimiento | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|
| RNF-01 | Usabilidad y navegación | La interfaz permite localizar y utilizar los módulos sin instrucciones adicionales complejas | Completado | Menú con nombres claros e Inicio con descripción de cada módulo |
| RNF-02 | Calidad visual | Existe consistencia en títulos, controles, tablas, gráficos, unidades y mensajes | Completado | Diseño uniforme de la semana 9 (D-01 a D-13) |
| RNF-03 | Organización modular del código | El código separa adecuadamente la interfaz, la conexión, las consultas y la lógica de la aplicación | Completado | Capas `pages/`, `services/`, `database/`; manual técnico §2 |
| RNF-04 | Nombres y legibilidad | Se utilizan nombres descriptivos y una estructura comprensible | Completado | Manual técnico §2 |
| RNF-05 | Rendimiento de las consultas | Las consultas se ejecutan en tiempos razonables y evitan extraer información innecesaria | Completado | Límites `TOP` en todas las consultas de monitoreo; manual técnico §2 |
| RNF-06 | Robustez | La solución maneja errores de conexión, consultas sin resultados y operaciones fallidas | Completado | Informe de pruebas, pruebas 2, 3, 4, 5 y 9 |
| RNF-07 | Configuración y portabilidad | Los parámetros de conexión y las dependencias pueden configurarse sin modificar múltiples partes del código | Completado | `config/.env.example`; `requirements.txt` |
| RNF-08 | Protección de información sensible | No existen credenciales reales en el código, la documentación ni el historial del repositorio | Completado | Revisión del historial completo en la semana 10 sin contraseñas reales; `.gitignore` |

## Repositorio y trabajo colaborativo

| ID | Requerimiento | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|
| REP-01 | Mantener un repositorio accesible y completo | El enlace funciona y contiene el código, los scripts, la documentación y la presentación | En proceso | Código, `sql/` y `docs/` completos; falta agregar la presentación final |
| REP-02 | Evidenciar un historial progresivo | Los cambios se distribuyen durante el periodo de desarrollo y no se concentran únicamente al final | Completado | Commits del 29 de agosto al 28 de octubre de 2026, distribuidos por semana |
| REP-03 | Identificar los aportes individuales | Los commits permiten reconocer claramente a la persona responsable de cada cambio | Completado | Commits desde las cuentas personales de cada integrante |
| REP-04 | Garantizar la participación del grupo | Todos los integrantes presentan aportes relevantes y verificables | Completado | Los cinco integrantes tienen commits y archivo de continuidad |
| REP-05 | Utilizar mensajes de commit claros | Los mensajes describen las funcionalidades, correcciones o documentos incorporados | Completado | Historial de `main` |
| REP-06 | Mantener organizado el repositorio | Las carpetas, los archivos, la rama principal y la versión final se encuentran ordenados | Completado | Estructura descrita en el README; etiqueta de versión final al cerrar la semana 10 |

### Reglas del repositorio

- El proyecto utilizará un único repositorio grupal.
- Cada integrante realizará sus aportes desde su cuenta personal.
- La rama `main` contendrá una versión estable y ejecutable.
- No se almacenarán credenciales ni información sensible.
- La entrega final se identificará mediante una etiqueta de versión.

## Documentación técnica

| ID | Requerimiento | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|---|
| DOC-01 | Documentar la arquitectura de la solución | Explica los componentes de presentación, lógica y acceso a datos, así como sus relaciones | Completado | `docs/arquitectura/arquitectura.md`; manual técnico §1 |
| DOC-02 | Documentar las decisiones de diseño | Justifica la selección de SQL Server, Python, Streamlit y la organización modular | Completado | Manual técnico §7; bitácora |
| DOC-03 | Crear un manual de instalación | Permite preparar el entorno, instalar dependencias y configurar la conexión | Completado | `docs/manuales/instalacion.md` |
| DOC-04 | Crear un manual de ejecución | Explica cómo iniciar la aplicación Streamlit y los demás elementos necesarios (Power BI se descartó en la semana 1) | Completado | Manual de instalación §9 y §10; manual de usuario §1 |
| DOC-05 | Crear un manual técnico | Explica las consultas, vistas, procedimientos, permisos, configuración y estructura del código | Completado | `docs/tecnica/manual-tecnico.md` |
| DOC-06 | Crear un manual de usuario | Explica cómo utilizar cada módulo e interpretar sus resultados | Completado | `docs/manuales/usuario.md` |
| DOC-07 | Mantener un archivo README | Presenta el proyecto y contiene instrucciones generales para instalarlo y ejecutarlo | Completado | `README.md` |
| DOC-08 | Documentar las dependencias | Identifica programas, controladores, bibliotecas y versiones necesarias | Completado | Manual de instalación §1; `requirements.txt` |
| DOC-09 | Incluir archivos de configuración de ejemplo | Permite configurar el sistema sin publicar credenciales reales | Completado | `config/.env.example` con variables consultivas y administrativas |
| DOC-10 | Mantener una bitácora de seguimiento | Registra semanalmente avances, decisiones, problemas y soluciones | Completado | `docs/bitacora/bitacora.md` (semanas 1 a 10) |
| DOC-11 | Mantener evidencias de pruebas | Incluye resultados verificables de operaciones exitosas y fallidas | Completado | `evidencias/semana-03` a `semana-09`; informe de pruebas |