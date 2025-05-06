# autenticacion.py
import os
import json
import streamlit as st

def cargar_usuarios():
    try:
        archivo_json = os.path.join(os.getcwd(), "usuarios.json")
        with open(archivo_json, "r") as file:
            usuarios = json.load(file)
        return usuarios
    except Exception as e:
        st.error(f"Error al cargar los usuarios: {e}")
        return {}

def autenticar_usuario(usuarios):
    st.title("Iniciar sesión")

    username = st.text_input("Usuario:")
    password = st.text_input("Contraseña:", type="password")

    if st.button("Iniciar sesión"):
        usuario_valido = False
        for usuario in usuarios:
            if usuario["username"] == username and usuario["password"] == password:
                usuario_valido = True
                st.session_state["usuario"] = username  # Guardar el usuario autenticado en session_state
                break

        if usuario_valido:
            st.success("Inicio de sesión exitoso!")
            st.experimental_rerun()  # Recargar la aplicación después de iniciar sesión
            return True
        else:
            st.error("Usuario o contraseña incorrectos. Intenta nuevamente.")
            return False

def verificar_acceso():
    if "usuario" not in st.session_state:
        usuarios = cargar_usuarios()
        autenticado = autenticar_usuario(usuarios)
        if not autenticado:
            st.stop()  # Detener la ejecución si no está autenticado
