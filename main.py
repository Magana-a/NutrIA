# Importa las librerías necesarias para la aplicación
import os
import sys
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Asegura que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from asistente import NutrIA

# Carga las variables de entorno
load_dotenv()

# Define las rutas para guardar el registro nutricional
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DIARIO = os.path.join(DIRECTORIO_BASE, "nutritional_diary.txt")

# Define la clase para gestionar el diario nutricional
class DiarioNutricional:
    # Inicializa la clase y carga los datos existentes
    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.datos = self.cargar_diario()

    # Método para extraer el valor de los macronutrientes usando expresiones regulares
    def parse_macro(self, pattern, text):
        match = re.search(pattern, text)
        return float(match.group(1)) if match else 0.0

    # Método para leer el archivo de texto y cargar el historial en un diccionario
    def cargar_diario(self):
        diario = {}
        if not os.path.exists(self.ruta_archivo):
            return diario

        with open(self.ruta_archivo, "r", encoding="utf-8-sig") as f:
            fecha_actual = None
            for linea in f:
                linea = linea.strip()
                if not linea: 
                    continue
                
                if linea.startswith("DATE:"):
                    fecha_actual = linea.replace("DATE:", "").strip()
                    if fecha_actual not in diario:
                        diario[fecha_actual] = []
                        
                elif linea.startswith("-") and fecha_actual:
                    try:
                        partes = linea[1:].split("|", 1)
                        item_str = partes[0].strip()
                        macros_str = partes[1].strip() if len(partes) > 1 else "Cals: 0, Carbs: 0, Protein: 0, Fat: 0"
                        
                        cat_alimento = item_str.split("]", 1)
                        categoria = cat_alimento[0].replace("[", "").strip()
                        alimento = cat_alimento[1].strip() if len(cat_alimento) > 1 else "Unknown"
                        
                        cals = self.parse_macro(r"Cals:\s*([\d\.]+)", macros_str)
                        carbs = self.parse_macro(r"Carbs:\s*([\d\.]+)", macros_str)
                        prot = self.parse_macro(r"Protein:\s*([\d\.]+)", macros_str)
                        fat = self.parse_macro(r"Fat:\s*([\d\.]+)", macros_str)
                        
                        diario[fecha_actual].append({
                            "categoria": categoria,
                            "alimento": alimento,
                            "calories": cals,
                            "carbs": carbs,
                            "protein": prot,
                            "fat": fat
                        })
                    except Exception as e:
                        st.error(f"Error reading history line: {linea}. Details: {e}") 
        return diario

    # Método para escribir y guardar los datos actuales en el archivo de texto
    def guardar_diario(self):
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            for fecha, comidas in sorted(self.datos.items(), reverse=True):
                if not comidas:
                    continue
                    
                f.write(f"DATE: {fecha}\n")
                
                total_cals = sum(c.get('calories', 0) for c in comidas)
                total_carbs = sum(c.get('carbs', 0) for c in comidas)
                total_prot = sum(c.get('protein', 0) for c in comidas)
                total_fat = sum(c.get('fat', 0) for c in comidas)
                
                f.write(f"TOTALS | Cals: {total_cals:.1f} | Carbs: {total_carbs:.1f}g | Protein: {total_prot:.1f}g | Fat: {total_fat:.1f}g\n")
                
                for item in comidas:
                    cals = item.get('calories', 0)
                    carbs = item.get('carbs', 0)
                    prot = item.get('protein', 0)
                    fat = item.get('fat', 0)
                    
                    if cals == 0 and carbs == 0 and prot == 0 and fat == 0:
                        f.write(f"- [{item['categoria']}] {item['alimento']}\n")
                    else:
                        f.write(f"- [{item['categoria']}] {item['alimento']} | Cals: {cals}, Carbs: {carbs}, Protein: {prot}, Fat: {fat}\n")
                f.write("\n")

    # Método para borrar un alimento específico de una fecha
    def eliminar_comida(self, fecha: str, index: int):
        if fecha in self.datos and 0 <= index < len(self.datos[fecha]):
            del self.datos[fecha][index]
            if not self.datos[fecha]:
                del self.datos[fecha]
            self.guardar_diario()


# Configura las propiedades básicas de la página
st.set_page_config(
    page_title="NutrIA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyecta los estilos visuales para la interfaz
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Título principal */
.nutria-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    color: #16a34a;
    text-align: center;
    margin-bottom: 0.2rem;
    line-height: 1.1;
}

