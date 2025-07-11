import os
import json
import streamlit as st

def _find_project_root(marker_file='requirements.txt'):
    """Encuentra el directorio raíz del proyecto buscando un archivo marcador."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if marker_file in os.listdir(current_dir):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir: 
            return os.path.dirname(os.path.abspath(__file__))
        current_dir = parent_dir

def _get_users():
    """
    Obtiene la lista de usuarios. Prioriza st.secrets, pero usa usuarios.json como respaldo.
    """
    # Método 1: Usar st.secrets (para la nube y desarrollo local con .streamlit/secrets.toml)
    if hasattr(st, 'secrets') and st.secrets:
        if 'users' in st.secrets:
            return st.secrets['users']
        else:
            st.error("Error de configuración: 'st.secrets' está disponible, pero no contiene la sección [[users]]. Verifique su archivo secrets.toml o la configuración en la nube.")
            return []
    
    # Método 2: Usar el archivo local usuarios.json (como último recurso)
    try:
        project_root = _find_project_root()
        archivo_json = os.path.join(project_root, "usuarios.json")
        if os.path.exists(archivo_json):
            with open(archivo_json, "r") as file:
                return json.load(file)
    except Exception:
        pass

    return []

def verificar_acceso(username, password):
    """
    Verifica las credenciales de un usuario.
    """
    usuarios = _get_users()

    if not usuarios:
        st.warning("No se ha configurado ninguna fuente de usuarios válida.")
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