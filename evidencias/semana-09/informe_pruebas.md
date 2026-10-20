# Informe de pruebas — Semana 9

**Responsable:** Nicky · **Fecha:** 2026-10-20
**Entorno:** SQL Server 2025 Express (`localhost\SQLEXPRESS`), base `BD_AdminSGBD`, Streamlit + pyodbc.
**Rama:** `semana9/integracion`
**Evidencias:** carpeta `evidencias/semana-09/` (archivos `semana_09_NN_...png`; abajo se cita solo el número NN).

## Resumen

| # | Prueba | Resultado | Evidencias |
|---|--------|-----------|------------|
| 1 | Conexión correcta | Aprobada | 05 |
| 2 | Conexión incorrecta | Aprobada | 22, 23 |
| 3 | Consultas sin resultados | Aprobada | 06, 07, 08 |
| 4 | Permisos insuficientes | Aprobada (tras corregir D-11) | 01, 19, 20, 21 |
| 5 | Servidor detenido | Aprobada | 24, 25 |
| 6 | Bloqueo real | Aprobada | 17, 18 |
| 7 | Objeto problemático (dependencia rota) | Aprobada (tras corregir D-15) | 03, 16 |
| 8 | Mantenimiento exitoso | Aprobada | 11, 12, 13, 14, 15 |
| 9 | Mantenimiento fallido | Aprobada | 09, 10 |

## Detalle por prueba

### Prueba 1 — Conexión correcta
- **Procedimiento:** abrir la página Inicio con la configuración normal.
- **Esperado:** mensaje de conexión exitosa con servidor, base y usuario.
- **Obtenido:** "Conexión exitosa con SQL Server". Evidencia 05.

### Prueba 2 — Conexión incorrecta
- **Procedimiento:** se simuló con una variable de entorno de servidor inválido, sin tocar `config/.env`. No se probó contraseña errónea para no bloquear el login.
- **Esperado:** mensaje de error claro, sin que la aplicación se caiga.
- **Obtenido:** Inicio y Auditoría muestran el error de conexión de forma controlada. Evidencias 22 y 23.

### Prueba 3 — Consultas sin resultados
- **Procedimiento:** abrir los módulos que no tenían datos (Respaldos, Mantenimiento, Almacenamiento).
- **Esperado:** mensaje informativo en lugar de tablas vacías o errores.
- **Obtenido:** cada módulo muestra su aviso de que no hay resultados. Evidencias 06, 07 y 08.

### Prueba 4 — Permisos insuficientes
- **Procedimiento:** retirar temporalmente el permiso VIEW SERVER STATE al usuario consultivo y abrir los módulos afectados.
- **Esperado:** error visible y claro; el resto de la aplicación sigue funcionando.
- **Obtenido:** los módulos afectados muestran el error de permiso y el servidor sigue funcionando. Evidencias 19, 20 y 21. Antes de corregir D-11, Auditoría ocultaba este tipo de error; ahora se muestra (evidencia 01). El permiso se volvió a otorgar al terminar.

### Prueba 5 — Servidor detenido
- **Procedimiento:** detener el servicio con `Stop-Service` y abrir Inicio y Almacenamiento; luego reiniciarlo con `Start-Service`.
- **Esperado:** errores controlados mientras está detenido; recuperación sin reiniciar Streamlit.
- **Obtenido:** Inicio muestra "No fue posible conectarse..." y Almacenamiento avisa que no hay conexión con SQL Server (evidencias 24 y 25). Al volver el servicio, Inicio mostró de nuevo "Conexión exitosa con SQL Server" sin reiniciar la aplicación.

### Prueba 6 — Bloqueo real
- **Procedimiento:** provocar un bloqueo entre sesiones sobre `dbo.PruebaBloqueo` y consultar el módulo de Rendimiento.
- **Esperado:** el bloqueo aparece mientras existe y desaparece al liberarse.
- **Obtenido:** bloqueo detectado (evidencia 17) y liberado tras revertir la transacción (evidencia 18).

### Prueba 7 — Objeto problemático
- **Procedimiento:** ejecutar `sql/05-auditoria/05_generar_dependencia_rota.sql` (vista que depende de una tabla eliminada) y abrir Auditoría.
- **Esperado:** la dependencia rota aparece en la lista de dependencias.
- **Obtenido:** detectada (evidencia 16). La vista se eliminó con `06_limpiar_dependencia_rota.sql`. Antes de corregir D-15 la consulta mostraba falsos positivos; ahora no (evidencia 03).

### Prueba 8 — Mantenimiento exitoso
- **Procedimiento:** ejecutar la actualización de estadísticas y el mantenimiento de un índice desde Módulo 6, con casilla de confirmación.
- **Esperado:** operación correcta, cambio visible en las tablas y registro en el historial.
- **Obtenido:** estadísticas antes/después (11, 12), índice antes/después (13, 14) e historial con resultado exitoso (15).

### Prueba 9 — Mantenimiento fallido
- **Procedimiento:** usar el botón "Probar caso fallido controlado" de Módulo 6.
- **Esperado:** mensaje de error claro, sin romper la aplicación, y registro del fallo.
- **Obtenido:** mensaje de error mostrado (evidencia 09) y operación registrada como fallida en el historial (evidencia 10).

## Corrección posterior: D-17
- **Defecto:** en Módulo 6, la casilla de confirmación quedaba marcada después de ejecutar un mantenimiento, y el selector pasaba al siguiente elemento. Un segundo clic en "Ejecutar" habría corrido el mantenimiento sobre otro objeto sin nueva confirmación.
- **Corrección (commit `74032ce`):** la casilla se desmarca sola después de cada ejecución (6 líneas en `6_Mantenimiento.py`). No se tocó la lógica de los procedimientos ni de REBUILD/REORGANIZE.
- **Verificación:** después de ejecutar la actualización de estadísticas de `dbo.PruebaBloqueo`, la casilla quedó desmarcada. Evidencia 26.
- **No verificado con captura esta semana:** el intento de ejecutar sin confirmar. Ese comportamiento ya existía y lo probó Andrey en la Semana 8 (`Andrey_semana8.md`, sección 9: "Ejecución sin confirmar la casilla — Aprobada").

## Notas generales
- Entorno restaurado al terminar: permiso VIEW SERVER STATE otorgado, variable de entorno eliminada, servicio en ejecución, vista de prueba eliminada, bloqueo revertido.
- Observaciones reales de la instancia (no son defectos de la aplicación): la base `MiBaseDeDatos` está en RECOVERY_PENDING y el disco C: tiene 11.9 % libre.
