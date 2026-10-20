import streamlit as st
from datetime import datetime

from database.queries.mantenimiento import (
    obtener_estadisticas_desactualizadas,
    obtener_indices_fragmentados,
    obtener_historial_mantenimiento,
    ejecutar_actualizacion_estadisticas,
    ejecutar_mantenimiento_indice,
)


def _mostrar_mensaje_pendiente(clave):
    """
    Muestra (y luego borra) un mensaje guardado en session_state.

    Streamlit dibuja toda la página de arriba hacia abajo en cada
    interacción. Si una acción se ejecuta en un botón que está más
    abajo que las tablas que muestran el resultado, esas tablas ya se
    dibujaron con datos viejos en esa misma pasada. Por eso, en vez de
    mostrar el mensaje inmediatamente, lo guardamos y forzamos una
    recarga (st.rerun()): en la recarga siguiente, las tablas de arriba
    ya consultan la base de datos con el resultado real, y aquí se
    muestra el mensaje de la acción que se acaba de ejecutar.
    """
    mensaje = st.session_state.pop(clave, None)
    if mensaje:
        tipo, texto = mensaje
        getattr(st, tipo)(texto)


st.title("Módulo 6 — Mantenimiento preventivo")

st.caption(
    "Este módulo ejecuta operaciones administrativas REALES sobre la base de "
    "datos. Las operaciones de detección son de solo lectura (usuario "
    "consultivo); las operaciones de ejecución usan un usuario administrativo "
    "separado y requieren confirmación explícita."
)

# =============================================================
# Sección 1 — Actualización de estadísticas
# =============================================================
st.header("1. Actualización de estadísticas")

_mostrar_mensaje_pendiente("flash_estadisticas")

try:
    estadisticas = obtener_estadisticas_desactualizadas()

    if not estadisticas:
        st.info("No se encontraron estadísticas en el esquema dbo.")
    else:
        st.dataframe(estadisticas, hide_index=True)

        opciones = [f"{e['esquema']}.{e['tabla']}" for e in estadisticas]
        seleccion = st.selectbox(
            "Tabla a la que se le actualizarán las estadísticas",
            options=sorted(set(opciones)),
            key="select_tabla_estadisticas",
        )

        st.warning(
            f"Esto ejecutará UPDATE STATISTICS WITH FULLSCAN sobre **{seleccion}** "
            "en la base de datos real. No se puede deshacer, aunque no borra datos."
        )
        confirmar = st.checkbox(
            "Confirmo que deseo actualizar las estadísticas de esta tabla.",
            key="confirmar_estadisticas",
        )

        if st.button("Ejecutar actualización de estadísticas", key="btn_estadisticas"):
            if not confirmar:
                st.session_state["flash_estadisticas"] = (
                    "error",
                    "Debes marcar la casilla de confirmación antes de ejecutar.",
                )
            else:
                esquema, tabla = seleccion.split(".", 1)
                try:
                    ejecutar_actualizacion_estadisticas(esquema, tabla)
                    st.session_state["flash_estadisticas"] = (
                        "success",
                        f"Estadísticas de {seleccion} actualizadas correctamente.",
                    )
                except Exception as error:
                    st.session_state["flash_estadisticas"] = (
                        "error",
                        f"No fue posible actualizar las estadísticas de {seleccion}: {error}",
                    )
            st.rerun()

except Exception as error:
    st.error("No fue posible consultar las estadísticas desactualizadas.")
    st.exception(error)

st.divider()

# =============================================================
# Sección 2 — Objetos problemáticos: índices fragmentados
# =============================================================
st.header("2. Índices fragmentados")

_mostrar_mensaje_pendiente("flash_indice")

try:
    indices = obtener_indices_fragmentados()
    indices_con_accion = [i for i in indices if i["accion_recomendada"] != "Sin accion necesaria"]

    if not indices:
        st.info("No se encontraron índices con datos para evaluar.")
    elif not indices_con_accion:
        st.success("Ningún índice necesita mantenimiento en este momento (todos por debajo de 5% de fragmentación).")
        st.dataframe(indices, hide_index=True)
    else:
        st.dataframe(indices, hide_index=True)

        etiquetas = [
            f"{i['esquema']}.{i['tabla']} / {i['indice']} "
            f"({i['porcentaje_fragmentacion']:.1f}% — {i['accion_recomendada']})"
            for i in indices_con_accion
        ]
        indice_elegido = st.selectbox(
            "Índice a reorganizar o reconstruir",
            options=range(len(indices_con_accion)),
            format_func=lambda idx: etiquetas[idx],
            key="select_indice",
        )
        objetivo = indices_con_accion[indice_elegido]

        st.warning(
            f"Esto ejecutará ALTER INDEX {objetivo['accion_recomendada']} sobre "
            f"**{objetivo['esquema']}.{objetivo['tabla']} / {objetivo['indice']}** "
            "en la base de datos real."
        )
        confirmar_indice = st.checkbox(
            "Confirmo que deseo ejecutar este mantenimiento de índice.",
            key="confirmar_indice",
        )

        if st.button("Ejecutar mantenimiento de índice", key="btn_indice"):
            if not confirmar_indice:
                st.session_state["flash_indice"] = (
                    "error",
                    "Debes marcar la casilla de confirmación antes de ejecutar.",
                )
            else:
                try:
                    ejecutar_mantenimiento_indice(
                        objetivo["esquema"],
                        objetivo["tabla"],
                        objetivo["indice"],
                        objetivo["accion_recomendada"],
                    )
                    st.session_state["flash_indice"] = (
                        "success",
                        f"{objetivo['accion_recomendada']} ejecutado correctamente sobre "
                        f"{objetivo['esquema']}.{objetivo['tabla']} / {objetivo['indice']}.",
                    )
                except Exception as error:
                    st.session_state["flash_indice"] = (
                        "error",
                        f"No fue posible ejecutar el mantenimiento de índice: {error}",
                    )
            st.rerun()

except Exception as error:
    st.error("No fue posible consultar los índices fragmentados.")
    st.exception(error)

st.divider()

# =============================================================
# Sección 3 — Prueba de manejo de errores (caso controlado)
# =============================================================
st.header("3. Prueba de manejo de errores")

st.caption(
    "Intenta ejecutar una actualización de estadísticas sobre una tabla que "
    "NO existe, para comprobar que el error se muestra de forma clara y queda "
    "registrado como 'Fallido', en vez de romper la aplicación."
)

mensaje_prueba_error = st.session_state.pop("flash_prueba_error", None)
if mensaje_prueba_error:
    tipo, texto = mensaje_prueba_error
    getattr(st, tipo)(texto)

if st.button("Probar caso fallido controlado", key="btn_prueba_error"):
    try:
        ejecutar_actualizacion_estadisticas("dbo", "TablaQueNoExiste")
        st.session_state["flash_prueba_error"] = (
            "warning", "No se esperaba que esto tuviera éxito.",
        )
    except Exception as error:
        st.session_state["flash_prueba_error"] = (
            "error",
            f"Error controlado recibido correctamente (esto es el resultado esperado): {error}",
        )
    st.rerun()

st.divider()

# =============================================================
# Sección 4 — Historial de mantenimiento
# =============================================================
st.header("4. Historial de mantenimiento")

try:
    historial = obtener_historial_mantenimiento()
    if not historial:
        st.info("Todavía no se ha registrado ninguna operación de mantenimiento.")
    else:
        st.dataframe(historial, hide_index=True)
except Exception as error:
    st.error("No fue posible consultar el historial de mantenimiento.")
    st.exception(error)

st.caption(f"Última actualización de esta página: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
