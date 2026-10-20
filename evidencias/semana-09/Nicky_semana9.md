# Semana 09 — Resumen y continuidad

## 1. Información general

- Responsable: Nicky
- Fecha de inicio: 2026-10-20
- Fecha de cierre: 2026-10-20
- Semana del cronograma: 9
- Objetivo de la semana: integración y pruebas de los seis módulos, diseño uniforme, manejo de errores, informe de pruebas y release candidate.

## 2. Estado recibido de la semana anterior

- Módulos 1 a 6 implementados por separado (semanas 3 a 8), cada uno con su página en `app/pages/`.
- Problemas heredados: `app/app.py` era la prueba de conexión de la semana 2 y no había menú; cada módulo tenía encabezados, formatos de fecha y tablas distintos.
- Decisiones que se conservaron: usuario consultivo de solo lectura para detectar, usuario administrativo solo para ejecutar mantenimiento (con confirmación), credenciales fuera del repositorio. No se tocó la lógica de los procedimientos de mantenimiento ni la decisión REBUILD/REORGANIZE (Módulo 6).

## 3. Trabajo realizado

- **Navegación:** `app/app.py` ahora usa `st.navigation` con 7 páginas (Inicio + 6 módulos). Nueva página `app/inicio.py` con prueba de conexión y lista de módulos.
- **Diseño uniforme:** encabezado "Módulo N — Nombre" con descripción, botón "Actualizar información" y hora de actualización; mismo formato de fecha (AAAA-MM-DD); tablas sin columna de índice; encabezados en español; `width="stretch"` en vez de `use_container_width`.
- **Manejo de errores:** Auditoría ya no oculta errores de consulta como listas vacías (D-11).
- **Consultas:** dependencias rotas sin falsos positivos (D-15); historial de mantenimiento limitado a 50 filas.
- **Permisos:** nuevo `sql/05-auditoria/00_otorgar_permisos_auditoria.sql` (VIEW ANY DEFINITION) para ver todos los logins (D-10).
- **Módulo 6:** la casilla de confirmación se desmarca después de ejecutar (D-17).
- **Pruebas:** 9 pruebas formales con 26 evidencias (ver sección 9).

## 4. Decisiones técnicas tomadas

- Se usó `st.navigation` (no `pages/` automático) para controlar nombres y orden del menú.
- Para simular conexión incorrecta se usó una variable de entorno, sin tocar `config/.env` ni probar contraseña errónea (evita bloquear el login).
- Los valores del Módulo 6 como "Sin accion necesaria" no se cambiaron porque la lógica los compara.

## 5. Cambios respecto al plan original

- No hubo cambios al plan. Se agregó la corrección D-17, detectada durante las pruebas.

## 6. Configuración actual

- SGBD: SQL Server 2025 Express, instancia `Nicky\SQLEXPRESS`; base `BD_AdminSGBD`.
- Python 3.11.9, streamlit 1.62.0, pyodbc, pandas; ODBC Driver 18.
- Variables: las de `config/.env.example`, sin variables nuevas.
- Permisos: `VIEW SERVER STATE`, `VIEW ANY DEFINITION` (nuevo), permisos de almacenamiento y de mantenimiento.
- No subir: `config/.env` real.

## 7. Archivos importantes

| Archivo | Propósito | Estado |
|---|---|---|
| `app/app.py`, `app/inicio.py` | Menú y página de inicio | Completo, validado |
| `app/pages/*.py` | Seis módulos con diseño uniforme | Completo, validado |
| `sql/05-auditoria/00_otorgar_permisos_auditoria.sql` | Permiso de metadatos | Completo, validado |
| `sql/05-auditoria/05_*.sql`, `06_*.sql` | Generar y limpiar dependencia rota | Completo, validado |
| `evidencias/semana-09/informe_pruebas.md` | Informe de las 9 pruebas | Completo |
| `evidencias/semana-09/lista_defectos.md` | Defectos corregidos y pendientes | Completo |

## 8. Orden de scripts SQL por máquina

Cada integrante debe correrlos en su propia instancia, en SSMS (orden tomado de la carpeta `sql/`; no se probó desde cero en una máquina limpia):

1. `sql/00-configuracion/` (base y usuario consultivo)
2. `sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql`
3. `sql/03-almacenamiento/01_` y `02_`
4. `sql/05-auditoria/00_otorgar_permisos_auditoria.sql`
5. `sql/06-mantenimiento/01_` a `04_` (en `01_` cambiar la contraseña de ejemplo y no subirla al repositorio)

## 9. Pruebas realizadas

Las 9 pruebas fueron aprobadas; detalle completo en `evidencias/semana-09/informe_pruebas.md`.

## 10. Evidencias

26 capturas en `evidencias/semana-09/` (`semana_09_01_...` a `semana_09_26_...`).

## 11. Problemas encontrados

- Auditoría mostraba listas vacías cuando faltaban permisos (D-11) y no veía todos los logins (D-10).
- Dependencias rotas con falsos positivos (D-15).
- Casilla de confirmación del Módulo 6 quedaba marcada (D-17).
- Streamlit no recarga los módulos de consultas importados: hay que reiniciarlo después de editarlos.

## 12. Tareas no completadas

Ninguna bloqueante: la semana se cumple completamente.

| Tarea | Motivo | Qué falta | Prioridad |
|---|---|---|---|
| Valores sin tildes en el Módulo 6 ("Sin accion necesaria", "Al dia", "maxima") y `None` en fechas de estadísticas nunca actualizadas | No se cambiaron porque la lógica del módulo compara esos textos exactos. Andrey indicó no modificar los procedimientos ni la decisión REORGANIZE/REBUILD (`Andrey_semana8.md`, sección 13: "no simplificar"). Cambiar los textos exige tocar consulta y lógica a la vez. | Si se quiere, cambiarlos consultando antes a Andrey | Baja |
| Cierre explícito de conexiones | Se revisó: no hay fugas ni sesiones acumuladas. `with conn` hace commit pero no cierra; hoy no causa problemas | Recomendación a futuro: cerrar la conexión explícitamente | Baja |

## 13. Instrucciones para la siguiente persona y su IA

- Revisar primero este archivo, `informe_pruebas.md` y `lista_defectos.md`.
- Qué no debe modificar sin consultar (heredado de Andrey, `Andrey_semana8.md` sección 13): los procedimientos de mantenimiento ("no simplificar") y la confirmación explícita antes de ejecutar. En la Semana 9 solo se hizo que la casilla se desmarque tras ejecutar (D-17), lo que refuerza la confirmación; no se tocó el resto.
- Repetir: `streamlit run app/app.py` y recorrer las 7 páginas del menú.
- Respetar: usuario consultivo para leer, administrativo solo para ejecutar.

## 14. Estado del criterio de cierre

- Criterio de cierre de la semana: solución integrada con diseño uniforme, manejo de errores, 9 pruebas con evidencia, lista de defectos y release candidate.
- ¿Se cumplió completamente?: Sí, pendiente de PR y revisión del equipo.
- Evidencia: secciones 9 y 10.

## 15. Resumen breve para el equipo

Se integraron los seis módulos en una sola aplicación con menú, página de inicio y diseño uniforme. Se corrigieron los defectos encontrados (los más graves: errores ocultos en Auditoría y logins incompletos) y se ejecutaron las 9 pruebas planificadas con evidencia. El release candidate es la rama `semana9/integracion`.
