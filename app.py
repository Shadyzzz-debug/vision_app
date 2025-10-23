import streamlit as st
import base64
import json
import time

# --- Configuraciones del LLM para el entorno ---
# Usamos la API de Gemini (disponible internamente) para la generación de respuestas.
GEMINI_CHAT_MODEL = "gemini-2.5-flash-preview-09-2025" 
API_KEY = "" # Clave dejada vacía para que sea provista por el entorno de Canvas

# --- CSS GÓTICO (Paleta Arcano-Escarlata) ---
gothic_css = """
<style>
/* Paleta base: Fondo #111111, Texto #E0E0E0 (Pergamino ligero), Acento #5A4832 (Bronce/Metal), Sangre #A50000 */
.stApp {
    background-color: #111111;
    color: #E0E0E0;
    font-family: 'Georgia', serif;
}

/* Título Principal (h1) */
h1 {
    color: #A50000; /* Rojo sangre */
    text-shadow: 3px 3px 8px #000000;
    font-size: 3.2em; 
    border-bottom: 5px solid #5A4832; /* Borde Bronce */
    padding-bottom: 10px;
    margin-bottom: 30px;
    text-align: center;
    letter-spacing: 2px;
}

/* Subtítulos (h2, h3): Énfasis en el bronce */
h2, h3 {
    color: #C0C0C0; /* Plata/gris claro */
    border-left: 5px solid #5A4832;
    padding-left: 10px;
    margin-top: 25px;
}

/* Input y TextArea (Pergamino de Inscripción) */
div[data-testid="stTextInput"], div[data-testid="stTextarea"], .stFileUploader, .stCameraInput {
    background-color: #1A1A1A;
    border: 1px solid #5A4832;
    padding: 10px;
    border-radius: 5px;
    color: #F5F5DC;
}

/* Botones (Sellos de Invocación) */
.stButton>button {
    background-color: #5A4832; /* Bronce Oscuro */
    color: #E0E0E0;
    border: 2px solid #A50000; /* Borde de Sangre */
    padding: 10px 20px;
    font-weight: bold;
    border-radius: 8px;
    transition: all 0.3s;
    box-shadow: 0 4px #2D2418;
}

.stButton>button:hover {
    background-color: #6C5B49;
    box-shadow: 0 6px #1A1A1A;
    transform: translateY(-2px);
}

.stButton>button:active {
    box-shadow: 0 2px #1A1A1A;
    transform: translateY(2px);
}

/* Toggle (Mecanismo Secreto) */
.stCheckbox, .stRadio, .stSelectbox {
    color: #C0C0C0;
}

/* Texto de Alertas (Revelaciones) */
.stSuccess { background-color: #20251B; color: #F5F5DC; border-left: 5px solid #5A4832; }
.stInfo { background-color: #1A1A25; color: #F5F5DC; border-left: 5px solid #5A4832; }
.stWarning { background-color: #352A1A; color: #F5F5DC; border-left: 5px solid #A50000; }
.stError { background-color: #4A1A1A; color: #F5F5DC; border-left: 5px solid #A50000; }

/* Placeholder para la respuesta */
div[data-testid="stMarkdownContainer"] {
    background-color: #1A1A1A;
    padding: 20px;
    border: 1px solid #5A4832;
    border-radius: 5px;
}
</style>
"""
st.markdown(gothic_css, unsafe_allow_html=True)


# --- Funciones de Utilidad (Uso de st.legacy_fetch para la API de Gemini) ---

