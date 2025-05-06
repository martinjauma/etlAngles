import streamlit as st
import json
import pandas as pd
from collections import Counter
import re
import os

def verificar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None

    if st.session_state["autenticado"]:
        st.sidebar.success(f"👤 Sesión iniciada como: {st.session_state['usuario']}")
        if st.sidebar.button("🔒 Cerrar sesión"):
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            st.info("Sesión cerrada. Recargá la página si querés volver a ingresar.")
            st.stop()
        return

    st.title("🔐 Login")
    input_user = st.text_input("Usuario")
    input_pass = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        try:
            secrets = st.secrets["usuario"]
            usuarios = {
                secrets[f"usuario_{i}"]: secrets.get(f"password_{i}", "")
                for i in range(1, 10) if f"usuario_{i}" in secrets
            }

            if input_user in usuarios and usuarios[input_user] == input_pass:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = input_user
                st.success("✅ Acceso concedido")
                st.stop()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
        except Exception as e:
            st.error(f"Error al cargar usuarios: {e}")
            st.stop()

    st.stop()

verificar_acceso()

st.title("🎯 Bienvenido a tu validador")

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


# ---- Subida de archivos solo una vez ----
if "clips" not in st.session_state:
    uploaded_clips = st.file_uploader("📼 Subí el archivo JSON a revisar", type="json", key="clips_uploader")
    if uploaded_clips:
        st.session_state["clips"] = json.load(uploaded_clips)
        st.success("✅ Archivo de clips cargado correctamente.")

if "reglas" not in st.session_state:
    uploaded_reglas = st.file_uploader("📋 Subí el archivo de reglas (JSON)", type="json", key="reglas_uploader")
    if uploaded_reglas:
        st.session_state["reglas"] = json.load(uploaded_reglas)
        st.success("✅ Reglas cargadas correctamente.")

# ---- Validación y descarga ----
if "clips" in st.session_state and "reglas" in st.session_state:
    try:
        reglas = st.session_state["reglas"]
        data_dict = st.session_state["clips"]
        rows_data = data_dict.get("rows", [])
        nombre_crudo = data_dict.get("description", "datosoriginales")
        nombre_base = limpiar_nombre_archivo(nombre_crudo)

        resumen_errores = validar_qualifiers(rows_data, reglas)

        st.subheader("📄 Resumen de errores")
        if resumen_errores:
            df_errores = pd.DataFrame(resumen_errores)
            st.dataframe(df_errores, use_container_width=True)
            csv = df_errores.to_csv(index=False)
            st.download_button("📥 Descargar errores CSV", csv, file_name=f"{nombre_base}-ETL.csv", mime="text/csv")
        else:
            st.success("🎉 No se encontraron errores en los clips.")

        # Descargar JSON original modificado
        st.download_button(
            label="💾 Descargar JSON original",
            data=json.dumps(data_dict, indent=2),
            file_name=f"{nombre_base}-mod.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"❌ Error procesando datos: {e}")
