import streamlit as st

from database.connection import get_connection


st.set_page_config(
    page_title="Administración SGBD",
    page_icon="🗄️",
)

st.title("Administración de Bases de Datos")
st.subheader("Prueba de conexión")

try:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                @@SERVERNAME AS servidor,
                DB_NAME() AS base_actual,
                @@VERSION AS version_sql_server;
        """)

        row = cursor.fetchone()

    st.success("Conexión exitosa con SQL Server")

    st.write(f"**Servidor:** {row.servidor}")
    st.write(f"**Base de datos:** {row.base_actual}")

    st.write("**Versión de SQL Server:**")
    st.code(row.version_sql_server)

except Exception as error:
    st.error("No fue posible conectarse a SQL Server.")
    st.exception(error)