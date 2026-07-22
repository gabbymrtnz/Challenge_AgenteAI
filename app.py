import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Análisis de CSV con IA",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 20px; border-radius: 6px 6px 0 0; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Análisis de CSV con IA")
st.caption("Sube un archivo CSV, explora sus gráficos y haz preguntas en lenguaje natural.")
st.divider()

api_key = os.getenv("GOOGLE_API_KEY", "")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuración")
    if api_key:
        st.success("API Key lista ✅")
    else:
        st.error("GOOGLE_API_KEY no encontrada en el archivo .env")
    st.divider()
    st.caption("**Modelo:** gemini-3.1-flash-lite")
    st.caption("**Motor:** LangChain + Google Gemini")

# --- File upload ---
uploaded_file = st.file_uploader(
    "📁 Sube tu archivo CSV",
    type=["csv"],
    help="Formatos aceptados: .csv",
)

if uploaded_file is None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📊 Visualizaciones**\n\nHistogramas, correlaciones, barras y scatter plots interactivos generados automáticamente.")
    with col2:
        st.info("**🤖 Preguntas en lenguaje natural**\n\nHaz cualquier pregunta sobre tus datos y la IA te responderá con código Python ejecutado en tiempo real.")
    with col3:
        st.info("**📋 Exploración de datos**\n\nEstadísticas descriptivas, tipos de columnas y valores nulos de un vistazo.")
    st.stop()

# --- Load data ---
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

st.success(f"✅ **{uploaded_file.name}** — {df.shape[0]:,} filas × {df.shape[1]} columnas")

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

tab_datos, tab_graficos, tab_ia = st.tabs(["📋 Datos", "📊 Gráficos", "🤖 Preguntar a la IA"])

# =========================================================
# TAB 1 — DATOS
# =========================================================
with tab_datos:
    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Estadísticas descriptivas")
        st.dataframe(df.describe(include="all").T, use_container_width=True)
    with col_right:
        st.subheader("Columnas y tipos de datos")
        info_df = pd.DataFrame({
            "Tipo": df.dtypes.astype(str),
            "Valores únicos": df.nunique(),
            "Nulos": df.isnull().sum(),
            "% Nulos": (df.isnull().mean() * 100).round(1).astype(str) + "%",
        })
        st.dataframe(info_df, use_container_width=True)

# =========================================================
# TAB 2 — GRÁFICOS
# =========================================================
with tab_graficos:
    if not numeric_cols and not categorical_cols:
        st.warning("No se encontraron columnas para graficar.")

    # --- Histogramas numéricos ---
    if numeric_cols:
        st.subheader("🔢 Distribución de variables numéricas")
        cols_per_row = 3
        rows = [numeric_cols[i : i + cols_per_row] for i in range(0, len(numeric_cols), cols_per_row)]
        for row in rows:
            grid = st.columns(len(row))
            for col_widget, col_name in zip(grid, row):
                with col_widget:
                    fig = px.histogram(
                        df,
                        x=col_name,
                        nbins=30,
                        title=col_name,
                        color_discrete_sequence=["#4C78A8"],
                    )
                    fig.update_layout(showlegend=False, height=280, margin=dict(t=40, b=20, l=20, r=10))
                    st.plotly_chart(fig, use_container_width=True)

        # --- Heatmap de correlación ---
        if len(numeric_cols) > 1:
            st.subheader("🔥 Mapa de correlación")
            corr = df[numeric_cols].corr().round(2)
            fig_heat = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                aspect="auto",
                title="Correlación de Pearson entre variables numéricas",
            )
            fig_heat.update_layout(height=max(350, len(numeric_cols) * 50))
            st.plotly_chart(fig_heat, use_container_width=True)

    # --- Barras categóricas ---
    if categorical_cols:
        st.subheader("📊 Variables categóricas")
        display_cats = categorical_cols[:8]
        cols_per_row = 2
        rows = [display_cats[i : i + cols_per_row] for i in range(0, len(display_cats), cols_per_row)]
        for row in rows:
            grid = st.columns(len(row))
            for col_widget, col_name in zip(grid, row):
                with col_widget:
                    vc = df[col_name].value_counts().head(15).reset_index()
                    vc.columns = [col_name, "Frecuencia"]
                    fig = px.bar(
                        vc,
                        x=col_name,
                        y="Frecuencia",
                        title=col_name,
                        color_discrete_sequence=["#F58518"],
                    )
                    fig.update_layout(showlegend=False, height=300, margin=dict(t=40, b=20, l=20, r=10))
                    st.plotly_chart(fig, use_container_width=True)

    # --- Scatter plot interactivo ---
    if len(numeric_cols) >= 2:
        st.subheader("🔵 Scatter plot personalizado")
        c1, c2, c3 = st.columns(3)
        with c1:
            x_axis = st.selectbox("Eje X", numeric_cols, key="sx")
        with c2:
            y_axis = st.selectbox("Eje Y", numeric_cols, index=min(1, len(numeric_cols) - 1), key="sy")
        with c3:
            color_by = st.selectbox("Color por", ["(ninguno)"] + categorical_cols, key="sc")

        color_col = None if color_by == "(ninguno)" else color_by
        fig_scatter = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            color=color_col,
            title=f"{y_axis} vs {x_axis}",
            opacity=0.7,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# =========================================================
