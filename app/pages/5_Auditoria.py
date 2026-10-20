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


def consultar(obtener, mensaje_error):
    """
    Ejecuta una consulta del módulo. Si falla, muestra el error en rojo
    y devuelve (None, False) para que la página NO presente el fallo
    como si fuera un resultado vacío.
    """
    try:
        return obtener(), True
    except Exception as error:
        st.error(mensaje_error)
        st.exception(error)
        return None, False


st.title("🔐 Módulo 5: Auditoría")
st.markdown("Consulta información de seguridad: logins, usuarios, roles, privilegios y objetos problemáticos del SGBD.")

tab1, tab2, tab3, tab4 = st.tabs(["Logins y Usuarios", "Roles y Miembros", "Permisos", "Objetos Problemáticos"])

with tab1:
    st.subheader("Logins de la Instancia (Servidor)")
    datos_logins, ok = consultar(obtener_logins, "No fue posible consultar los logins de la instancia.")
    if not ok:
        pass
    elif datos_logins:
        df_logins = pd.DataFrame(datos_logins)
        st.dataframe(df_logins, use_container_width=True)
    else:
        st.info("La consulta no devolvió logins visibles para el usuario actual.")

    st.subheader("Usuarios de la Base de Datos")
    datos_usuarios, ok = consultar(obtener_usuarios, "No fue posible consultar los usuarios de la base de datos.")
    if not ok:
        pass
    elif datos_usuarios:
        df_usuarios = pd.DataFrame(datos_usuarios)
        st.dataframe(df_usuarios, use_container_width=True)
    else:
        st.info("La consulta no devolvió usuarios visibles para el usuario actual.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Roles de Servidor")
        datos_roles_srv, ok = consultar(obtener_roles_servidor, "No fue posible consultar los roles de servidor.")
        if not ok:
            pass
        elif datos_roles_srv:
            df_roles_srv = pd.DataFrame(datos_roles_srv)
            st.dataframe(df_roles_srv, use_container_width=True)
        else:
            st.info("La consulta no devolvió roles de servidor visibles para el usuario actual.")
            
    with col2:
        st.subheader("Roles de Base de Datos")
        datos_roles_bd, ok = consultar(obtener_roles_bd, "No fue posible consultar los roles de base de datos.")
        if not ok:
            pass
        elif datos_roles_bd:
            df_roles_bd = pd.DataFrame(datos_roles_bd)
            st.dataframe(df_roles_bd, use_container_width=True)
        else:
            st.info("La consulta no devolvió roles de base de datos visibles para el usuario actual.")

with tab3:
    st.subheader("Permisos y Privilegios")
    datos_permisos, ok = consultar(obtener_permisos, "No fue posible consultar los permisos.")
    if not ok:
        pass
    elif datos_permisos:
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
        st.info("La consulta no devolvió permisos visibles para el usuario actual.")

with tab4:
    st.subheader("Objetos Problemáticos")
    st.markdown("Muestra objetos (ej: vistas, funciones, procedimientos) que tienen dependencias rotas porque hacen referencia a otros objetos que ya no existen.")
    datos_prob, ok = consultar(
        obtener_objetos_problematicos,
        "No fue posible consultar las dependencias de los objetos.",
    )
    if not ok:
        pass
    elif datos_prob:
        df_prob = pd.DataFrame(datos_prob)
        st.error("¡Se detectaron objetos con dependencias rotas!")
        st.dataframe(df_prob, use_container_width=True)
    else:
        # Solo se llega aquí si la consulta se ejecutó correctamente.
        st.success("No se detectaron objetos con dependencias rotas.")
