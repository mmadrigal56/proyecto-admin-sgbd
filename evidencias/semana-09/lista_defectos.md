# Lista de defectos — Semana 9

**Responsable:** Nicky · **Fecha:** 2026-10-20 · **Rama:** `semana9/integracion`

## Corregidos (cada uno con su commit)

| ID | Defecto | Módulo | Gravedad | Commit |
|----|---------|--------|----------|--------|
| D-11 | Un error de consulta se mostraba como "todo bien" (lista vacía en verde) | 5 | Alta | da79cca |
| D-10 | Logins y roles incompletos por falta de permiso de metadatos | 5 | Alta | f98f3a7 |
| D-15 | Falsos positivos en dependencias rotas | 5 | Alta | d7470d8 |
| D-01 | Menú con "app" y página de inicio que era la prueba de conexión de la semana 2 | General | Media | ab82f40 |
| D-05 | Título con emoji y dos puntos, distinto a "Módulo N — Nombre" | 5 | Media | ab2200c |
| D-04 | Faltaban descripción, botón de actualizar y hora de actualización | 4, 5 | Media | d15d3c8, ab2200c |
| D-07 | `layout="wide"` solo en esa página | 5 | Baja | ab2200c |
| D-06 | Columnas en inglés (LoginName) y sin tildes | 5, 6 | Baja | 94f9c9d, 9b13df6 |
| D-02 | Valores grandes cortados con "…" | 1 | Baja | c47aed8 |
| D-03 | Columna de índice 0, 1, 2… innecesaria | 2, 5 | Baja | f0a5573 |
| D-09 | `use_container_width` obsoleto | 1, 2, 5 | Baja | 65a1fa8 |
| D-13 | Fechas en dos formatos | 4, 6 | Baja | 5a9a9aa |
| D-17 | Casilla de confirmación quedaba marcada tras ejecutar mantenimiento | 6 | Media | 74032ce |

## Otros cambios con commit

- `836491f`: el historial de mantenimiento se limita a las 50 operaciones más recientes.
- `d3593c9`: scripts para generar y limpiar una dependencia rota (apoyo a la prueba 7).

## Pendientes

- D-06 (parcial): valores sin tildes ("Sin accion necesaria", "Al dia", "maxima") y `None` en fechas de estadísticas nunca actualizadas. Se dejaron porque la lógica del Módulo 6 compara esos textos.
- Aviso "File change. Rerun" de Streamlit: cosmético.
- Cierre explícito de conexiones: se revisó y no hay fugas; queda como recomendación.

## Numeración sin commit asociado

D-08, D-12, D-14 y D-16 no tienen commit en la rama, así que no se cuentan como corregidos.
