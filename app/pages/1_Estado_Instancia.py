from datetime import datetime

import streamlit as st

from database.queries.estado_instancia import (
    obtener_actividad,
    obtener_bases_de_datos,
    obtener_memoria,
    obtener_servidor_instancia,
)


st.title("Módulo 1 — Estado general de la instancia")
st.caption(
    "Información obtenida directamente de la instancia de SQL Server "
    "configurada en config/.env."
)

if st.button("Actualizar información"):
    st.rerun()

st.divider()

# ---------------------------------------------------------------
# Servidor e instancia
# ---------------------------------------------------------------
st.subheader("Servidor e instancia")

try:
    info = obtener_servidor_instancia()

    col1, col2, col3 = st.columns(3)
    col1.metric("Servidor", info["servidor"])
    col2.metric("Instancia", info["instancia"])
    col3.metric("Edición", info["edicion"])

    st.write(f"**Versión del producto:** {info['version_producto']}")
    st.write(f"**Nivel del producto (Service Pack/CU):** {info['nivel_producto']}")
    st.write(f"**Collation del servidor:** {info['collation_servidor']}")

except Exception as error:
    st.error(
        "No fue posible obtener la información del servidor e instancia. "
        "Verifique la conexión configurada en config/.env."
    )
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Estado operativo, inicio y tiempo de actividad
# ---------------------------------------------------------------
st.subheader("Estado operativo")

try:
    actividad = obtener_actividad()

    st.success("La instancia está en línea y respondiendo consultas.")

    col1, col2 = st.columns(2)
    col1.metric("Fecha y hora de inicio", str(actividad["fecha_inicio"]))
    horas = actividad["horas_actividad"]
    dias = horas // 24
    horas_restantes = horas % 24
    col2.metric("Tiempo de actividad", f"{dias} días, {horas_restantes} horas")

except Exception as error:
    st.error(
        "No fue posible determinar el estado operativo de la instancia. "
        "Esto puede indicar que el servidor no responde o que la conexión "
        "configurada no tiene los permisos necesarios."
    )
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Memoria
# ---------------------------------------------------------------
st.subheader("Memoria")

try:
    memoria = obtener_memoria()

    col1, col2, col3 = st.columns(3)
    col1.metric("Memoria física en uso", f"{memoria['memoria_fisica_en_uso_mb']:.1f} MB")
    col2.metric(
        "Memoria virtual comprometida",
        f"{memoria['memoria_virtual_comprometida_mb']:.1f} MB",
    )
    col3.metric(
        "Memoria en páginas grandes",
        f"{memoria['memoria_paginas_grandes_mb']:.1f} MB",
    )

except Exception as error:
    st.error(
        "No fue posible obtener la información de memoria. Esta consulta "
        "requiere el permiso de servidor VIEW SERVER STATE — verifique que "
        "se ejecutó sql/01-estado-instancia/otorgar_permisos_estado_instancia.sql."
    )
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Bases de datos administradas
# ---------------------------------------------------------------
st.subheader("Bases de datos administradas")

try:
    bases = obtener_bases_de_datos()

    if not bases:
        st.info("La instancia no reporta bases de datos visibles para este usuario.")
    else:
        st.dataframe(bases, use_container_width=True)

except Exception as error:
    st.error("No fue posible listar las bases de datos administradas.")
    st.exception(error)

st.divider()
st.caption(f"Última actualización de esta página: {datetime.now():%Y-%m-%d %H:%M:%S}")
