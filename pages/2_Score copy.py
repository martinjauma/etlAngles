import streamlit as st
import json

st.title("📊 Resumen de Puntos - Partido de Rugby")

# === Subir archivo JSON ===
uploaded_file = st.file_uploader("📁 Sube el archivo JSON de Timeline", type="json")

if uploaded_file:
    try:
        data = json.load(uploaded_file)

        resumen = {}

        # === Recorremos los eventos ===
        for row in data.get("rows", []):
            tipo_evento = row.get("row_name", "")
            for clip in row.get("clips", []):
                eq_name = None
                tantos = []
                resultado = None
                tipo_especial = None

                for q in clip.get("qualifiers", {}).get("qualifiers_array", []):
                    if q.get("category") == "EQ NAME":
                        eq_name = q.get("name")
                    elif q.get("category") == "TANTOS":
                        tantos.append(q.get("name"))
                    elif q.get("category") == "RESULTADO":
                        resultado = q.get("name")
                    elif q.get("category") == "TYPE":
                        tipo_especial = q.get("name")

                if not eq_name:
                    continue

                if eq_name not in resumen:
                    resumen[eq_name] = {
                        "tries": 0,
                        "tries_penales": 0,
                        "goals_convertidos": 0,
                        "goals_errados": 0,
                        "penales": 0,
                        "drops": 0,
                        "puntos": 0,
                    }

                if tipo_evento == "TRY" and "TRY" in tantos:
                    if tipo_especial == "PENAL":
                        resumen[eq_name]["tries_penales"] += 1
                        resumen[eq_name]["puntos"] += 7
                    else:
                        resumen[eq_name]["tries"] += 1
                        resumen[eq_name]["puntos"] += 5

                elif tipo_evento == "GOAL" and "GOAL" in tantos:
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["goals_convertidos"] += 1
                        resumen[eq_name]["puntos"] += 2
                    elif resultado == "ERRADO":
                        resumen[eq_name]["goals_errados"] += 1

                elif tipo_evento == "PENALTY KICK":
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["penales"] += 1
                        resumen[eq_name]["puntos"] += 3

                elif tipo_evento == "DROP":
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["drops"] += 1
                        resumen[eq_name]["puntos"] += 3

        # === Mostrar en dos columnas ===
        if resumen:
            col1, col2 = st.columns(2)
            columnas = [col1, col2]
            for i, (eq, stats) in enumerate(resumen.items()):
                with columnas[i % 2]:
                    st.subheader(f"🏉 {eq}")
                    st.markdown(f"**Puntos totales:** {stats['puntos']}")
                    st.markdown(f"- Tries comunes: {stats['tries']}")
                    st.markdown(f"- Tries penales: {stats['tries_penales']}")
                    st.markdown(f"- Goals convertidos: {stats['goals_convertidos']}")
                    st.markdown(f"- Goals errados: {stats['goals_errados']}")
                    st.markdown(f"- Penales: {stats['penales']}")
                    st.markdown(f"- Drops: {stats['drops']}")
                    st.markdown("---")
        else:
            st.warning("No se encontraron eventos válidos en el archivo.")

    except json.JSONDecodeError:
        st.error("❌ Error al leer el archivo. Asegúrate de que sea un JSON válido.")
else:
    st.info("Por favor, subí un archivo JSON para procesar.")
