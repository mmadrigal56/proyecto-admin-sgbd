# Semana 10 — Resumen y continuidad

## 1. Información general

- Responsable: Juan Artavia
- Fecha de inicio: 2026-10-28
- Fecha de cierre: [COMPLETAR al publicar el enlace en el aula virtual]
- Semana del cronograma: 10
- Objetivo de la semana: preparar la versión definitiva del repositorio y una demostración funcional de aproximadamente 15 minutos.

## 2. Estado recibido de la semana anterior

- Funcionalidades disponibles: aplicación integrada con menú de siete páginas (Inicio y módulos 1 a 6), diseño uniforme y nueve pruebas aprobadas (PR #13 de la semana 9, integrado en `main`).
- Pendientes heredados:
  - Bitácora sin entradas de las semanas 2, 4, 6 y 7.
  - Matriz de requerimientos con casi todos los requisitos en "Pendiente" aunque estaban implementados.
  - README, arquitectura y manual de instalación con la información de las primeras semanas.
  - `config/.env.example` sin las variables administrativas que necesita el Módulo 6.
  - Faltaban el manual de usuario y el manual técnico.
- Decisiones que se conservaron: todas las de la arquitectura base; no se modificó código.

## 3. Trabajo realizado

| Archivo | Cambio |
|---|---|
| `README.md` | Reescrito: módulos, tecnologías, inicio rápido, seguridad, enlaces a la documentación, estructura real, organización por semanas y limitaciones |
| `docs/manuales/instalacion.md` | Reescrito: requisitos con versiones probadas, autenticación mixta, `.env` con variables administrativas, los nueve scripts obligatorios en orden, datos de demostración, captura periódica y tabla de solución de problemas |
| `docs/manuales/usuario.md` | Nuevo: uso e interpretación de cada página |
| `docs/tecnica/manual-tecnico.md` | Nuevo: arquitectura, estructura del código, consultas por módulo, objetos creados, modelo de permisos, transacciones, decisiones y limitaciones |
| `docs/arquitectura/arquitectura.md` | Actualizado al estado final (tiempos verbales, comando de ejecución, conexiones reales) |
| `config/.env.example` | Agregadas `DB_ADMIN_USER` y `DB_ADMIN_PASSWORD` con valores de ejemplo |
| `docs/matriz-requerimientos.md` | Estado y columna de evidencia en cada requisito; DOC-04 ya no menciona Power BI |
| `docs/bitacora/bitacora.md` | Entradas de las semanas 2, 4, 6 y 7 (indicadas como redactadas en la semana 10) y entrada de la semana 10 |

## 4. Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Credenciales en el historial completo de Git (todas las ramas) | Sin contraseñas reales; solo `CAMBIAR_ESTA_CONTRASEÑA` y `CAMBIAR_POR_LA_CONTRASENA_LOCAL` |
| `config/.env` o `.bak` en el historial | Nunca se versionaron |
| Aportes por integrante (`git shortlog`) | Los cinco integrantes tienen commits desde sus cuentas |
| Distribución del historial | Commits del 29 de agosto al 20 de octubre en 10 fechas distintas |
| Requisitos de la matriz | 76 completados, 1 en proceso (REP-01, falta la presentación), 1 parcial (M5-06) y 1 pendiente (M6-04) |
| Aplicación completa en la máquina de Juan | Las siete páginas cargan sin errores con datos reales (`semana_10_05` a `semana_10_20`) |

## 5. Decisiones técnicas tomadas

| Decisión | Motivo |
|---|---|
| Marcar M6-04 como pendiente y M5-06 como parcial | La regla de veracidad del cronograma: no se marca como completado lo que no tiene evidencia |
| Redactar las entradas faltantes de la bitácora indicando que se hicieron en la semana 10 | Completar el registro sin presentar como contemporáneo algo escrito después |
| No modificar código en la semana 10 | El cronograma pide corregir solo problemas importantes; ningún defecto bloqueante quedó abierto |
| Presentar desde la computadora de Juan | Tiene el historial de almacenamiento acumulado desde el 24 de septiembre |

## 6. Configuración de la demostración

- SGBD: SQL Server 2025 Express 17.0.1000.7, instancia `Juan\SQLEXPRESS`, base `BD_AdminSGBD`.
- Python 3.12.7, entorno `.venv`, ODBC Driver 18.
- Scripts que deben estar ejecutados: los nueve obligatorios del manual de instalación (paso 7) y los de datos de demostración que se vayan a usar.
- `config/.env` con las variables consultivas y administrativas (no se sube).

### Estado de la máquina de Juan

La instancia de Juan solo tenía configurados los módulos 1 a 3 (semana 5). El 28 y 29 de octubre se ejecutaron:

| Script | Resultado | Evidencia |
|---|---|---|
| `sql/05-auditoria/00_otorgar_permisos_auditoria.sql` | `VIEW ANY DEFINITION` y lectura de dependencias otorgados | `semana_10_01` |
| `sql/06-mantenimiento/01_crear_usuario_administrativo.sql` | `adminsgbd_mantenimiento` creado con `db_ddladmin` | `semana_10_02` |
| `sql/06-mantenimiento/02_otorgar_permisos_mantenimiento.sql` | Permisos de detección; `VIEW DEFINITION` y el esquema `monitoreo` ya existían desde la semana 5 | `semana_10_03` |
| `sql/06-mantenimiento/03_crear_procedimientos_mantenimiento.sql` | Esquema `mantenimiento` y procedimientos creados | `semana_10_04` |
| `sql/04-respaldos/crear_respaldo.sql` | Respaldo completo de 33.33 MB, sin daños | `semana_10_15`, `semana_10_16` |
| `sql/06-mantenimiento/04_generar_escenario_prueba.sql` | 2 estadísticas sin actualizar e índices de `dbo.PruebaMantenimiento` al 95.9 % y 54.5 % | `semana_10_17` a `semana_10_19` |

`config/.env` tiene las variables consultivas y administrativas (no se versiona).

Observaciones:

- El Módulo 6 solo revisa el esquema `dbo`; antes del escenario de prueba mostraba "No se encontraron estadísticas" porque las tablas de Juan están en `prueba` y `monitoreo`.
- `IX_Carga_codigo` (tabla de prueba de la semana 5) tiene 99.1 % de fragmentación real.
- El Módulo 3 muestra 53 mediciones en 33.8 días, con un crecimiento promedio de 0.84 MB por día.
- El Módulo 2 mostró el caché de planes vacío hasta que hubo actividad en la instancia; después mostró las 10 consultas (`semana_10_20`).
- El script `04_generar_escenario_prueba.sql` muestra una advertencia de SQL Server sobre la longitud máxima de la clave del índice (`NVARCHAR(1000)`); es esperada y no impide crear el escenario.

## 7. Pendientes para cerrar la entrega

| Tarea | Responsable | Estado |
|---|---|---|
| Revisar la documentación en el PR de la semana 10 | Equipo | Pendiente |
| Confirmar en persona la distribución de la exposición | Equipo | Pendiente |
| Ensayo cronometrado completo | Equipo | Pendiente |
| Agregar la presentación final al repositorio | Equipo | Pendiente |
| Verificación final un día antes | Juan | Pendiente |
| Confirmar que el profesor tiene acceso al repositorio | Mariana (dueña del repositorio) | Pendiente |
| Etiqueta `v1.0` sobre `main` después del merge | Juan | Pendiente |
| Publicar el enlace del repositorio en el aula virtual | Juan | Pendiente |

## 8. Pendientes funcionales conocidos

| Requisito | Situación | Qué haría falta |
|---|---|---|
| M6-04 | El Módulo 6 no actualiza ni valida la definición de módulos SQL | Un procedimiento que ejecute `sp_refreshsqlmodule` sobre la vista o procedimiento elegido, con el mismo registro y confirmación que los demás |
| M5-06 | Permisos por rol e integrantes del rol en pestañas separadas | Una consulta que una `sys.database_role_members` con `sys.database_permissions` para mostrar usuario → rol → permiso |
| Textos sin tildes en el Módulo 6 | La lógica compara esos textos | Cambiar consulta y lógica a la vez, consultando a Andrey |

## 9. Problemas encontrados

- `config/.env.example` no tenía las variables administrativas: una instalación nueva siguiendo el manual habría fallado en el Módulo 6. Se agregaron con valores de ejemplo.
- El README y la arquitectura describían el proyecto en futuro y con una estructura que no coincidía con la real. Se actualizaron.

## 10. Estado del criterio de cierre

- Criterio: el repositorio debe contener todo lo solicitado y la demostración debe funcionar con información real en menos de 15 minutos.
- ¿Se cumplió completamente?: [COMPLETAR después del ensayo y de la verificación del día anterior]

## 11. Resumen para el equipo

La documentación quedó completa y alineada con lo que realmente hace la aplicación: README, manuales de instalación, usuario y técnico, arquitectura, matriz con evidencia por requisito y bitácora de las diez semanas. Quedan pendientes la presentación, el ensayo, la etiqueta `v1.0` y la publicación del enlace; en lo funcional, M6-04 no está implementado y M5-06 es parcial, ambos documentados.
