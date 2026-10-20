import streamlit as st

from database.connection import get_connection


st.title("Administración de Bases de Datos")
st.caption(
    "Panel de administración de SQL Server. La información se obtiene "
    "directamente de la instancia configurada en config/.env."
)

st.divider()

# ---------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------
st.subheader("Conexión")

try:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                @@SERVERNAME AS servidor,
                DB_NAME() AS base_actual,
                SUSER_NAME() AS usuario;
        """)
        fila = cursor.fetchone()

    st.success("Conexión exitosa con SQL Server")
    st.write(f"**Servidor:** {fila.servidor}")
    st.write(f"**Base de datos:** {fila.base_actual}")
    st.write(f"**Usuario de consulta:** {fila.usuario}")

except Exception as error:
    st.error(
        "No fue posible conectarse a SQL Server. Verifique la conexión "
        "configurada en config/.env y que el servicio esté iniciado."
    )
    st.exception(error)

st.divider()

# ---------------------------------------------------------------
# Módulos
# ---------------------------------------------------------------
st.subheader("Módulos")

modulos = [
    (
        "pages/1_Estado_Instancia.py",
        "Estado de la instancia",
        "Servidor, versión, tiempo de actividad, memoria y bases de datos.",
    ),
    (
        "pages/2_Rendimiento.py",
        "Rendimiento",
        "Consultas de mayor consumo, sesiones activas y sesiones bloqueadas.",
    ),
    (
        "pages/3_Almacenamiento.py",
        "Almacenamiento",
        "Tamaño de la base, archivos, filegroups, disco, objetos de mayor "
        "tamaño e historial de crecimiento.",
    ),
    (
        "pages/4_Respaldos.py",
        "Respaldos",
        "Historial de respaldos y antigüedad del último.",
    ),
    (
        "pages/5_Auditoria.py",
        "Auditoría",
        "Logins, usuarios, roles, permisos y objetos con dependencias rotas.",
    ),
    (
        "pages/6_Mantenimiento.py",
        "Mantenimiento",
        "Actualización de estadísticas y mantenimiento de índices, con "
        "confirmación e historial.",
    ),
]

for ruta, titulo, descripcion in modulos:
    st.page_link(ruta, label=titulo)
    st.caption(descripcion)
