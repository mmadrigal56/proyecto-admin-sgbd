# Manual de usuario

Este manual explica cómo usar cada página de la aplicación y cómo interpretar sus resultados. Para instalarla, ver el [manual de instalación](instalacion.md).

## 1. Iniciar la aplicación

```powershell
cd proyecto-admin-sgbd
.venv\Scripts\Activate.ps1
streamlit run app/app.py
```

El navegador abre `http://localhost:8501`. El menú de la izquierda tiene siete páginas: **Inicio** y los módulos **1 a 6**.

## 2. Elementos comunes

| Elemento | Qué hace |
|---|---|
| **Actualizar información** | Vuelve a consultar SQL Server y redibuja la página |
| *Última actualización de esta página* | Hora local en que se leyeron los datos |
| Cuadro verde | Resultado correcto o ausencia de problemas |
| Cuadro azul | Información, por ejemplo una consulta sin resultados |
| Cuadro amarillo | Advertencia que conviene revisar |
| Cuadro rojo | Error de conexión, de permisos o de consulta; debajo aparece el detalle técnico |

Cada sección consulta SQL Server por separado: si una falla (por ejemplo, por un permiso faltante), las demás siguen funcionando. Una consulta **sin resultados** se muestra en azul o verde; un **error** se muestra siempre en rojo, para no confundir "no hay datos" con "no se pudo consultar".

## 3. Inicio

Prueba la conexión con la cuenta consultiva y muestra **servidor**, **base de datos** y **usuario de consulta**. Si aparece "No fue posible conectarse a SQL Server", revisar que el servicio esté iniciado y que `config/.env` sea correcto. Debajo hay un enlace a cada módulo con una descripción breve.

## 4. Módulo 1 — Estado de la instancia

| Sección | Cómo interpretarla |
|---|---|
| Servidor e instancia | Nombre del servidor, instancia, edición, versión del producto, nivel (RTM/CU) y collation |
| Estado operativo | Si la consulta responde, la instancia está en línea; muestra la fecha y hora de inicio del servicio y el tiempo de actividad |
| Memoria | Memoria física en uso, memoria virtual comprometida y páginas grandes **del proceso de SQL Server**, en MB (no de todo Windows) |
| Bases de datos administradas | Nombre, estado (`ONLINE`, `RECOVERY_PENDING`, etc.), modelo de recuperación y fecha de creación |

El tiempo de actividad vuelve a cero cada vez que se reinicia el servicio. Una base en un estado distinto de `ONLINE` requiere revisión.

## 5. Módulo 2 — Rendimiento

| Sección | Cómo usarla |
|---|---|
| Consultas de mayor consumo | Las 10 sentencias con más CPU acumulada desde que inició el servicio. El selector **Ordenar por** cambia la métrica: CPU total o promedio (ms), duración total o promedio (ms), lecturas o veces ejecutada |
| Sesiones activas | Hasta 20 sesiones de usuario: usuario, estado, equipo, aplicación, CPU (ms) y memoria (páginas de 8 KB). El filtro **Filtrar por estado** muestra solo los estados elegidos |
| Sesiones bloqueadas | Sesión bloqueada, sesión bloqueadora, tipo y tiempo de espera |

"No hay bloqueos activos en este momento" (verde) es la condición normal. Si hay bloqueos, aparece una advertencia con la tabla; la columna **Sesión bloqueadora** indica qué sesión retiene el recurso.

## 6. Módulo 3 — Almacenamiento

Trabaja sobre la base configurada (`BD_AdminSGBD`).

- **Asignado:** tamaño que el archivo ocupa en disco.
- **Utilizado:** parte del archivo que tiene datos.
- **Disponible:** asignado − utilizado. Se usa antes de que el archivo tenga que crecer.

| Sección | Cómo interpretarla |
|---|---|
| Indicadores de advertencia | Resumen de riesgos. Verde: sin riesgos. Amarillo o rojo: revisar el motivo indicado. Si no hay conexión, avisa que no se pudo evaluar |
| Tamaño de la base de datos | Total en disco, datos y registro (log) con su porcentaje utilizado; gráfico de utilizado frente a disponible; uso del límite de la edición Express (50 GB por base en SQL Server 2025) |
| Archivos de datos y de registro | Nombre lógico, tipo, filegroup, ubicación, tamaños, crecimiento configurado, tamaño máximo y nivel |
| Filegroups | Grupos de archivos de datos y su espacio; el log no pertenece a ningún filegroup |
| Espacio en el disco | Porcentaje libre de la unidad donde están los archivos |
| Objetos de mayor tamaño | Pestañas **Tablas** e **Índices**, ordenadas de mayor a menor espacio reservado; el control deslizante elige cuántos mostrar (5 a 30) |
| Historial de crecimiento | Gráfico temporal de las mediciones guardadas, cambio entre la primera y la última, y promedio diario cuando el periodo supera un día |

