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