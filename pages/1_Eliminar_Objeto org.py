import streamlit as st
import json

st.title("🧹 Eliminar categoría / nombre del JSON")

uploaded_file = st.file_uploader("📤 Subí tu archivo JSON", type="json")

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        rows = data.get("rows", [])

        # Obtener categorías y nombres únicos
        categorias = set()
        nombres = set()

        for row in rows:
            for clip in row.get("clips", []):
                qualifiers = clip.get("qualifiers", {}).get("qualifiers_array", [])
                for q in qualifiers:
                    if isinstance(q, dict):
                        categorias.add(q.get("category", ""))
                        nombres.add(q.get("name", ""))

        categoria_a_borrar = st.selectbox("Seleccioná la categoría a eliminar", sorted(categorias))
        borrar_por_nombre = st.checkbox("❓ Eliminar sólo ese nombre", value=True)

        if borrar_por_nombre:
            nombre_a_borrar = st.selectbox("Seleccioná el nombre a eliminar", sorted(nombres))
        else:
            nombre_a_borrar = None  # No importa el nombre

        if st.button("🗑️ Eliminar del JSON"):
            filtros = [{'category': categoria_a_borrar}]
            if nombre_a_borrar:
                filtros[0]['name'] = nombre_a_borrar

            # Función de limpieza general
            for row in rows:
                for clip in row.get("clips", []):
                    qualifiers = clip.get("qualifiers", {}).get("qualifiers_array", [])
                    clip["qualifiers"]["qualifiers_array"] = [
                        q for q in qualifiers
                        if not (q.get("category") == filtros[0].get('category') and
                                (filtros[0].get('name') is None or q.get("name") == filtros[0].get('name')))
                    ]

            st.success("Se eliminaron las entradas correctamente.")

            # Descargar
            data["rows"] = rows
            st.download_button(
                label="📥 Descargar JSON modificado",
                data=json.dumps(data, indent=2),
                file_name="json_modificado.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
