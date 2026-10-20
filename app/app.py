import streamlit as st

st.set_page_config(page_title="Administración SGBD")

paginas = [
    st.Page("inicio.py", title="Inicio", default=True),
    st.Page("pages/1_Estado_Instancia.py", title="Estado de la instancia"),
    st.Page("pages/2_Rendimiento.py", title="Rendimiento"),
    st.Page("pages/3_Almacenamiento.py", title="Almacenamiento"),
    st.Page("pages/4_Respaldos.py", title="Respaldos"),
    st.Page("pages/5_Auditoria.py", title="Auditoría"),
    st.Page("pages/6_Mantenimiento.py", title="Mantenimiento"),
]

st.navigation(paginas).run()
