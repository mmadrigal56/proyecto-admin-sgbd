# Traspaso de la semana 7 a Andrey – Semana 8, módulo 6: mantenimiento preventivo

**Proyecto:** [proyecto-admin-sgbd](https://github.com/mmadrigal56/proyecto-admin-sgbd)  
**Entrega anterior:** [Módulo 5 de auditoría]  
**Responsable siguiente:** Andrey.  
**Fecha del traspaso:** 6 de octubre de 2026.

## 1. Qué recibís

- Una aplicación web local en Streamlit con los módulos 1 a 5 ya funcionales: estado de instancia, rendimiento, almacenamiento, respaldos y ahora **auditoría** (página `5_Auditoria.py`).
- El módulo 5 (Auditoría) implementado con las consultas en `app/database/queries/auditoria.py` y los scripts SQL originales en la carpeta `sql/05-auditoria/`.
- La página de auditoría consulta `sys.server_principals`, `sys.database_principals`, roles de servidor y base de datos, así como el mapeo de `sys.database_permissions`. Además, incorpora un filtro interactivo en Streamlit y revisa dependencias rotas de código (objetos problemáticos) a través de `sys.sql_expression_dependencies`.

## 2. Resultados reales de la semana 7

| Verificación | Resultado |
|---|---|
| Logins de servidor y usuarios | Se enlistan exitosamente los existentes; a considerar que con la cuenta `adminsgbd_consulta` puede que algunos logins a nivel servidor estén ocultos. |
| Roles y Miembros | Funcionando. Identifica los integrantes de cada rol. |
| Permisos Directos y Heredados | La vista de `sys.database_permissions` refleja los permisos otorgados a los usuarios y los permisos a nivel de rol, permitiendo el rastreo. |
| Objetos Problemáticos (Dependencias Rotas) | Verificado. Muestra alertas de aquellos procedimientos y vistas que apuntan a entidades eliminadas. |

## 3. Decisiones y precauciones para tu módulo

1. **Tu alcance: Mantenimiento Preventivo (Módulo 6)**: El objetivo de la **semana 8** es proveer la capacidad de realizar operaciones de mantenimiento en base de datos.
2. **Cuenta administrativa requerida**: Las operaciones destructivas o de mantenimiento (ej: matar sesiones bloqueadas, limpiar caché, recompilar o defragmentar índices) requerirán **credenciales administrativas**, no utilices la cuenta consultiva que hemos usado para los reportes o no funcionará.
3. **Mecanismo de control**: Toda acción de mantenimiento debe tener un control previo. Muestra confirmaciones en la interfaz de Streamlit (`st.warning` o modales, botones de confirmación, etc.) antes de ejecutar cualquier script destructivo sobre el SGBD real.

## 4. Cómo levantar el proyecto

1. Actualizá tu copia local de la rama principal luego del Pull Request del módulo 5.
2. Activá tu entorno y asegurate de tener el archivo `.env` configurado.
3. Levantá la app con `python -m streamlit run app/app.py`.
4. El desarrollo de tu semana debe centrarse en la carpeta `sql/06-mantenimiento/`, agregando la lógica en un nuevo archivo `app/database/queries/mantenimiento.py` y la interfaz en `app/pages/6_Mantenimiento.py`.

Cualquier duda, no dudes en escribirme para ver las funcionalidades de esta semana. ¡Éxitos con tu módulo!
