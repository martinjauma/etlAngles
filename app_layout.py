
import streamlit as st

# Fila superior con dos columnas: A y B
col1, col2 = st.columns(2)

with col1:
    st.subheader("Resumen General (Imagen A)")
    # Aquí va el contenido correspondiente a la imagen A (resumen general)
    # st.metric(), st.write(), st.image(), etc.

with col2:
    st.subheader("Detalle / Tabla (Imagen B)")
    # Aquí va el contenido correspondiente a la imagen B (tabla de datos, detalles, etc.)

# Fila inferior con ancho completo: C
st.subheader("Gráfico / Visualización (Imagen C)")
# Aquí va el contenido correspondiente a la imagen C (gráfico circular, donut, etc.)
