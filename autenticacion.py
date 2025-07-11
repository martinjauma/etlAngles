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
        if parent_dir == current_dir: # Se ha alcanzado la raíz del sistema de archivos
            raise FileNotFoundError(f"No se pudo encontrar la raíz del proyecto (marcador: {marker_file})")
        current_dir = parent_dir

def verificar_acceso(username, password):
    """
    Verifica las credenciales de un usuario contra un archivo JSON.
    Devuelve True si son correctas, False en caso contrario.
    """
    try:
        project_root = _find_project_root()
        archivo_json = os.path.join(project_root, "usuarios.json")

        if not os.path.exists(archivo_json):
            st.error(f"Error Crítico: El archivo 'usuarios.json' no se encuentra en la raíz del proyecto: {project_root}")
            return False

        with open(archivo_json, "r") as file:
            usuarios = json.load(file)

        for usuario in usuarios:
            if usuario.get("username") == username and usuario.get("password") == password:
                return True
        
        return False

    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo de usuarios: {e}")
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