def safe_fetch(url, method='POST', headers=None, body=None, max_retries=3, delay=1):
    """Realiza llamadas a la API con reintentos y retroceso exponencial usando st.legacy_fetch."""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    for attempt in range(max_retries):
        try:
            # Usar st.legacy_fetch (síncrona)
            response = st.legacy_fetch(url, method=method, headers=headers, body=body)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            else:
                error_detail = response.text if response.text else f"Código de estado: {response.status_code}"
                raise Exception(f"Fallo en la llamada a la API. {error_detail}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            raise e
    raise Exception("Llamada a la API fallida después de múltiples reintentos.")


def get_gemini_vision_answer(base64_image: str, mime_type: str, user_prompt: str) -> str:
    """Invoca la API de Gemini para análisis de visión."""
    
    # Construcción del payload
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    }
    
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_CHAT_MODEL}:generateContent?key={API_KEY}"

    response_data = safe_fetch(apiUrl, body=json.dumps(payload))
    
    # Manejo de la respuesta
    candidate = response_data.get('candidates', [{}])[0]
    text = candidate.get('content', {}).get('parts', [{}])[0].get('text', None)

    if text:
        return text
    
    # Revisar si hay un mensaje de error explícito de la API
    error_message = response_data.get('error', {}).get('message', 'Respuesta incompleta o vacía del Oráculo.')
    raise Exception(f"Fallo de la Visión Arcana: {error_message}")


# --- Streamlit App Setup ---

# La clave de API de OpenAI es reemplazada por el Sello Arcano de acceso
st.title("👁️ El Ojo del Arcano: Análisis de Reliquias Visuales")
st.markdown("---")

# Input para la API Key (Sello Arcano)
ke = st.text_input('Ingresa el Sello Arcano (Clave API)', type="password", key="api_key_input")
# NOTE: En este entorno simulado, si 'ke' se proporciona, se asume que se usa para 'API_KEY'. 
# Para la llamada real a Gemini en Canvas, la variable `API_KEY` se dejará vacía.
if ke:
    pass # Simulamos que la clave se aplica al entorno.
else:
    st.info("Introduce el Sello Arcano para dotar de Visión al Ojo.")


# File uploader (Reliquia Visual)
uploaded_file = st.file_uploader("Consagra la Reliquia Visual (Carga una imagen)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Reliquia Consagrada", expanded = True):
        st.image(uploaded_file, caption=f"Reliquia: {uploaded_file.name}", use_container_width=True)

# Toggle para la pregunta específica (Invocación de Contexto)
show_details = st.toggle("Invocar Contexto Específico", value=False)

additional_details = ""
if show_details:
    # Text input para detalles adicionales
    additional_details = st.text_area(
        "Dicta la Pregunta Específica (Contexto de la Reliquia):",
        placeholder="Ej: Describe la arquitectura del edificio en el centro de esta reliquia...",
        disabled=not show_details,
        key="context_area"
    )

# Button to trigger the analysis (Apertura del Ojo)
analyze_button = st.button("Abre el Ojo del Arcano (Analizar)", type="secondary")

# Check if conditions are met
if uploaded_file is not None and analyze_button:
    # El Sello Arcano (ke) no es estrictamente necesario si el Canvas provee la API Key,
    # pero advertimos si el usuario no la ingresó.
    if not ke:
        st.warning("El Sello Arcano es obligatorio para invocar la Visión. Por favor, ingrésalo.")
        st.stop()
        
    with st.spinner("El Ojo del Arcano se está abriendo..."):
        try:
            # 1. Preparar la Reliquia (Codificación Base64)
            file_bytes = uploaded_file.getvalue()
            base64_image = base64.b64encode(file_bytes).decode("utf-8")
            mime_type = uploaded_file.type

            # 2. Construir el Conjuro (Prompt)
            prompt_text = "Describe detalladamente lo que observas en esta imagen. Responde en español y mantén un tono solemne y descriptivo."
            
            if show_details and additional_details:
                prompt_text += (
                    f"\n\n**CONTEXTO ESPECÍFICO INVOCADO:** {additional_details}"
                )
            
            # 3. Invocar la Visión
            # Usamos una función simple en lugar de streaming para simplificar el reemplazo
            response = get_gemini_vision_answer(base64_image, mime_type, prompt_text)
            
            # 4. Mostrar la Revelación
            st.markdown("### 📜 La Revelación del Oráculo:")
            st.markdown(response)
            
        except Exception as e:
            st.error(f"Fallo en la Invocación. El Ojo no pudo abrirse: {e}")
            
else:
    # Mensajes de estado
    if analyze_button:
        if not uploaded_file:
            st.warning("Consagra primero una Reliquia Visual (carga una imagen).")
