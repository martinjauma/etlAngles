import streamlit as st
from autenticacion import mostrar_formulario_login
import json
import pandas as pd
import re
from collections import Counter

# --- GESTIÓN DE ESTADO DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    mostrar_formulario_login()
    st.stop()

# --- SI ESTÁ LOGUEADO, MOSTRAR APP PRINCIPAL ---
st.sidebar.success(f"👤 Sesión iniciada")
if st.sidebar.button("🔒 Cerrar sesión"):
    st.session_state.logged_in = False
    st.rerun()

# El resto de tu código de la aplicación principal va aquí
# ... (el código de validación de clips, etc.) ...


# Función para limpiar nombre del archivo
def limpiar_nombre_archivo(nombre):
    return re.sub(r'[^\w\-_.]', '_', nombre)

def validar_qualifiers(data, reglas):
    errores = []
    tabla_resumen = []

    for row in data:
        if not isinstance(row, dict):
            continue

        row_name = row.get("row_name")
        if row_name not in reglas:
            continue

        regla = reglas[row_name]
        obligatorias = regla.get("obligatorias", [])
        opcionales = regla.get("opcionales", [])

        todas_las_categorias_presentes = []

        for i, clip in enumerate(row.get("clips", [])):
            qualifiers_array = clip.get("qualifiers", {}).get("qualifiers_array", [])
            if not isinstance(qualifiers_array, list):
                continue

            categorias_presentes = [q.get("category") for q in qualifiers_array if isinstance(q, dict)]
            conteo_categorias = Counter(categorias_presentes)

            todas_las_categorias_presentes.extend(categorias_presentes)

            for categoria in obligatorias:
                if conteo_categorias[categoria] != 1:
                    tipo_error = "obligatoria faltante" if conteo_categorias[categoria] == 0 else "obligatoria repetida"
                    tabla_resumen.append({
                        "row_name": row_name,
                        "clip_index": i,
                        "categoría": categoria,
                        "tipo_error": tipo_error
                    })

            for categoria in opcionales:
                if conteo_categorias[categoria] > 1:
                    tabla_resumen.append({
                        "row_name": row_name,
                        "clip_index": i,
                        "categoría": categoria,
                        "tipo_error": "opcional repetida"
                    })

            categorias_definidas = set(obligatorias + opcionales)
            categorias_extra = [cat for cat in conteo_categorias if cat not in categorias_definidas]
            for extra in categorias_extra:
                tabla_resumen.append({
                    "row_name": row_name,
                    "clip_index": i,
                    "categoría": extra,
                    "tipo_error": "no permitida"
                })

        conteo_total = Counter(todas_las_categorias_presentes)
        faltantes_generales = [cat for cat in obligatorias if conteo_total[cat] == 0]
        for cat in faltantes_generales:
            tabla_resumen.append({
                "row_name": row_name,
                "clip_index": "TODOS",
                "categoría": cat,
                "tipo_error": "obligatoria nunca presente"
            })

    row_names_en_clips = set(row.get("row_name") for row in data if isinstance(row, dict))
    reglas_no_utilizadas = [nombre for nombre in reglas if nombre not in row_names_en_clips]
    for nombre in reglas_no_utilizadas:
        tabla_resumen.append({
            "row_name": nombre,
            "clip_index": "NINGUNO",
            "categoría": "-",
            "tipo_error": "regla no usada (no hay clips)"
        })

    return tabla_resumen

# Streamlit App
st.title("Validador de Clips por Row Name y Categorías")

uploaded_clips = st.file_uploader("📼 Subí el archivo JSON a revisar", type="json")
uploaded_reglas = st.file_uploader("📋 Subí el archivo JSON con las reglas (por row_name)", type="json")

if uploaded_clips is not None:
    st.session_state["clips"] = json.load(uploaded_clips)

if uploaded_reglas is not None:
    st.session_state["reglas"] = json.load(uploaded_reglas)

if "clips" in st.session_state and "reglas" in st.session_state:
    try:
        reglas = st.session_state["reglas"]
        if not isinstance(reglas, dict):
            raise ValueError("El archivo de reglas debe contener un diccionario con row_names y sus categorías.")

        data_dict = st.session_state["clips"]
        if "rows" not in data_dict:
            raise ValueError("El archivo JSON con los clips debe contener una clave 'rows'.")

        rows_data = data_dict["rows"]
        nombre_crudo = data_dict.get("description", "errores_clips")
        nombre_base = limpiar_nombre_archivo(nombre_crudo)

        with st.expander("📖 Reglas Cargadas (click para ver)"):
            st.json(reglas)

        resumen_errores = validar_qualifiers(rows_data, reglas)

        if resumen_errores:
            st.error(f"Se encontraron {len(resumen_errores)} errores en total.")
            df_errores = pd.DataFrame(resumen_errores)
            st.dataframe(df_errores, use_container_width=True)

            st.info(f"Nombre del archivo: **{nombre_base}-ETL.csv**")

            csv = df_errores.to_csv(index=False)
            st.download_button(
                label="📥 Descargar errores como CSV",
                data=csv,
                file_name=f"{nombre_base}.csv",
                mime="text/csv"
            )
        else:
            st.success("✔ Todos los clips cumplen con las reglas.")

    except Exception as e:
        st.error(f"Error procesando el archivo de los clips o las reglas: {e}")
