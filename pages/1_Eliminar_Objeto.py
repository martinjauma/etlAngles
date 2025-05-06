import streamlit as st
from autenticacion import verificar_acceso
st.set_page_config(layout="wide")

verificar_acceso()

st.title("🧹 Eliminar Objeto de Clips")

# Verificamos si ya hay JSON cargado en session_state
if "clips" not in st.session_state:
    st.warning("⚠ Primero subí el archivo JSON desde la página principal.")
    st.stop()

clips_data = st.session_state["clips"]

if "rows" not in clips_data:
    st.error("El JSON no contiene 'rows'.")
    st.stop()

rows = clips_data["rows"]
row_names = [row.get("row_name", "Sin nombre") for row in rows]

# Interfaz para seleccionar y eliminar
row_to_delete = st.selectbox("Seleccioná el row_name a eliminar", options=row_names)

if st.button("🗑 Eliminar row"):
    st.session_state["clips"]["rows"] = [r for r in rows if r.get("row_name") != row_to_delete]
    st.success(f"✅ Row eliminado: {row_to_delete}")