.nutria-sub {
    text-align: center;
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* Tarjetas de macros */
.macro-card {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1.5px solid #86efac;
    border-radius: 14px;
    padding: 1.1rem;
    text-align: center;
}
.macro-val {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #15803d;
    display: block;
}
.macro-lbl {
    font-size: 0.78rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Burbuja chat usuario */
.bubble-user {
    background: #16a34a;
    color: white;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.4rem 0 0.4rem auto;
    max-width: 78%;
    width: fit-content;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* Burbuja chat IA */
.bubble-ia {
    background: #f9fafb;
    border: 1px solid #d1fae5;
    color: #111827;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.4rem auto 0.4rem 0;
    max-width: 82%;
    width: fit-content;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Botones */
.stButton > button, .stFormSubmitButton > button {
    background: #16a34a !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.45rem 1.4rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #15803d !important;
    box-shadow: 0 3px 10px rgba(22,163,74,0.3) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
}

/* Input */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border-color: #86efac !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 40px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    font-weight: 500 !important;
}

hr { border-color: #d1fae5; }
</style>
""", unsafe_allow_html=True)


# Inicializa las variables en el estado de la sesión para preservar la información
def init_estado():
    if "gestor_diario" not in st.session_state:
        st.session_state.gestor_diario = DiarioNutricional(ARCHIVO_DIARIO)
    if "asistente" not in st.session_state:
        st.session_state.asistente = NutrIA()
    if "chat_historial" not in st.session_state:
        st.session_state.chat_historial = [{"rol": "ia", "texto": "Hello! I'm NutrIA. How can I help you today?"}]
    if "ultimo_registro" not in st.session_state:
        st.session_state.ultimo_registro = None


# Construye el panel lateral con el resumen del día actual
def sidebar():
    with st.sidebar:
        # Muestra el logo en el panel lateral reduciendo su tamaño
        st.image("nutrialogo.png", width=150)
        st.caption("Intelligent nutrition assistant")
        st.markdown("---")

        hoy = datetime.now().strftime("%Y-%m-%d")
        diario = st.session_state.gestor_diario.datos
        if hoy in diario and diario[hoy]:
            comidas_hoy = diario[hoy]
            total_cals = sum(c.get('calories', 0) for c in comidas_hoy)
            total_prot = sum(c.get('protein', 0) for c in comidas_hoy)
            st.markdown(f"** Today ({hoy})**")
            st.success(f" {total_cals:.0f} kcal  |   {total_prot:.0f}g prot")
            st.caption(f"{len(comidas_hoy)} food(s) logged")
        else:
            st.info("No logs for today yet.")

        st.markdown("---")
        st.markdown("<small style='color:#9ca3af'>FatSecret API + Groq AI</small>", unsafe_allow_html=True)


# Crea la pestaña encargada de buscar y guardar nuevos alimentos
def tab_registrar():
    st.markdown(" Log Meals")

    fecha = st.date_input("Date")
    fecha_str = fecha.strftime("%Y-%m-%d")

    st.markdown("---")
    st.markdown("Search on FatSecret")

    # Formulario para habilitar la búsqueda con la tecla Enter
    with st.form("form_busqueda"):
        col1, col2 = st.columns([4, 1])
        with col1:
            alimento = st.text_input("Food name", placeholder="Ex: Burrito, Apple, Grilled Chicken...", label_visibility="collapsed")
        with col2:
            buscar = st.form_submit_button("Search", use_container_width=True)

    if buscar and alimento.strip():
        alimento_str = alimento.strip()
        
        if not any(c.isalpha() for c in alimento_str):
            st.warning("Please enter a valid food name containing letters, not just numbers or symbols.")
        elif len(alimento_str) == 1:
            st.warning(f"Specific food '{alimento_str}' not found. Please provide a more complete name instead of a single letter.")
        else:
            with st.spinner(f"Consulting FatSecret + NutrIA for '{alimento_str}'..."):
                try:
                    datos = st.session_state.asistente.consultar(alimento_str)
                    st.session_state.ultimo_registro = {
                        "fecha": fecha_str,
                        "alimento": alimento_str,
                        "datos": datos,
                    }
                except Exception as e:
                    st.error(f"Error consulting: {e}")
                    return

    if st.session_state.ultimo_registro:
        reg = st.session_state.ultimo_registro
        datos = reg["datos"]

        st.markdown("---")
        st.markdown(f"#### Result for: **{reg['alimento']}**")

        st.info(f" **NutrIA:** {datos.get('explanation', 'No explanation available.')}")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="macro-card"><span class="macro-val"> {datos.get("calories", 0):.0f}</span><span class="macro-lbl">kcal</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="macro-card"><span class="macro-val"> {datos.get("carbs", 0):.1f}g</span><span class="macro-lbl">Carbs</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="macro-card"><span class="macro-val"> {datos.get("protein", 0):.1f}g</span><span class="macro-lbl">Protein</span></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="macro-card"><span class="macro-val"> {datos.get("fat", 0):.1f}g</span><span class="macro-lbl">Fat</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_g, col_c = st.columns([1, 1])
        with col_g:
            if st.button(f" Save '{reg['alimento']}' to diary", use_container_width=True):
                if reg["fecha"] not in st.session_state.gestor_diario.datos:
                    st.session_state.gestor_diario.datos[reg["fecha"]] = []
                
                st.session_state.gestor_diario.datos[reg["fecha"]].append({
                    "categoria": "API Search",
                    "alimento": reg["alimento"],
                    "calories": datos.get('calories', 0),
                    "carbs": datos.get('carbs', 0),
                    "protein": datos.get('protein', 0),
                    "fat": datos.get('fat', 0),
                })
                st.session_state.gestor_diario.guardar_diario()
                st.session_state.ultimo_registro = None
                st.success(f" '{reg['alimento']}' saved to the diary on {reg['fecha']}.")
                st.rerun()
        with col_c:
            if st.button("Cancel", use_container_width=True):
                st.session_state.ultimo_registro = None
                st.rerun()


# Crea la pestaña para mostrar los registros guardados organizados por fecha
def tab_historial():
    st.markdown("Nutritional History")

    diario = st.session_state.gestor_diario.datos

    if not diario:
        st.info("Your history is empty. Start logging your meals!")
        return

    for fecha, comidas in sorted(diario.items(), reverse=True):
        if not comidas:
            continue

        total_cals  = sum(c.get('calories', 0) for c in comidas)
        total_carbs = sum(c.get('carbs', 0) for c in comidas)
        total_prot  = sum(c.get('protein', 0) for c in comidas)
        total_fat   = sum(c.get('fat', 0) for c in comidas)

        with st.expander(f" {fecha}  —  {total_cals:.0f} kcal  |  {total_prot:.0f}g prot", expanded=(fecha == datetime.now().strftime("%Y-%m-%d"))):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{total_cals:.0f} kcal")
            c2.metric("Carbs", f"{total_carbs:.1f} g")
            c3.metric("Protein", f"{total_prot:.1f} g")
            c4.metric("Fat", f"{total_fat:.1f} g")

            st.markdown("**Logged foods:**")
            for i, item in enumerate(comidas):
                col_text, col_btn = st.columns([0.9, 0.1])
                with col_text:
                    st.markdown(
                        f"- [{item.get('categoria', 'API Search')}] **{item.get('alimento', 'Unknown')}** — "
                        f"{item.get('calories', 0):.0f} kcal | "
                        f"Carbs: {item.get('carbs', 0):.1f}g | "
                        f"Prot: {item.get('protein', 0):.1f}g | "
                        f"Fat: {item.get('fat', 0):.1f}g"
                    )
                with col_btn:
                    if st.button("🗑️", key=f"del_{fecha}_{i}"):
                        st.session_state.gestor_diario.eliminar_comida(fecha, i)
                        st.rerun()


# Crea la pestaña de mensajería para hablar con el asistente inteligente
def tab_chat():
    st.markdown("Chat with NutrIA")
    st.caption("Ask me about nutrition, foods, diets, or healthy habits.")

    for msg in st.session_state.chat_historial:
        if msg["rol"] == "user":
            st.markdown(f'<div class="bubble-user">{msg["texto"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-ia"> {msg["texto"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_chat", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            pregunta = st.text_input(
                "Message",
                placeholder="Is avocado healthy? How much protein do I need a day?...",
                label_visibility="collapsed",
            )
        with col_btn:
            enviar = st.form_submit_button("Send", use_container_width=True)

    if enviar and pregunta.strip():
        st.session_state.chat_historial.append({"rol": "user", "texto": pregunta})
        with st.spinner("NutrIA is thinking..."):
            try:
                respuesta = st.session_state.asistente.preguntar(pregunta)
            except Exception as e:
                respuesta = f" Error connecting to AI: {e}"
        st.session_state.chat_historial.append({"rol": "ia", "texto": respuesta})
        st.rerun()

    if len(st.session_state.chat_historial) > 1:
        if st.button("Clear conversation"):
            st.session_state.chat_historial = [{"rol": "ia", "texto": "Hello! I'm NutrIA. How can I help you today?"}]
            if hasattr(st.session_state.asistente, 'limpiar_historial'):
                st.session_state.asistente.limpiar_historial()
            st.rerun()


# Define el flujo principal de ejecución de la interfaz web
def main():
    init_estado()
    sidebar()

    # Añade un pequeño espacio en blanco para empujar el logo hacia abajo
    st.markdown("<br>", unsafe_allow_html=True)

    # Crea columnas para centrar el logo y hacer que ocupe el 25% del ancho de la pantalla
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        # Muestra la imagen del logo adaptada al ancho de esta columna más estrecha
        st.image("nutrialogo.png", use_container_width=True)

    st.markdown('<div class="nutria-sub">Your intelligent nutrition assistant · FatSecret + Groq AI</div>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Log Meals", "History", "Chat with NutrIA"])

    with tab1:
        tab_registrar()
    with tab2:
        tab_historial()
    with tab3:
        tab_chat()


# Punto de entrada para iniciar la aplicación Streamlit
if __name__ == "__main__":
    main()