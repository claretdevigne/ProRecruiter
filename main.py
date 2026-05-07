import streamlit as st
import urllib.parse

# INICIA APP
st.set_page_config(
    page_title="Pro Recruiter v2026", 
    page_icon="🕵️",
    layout="centered")

st.title("Pro Recruiter")
st.markdown("By Maomeno")

with st.form("search_form"):
    puesto = st.text_input("¿Qué perfil buscas?", placeholder="Ej: Especialista en Ciberseguridad")
    keywords = st.text_input("Keywords o Skills", placeholder="Ej: CISSP, Python, Remoto, Senior")
    ubicacion = st.text_input("Ubicación", placeholder="Ej: Cancún")
    
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
        
        CONTEXTO: Necesito generar una query de X-Ray para encontrar talento específico en linkedin
        
        PARÁMETROS
        - Puesto Core: {puesto}
        - Skills críticas: {keywords}
        - Ubicación: {ubicacion}
        - Job Description proporcionada: {jd if jd else "N/A"}
        
        INSTRUCCIONES TÉCNICAS OBLIGATORIAS:
        1. Inicio: La query X-Ray debe empezar estrictamente con site:linkedin.com/in/
        2. Expansión de Títulos: Incluye sinónimos comunes tanto en inglés como en español (mínimo 5 variaciones).
        3. Capa de Validación: Incluye un grupo (OR) con herramientas, certificaciones estándard de la industria que validen las Skills Críticas (ej. si es DevOps, añade Docker/Kubernetes aunque no vengan en el input). 
        4. Capa de Limpieza: Aplica obligatoriamente -intitle:job -intitle:hiring -intitle:vacante -intitle:empleo para evitar anuncios de trabajo.
        5. Ubicación: Desglosa la ciudad por siglas, nombres oficiales y zonas de influencia. Usa comillas para nombres compuestos.
        6. Si solo proporciono la Job Description, extrae tú mismo el Puesto Core, las Skills Críticas y la Ubicación para construir la query siguiendo las mismas reglas técnicas"
        
        ENTREGA: Devuelve únicamente la cadena de texto de la query final (lista para copiar en Google).
        """
        
        with st.spinner("Consultando datos..."):
            try:
                # Configuración del cliente
                from openai import OpenAI
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                response = client.chat.completions.create(
                  model="gpt-4o-mini-2024-07-18",
                  messages=[{"role":"user", "content": prompt_texto}]
                )
                
                # Extrae y limpia profesionalmente el mensaje recibido
                raw_text = response.choices[0].message.content.strip()
                print(raw_text)
                
                if "```" in raw_text:
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("text"): raw_text = raw_text[4:].strip()
                    elif raw_text.startswith("sql"): raw_text = raw_text[3:]
                    raw_text = raw_text.strip()
            
                query_final = raw_text
                
                metadatos = {
                  "puesto": puesto,
                  "skills": keywords,
                  "ubicacion": ubicacion,
                }
                
                if "site:linkedin.com/in/" in query_final:
                    query_encode = urllib.parse.quote(query_final)
                    params_extension = urllib.parse.urlencode(metadatos)
                    url_google = f"https://www.google.com/search?q={query_final}&{params_extension}"
                    
                    st.success("¡Búsqueda generada con éxito!")
                    st.code(query_final, language="text")
                    st.link_button("VER CANDIDATOS", url_google, type="primary", use_container_width=True)
                
            except Exception as e:
              st.error(f"Error al decodificar JSON: {e}")

st.divider()

# Opción con link directo y un toque de estilo
st.markdown(
    """
    <div style="text-align: center;">
        <a href="https://github.com/claretdevigne/ProRecruiterExtension/archive/refs/heads/main.zip" 
           style="text-decoration: none; color: #27ae60; font-weight: bold; font-size: 18px;">
           📥 Descargar extensión
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)
