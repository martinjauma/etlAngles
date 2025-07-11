import os
import json
import streamlit as st

def _get_users():
    """
    Obtiene la lista de usuarios. Prioriza st.secrets, pero usa usuarios.json como respaldo.
    """
    # Método 1: Usar st.secrets (ideal para la nube)
    if hasattr(st, 'secrets') and 'users' in st.secrets:
        return st.secrets['users']
    
    # Método 2: Usar el archivo local usuarios.json (para desarrollo)
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        archivo_json = os.path.join(project_root, "usuarios.json")
        if os.path.exists(archivo_json):
            with open(archivo_json, "r") as file:
                return json.load(file)
    except Exception:
        pass # Ignorar errores si el archivo no existe o falla la carga

    # Si no se encuentra ninguna fuente de usuarios
    return []

def verificar_acceso(username, password):
    """
    Verifica las credenciales de un usuario contra st.secrets o un archivo JSON local.
    """
    usuarios = _get_users()

    if not usuarios:
        st.error("No se ha configurado ninguna fuente de usuarios (ni st.secrets ni usuarios.json).")
        return False

    for usuario in usuarios:
        if usuario.get("username") == username and usuario.get("password") == password:
            return True
    
    return False

def mostrar_formulario_login():
    """
    Muestra el formulario de login y maneja la lógica de autenticación.
    """
    st.title("🔐 Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if verificar_acceso(username, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
