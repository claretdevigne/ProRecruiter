import json
import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- CONFIGURACIÓN ---
if "GOOGLE_API_KEY" in st.secrets:
  API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
  API_KEY = ""
  
if API_KEY:  
  genai.configure(api_key=API_KEY)
else:
  st.error("No se encontró la Api Key de Google.")

# INICIA APP
st.set_page_config(page_title="Pro Recruiter v2026", layout="centered")

st.title("🤖 Pro Recruiter")
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
        Actúa como un experto en Sourcing y análisis de datos.
        Analiza los siguientes parámetros de búsqueda:
        - Puesto: {puesto}
        - Skills: {skills}
        - Ubicación: {ubicacion}
        - Mínimo de experiencia: {experiencia} años
        - Job Description proporcionada: {jd if jd else "N/A"}
        
        TAREAS:
        1. Genera una query X-Ray robusta para Linkedin que empiece con site:linkedin.com/in/
        2. Identifica la región, estado o departamento de la ubicación original y devuelvemela en una lista
        3. Extrae las 5-7 skills más críticas (normalizadas) basadas en el puesto y la JD.
        4. Si hay una Job Description, analiza los requisitos clave y mézclalos con el puesto y skills para crear una query robusta.
        5. Si la experiencia es > 0, intenta incluir términos como "{experiencia}..15 years" o variaciones que sugieran antigüedad o términos como "Senior" o "Lead".
        6. Si la experienca es 0 no añadas filtros de años. 
        7. Usa operadores booleanos (AND, OR, NOT) y comillas para términos exactos. 
        8. Usa sinónimos en español e inglés.
        
        Devuelve ÚNICAMENTE UN OBJETO JSON con este formato:
        {{
          "google_query": "la cadena de búsqueda aquí",
          "ubicaciones_expandidas": ["Ciudad", "Estado/Departamento", "País"],
          "skills_extraidas": ["skill1", "skill2", "skill3"]
          }}.
        """
        
        with st.spinner("Consultando datos..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                response = model.generate_content(prompt_texto)
                
                # 1. Limpieza profesional de JSON (maneja los ```json del modelo)
                raw_text = response.text.strip()
                if "```" in raw_text:
                    raw_text = raw_text.split("```")[1].replace("json", "").strip()
                
                data_json = json.loads(raw_text)
                
                query_final = data_json.get("google_query", "")
                # Usamos los datos enriquecidos por la IA para la extensión
                lista_ubicaciones = data_json.get("ubicaciones_expandidas", [])
                lista_skills = data_json.get("skills_extraidas", [])

            except Exception as e:
              st.error(f"Error al decodificar JSON: {e}")
                
            if "site:linkedin.com/in/" in query_final:
                    # 2. Pasamos los datos ENRIQUECIDOS a la URL
                    metadatos = {
                      "puesto": puesto,
                      "ubicacion": ", ".join(lista_ubicaciones), # Ahora incluye Antioquia, etc.
                      "skills": ", ".join(lista_skills),        # Ahora incluye sinónimos de la IA
                      "reclutador_pro": "true"
                    }
                    
                    params_extension = urllib.parse.urlencode(metadatos)
                    query_encoded = urllib.parse.quote(query_final)
                    url_google = f"https://www.google.com/search?q={query_encoded}&{params_extension}"
                    
                    st.success("¡Búsqueda generada con éxito!")
                    st.code(query_encoded, language="text")
                    st.link_button("VER CANDIDATOS", url_google, type="primary", use_container_width=True)

st.divider()
