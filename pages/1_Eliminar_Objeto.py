import streamlit as st
import json

st.set_page_config(layout="wide")
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
