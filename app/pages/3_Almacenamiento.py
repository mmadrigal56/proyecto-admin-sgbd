from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from database.connection import get_connection
from database.queries.almacenamiento import (
    obtener_archivos,
    obtener_edicion,
    obtener_filegroups,
    obtener_historial,
    obtener_indices_mayor_tamano,
    obtener_resumen_base,
    obtener_tablas_mayor_tamano,
    obtener_volumenes,
    registrar_medicion,
)
from services.almacenamiento import (
    DISCO_LIBRE_ADVERTENCIA,
    DISCO_LIBRE_CRITICO,
    UMBRAL_ADVERTENCIA,
    UMBRAL_CRITICO,
    estimar_dias_hasta_limite,
    evaluar_archivo,
    evaluar_limite_edicion,
    evaluar_volumen,
    limite_edicion_mb,
    porcentaje,
    resumir_crecimiento,
)


ETIQUETA_NIVEL = {"ok": "OK", "advertencia": "Advertencia", "critico": "Crítico"}


def fmt_mb(valor):
    """Muestra MB con dos decimales; si supera 1 GB también lo indica en GB."""
    if valor is None:
        return "—"
    if valor >= 1024:
        return f"{valor:,.2f} MB ({valor / 1024:,.2f} GB)"
    return f"{valor:,.2f} MB"


def fmt_pct(valor):
    return "—" if valor is None else f"{valor:.1f} %"


st.title("Módulo 3 — Gestión del almacenamiento")
st.caption(
    "Información obtenida directamente de la instancia de SQL Server "
    "configurada en config/.env. Las métricas corresponden a la base de "
    "datos de la conexión (DB_NAME)."
)

if st.button("Actualizar información"):
    st.rerun()

with st.expander("¿Qué significa asignado, utilizado y disponible?"):
    st.markdown(
        """
- **Espacio asignado:** tamaño que el archivo ocupa en el disco. SQL Server
  ya lo reservó aunque no esté lleno (`sys.database_files.size`).
- **Espacio utilizado:** parte del archivo que realmente contiene datos
  (`FILEPROPERTY(nombre, 'SpaceUsed')`).
- **Espacio disponible:** asignado − utilizado. Es espacio libre *dentro*
  del archivo; se usa antes de que el archivo tenga que crecer.
- Cuando el disponible se agota, SQL Server **autocrece** el archivo según
  su configuración de crecimiento, hasta su tamaño máximo o hasta que se
  llene el disco.
- SQL Server mide todo en **páginas de 8 KB**; aquí se convierte a MB
  (páginas × 8 ÷ 1024).
        """
    )

st.subheader("Indicadores de advertencia")
contenedor_alertas = st.container()

try:
    with get_connection():
        pass
except Exception as error:
    with contenedor_alertas:
        st.warning("No se pudo evaluar el almacenamiento: no hay conexión con SQL Server.")
    st.error(
        "No fue posible conectarse a SQL Server. Verifique que el servicio esté "
        "iniciado y que la configuración de config/.env sea correcta."
    )
    st.exception(error)
    st.stop()

st.divider()

alertas = []            # (nivel, mensaje)
secciones_con_error = []  # secciones que no se pudieron evaluar

resumen = None
edicion = None
try:
    resumen = obtener_resumen_base()
    edicion = obtener_edicion()
except Exception as error:
    secciones_con_error.append("tamaño de la base")
    st.error(
        "No fue posible obtener el tamaño de la base de datos. "
        "Verifique la conexión configurada en config/.env."
    )
    st.exception(error)

st.subheader("Tamaño de la base de datos")

