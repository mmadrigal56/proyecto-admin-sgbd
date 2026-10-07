import streamlit as st
import pandas as pd
from database.queries.auditoria import (
    obtener_logins,
    obtener_usuarios,
    obtener_roles_servidor,
    obtener_roles_bd,
    obtener_permisos,
    obtener_objetos_problematicos
)

st.set_page_config(page_title="Módulo 5: Auditoría", page_icon="🔐", layout="wide")

st.title("🔐 Módulo 5: Auditoría")
st.markdown("Consulta información de seguridad: logins, usuarios, roles, privilegios y objetos problemáticos del SGBD.")

tab1, tab2, tab3, tab4 = st.tabs(["Logins y Usuarios", "Roles y Miembros", "Permisos", "Objetos Problemáticos"])

with tab1:
    st.subheader("Logins de la Instancia (Servidor)")
    datos_logins = obtener_logins()
    if datos_logins:
        df_logins = pd.DataFrame(datos_logins)
        st.dataframe(df_logins, use_container_width=True)
    else:
        st.info("No se encontraron logins o el usuario actual no tiene permisos suficientes para consultarlos.")

    st.subheader("Usuarios de la Base de Datos")
    datos_usuarios = obtener_usuarios()
    if datos_usuarios:
        df_usuarios = pd.DataFrame(datos_usuarios)
        st.dataframe(df_usuarios, use_container_width=True)
    else:
        st.info("No se encontraron usuarios o permisos insuficientes.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Roles de Servidor")
        datos_roles_srv = obtener_roles_servidor()
        if datos_roles_srv:
            df_roles_srv = pd.DataFrame(datos_roles_srv)
            st.dataframe(df_roles_srv, use_container_width=True)
        else:
            st.info("No se encontraron roles de servidor o no hay permisos suficientes.")
            
    with col2:
        st.subheader("Roles de Base de Datos")
        datos_roles_bd = obtener_roles_bd()
        if datos_roles_bd:
            df_roles_bd = pd.DataFrame(datos_roles_bd)
            st.dataframe(df_roles_bd, use_container_width=True)
        else:
            st.info("No se encontraron roles de base de datos o permisos insuficientes.")

with tab3:
    st.subheader("Permisos y Privilegios")
    datos_permisos = obtener_permisos()
    if datos_permisos:
        df_permisos = pd.DataFrame(datos_permisos)
        
        # Filtros
        col1, col2 = st.columns(2)
        filtro_usuario = col1.multiselect("Filtrar por Usuario/Rol", df_permisos['GranteeName'].unique())
        filtro_permiso = col2.multiselect("Filtrar por Permiso", df_permisos['Permission'].unique())
        
        df_filtrado = df_permisos
        if filtro_usuario:
            df_filtrado = df_filtrado[df_filtrado['GranteeName'].isin(filtro_usuario)]
        if filtro_permiso:
            df_filtrado = df_filtrado[df_filtrado['Permission'].isin(filtro_permiso)]
            
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("No se encontraron permisos o permisos insuficientes.")

with tab4:
    st.subheader("Objetos Problemáticos")
    st.markdown("Muestra objetos (ej: vistas, funciones, procedimientos) que tienen dependencias rotas porque hacen referencia a otros objetos que ya no existen.")
    datos_prob = obtener_objetos_problematicos()
    if datos_prob:
        df_prob = pd.DataFrame(datos_prob)
        st.error("¡Se detectaron objetos con dependencias rotas!")
        st.dataframe(df_prob, use_container_width=True)
    else:
        st.success("No se detectaron objetos con dependencias rotas.")
