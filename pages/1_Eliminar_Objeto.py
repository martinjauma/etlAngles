import streamlit as st
import json
import streamlit as st
from autenticacion import verificar_acceso
st.set_page_config(layout="wide")
import os

# --- FUNCIÓN DE LOGIN ---
def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None

    # Si ya está autenticado, mostramos nombre de usuario y botón para cerrar sesión
    if st.session_state["autenticado"]:
        st.sidebar.success(f"👤 Sesión iniciada como: {st.session_state['usuario']}")
        if st.sidebar.button("🔒 Cerrar sesión"):
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            st.experimental_rerun()
        return  # Salimos para que se muestre el resto de la app

    # FORMULARIO DE LOGIN
    st.title("🔐 Login")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        try:
            with open("usuarios.json", "r") as file:
                usuarios = json.load(file)

            # Recorremos lista de usuarios buscando match
            for user in usuarios:
                if user["username"] == usuario and user["password"] == password:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.success("Acceso concedido")
                    st.experimental_rerun()
                    return

            st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error(f"Error al cargar usuarios: {e}")

    st.stop()  # Detiene el resto de la app si no está logueado


# --- LLAMADA A FUNCIÓN DE LOGIN ---
verificar_acceso()

# --- CÓDIGO PRINCIPAL DE LA APP (si pasó el login) ---
st.title("🎯 Bienvenido a tu validador")
st.write("Este contenido solo es visible si estás autenticado.")



# Si está autenticado, mostrar la página secundaria
st.title("🧹 Eliminar categoría / nombre del JSON")



# Cargar archivo si no está ya en session_state
if "json_data" not in st.session_state:
    st.session_state["json_data"] = None
    st.session_state["rows"] = []

uploaded_file = st.file_uploader("📤 Subí tu archivo JSON", type="json")

if uploaded_file is not None and st.session_state["json_data"] is None:
    try:
        data = json.load(uploaded_file)
        rows = data.get("rows", [])
        st.session_state["json_data"] = data
        st.session_state["rows"] = rows
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# Continuar solo si hay datos en session_state
if st.session_state["json_data"] is not None:
    data = st.session_state["json_data"]
    rows = st.session_state["rows"]

    sin_qualifiers_logs = []
    row_names = sorted({row.get("row_name", "SIN NOMBRE") for row in rows if "clips" in row})
    row_selected = st.selectbox("🎯 Seleccionar Row", options=["TODOS"] + row_names)

    categorias = set()
    nombres = set()

    for row in rows:
        if row_selected != "TODOS" and row.get("row_name") != row_selected:
            continue
        for clip in row.get("clips", []):
            qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array")
            if qualifiers_array is None:
                sin_qualifiers_logs.append(row.get("row_name", "SIN NOMBRE"))
                continue
            for q in qualifiers_array:
                if isinstance(q, dict):
                    categorias.add(q.get("category", ""))

    if categorias:
        categoria_a_borrar = st.selectbox("🗂️ Seleccioná la categoría a eliminar", sorted(categorias))

        for row in rows:
            if row_selected != "TODOS" and row.get("row_name") != row_selected:
                continue
            for clip in row.get("clips", []):
                qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array")
                if qualifiers_array is None:
                    continue
                for q in qualifiers_array:
                    if isinstance(q, dict) and q.get("category") == categoria_a_borrar:
                        nombres.add(q.get("name", ""))

        borrar_por_nombre = st.checkbox("❓ Eliminar sólo un nombre específico", value=True)
        nombre_a_borrar = None
        if borrar_por_nombre:
            nombre_a_borrar = st.selectbox("🔠 Seleccioná el nombre a eliminar", sorted(nombres))

        mostrar_preview = st.checkbox("👁️ Ver cuántos qualifiers se eliminarán", value=True)
        total_encontrados = 0

        if mostrar_preview:
            for row in rows:
                if row_selected != "TODOS" and row.get("row_name") != row_selected:
                    continue
                for clip in row.get("clips", []):
                    qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array", [])
                    for q in qualifiers_array:
                        if isinstance(q, dict) and q.get("category") == categoria_a_borrar:
                            if not nombre_a_borrar or q.get("name") == nombre_a_borrar:
                                total_encontrados += 1
            st.info(f"👀 Se eliminarán {total_encontrados} qualifiers.")

        if st.button("🗑️ Eliminar del JSON"):
            total_eliminados = 0
            for row in rows:
                if row_selected != "TODOS" and row.get("row_name") != row_selected:
                    continue
                for clip in row.get("clips", []):
                    qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array")
                    if qualifiers_array is None:
                        continue
                    originales = len(qualifiers_array)
                    qualifiers_filtrados = [
                        q for q in qualifiers_array
                        if not (q.get("category") == categoria_a_borrar and
                                (not nombre_a_borrar or q.get("name") == nombre_a_borrar))
                    ]
                    eliminados = originales - len(qualifiers_filtrados)
                    total_eliminados += eliminados
                    clip["qualifiers"]["qualifiers_array"] = qualifiers_filtrados

            st.success(f"✅ Se eliminaron {total_eliminados} qualifiers del JSON.")

            st.download_button(
                label="📥 Descargar JSON modificado",
                data=json.dumps(data, indent=2),
                file_name="json_modificado.json",
                mime="application/json"
            )

    if sin_qualifiers_logs:
        with st.expander("ℹ️ Clips sin qualifiers"):
            for name in sin_qualifiers_logs:
                st.markdown(f"• El row **'{name}'** tiene un clip sin qualifiers.")