if resumen:
    datos_asig = resumen["datos_asignado_mb"] or 0.0
    datos_usado = resumen["datos_usado_mb"]
    log_asig = resumen["log_asignado_mb"] or 0.0
    log_usado = resumen["log_usado_mb"]

    if datos_usado is None or log_usado is None:
        st.warning(
            "SQL Server no devolvió el espacio utilizado (FILEPROPERTY = NULL). "
            "Normalmente indica que falta ejecutar "
            "sql/03-almacenamiento/02_otorgar_permisos_almacenamiento.sql."
        )

    datos_disp = datos_asig - datos_usado if datos_usado is not None else None
    pct_datos = porcentaje(datos_usado, datos_asig)

    st.write(f"**Base de datos:** {resumen['base_datos']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tamaño total en disco", fmt_mb(datos_asig + log_asig),
                help="Datos + registro (espacio asignado).")
    col2.metric("Datos: asignado", fmt_mb(datos_asig))
    col3.metric("Datos: utilizado", fmt_mb(datos_usado))
    col4.metric("Datos: disponible", fmt_mb(datos_disp))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Datos: % utilizado", fmt_pct(pct_datos),
                help="Utilizado ÷ asignado de los archivos de datos.")
    col2.metric("Registro (log): asignado", fmt_mb(log_asig))
    col3.metric("Registro (log): utilizado", fmt_mb(log_usado))
    col4.metric("Registro (log): % utilizado", fmt_pct(porcentaje(log_usado, log_asig)))

    if datos_usado is not None and log_usado is not None:
        df_barras = pd.DataFrame({
            "archivo": ["Datos", "Datos", "Registro (log)", "Registro (log)"],
            "espacio": ["Utilizado", "Disponible", "Utilizado", "Disponible"],
            "mb": [datos_usado, datos_asig - datos_usado, log_usado, log_asig - log_usado],
        })
        fig = px.bar(
            df_barras, x="mb", y="archivo", color="espacio", orientation="h",
            barmode="stack", text_auto=".2f",
            labels={"mb": "MB", "archivo": "", "espacio": ""},
            title="Espacio asignado dividido en utilizado y disponible",
        )
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=50, b=10),
                          legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig, width="stretch")

    limite_ed = limite_edicion_mb(edicion)
    if edicion:
        if limite_ed is None:
            st.info(f"Edición **{edicion['edicion']}**: sin límite de tamaño por base de datos.")
        else:
            pct_ed, nivel_ed = evaluar_limite_edicion(datos_asig, limite_ed)
            st.write(
                f"**Límite de la edición {edicion['edicion']}:** {limite_ed / 1024:.0f} GB "
                f"por base de datos (solo archivos de datos). Uso actual: {fmt_pct(pct_ed)}."
            )
            st.progress(min((pct_ed or 0) / 100.0, 1.0))
            if nivel_ed != "ok":
                alertas.append((nivel_ed, f"La base usa {pct_ed:.1f} % del límite de {limite_ed / 1024:.0f} GB de la edición Express."))
else:
    st.info("No hay información de tamaño disponible (ver el error mostrado arriba).")

st.divider()

st.subheader("Archivos de datos y de registro")
st.caption(
    f"Nivel: se compara el espacio utilizado contra el tamaño MÁXIMO que el archivo "
    f"puede alcanzar. ≥ {UMBRAL_ADVERTENCIA:.0f} % = advertencia, ≥ {UMBRAL_CRITICO:.0f} % = crítico. "
    "Un archivo con autocrecimiento ilimitado no se marca como riesgo aunque esté lleno."
)

try:
    archivos = [evaluar_archivo(a) for a in obtener_archivos()]

    if not archivos:
        st.info("No se encontraron archivos para esta base de datos.")
    else:
        for a in archivos:
            if a["nivel"] != "ok":
                alertas.append((a["nivel"], f"Archivo {a['nombre_logico']} ({a['tipo']}): {a['motivo']}"))

        df_arch = pd.DataFrame(archivos)
        df_arch["nivel"] = df_arch["nivel"].map(ETIQUETA_NIVEL)
        df_arch["filegroup"] = df_arch["filegroup"].fillna("— (el log no usa filegroup)")

        st.dataframe(
            df_arch[[
                "nivel", "nombre_logico", "tipo", "filegroup", "ubicacion", "estado",
                "asignado_mb", "usado_mb", "disponible_mb", "pct_usado",
                "crecimiento", "limite", "motivo",
            ]],
            width="stretch",
            hide_index=True,
            column_config={
                "nivel": "Nivel",
                "nombre_logico": "Nombre lógico",
                "tipo": "Tipo",
                "filegroup": "Filegroup",
                "ubicacion": "Ubicación física",
                "estado": "Estado",
                "asignado_mb": st.column_config.NumberColumn("Asignado (MB)", format="%.2f"),
                "usado_mb": st.column_config.NumberColumn("Utilizado (MB)", format="%.2f"),
                "disponible_mb": st.column_config.NumberColumn("Disponible (MB)", format="%.2f"),
                "pct_usado": st.column_config.ProgressColumn(
                    "% utilizado", format="%.1f %%", min_value=0, max_value=100),
                "crecimiento": "Crecimiento configurado",
                "limite": "Tamaño máximo",
                "motivo": "Observación",
            },
        )

