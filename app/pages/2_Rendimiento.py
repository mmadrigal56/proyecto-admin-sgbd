from datetime import datetime

import pandas as pd
import streamlit as st

from database.queries.rendimiento import (
    obtener_consultas_costosas,
    obtener_sesiones_activas,
    obtener_sesiones_bloqueadas,
)


st.title("Módulo 2 — Monitoreo de rendimiento")
st.caption(
    "Información obtenida directamente de la instancia de SQL Server "
    "configurada en config/.env."
)

if st.button("Actualizar información"):
    st.rerun()

st.divider()

# ---------------------------------------------------------------
# Consultas de mayor consumo
# ---------------------------------------------------------------
st.subheader("Consultas de mayor consumo")
st.caption(
    "Top 10 sentencias SQL cacheadas por la instancia, con mayor consumo "
    "acumulado de CPU desde que arrancó el servicio."
)

try:
    consultas = obtener_consultas_costosas()

    if not consultas:
        st.info(
            "La instancia todavía no tiene consultas registradas en el "
            "caché de planes de ejecución."
        )
    else:
        df_consultas = pd.DataFrame(consultas)

        metrica = st.selectbox(
            "Ordenar por:",
            options=[
                "cpu_total_ms",
                "cpu_promedio_ms",
                "duracion_total_ms",
                "duracion_promedio_ms",
                "lecturas_totales",
                "veces_ejecutada",
            ],
            format_func=lambda columna: {
                "cpu_total_ms": "CPU total (ms)",
                "cpu_promedio_ms": "CPU promedio (ms)",
                "duracion_total_ms": "Duración total (ms)",
                "duracion_promedio_ms": "Duración promedio (ms)",
                "lecturas_totales": "Lecturas totales",
                "veces_ejecutada": "Veces ejecutada",
            }[columna],
        )

        df_consultas = df_consultas.sort_values(by=metrica, ascending=False)

        st.dataframe(
            df_consultas,
            use_container_width=True,
            column_config={
                "veces_ejecutada": "Veces ejecutada",
                "cpu_total_ms": st.column_config.NumberColumn("CPU total (ms)", format="%.2f"),
                "cpu_promedio_ms": st.column_config.NumberColumn("CPU promedio (ms)", format="%.2f"),
                "duracion_total_ms": st.column_config.NumberColumn("Duración total (ms)", format="%.2f"),
                "duracion_promedio_ms": st.column_config.NumberColumn("Duración promedio (ms)", format="%.2f"),
                "lecturas_totales": "Lecturas totales",
                "lecturas_promedio": "Lecturas promedio",
                "texto_consulta": "Texto de la consulta",
            },
        )

except Exception as error:
    st.error(
        "No fue posible obtener las consultas de mayor consumo. "
        "Verifique la conexión configurada en config/.env."
    )
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Sesiones activas
# ---------------------------------------------------------------
st.subheader("Sesiones activas")
st.caption("Sesiones de usuario conectadas actualmente a la instancia.")

try:
    sesiones = obtener_sesiones_activas()

    if not sesiones:
        st.info("No hay sesiones de usuario activas en este momento.")
    else:
        df_sesiones = pd.DataFrame(sesiones)

        estados_disponibles = sorted(df_sesiones["estado"].dropna().unique().tolist())
        estados_seleccionados = st.multiselect(
            "Filtrar por estado:",
            options=estados_disponibles,
            default=estados_disponibles,
        )

        df_sesiones = df_sesiones[df_sesiones["estado"].isin(estados_seleccionados)]

        st.dataframe(
            df_sesiones,
            use_container_width=True,
            column_config={
                "id_sesion": "ID sesión",
                "usuario": "Usuario",
                "estado": "Estado",
                "equipo": "Equipo",
                "aplicacion": "Aplicación",
                "hora_inicio_sesion": "Hora de inicio",
                "tiempo_cpu_ms": st.column_config.NumberColumn("Tiempo CPU (ms)"),
                "memoria_paginas_de_8kb": st.column_config.NumberColumn("Memoria (páginas de 8 KB)"),
            },
        )

except Exception as error:
    st.error("No fue posible obtener las sesiones activas.")
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Sesiones bloqueadas y bloqueadoras
# ---------------------------------------------------------------
st.subheader("Sesiones bloqueadas")
st.caption(
    "Sesiones que están esperando a que otra sesión libere un recurso "
    "(bloqueo). La ausencia de bloqueos es una condición normal, no un error."
)

try:
    bloqueos = obtener_sesiones_bloqueadas()

    if not bloqueos:
        st.success("No hay bloqueos activos en este momento.")
    else:
        st.warning(f"Se detectaron {len(bloqueos)} sesión(es) bloqueada(s).")

        df_bloqueos = pd.DataFrame(bloqueos)

        st.dataframe(
            df_bloqueos,
            use_container_width=True,
            column_config={
                "sesion_bloqueada": "Sesión bloqueada",
                "sesion_bloqueadora": "Sesión bloqueadora",
                "tipo_espera": "Tipo de espera",
                "tiempo_espera_segundos": st.column_config.NumberColumn("Tiempo de espera (s)", format="%.2f"),
                "estado": "Estado",
                "usuario_bloqueado": "Usuario bloqueado",
                "comando": "Comando",
            },
        )

except Exception as error:
    st.error(
        "No fue posible consultar las sesiones bloqueadas. Esto es un "
        "error de conexión o permisos, distinto de 'no hay bloqueos'."
    )
    st.exception(error)

st.divider()
st.caption(f"Última actualización de esta página: {datetime.now():%Y-%m-%d %H:%M:%S}")