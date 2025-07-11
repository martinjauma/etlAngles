import streamlit as st
import json
import os
from autenticacion import mostrar_formulario_login

# --- VERIFICACIÓN DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    mostrar_formulario_login()
    st.stop()

# --- BARRA LATERAL DE SESIÓN ---
st.sidebar.success(f"👤 Sesión iniciada")
if st.sidebar.button("🔒 Cerrar sesión"):
    st.session_state.logged_in = False
    st.rerun()

# --- CÓDIGO PRINCIPAL DE LA APP ---
st.title("🧹 Eliminar categoría / nombre del JSON")

# Cargar archivo si no está ya en session_state
if "json_data" not in st.session_state:
    st.session_state["json_data"] = None
    st.session_state["rows"] = []
    st.session_state["categorias"] = set()
    st.session_state["nombres"] = set()
    st.session_state["row_names"] = []

uploaded_file = st.file_uploader("📤 Subí tu archivo JSON", type="json")

# Cuando se sube un archivo nuevo, se actualizan los datos
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        rows = data.get("rows", [])
        st.session_state["json_data"] = data
        st.session_state["rows"] = rows

        # Limpiar filtros anteriores
        st.session_state["categorias"] = set()
        st.session_state["nombres"] = set()
        st.session_state["row_names"] = sorted({row.get("row_name", "SIN NOMBRE") for row in rows if "clips" in row})

        # Obtener categorías y nombres
        for row in rows:
            for clip in row.get("clips", []):
                qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array")
                if qualifiers_array is None:
                    continue
                for q in qualifiers_array:
                    if isinstance(q, dict):
                        st.session_state["categorias"].add(q.get("category", ""))
                        st.session_state["nombres"].add(q.get("name", ""))
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# Continuar solo si hay datos en session_state
if st.session_state["json_data"] is not None:
    data = st.session_state["json_data"]
    rows = st.session_state["rows"]

    sin_qualifiers_logs = []

    row_selected = st.selectbox("🎯 Seleccionar Row", options=["TODOS"] + st.session_state["row_names"])

    categoria_a_borrar = None
    nombre_a_borrar = None
    borrar_por_nombre = False

    if st.session_state["categorias"]:
        categoria_a_borrar = st.selectbox("🗂️ Seleccioná la categoría a eliminar", sorted(st.session_state["categorias"]))

    if categoria_a_borrar:
        # Filtrar los nombres relacionados con la categoría seleccionada
        nombres_filtrados = set()
        for row in rows:
            if row_selected != "TODOS" and row.get("row_name") != row_selected:
                continue
            for clip in row.get("clips", []):
                qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array")
                if qualifiers_array is None:
                    continue
                for q in qualifiers_array:
                    if isinstance(q, dict) and q.get("category") == categoria_a_borrar:
                        nombres_filtrados.add(q.get("name", ""))

        borrar_por_nombre = st.checkbox("❓ Eliminar sólo un nombre específico", value=True)
        if borrar_por_nombre and nombres_filtrados:
            nombre_a_borrar = st.selectbox("🔠 Seleccioná el nombre a eliminar", sorted(nombres_filtrados))

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

        # Corregir nombre del archivo modificado (con -mod)
        base_filename = "json_modificado"  # Puedes cambiarlo si deseas personalizarlo
        st.download_button(
            label="📥 Descargar JSON modificado",
            data=json.dumps(data, indent=2),
            file_name=f"{base_filename}-mod.json",  # Sufijo -mod al nombre
            mime="application/json"
        )

    if sin_qualifiers_logs:
        with st.expander("ℹ️ Clips sin qualifiers"):
            for name in sin_qualifiers_logs:
                st.markdown(f"• El row **'{name}'** tiene un clip sin qualifiers.")