except Exception as error:
    secciones_con_error.append("archivos")
    st.error("No fue posible obtener los archivos de la base de datos.")
    st.exception(error)

st.divider()

st.subheader("Filegroups")
st.caption(
    "Un filegroup agrupa uno o más archivos de datos. Las tablas e índices se "
    "crean dentro de un filegroup (por defecto PRIMARY)."
)

try:
    filegroups = obtener_filegroups()

    if not filegroups:
        st.info("La base no tiene filegroups visibles para este usuario.")
    else:
        df_fg = pd.DataFrame(filegroups)
        df_fg["disponible_mb"] = df_fg["asignado_mb"] - df_fg["usado_mb"]
        df_fg["pct_usado"] = [porcentaje(u, a) for u, a in zip(df_fg["usado_mb"], df_fg["asignado_mb"])]
        df_fg["es_predeterminado"] = df_fg["es_predeterminado"].map({True: "Sí", False: "No"})
        df_fg["solo_lectura"] = df_fg["solo_lectura"].map({True: "Sí", False: "No"})

        st.dataframe(
            df_fg,
            width="stretch",
            hide_index=True,
            column_config={
                "filegroup": "Filegroup",
                "tipo": "Tipo",
                "es_predeterminado": "Predeterminado",
                "solo_lectura": "Solo lectura",
                "cantidad_archivos": "Archivos",
                "asignado_mb": st.column_config.NumberColumn("Asignado (MB)", format="%.2f"),
                "usado_mb": st.column_config.NumberColumn("Utilizado (MB)", format="%.2f"),
                "disponible_mb": st.column_config.NumberColumn("Disponible (MB)", format="%.2f"),
                "pct_usado": st.column_config.ProgressColumn(
                    "% utilizado", format="%.1f %%", min_value=0, max_value=100),
            },
        )

except Exception as error:
    st.error("No fue posible obtener los filegroups.")
    st.exception(error)

st.divider()

st.subheader("Espacio en el disco donde están los archivos")
st.caption(
    f"Si el disco se llena, los archivos no pueden autocrecer. "
    f"Libre < {DISCO_LIBRE_ADVERTENCIA:.0f} % = advertencia, < {DISCO_LIBRE_CRITICO:.0f} % = crítico."
)

try:
    volumenes = [evaluar_volumen(v) for v in obtener_volumenes()]

    if not volumenes:
        st.info("SQL Server no devolvió información del disco.")
    else:
        cols = st.columns(len(volumenes))
        for col, v in zip(cols, volumenes):
            col.metric(
                f"Unidad {v['unidad']} {('(' + v['etiqueta'] + ')') if v['etiqueta'] else ''}",
                f"{fmt_pct(v['pct_libre'])} libre",
                help=f"Libre: {fmt_mb(v['disponible_mb'])} de {fmt_mb(v['total_mb'])}",
            )
            col.caption(f"{fmt_mb(v['disponible_mb'])} libres de {fmt_mb(v['total_mb'])}")
            if v["nivel"] != "ok":
                alertas.append((v["nivel"], f"La unidad {v['unidad']} tiene solo {fmt_pct(v['pct_libre'])} libre."))

except Exception as error:
    secciones_con_error.append("disco")
    st.error(
        "No fue posible consultar el espacio del disco. Verifique la conexión "
        "y el permiso VIEW SERVER STATE."
    )
    st.exception(error)

st.divider()

with contenedor_alertas:
    if secciones_con_error:
        st.warning(
            "No se pudieron evaluar todas las secciones ("
            + ", ".join(secciones_con_error)
            + "). Los indicadores pueden estar incompletos; ver los errores más abajo."
        )
    if not alertas and not secciones_con_error:
        st.success("No se detectaron riesgos de almacenamiento con los umbrales definidos.")
    elif alertas:
        for nivel, mensaje in sorted(alertas, key=lambda x: x[0] != "critico"):
            (st.error if nivel == "critico" else st.warning)(f"**{ETIQUETA_NIVEL[nivel]}:** {mensaje}")

