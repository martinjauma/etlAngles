import os
import json
import streamlit as st

def verificar_acceso(username, password):
    """
    Verifica las credenciales de un usuario contra un archivo JSON.
    Devuelve True si son correctas, False en caso contrario.
    """
    try:
        # Usamos una ruta relativa al script para encontrar usuarios.json
        base_dir = os.path.dirname(os.path.abspath(__file__))
        archivo_json = os.path.join(base_dir, "usuarios.json")

        if not os.path.exists(archivo_json):
            # Este error es para el desarrollador, no debería aparecer en producción
            st.error("No se encontró el archivo 'usuarios.json' en el directorio principal.")
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
    Esta función no devuelve nada, pero actualiza el session_state y causa un rerun.
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
