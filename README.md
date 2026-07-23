# 📊 Analisis de finanzas (COPITO DE NIEVE).

Es una aplicación web interactiva desarrollada con **Streamlit**, **LangChain** y **Google Gemini** que permite cargar archivos CSV, explorar visualizaciones de datos automáticas y realizar consultas sobre los datos utilizando lenguaje natural ejecutado dinámicamente con Python.

---

## 🏗️ Arquitectura

El flujo de trabajo de la aplicación se divide en las siguientes etapas principales:

1. **Carga y Preparación de Datos:** El usuario sube un archivo `.csv`. Pandas procesa la información, extrae el esquema, tipos de datos y estadísticas descriptivas básicas.
2. **Visualización Exploratoria:** Generación automática de histogramas, mapas de correlación de Pearson y gráficos categóricos usando Plotly Express.
3. **Módulo Conversacional (LLM):** - El esquema del DataFrame y la pregunta del usuario se envían a Gemini mediante LangChain.
* La IA genera un script de Python puro que almacena el resultado en la variable `result`.


4. **Ejecución Dinámica:** El código generado se evalúa de manera local (`exec`) sobre el DataFrame real y el resultado (tabla, gráfico interactivo o texto) se despliega en la interfaz del chat.



```

[ Usuario ] ──> [ Interfaz Streamlit ]
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[ Renderizado de Gráficos ]     [ Generador de Código (LLM) ]
    (Plotly Express)              (LangChain + Gemini API)
                                          │
                                          ▼
                                [ Evaluación Python (exec) ]
                                          │
                                          ▼
                                [ Resultado en Chat UI ]

```

---

## 🛠️ Tecnologías utilizadas

* **Framework Web:** [Streamlit](https://streamlit.io/)
* **Modelos de IA / Orquestación:** [LangChain](https://www.langchain.com/), `langchain-google-genai` (Modelo: `gemini-3.1-flash-lite`)
* **Procesamiento de Datos:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Visualización de Datos:** [Plotly Express](https://plotly.com/python/plotly-express/)
* **Gestión de Entorno:** `python-dotenv`

---

## 💻 Instrucciones de instalación

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

```

### 2. Crear y activar un entorno virtual

```bash
# En Linux / macOS
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate

```

### 3. Instalar las dependencias

```bash
pip install streamlit pandas plotly numpy langchain-google-genai python-dotenv

```

### 4. Configurar la API Key de Google

Crea un archivo llamado `.env` en la raíz de tu proyecto e incluye tu API Key de Google AI:

```env
GOOGLE_API_KEY=tu_api_key_de_gemini_aqui

```

### 5. Ejecutar la aplicación

```bash
streamlit run app.py

```

---

### ❓ Preguntas sobre las Ventas y Rendimiento

* `¿Cuál fue el total general de ingresos por ventas ($ USD) registrados durante el mes de julio?`
* `¿Cuál es el producto del menú que generó mayores ingresos totales ($ USD)?`
* `¿Cuál es la categoría de menú más vendida en términos de cantidad de unidades (Cantidad)?`
* `Genera un gráfico del total general de ingresos por ventas ($ USD) registrados durante el mes de julio`

---

### 💬 Ejemplos de Respuestas

> **Pregunta:** `¿Cuál fue el total general de ingresos por ventas ($ USD) registrados durante el mes de julio?`  
> **Respuesta:** *El total general de ingresos por ventas en julio fue de **$552.28 USD**.*

---

> **Pregunta:** `¿Cuál es el producto del menú que generó mayores ingresos totales ($ USD)?`  
> **Respuesta:** *El producto que generó mayores ingresos fue **Arepa de carne (Combo)** con un total de **$84.00 USD**.*

---

> **Pregunta:** `¿Cuál es la categoría de menú más vendida en términos de cantidad de unidades (Cantidad)?`  
> **Respuesta:** *La categoría más vendida fue **Bebidas** con un total de **57 unidades** vendidas.*

---