# TAB 3 — IA
# =========================================================
with tab_ia:
    st.subheader("🤖 Pregunta a la IA sobre tus datos")

    if not api_key:
        st.error("⚠️ No se encontró GOOGLE_API_KEY en el archivo .env. Agrégala y reinicia la app.")
        st.stop()

    # Esquema del DataFrame para enviar al LLM
    schema_info = f"""Shape: {df.shape[0]:,} filas × {df.shape[1]} columnas

Columnas y tipos:
{df.dtypes.to_string()}

Primeras 3 filas:
{df.head(3).to_string()}

Estadísticas descriptivas:
{df.describe(include='all').to_string()}
"""

    # Ejemplos rápidos
    st.caption("Ejemplos de preguntas:")
    ejemplo_cols = st.columns(3)
    examples = [
        "¿Cuántas filas tiene el dataset?",
        "¿Cuál es el promedio de cada columna numérica?",
        "¿Hay valores nulos? ¿En cuáles columnas?",
        "¿Cuál es la correlación entre las variables numéricas?",
        "¿Cuáles son los valores únicos de las columnas categóricas?",
        "Muéstrame un resumen estadístico completo.",
    ]
    for i, ex in enumerate(examples):
        with ejemplo_cols[i % 3]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["pregunta_rapida"] = ex

    st.divider()

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("code"):
                with st.expander("Ver código generado"):
                    st.code(msg["code"], language="python")
            st.markdown(msg["content"])

    # Input — puede venir de un botón de ejemplo o del chat
    prompt = st.chat_input("Haz una pregunta sobre los datos...")
    if "pregunta_rapida" in st.session_state and st.session_state["pregunta_rapida"]:
        prompt = st.session_state.pop("pregunta_rapida")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generando código y analizando datos..."):
                try:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-3.1-flash-lite",
                        google_api_key=api_key,
                        temperature=0,
                    )

                    system_prompt = f"""Tienes acceso a un DataFrame de pandas llamado `df` con el siguiente esquema:

{schema_info}

Reglas:
- Si la pregunta SE PUEDE responder con los datos: escribe código Python puro. Guarda el resultado en `result`. Disponibles: `pd` (pandas), `np` (numpy), `px` (plotly.express). No importes nada más.
- Si piden un gráfico: usa `px` para crearlo y guárdalo en `result` (ej: result = px.pie(...)).
- Si la pregunta NO tiene relación con los datos o pide información que no está en el esquema: escribe result = "una respuesta directa en texto explicando que no está en los datos".
- NUNCA uses matplotlib ni seaborn.
- Devuelve ÚNICAMENTE código Python puro. Sin explicaciones, sin markdown, sin ```.

Pregunta: {prompt}"""

                    response = llm.invoke(system_prompt)
                    content = response.content
                    if isinstance(content, list):
                        code = "".join(
                            p.get("text", "") if isinstance(p, dict) else str(p)
                            for p in content
                        )
                    else:
                        code = content
                    code = code.strip()

                    # Quitar bloques markdown si el LLM los incluye
                    code = re.sub(r'^```(?:python)?\n?', '', code)
                    code = re.sub(r'\n?```$', '', code)
                    code = code.strip()

                    # Ejecutar el código sobre el DataFrame real
                    local_vars = {}
                    exec(code, {"df": df, "pd": pd, "np": np, "px": px}, local_vars)
                    result = local_vars.get("result", "Sin resultado.")

                    # Mostrar código generado (colapsable)
                    with st.expander("Ver código generado"):
                        st.code(code, language="python")

                    # Mostrar resultado según tipo
                    import plotly.graph_objects as go
                    if isinstance(result, go.Figure):
                        st.plotly_chart(result, use_container_width=True)
                        answer = "Gráfico generado."
                    elif isinstance(result, (pd.DataFrame, pd.Series)):
                        st.dataframe(result, use_container_width=True)
                        answer = f"Resultado: {type(result).__name__} con {result.shape if hasattr(result, 'shape') else len(result)} elementos."
                    else:
                        answer = str(result)
                        st.markdown(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "code": code,
                    })

                except Exception as e:
                    err = f"**Error:** {e}"
                    st.error(err)
                    st.session_state.chat_history.append({"role": "assistant", "content": err})

    if st.session_state.chat_history:
        if st.button("🗑️ Limpiar conversación"):
            st.session_state.chat_history = []
            st.rerun()
