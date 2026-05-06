import streamlit as st
import google.generativeai as genai
import urllib.parse
import webbrowser

# --- CONFIGURACIÓN ---
# Asegúrate de que esta API Key sea la misma que usaste para listar los modelos
if "GOOGLE_API_KEY" in st.secrets:
  API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
  API_KEY = ""
  
if API_KEY:  
  genai.configure(api_key=API_KEY)
else:
  st.error("No se encontró la Api Key de Google.")
  
st.set_page_config(page_title="Reclutador Pro v2026", layout="centered")

st.title("🤖 Reclutador Inteligente")
st.markdown("By Maomeno")

with st.form("search_form"):
    puesto = st.text_input("¿Qué perfil buscas?", placeholder="Ej: Especialista en Ciberseguridad")
    skills = st.text_input("Skills o requisitos", placeholder="Ej: CISSP, Python, Remoto")
    ubicacion = st.text_input("Ubicación", placeholder="Ej: Cancún")
    experiencia = st.number_input("Años mínimos de experiencia (opcional)", min_value=0, max_value=40, value=0)
    
    # Campo de Job Description (Área de texto grande)
    jd = st.text_area("Job Description (Opcional)", height=250, 
                      placeholder="Pega aquí la Job Description (Opcional).")
    
    submit = st.form_submit_button("Buscar")

if submit:
    if not ubicacion or (not puesto and not jd):
        st.error("Es obligatorio ingresar la ubicación y al menos el puesto o la Job Description.")
    else:
        # Prompt optimizado para la serie Gemini 3
        prompt_texto = f"""
        Actúa como un experto en Sourcing. Crea una query de Google (X-Ray) para perfiles de LinkedIn.
        
        CRITERIOS:
        - Puesto: {puesto}
        - Skills: {skills}
        - Ubicación: {ubicacion}
        - Mínimo de experiencia: {experiencia} años
        - Job Description proporcionada: {jd if jd else "N/A"}
        
        REGLAS:
        1. Empieza con site:linkedin.com/in/
        2. Si hay una Job Description, analiza los requisitos clave y mézclalos con el puesto y skills para crear una query robusta.
        3. Si la experiencia es > 0, intenta incluir términos como "{experiencia}..15 years" o variaciones que sugieran antigüedad o términos como "Senior" o "Lead".
        4. Si la experienca es 0 no añadas filtros de años. 
        5. Usa operadores booleanos (AND, OR, NOT) y comillas para términos exactos. 
        6. Usa sinónimos en español e inglés.
        7. Devuelve ÚNICAMENTE la cadena de búsqueda.
        """
        
        with st.spinner("Consultando datos..."):
            try:
                # Usamos el modelo que aparece en tu lista (índice 16)
                model = genai.GenerativeModel('Gemini 2.5 Flash-Lite')
                response = model.generate_content(prompt_texto)
                
                query_final = response.text.strip().replace("`", "")
                
                # Limpiar cualquier residuo de texto que no sea la query
                if "site:linkedin.com/in/" in query_final:
                    requisitos_url = urllib.parse.quote(f"{puesto}|{ubicacion}|{skills}")
                    url_google = f"https://www.google.com/search?q={urllib.parse.quote(query_final)}&reclutador_pro={requisitos_url}"
                    # url_google = f"https://www.google.com/search?q={urllib.parse.quote(query_final)}"
                    webbrowser.open_new_tab(url_google)
                    st.success("¡Búsqueda generada con éxito!")
                    st.code(query_final, language="text")
                    st.link_button("VER CANDIDATOS", url_google, type="primary", use_container_width=True)
                else:
                    st.warning("Se generó una respuesta inesperada. Intenta ser más específico.")
                    st.write(query_final) # Para ver qué respondió la IA
                
            except Exception as e:
                st.error(f"Error técnico con el modelo de IA: {e}")

st.divider()