st.subheader("Objetos de mayor tamaño")

limite_top = st.slider("Cantidad de objetos a mostrar", min_value=5, max_value=30, value=10, step=5)

tab_tablas, tab_indices = st.tabs(["Tablas", "Índices"])

with tab_tablas:
    st.caption(
        "Reservado = páginas reservadas para la tabla (datos + índices), incluyendo "
        "espacio aún sin usar dentro de sus extents."
    )
    try:
        tablas = obtener_tablas_mayor_tamano(limite_top)
        if not tablas:
            st.info(
                "No hay tablas de usuario en esta base, o el usuario no tiene "
                "VIEW DEFINITION para verlas."
            )
        else:
            df_tab = pd.DataFrame(tablas)
            df_tab["objeto"] = df_tab["esquema"] + "." + df_tab["tabla"]
            fig = px.bar(
                df_tab.sort_values("reservado_mb"),
                x="reservado_mb", y="objeto", orientation="h",
                labels={"reservado_mb": "Espacio reservado (MB)", "objeto": "Tabla"},
                title="Tablas por espacio reservado",
            )
            fig.update_layout(height=max(250, 35 * len(df_tab)), margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(
                df_tab.drop(columns=["objeto"]),
                width="stretch",
                hide_index=True,
                column_config={
                    "esquema": "Esquema",
                    "tabla": "Tabla",
                    "filas": st.column_config.NumberColumn("Filas", format="%d"),
                    "reservado_mb": st.column_config.NumberColumn("Reservado (MB)", format="%.2f"),
                    "usado_mb": st.column_config.NumberColumn("Utilizado (MB)", format="%.2f"),
                    "datos_mb": st.column_config.NumberColumn("Datos (MB)", format="%.2f"),
                    "indices_mb": st.column_config.NumberColumn("Índices no agrupados (MB)", format="%.2f"),
                },
            )
    except Exception as error:
        st.error("No fue posible obtener las tablas de mayor tamaño.")
        st.exception(error)

with tab_indices:
    st.caption(
        "Incluye el índice agrupado (que contiene las filas de la tabla), los índices "
        "no agrupados y los heaps (tablas sin índice agrupado)."
    )
    try:
        indices = obtener_indices_mayor_tamano(limite_top)
        if not indices:
            st.info("No hay índices de tablas de usuario en esta base.")
        else:
            st.dataframe(
                pd.DataFrame(indices),
                width="stretch",
                hide_index=True,
                column_config={
                    "esquema": "Esquema",
                    "tabla": "Tabla",
                    "indice": "Índice",
                    "tipo_indice": "Tipo",
                    "filas": st.column_config.NumberColumn("Filas", format="%d"),
                    "reservado_mb": st.column_config.NumberColumn("Reservado (MB)", format="%.2f"),
                    "usado_mb": st.column_config.NumberColumn("Utilizado (MB)", format="%.2f"),
                },
            )
    except Exception as error:
        st.error("No fue posible obtener los índices de mayor tamaño.")
        st.exception(error)

st.divider()

st.subheader("Historial de crecimiento")
st.caption(
    "SQL Server no guarda el historial del espacio usado, por eso el proyecto lo registra "
    "en la tabla propia monitoreo.HistorialAlmacenamiento mediante el procedimiento "
    "monitoreo.sp_capturar_almacenamiento. Las capturas automáticas las hace una tarea "
    "programada de Windows (scripts/capturar_almacenamiento.py)."
)

if st.button("Registrar una medición ahora"):
    try:
        registradas = registrar_medicion(origen="aplicacion")
        st.success(f"Medición registrada: {len(registradas)} archivo(s) guardados en el historial.")
    except Exception as error:
        st.error(
            "No fue posible registrar la medición. Verifique que se ejecutaron "
            "01_crear_objetos_historial.sql y 02_otorgar_permisos_almacenamiento.sql."
        )
        st.exception(error)

try:
    historial = obtener_historial(limite=200)

    if not historial:
        st.info(
            "Todavía no hay mediciones registradas. Use el botón «Registrar una medición "
            "ahora» o ejecute EXEC monitoreo.sp_capturar_almacenamiento."
        )
    else:
        historial_asc = list(reversed(historial))
        df_hist = pd.DataFrame(historial_asc)

        if len(df_hist) == 1:
            st.info("Solo hay una medición. Se necesitan al menos dos, en momentos distintos, para comparar crecimiento.")

        df_largo = df_hist.melt(
            id_vars=["fecha_captura"],
            value_vars=["datos_asignado_mb", "datos_usado_mb", "log_asignado_mb", "log_usado_mb"],
            var_name="serie", value_name="mb",
        )
        df_largo["serie"] = df_largo["serie"].map({
            "datos_asignado_mb": "Datos - asignado",
            "datos_usado_mb": "Datos - utilizado",
            "log_asignado_mb": "Log - asignado",
            "log_usado_mb": "Log - utilizado",
        })
        fig = px.line(
            df_largo, x="fecha_captura", y="mb", color="serie", markers=True,
            labels={"fecha_captura": "Fecha de la medición", "mb": "Espacio (MB)", "serie": "Serie"},
            title="Evolución del espacio de la base de datos",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, width="stretch")

        crecimiento = resumir_crecimiento(historial_asc)
        if crecimiento:
            col1, col2, col3 = st.columns(3)
            col1.metric("Mediciones comparadas", crecimiento["mediciones"],
                        help=f"Desde {crecimiento['desde']} hasta {crecimiento['hasta']}")
            col2.metric("Cambio en datos utilizados", f"{crecimiento['delta_datos_usado_mb']:+,.2f} MB")
            col3.metric("Cambio en tamaño asignado total", f"{crecimiento['delta_total_asignado_mb']:+,.2f} MB")

            prom = crecimiento["promedio_diario_datos_mb"]
            if prom is None:
                st.caption("El periodo medido es menor a un día: aún no se calcula un promedio diario.")
            else:
                texto = f"Crecimiento promedio de los datos: **{prom:+,.2f} MB por día** en {crecimiento['dias']:.1f} días."
                limite_ed = limite_edicion_mb(edicion)
                dias_limite = estimar_dias_hasta_limite(
                    historial_asc[-1]["datos_usado_mb"], limite_ed, prom)
                if dias_limite is not None:
                    texto += (f" Si siguiera creciendo al mismo ritmo, alcanzaría el límite de la "
                              f"edición en aproximadamente **{dias_limite:,.0f} días** (proyección lineal simple).")
                st.write(texto)

        with st.expander("Ver tabla de mediciones"):
            st.dataframe(
                df_hist.iloc[::-1],
                width="stretch",
                hide_index=True,
                column_config={
                    "fecha_captura": st.column_config.DatetimeColumn("Fecha", format="YYYY-MM-DD HH:mm:ss"),
                    "origen": "Origen",
                    "datos_asignado_mb": st.column_config.NumberColumn("Datos asignado (MB)", format="%.2f"),
                    "datos_usado_mb": st.column_config.NumberColumn("Datos utilizado (MB)", format="%.2f"),
                    "datos_disponible_mb": st.column_config.NumberColumn("Datos disponible (MB)", format="%.2f"),
                    "log_asignado_mb": st.column_config.NumberColumn("Log asignado (MB)", format="%.2f"),
                    "log_usado_mb": st.column_config.NumberColumn("Log utilizado (MB)", format="%.2f"),
                    "total_asignado_mb": st.column_config.NumberColumn("Total asignado (MB)", format="%.2f"),
                    "total_usado_mb": st.column_config.NumberColumn("Total utilizado (MB)", format="%.2f"),
                },
            )

except Exception as error:
    st.error(
        "No fue posible leer el historial. Verifique que existe la tabla "
        "monitoreo.HistorialAlmacenamiento (01_crear_objetos_historial.sql) y que el "
        "usuario tiene SELECT sobre el esquema monitoreo (02_otorgar_permisos_almacenamiento.sql)."
    )
    st.exception(error)

st.divider()
st.caption(f"Última actualización de esta página: {datetime.now():%Y-%m-%d %H:%M:%S}")