**Umbrales:** un archivo se marca en advertencia al llegar al 80 % de su tamaño **máximo** y en crítico al 90 %. Un archivo casi lleno pero con autocrecimiento ilimitado no es un riesgo, porque SQL Server lo agranda solo. El disco está en advertencia con menos de 20 % libre y en crítico con menos de 10 %.

**Registrar una medición ahora** guarda una medición en el historial. Las mediciones automáticas las hace la tarea programada de Windows. En la tabla de mediciones, la columna **Origen** indica si la medición vino de la aplicación, de la tarea programada o de una ejecución manual.

## 7. Módulo 4 — Respaldos

| Elemento | Cómo interpretarlo |
|---|---|
| Último respaldo | Fecha y hora de finalización, tipo (completo, diferencial o de registro) y tamaño |
| Estado | Verde si SQL Server no marcó el respaldo como dañado; rojo si lo marcó |
| Antigüedad | Advertencia cuando el último respaldo tiene más de 24 horas |
| Historial | Los 20 respaldos más recientes de la base, con el archivo de destino |

"Todavía no hay respaldos registrados" significa que `msdb` no tiene respaldos de esta base en esta instancia. El historial confirma que un respaldo se registró, no que el archivo siga existiendo ni que se pueda restaurar; eso se comprueba con una restauración de prueba.

## 8. Módulo 5 — Auditoría

| Pestaña | Contenido |
|---|---|
| Logins y Usuarios | Logins de la instancia (tipo, deshabilitado, fecha de creación) y usuarios de la base |
| Roles y Miembros | Roles de servidor y de base de datos con sus integrantes |
| Permisos | Permisos de la base: tipo de objeto, objeto, permiso, estado (`GRANT`/`DENY`) y usuario o rol que lo recibe. Filtros por usuario/rol y por permiso |
| Objetos Problemáticos | Vistas, funciones o procedimientos que hacen referencia a objetos que ya no existen |

Para saber qué permisos tiene un usuario a través de un rol: buscar sus roles en **Roles y Miembros** y luego filtrar por ese rol en **Permisos**. Los permisos implícitos de los roles fijos (por ejemplo `db_ddladmin`) no aparecen como filas en la tabla de permisos.

En **Objetos Problemáticos**, verde significa que no hay dependencias rotas; rojo lista cada objeto y la dependencia faltante.

## 9. Módulo 6 — Mantenimiento

Este módulo **modifica la base de datos real**. La detección usa la cuenta consultiva (solo lectura); la ejecución usa la cuenta administrativa.

1. **Actualización de estadísticas:** la tabla muestra cada estadística del esquema `dbo` con su última actualización, filas modificadas y estado (*Nunca actualizada*, *Desactualizada* si cambió 20 % o más, *Al dia*). Elegir la tabla, marcar la casilla de confirmación y presionar **Ejecutar actualización de estadísticas** (`UPDATE STATISTICS ... WITH FULLSCAN`).
2. **Índices fragmentados:** muestra el porcentaje de fragmentación y la acción recomendada, que calcula la aplicación: `REORGANIZE` entre 5 % y 30 %, `REBUILD` desde 30 %. Elegir el índice, confirmar y presionar **Ejecutar mantenimiento de índice**.
3. **Prueba de manejo de errores:** intenta actualizar una tabla inexistente para demostrar que el error se muestra claramente y queda registrado como fallido.
4. **Historial de mantenimiento:** las 50 operaciones más recientes con fecha, operación, objeto, usuario y resultado.

Sin la casilla marcada, el botón no ejecuta nada y muestra un mensaje. Después de cada ejecución, la casilla se desmarca sola. Después de ejecutar, las tablas se recargan: las estadísticas deberían pasar a *Al dia* y el índice reconstruido debería bajar cerca de 0 % de fragmentación.

## 10. Mensajes de error frecuentes

| Mensaje | Qué significa |
|---|---|
| No fue posible conectarse a SQL Server | El servicio está detenido o `config/.env` es incorrecto |
| Error que menciona `permission` o `denied` | A la cuenta consultiva le falta un permiso en esta instancia; ejecutar el script correspondiente del manual de instalación |
| Faltan variables de entorno | `config/.env` incompleto; en el Módulo 6, faltan las variables administrativas |
| La tabla ... no existe en esta base de datos | Error controlado del Módulo 6; queda registrado en el historial |
