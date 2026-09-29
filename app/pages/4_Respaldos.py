import streamlit as st
from datetime import datetime

from database.queries.respaldos import obtener_historial_respaldos


st.title("Módulo 4 — Respaldos y recuperación")

try:
    respaldos = obtener_historial_respaldos()

    if not respaldos:
        st.warning("Todavía no hay respaldos registrados para esta base de datos.")
    else:
        ultimo = respaldos[0]

        st.metric(
            "Último respaldo",
            ultimo["fecha_finalizacion"].strftime("%d/%m/%Y %H:%M"),
        )
        st.write(f"**Tipo:** {ultimo['tipo']}")
        st.write(f"**Tamaño:** {float(ultimo['tamano_mb']):.2f} MB")

        if ultimo["marcado_como_danado"]:
            st.error("SQL Server marcó este respaldo como dañado.")
        else:
            st.success("Respaldo registrado sin daños detectados.")

        horas_desde_respaldo = (
            datetime.now() - ultimo["fecha_finalizacion"]
        ).total_seconds() / 3600

        if horas_desde_respaldo > 24:
            st.warning(
                f"El último respaldo tiene {horas_desde_respaldo:.1f} horas. "
                "Conviene generar uno nuevo."
            )
        else:
            st.info("El último respaldo tiene menos de 24 horas.")

        st.subheader("Historial de respaldos")
        st.dataframe(respaldos, hide_index=True)

        st.caption(
            "El historial proviene de SQL Server. Para comprobar que una copia "
            "se puede recuperar, hay que probar su restauración."
        )

except Exception as error:
    st.error("No fue posible consultar los respaldos.")
    st.exception(error)