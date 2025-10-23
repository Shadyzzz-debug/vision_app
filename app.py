import streamlit as st
import base64
import json
import requests # Requerido para la llamada HTTP
import time

# --- Configuraciones del LLM para el entorno ---
GEMINI_CHAT_MODEL = "gemini-2.5-flash-preview-09-2025" 
# La clave se leerá desde el input.

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


# --- Funciones de Utilidad (Uso de 'requests' para la API de Gemini) ---

def safe_fetch_request(url, api_key, method='POST', headers=None, body=None, max_retries=3, delay=1):
    """Realiza llamadas a la API con reintentos y retroceso exponencial usando 'requests'."""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    # Agregar la clave API a la URL
    url_with_key = f"{url}?key={api_key}"
    
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url_with_key, headers=headers, data=body, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            else:
                error_detail = response.text if response.text else f"Código de estado: {response.status_code}"
                raise Exception(f"Fallo en la llamada a la API ({response.status_code}). {error_detail}")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            raise Exception(f"Error de red/conexión: {e}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            raise e
    raise Exception("Llamada a la API fallida después de múltiples reintentos.")


def get_gemini_vision_answer(base64_image: str, mime_type: str, user_prompt: str, api_key: str) -> str:
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
    
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_CHAT_MODEL}:generateContent"

    response_data = safe_fetch_request(apiUrl, api_key, body=json.dumps(payload))
    
    # Manejo de la respuesta
    candidate = response_data.get('candidates', [{}])[0]
    text = candidate.get('content', {}).get('parts', [{}])[0].get('text', None)

    if text:
        return text
    
    # Revisar si hay un mensaje de error explícito de la API
    error_message = response_data.get('error', {}).get('message', 'Respuesta incompleta o vacía del Oráculo.')
    raise Exception(f"Fallo de la Visión Arcana: {error_message}")


# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


# --- Streamlit App Setup ---
st.set_page_config(page_title="El Ojo del Arcano", layout="centered", initial_sidebar_state="collapsed")
st.title("👁️ El Ojo del Arcano: Visión de Reliquias")
st.markdown("---")

# Input para la API Key (Sello Arcano)
ke = st.text_input('Ingresa el Sello Arcano (Clave API)', type="password", key="api_key_upload_input")
if not ke:
    st.info("Introduce el Sello Arcano para dotar de Visión al Ojo.")


# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Consagrar la Reliquia Visual (Subir Imagen)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    st.subheader("Reliquia Consagrada")
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Invocar Profundización de Análisis", value=False)

additional_details = ""
if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Dicta la Pregunta Específica sobre la Reliquia:",
        placeholder="Ej: Describe la arquitectura de este templo antiguo con detalle arcano.",
        disabled=not show_details,
        key="context_area_upload"
    )

# Button to trigger the analysis
analyze_button = st.button("Abre el Ojo del Arcano (Analizar Reliquia)", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and analyze_button:
    
    if not ke:
        st.warning("El Sello Arcano es obligatorio para invocar la Visión. Por favor, ingrésalo.")
        st.stop()

    with st.spinner("El Ojo del Arcano está interpretando los grabados dimensionales..."):
        try:
            # 1. Preparar la Reliquia (Codificación Base64)
            # Rebobinar el archivo antes de codificarlo
            uploaded_file.seek(0)
            base64_image = encode_image(uploaded_file)
            mime_type = uploaded_file.type # Usar el tipo de archivo original

            # 2. Construir el Conjuro (Prompt)
            prompt_text = ("Describe lo que ves en esta reliquia visual (imagen) en español, con un tono solemne y formal.")
            
            if show_details and additional_details:
                prompt_text += (
                    f"\n\n**INSTRUCCIÓN DE PROFUNDIZACIÓN INVOCADA:** {additional_details}"
                )
            
            # 3. Invocar la Visión
            response = get_gemini_vision_answer(base64_image, mime_type, prompt_text, ke)
            
            # 4. Mostrar la Revelación
            st.markdown("### 📜 La Revelación del Oráculo:")
            st.markdown(response)
            
        except Exception as e:
            st.error(f"Fallo en la Invocación. El Ojo no pudo abrirse: {e}")
            
else:
    # Advertencia si falta la imagen y se presiona el botón
    if uploaded_file is None and analyze_button:
        st.warning("Por favor, consagra una Reliquia Visual para su análisis.")
