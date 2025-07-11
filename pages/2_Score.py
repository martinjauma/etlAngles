import streamlit as st
import json
from datetime import timedelta
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

st.title("📊 Resumen de Puntos - Partido de Rugby")

uploaded_file = st.file_uploader("📁 Sube el archivo JSON de Timeline", type="json")

def convertir_a_hora_minuto_segundos(segundos):
    """Convierte el tiempo en segundos a formato hh:mm:ss.00"""
    # Convertimos a formato hh:mm:ss
    tiempo = str(timedelta(seconds=segundos))
    # Aseguramos que esté en el formato adecuado, añadiendo milisegundos
    horas, minutos, segundos = tiempo.split(":")
    segundos, milisegundos = segundos.split(".")
    # Reagregamos milisegundos al final
    return f"{horas}:{minutos}:{segundos}.{milisegundos[:2]}"

if uploaded_file:
    try:
        data = json.load(uploaded_file)

        resumen = {}
        timeline = []

        for row in data.get("rows", []):
            tipo_evento = row.get("row_name", "")
            for clip in row.get("clips", []):
                eq_name = None
                tantos = []
                resultado = None
                tipo_especial = None
                tiempo = clip.get("time_start", 0)

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

                punto_sumado = False
                icono = ""

                if tipo_evento in ["TRY", "TRY PENAL"]:
                    if tipo_evento == "TRY PENAL" or tipo_especial == "PENAL":
                        resumen[eq_name]["tries_penales"] += 1
                        resumen[eq_name]["puntos"] += 7
                        punto_sumado = True
                        icono = "🟥🏉"
                    else:
                        resumen[eq_name]["tries"] += 1
                        resumen[eq_name]["puntos"] += 5
                        punto_sumado = True
                        icono = "🏉"

                elif tipo_evento == "GOAL" and "GOAL" in tantos:
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["goals_convertidos"] += 1
                        resumen[eq_name]["puntos"] += 2
                        punto_sumado = True
                        icono = "🎯"
                    elif resultado == "ERRADO":
                        resumen[eq_name]["goals_errados"] += 1

                elif tipo_evento == "PENALTY KICK":
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["penales"] += 1
                        resumen[eq_name]["puntos"] += 3
                        punto_sumado = True
                        icono = "🥅"

                elif tipo_evento == "DROP":
                    if resultado == "CONVERTIDO":
                        resumen[eq_name]["drops"] += 1
                        resumen[eq_name]["puntos"] += 3
                        punto_sumado = True
                        icono = "💥"

                if punto_sumado:
                    timeline.append({
                        "tiempo": tiempo,
                        "equipo": eq_name,
                        "evento": tipo_evento,
                        "resultado": resultado,
                        "icono": icono
                    })

        # === Mostrar resumen por equipo ===
        st.subheader("📌 Estadísticas por equipo")
        col1, col2 = st.columns(2)
        columnas = [col1, col2]
        for i, (eq, stats) in enumerate(resumen.items()):
            with columnas[i % 2]:
                st.markdown(
                    f"<h3 style='color:#4CAF50'>🏆 {eq} — {stats['puntos']} puntos</h3>",
                    unsafe_allow_html=True
                )
                with st.expander("Ver detalle", expanded=False):
                    st.markdown(f"- Tries comunes: {stats['tries']}")
                    st.markdown(f"- Tries penales: {stats['tries_penales']}")
                    st.markdown(f"- Goals convertidos: {stats['goals_convertidos']}")
                    st.markdown(f"- Goals errados: {stats['goals_errados']}")
                    st.markdown(f"- Penales: {stats['penales']}")
                    st.markdown(f"- Drops: {stats['drops']}")

        # === Mostrar línea de tiempo ===
        st.subheader("⏱️ Línea de Tiempo de Eventos con Puntos")
        timeline.sort(key=lambda x: x["tiempo"])
        equipos = list(resumen.keys())
        if len(equipos) < 2:
            equipos = [equipos[0], "OTRO"]

        left, center, right = st.columns([4, 1, 4])
        with left:
            st.markdown("### " + equipos[0])
        with center:
            st.markdown("### ⏳")
        with right:
            st.markdown("### " + equipos[1])

        for evento in timeline:
            with st.container():
                left, center, right = st.columns([4, 1, 4])
                tiempo = convertir_a_hora_minuto_segundos(evento["tiempo"])
                texto = f"{evento['icono']} {evento['evento']} ({evento['resultado']})" if evento['resultado'] else f"{evento['icono']} {evento['evento']}"

                if evento["equipo"] == equipos[0]:
                    with left:
                        st.markdown(f"**{tiempo}** — {texto}")
                    with center:
                        st.markdown("⬤")
                    with right:
                        st.markdown("")
                else:
                    with left:
                        st.markdown("")
                    with center:
                        st.markdown("⬤")
                    with right:
                        st.markdown(f"{texto} — **{tiempo}**")

    except json.JSONDecodeError:
        st.error("❌ Error al leer el archivo. Asegúrate de que sea un JSON válido.")
else:
    st.info("Por favor, subí un archivo JSON para procesar.")
