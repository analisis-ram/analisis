import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pdfplumber
import re
import time
import openai
import base64
import os

# ============================================
# 1. CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="TODO MODELO 200",
    page_icon="💼",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ============================================
# 2. CSS MEJORADO (ESTILO CAJETÍN NARANJA EXACTO)
# ============================================
st.markdown("""
<style>
    /* --- ESTILOS DE LA BARRA LATERAL (NARANJA APAGADO) --- */
    [data-testid="stSidebar"] { 
        background-color: #D97706 !important; 
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] input {
        color: #1A1A1A !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* --- ESTILO DEL BOTÓN DE BORRAR (LETRA Y PAPELERA MÁS GORDA) --- */
    [data-testid="stSidebar"] button[kind="primary"], .main button[kind="primary"] {
        font-weight: 900 !important; 
        font-size: 16px !important;  
        border-radius: 8px !important;
        padding: 10px !important;
    }
    [data-testid="stSidebar"] button[kind="primary"] p, .main button[kind="primary"] p {
        font-weight: 900 !important;
        font-size: 16px !important;
    }

    /* ==========================================================
       ESTILOS DEL CAJETÍN DE SUBIDA NARANJA (EXACTO A LA IMAGEN)
       ========================================================== */
    
    /* Etiqueta superior ("Arrastra aquí tus PDFs...") */
    [data-testid="stFileUploader"] label p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #FAFAFA !important;
        margin-bottom: 6px !important;
    }

    /* Contenedor principal (Cajetín Naranja) */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #F8B155 !important; /* Naranja exacto de tu imagen */
        border: 4px solid #262730 !important; /* Borde exterior oscuro sutil */
        border-radius: 10px !important;
        padding: 18px 22px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 80px !important;
    }

    /* Ocultar el icono de nube por defecto y el texto "Drag and drop file here" */
    [data-testid="stFileUploaderDropzoneInstructions"] svg,
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
        display: none !important;
    }

    /* Bloque de instrucciones (donde queda "200MB per file • PDF") */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        order: 2 !important;
        background-color: #262730 !important; /* Fondo oscuro del recuadro interno */
        padding: 8px 16px 8px 10px !important;
        border-radius: 0 8px 8px 0 !important;
        margin: 0 !important;
        height: 42px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Texto "200MB per file • PDF" */
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzone"] small {
        color: #A3A8B8 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* Botón de "Browse files" / "Upload" */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        order: 1 !important;
        background-color: #14161F !important; /* Casi negro para destacar el botón */
        color: #FFFFFF !important;
        border: 4px solid #262730 !important; /* Conecta visualmente con el bloque de al lado */
        border-radius: 8px 0 0 8px !important;
        padding: 0 16px !important;
        height: 42px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        box-shadow: none !important;
    }

    /* Añadir icono de subida antes del texto del botón */
    [data-testid="stFileUploaderDropzone"] button::before {
        content: "↑";
        font-weight: 900;
        font-size: 15px;
        margin-right: 4px;
        border-bottom: 2px solid #FFFFFF;
        line-height: 0.8;
        padding-bottom: 1px;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #1F2230 !important;
        color: #FFFFFF !important;
        border-color: #262730 !important;
    }

    /* --- ESTILOS GENERALES --- */
    .block-container { padding-top: 2rem; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    div[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; }
    
    /* Ocultar el icono de enlace (cadena) al lado de los títulos H1 */
    h1 a { display: none !important; }

    /* Alertas */
    .alert-critical { background-color: #EF4444; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-warning { background-color: #F59E0B; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-success { background-color: #10B981; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    
    /* Banner de Contacto Urgente */
    .contact-banner { background-color: #FEF2F2; border: 2px solid #EF4444; color: #991B1B !important; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px; font-weight: bold; text-align: center; }
    .contact-banner a { color: #EF4444; text-decoration: underline; }

    /* KPIs */
    div[data-testid="stMetric"] { 
        background-color: transparent !important; 
        border: 1px solid rgba(128, 128, 128, 0.3); 
        padding: 15px; 
        border-radius: 10px; 
    }

    /* --- ESTILOS DEL MODAL DE CARGA (IMPRESORA) --- */
    .loader-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0, 0, 0, 0.85); backdrop-filter: blur(5px);
        display: flex; justify-content: center; align-items: center; z-index: 99999;
    }
    .loader-card {
        background-color: #262730; padding: 50px 80px; border-radius: 30px;
        border-left: 15px solid #D97706; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 80vw; max-width: 800px;
    }
    .printer-scene {
        position: relative; width: 100%; height: 280px;
        display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; overflow: hidden;
    }
    .printer-body {
        position: absolute; top: 90px; width: 220px; height: 90px;
        background: #1f2937; border-radius: 15px; border-bottom: 8px solid #111;
        z-index: 10; display: flex; flex-direction: column; align-items: center;
        box-shadow: 0 15px 30px rgba(0,0,0,0.8), inset 0 2px 5px rgba(255,255,255,0.1);
    }
    .printer-light {
        width: 15px; height: 15px; background: #10B981; border-radius: 50%;
        margin-top: 15px; animation: blink 0.8s infinite alternate; box-shadow: 0 0 15px #10B981;
    }
    .printer-slot {
        width: 160px; height: 10px; background: #000; border-radius: 5px;
        margin-top: 15px; box-shadow: inset 0 5px 10px rgba(0,0,0,0.9);
    }
    .doc-input { position: absolute; top: -100px; width: 110px; z-index: 5; animation: feedDoc 4s infinite; }
    .doc-output {
        position: absolute; top: 150px; width: 150px; height: 200px;
        background: white; border-radius: 5px; z-index: 5; padding: 15px; box-sizing: border-box;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5); animation: printReport 4s infinite;
        transform-origin: top center; display: flex; flex-direction: column;
    }
    .rep-line { height: 6px; background: #d1d5db; margin-bottom: 8px; border-radius: 3px; }
    .rep-line.short { width: 60%; }
    .rep-title { font-family: sans-serif; font-weight: bold; color: #1f2937; font-size: 11px; margin-bottom: 15px; text-align: center; }
    .rep-chart { font-size: 36px; text-align: center; margin-top: auto; margin-bottom: 10px; }

    @keyframes blink { 0% { opacity: 0.3; } 100% { opacity: 1; } }
    @keyframes feedDoc {
        0% { transform: translateY(0); opacity: 1; }
        35% { transform: translateY(220px); opacity: 1; }
        40% { transform: translateY(220px); opacity: 0; }
        100% { transform: translateY(220px); opacity: 0; }
    }
    @keyframes printReport {
        0% { transform: scaleY(0); opacity: 0; }
        40% { transform: scaleY(0); opacity: 0; }
        45% { transform: scaleY(0.1); opacity: 1; }
        85% { transform: scaleY(1); opacity: 1; }
        95% { transform: scaleY(1); opacity: 1; }
        100% { transform: scaleY(1); opacity: 0; }
    }
    .loader-title { color: #FAFAFA; font-size: 36px; font-weight: bold; margin-bottom: 10px; margin-top: 20px; }
    .loader-subtitle { color: #A0A0A0; font-size: 20px; margin-bottom: 30px; }
    .progress-container {
        width: 80%; height: 30px; background-color: #111111; border-radius: 20px;
        overflow: hidden; display: flex; align-items: center; box-shadow: inset 0 5px 10px rgba(0,0,0,0.8);
    }
    .progress-bar-animated {
        height: 100%; width: 100%;
        background: repeating-linear-gradient(-45deg, #4CAF50, #4CAF50 25px, #2E7D32 25px, #2E7D32 50px);
        background-size: 70.7px 70.7px; animation: move-stripes 1s linear infinite;
    }
    @keyframes move-stripes { 0% { background-position: 0 0; } 100% { background-position: 70.7px 0; } }
</style>
""", unsafe_allow_html=True)

# Diccionario de nombres de cuentas
NOMBRES_CUENTAS = {
    '00239': 'Acreedores comerciales y otras cuentas a pagar',
    '00240': 'Proveedores',
    '00241': 'Proveedores a largo plazo',
    '00242': 'Proveedores a corto plazo',
    '00243': 'Proveedores, empresas del grupo y asociadas',
    '00244': 'Acreedores varios',
    '00245': 'Personal (remuneraciones pendientes de pago)',
    '00246': 'Pasivos por impuesto corriente',
    '00247': 'Otras deudas con las Administraciones Públicas',
    '00248': 'Anticipos de clientes',
    '00249': 'Otros acreedores'
}

# ============================================
# 3. FUNCIONES DE EXTRACCIÓN DE PDF
# ============================================
def parse_spanish_number(num_str):
    if not num_str:
        return None
    try:
        return float(num_str.replace('.', '').replace(',', '.').strip())
    except:
        return None

def extract_data_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    
    data = {
        'year': 0, 'nif': 'Desconocido', 'empresa': 'Desconocida', 
        'ingresos': 0.0, 'aprovisionamientos': 0.0, 
        'gastos_personal': 0.0, 'amortizacion': 0.0, 'resultado_explotacion': 0.0, 
        'resultado_neto': 0.0, 'activo_total': 0.0, 'patrimonio_neto': 0.0, 
        'pasivo_no_corriente': 0.0, 'pasivo_corriente': 0.0, 'clientes': 0.0, 
        'tesoreria': 0.0, 'deuda_bancaria': 0.0, 'base_imponible': 0.0,
        'existencias_00138': None, 'acreedores_00239': None, 
        'proveedores_00240': None, 'accionistas_b2': [],
        'errores_acreedores': [] 
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        if "Ejercicio" in line or "De 01/01/" in line or "EL 1 1 " in line:
            year_match = re.search(r'(20\d{2})', line)
            if year_match:
                data['year'] = int(year_match.group(1))
        
        if "Apellidos y nombre o razón social" in line or "Apellidos y Nombre / Razón social" in line:
            if i + 1 < len(lines):
                posible_nombre = lines[i+1]
                if not posible_nombre.isdigit() and "NIF" not in posible_nombre and "Teléfono" not in posible_nombre and len(posible_nombre) > 3:
                    data['empresa'] = posible_nombre
                    break 

    nif_empresa_match = re.search(r'Identificaci[oó]n[\s\S]*?NIF\s*([A-Z]\d{8})', text, re.IGNORECASE)
    if nif_empresa_match:
        data['nif'] = nif_empresa_match.group(1).strip()
    else:
        nif_empresa_match = re.search(r'\b([A-Z]\d{8})\b', text)
        if nif_empresa_match:
            data['nif'] = nif_empresa_match.group(1).strip()
        else:
            nif_dni_match = re.search(r'Identificaci[oó]n[\s\S]*?NIF\s*(\d{8}[A-Z])', text, re.IGNORECASE)
            if nif_dni_match:
                data['nif'] = nif_dni_match.group(1).strip()

    def get_val(casilla):
        pattern = rf"\b{casilla}\b.*?(-?[\d\.]+,\d{{2}}|-?\d+)\b"
        match = re.search(pattern, text)
        if match:
            return parse_spanish_number(match.group(1))
        return None 

    data['ingresos'] = get_val('00255') or 0.0
    data['aprovisionamientos'] = abs(get_val('00260') or 0.0)
    data['gastos_personal'] = abs(get_val('00270') or 0.0)
    data['amortizacion'] = abs(get_val('00284') or 0.0)
    data['resultado_explotacion'] = get_val('00296') or 0.0
    data['resultado_neto'] = get_val('00500') or 0.0
    data['activo_total'] = get_val('00180') or 0.0
    data['patrimonio_neto'] = get_val('00185') or 0.0
    data['pasivo_no_corriente'] = get_val('00210') or 0.0
    data['pasivo_corriente'] = get_val('00228') or 0.0
    data['clientes'] = get_val('00149') or 0.0
    data['tesoreria'] = get_val('00177') or 0.0
    data['deuda_bancaria'] = get_val('00218') or 0.0
    data['base_imponible'] = get_val('00552') or 0.0
    
    data['existencias_00138'] = get_val('00138')
    data['acreedores_00239'] = get_val('00239')
    data['proveedores_00240'] = get_val('00240')
    
    for code in ['00239', '00240', '00241', '00242', '00243', '00244', '00245', '00246', '00247', '00248', '00249']:
        val = get_val(code)
        nombre_cuenta = NOMBRES_CUENTAS.get(code, f"Cuenta {code}")
        if val is not None and val < 0:
            data['errores_acreedores'].append(f"La cuenta **{nombre_cuenta} ({code})** está en NEGATIVO ({val:,.2f} €).")
        if code == '00240' and (val is None or val == 0):
            data['errores_acreedores'].append(f"La cuenta **{nombre_cuenta} ({code})** está VACÍA o a CERO.")
            
    b2_match = re.search(r'B\.2\.\s+Participaciones de personas.*?(?=C\.|D\.|$)', text, re.DOTALL | re.IGNORECASE)
    if b2_match:
        b2_text = b2_match.group(0)
        nifs = re.findall(r'\b[A-Z0-9]\d{7}[A-Z0-9]\b', b2_text)
        nifs_clean = [n for n in nifs if n != data['nif']]
        data['accionistas_b2'] = sorted(list(set(nifs_clean)))

    return data

# ============================================
# 4. LÓGICA DE LA IA
# ============================================
def generate_ai_report(api_key, financial_summary, rules_audit):
    client = openai.OpenAI(api_key=api_key)
    system_prompt = "Eres un Analista Financiero Senior con 22 años de experiencia. Tono formal, técnico y directo."
    user_prompt = f"Datos:\n{financial_summary}\n\nReglas/Auditoría:\n{rules_audit}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al conectar con la IA: {e}"

# ============================================
# 5. INTERFAZ SIDEBAR Y GESTIÓN DE ESTADO
# ============================================
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

st.sidebar.title("💼 TODO MODELO 200")
st.sidebar.markdown("El sistema analizará los Modelos 200 que subas en la pantalla principal.")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 IA Privada")
st.sidebar.markdown("Introduce tu API Key. *No se almacena.*")
api_key = st.sidebar.text_input("API Key (OpenAI)", type="password")

if st.session_state.uploaded_files is not None:
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Borrar documentos y empezar de nuevo", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

datos_empresa = []

# ============================================
# 6. PANTALLA PRINCIPAL Y SUBIDOR DE ARCHIVOS
# ============================================
if not st.session_state.uploaded_files:
    st.markdown("""
        <div style="text-align: center; margin-top: 5vh; margin-bottom: 30px;">
            <h1 style="color: #D97706; font-size: 3.5rem; font-weight: 800; margin-bottom: 20px;">TODO MODELO 200</h1>
            <p style="font-size: 1.3rem; color: #A0A0A0;">Sube al menos 2 Modelos 200 de la misma empresa para comenzar el análisis.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded = st.file_uploader(
            "Arrastra aquí tus PDFs (mínimo 2)", 
            type="pdf", 
            accept_multiple_files=True, 
            key=f"uploader_{st.session_state.uploader_key}"
        )
        if uploaded:
            st.session_state.uploaded_files = uploaded
            st.rerun()

    st.stop()

uploaded_files = st.session_state.uploaded_files

# --- BOTÓN DE REINICIO EN EL CENTRO ---
st.markdown("---")
if st.button("🗑️ Borrar todos los archivos y actualizar la web", type="primary", use_container_width=True):
    st.session_state.clear()
    st.rerun()
st.markdown("---")

img_base64 = ""
if os.path.exists("modelo200.png"):
    with open("modelo200.png", "rb") as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode()

if uploaded_files:
    for file in uploaded_files:
        loader_placeholder = st.empty()
        
        if img_base64:
            imagen_html = f'<img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:4px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);" alt="Modelo 200">'
        else:
            imagen_html = '<div style="width: 100px; height: 80px; background: linear-gradient(135deg, #3B82F6, #1E3A8A); color: white; font-size: 14px; font-weight: 900; display: flex; justify-content: center; align-items: center; border-radius: 4px;">MOD.<br>200</div>'

        loader_html = f"""
        <div class="loader-overlay">
            <div class="loader-card">
                <div class="printer-scene">
                    <div class="printer-body">
                        <div class="printer-light"></div>
                        <div class="printer-slot"></div>
                    </div>
                    <div class="doc-input">{imagen_html}</div>
                    <div class="doc-output">
                        <div class="rep-title">INFORME FINANCIERO</div>
                        <div class="rep-line"></div>
                        <div class="rep-line short"></div>
                        <div class="rep-line"></div>
                        <div class="rep-line short"></div>
                        <div class="rep-line"></div>
                        <div class="rep-chart">📊</div>
                    </div>
                </div>
                <div class="loader-title">Extrayendo datos del Modelo 200...</div>
                <div class="loader-subtitle">{file.name}</div>
                <div class="progress-container">
                    <div class="progress-bar-animated"></div>
                </div>
            </div>
        </div>
        """
        
        with loader_placeholder:
            st.markdown(loader_html, unsafe_allow_html=True)
            time.sleep(2.5) 
            
        try:
            extracted = extract_data_from_pdf(file)
            datos_empresa.append(extracted)
        except Exception as e:
            st.error(f"Error con {file.name}: {e}")
        finally:
            loader_placeholder.empty()
    
    if datos_empresa:
        datos_empresa = sorted(datos_empresa, key=lambda x: x['year'])
        st.success(f"✅ Se han cargado {len(datos_empresa)} años.")
else:
    st.info("Esperando archivos...")

# ============================================
# 7. VALIDACIÓN DE MISMA EMPRESA
# ============================================
if datos_empresa:
    nifs = set([d['nif'] for d in datos_empresa])
    nifs_validos = {n for n in nifs if n != 'Desconocido'} 
    if len(nifs_validos) > 1:
        st.error(f"🚨 **ALERTA CRÍTICA:** Los archivos subidos son de diferentes empresas. NIFs: {nifs_validos}.")
        st.stop()

# ============================================
# 8. RENDERIZADO PRINCIPAL (DASHBOARD Y GRÁFICAS)
# ============================================
if datos_empresa and len(datos_empresa) >= 2:
    nombre_empresa = datos_empresa[0]['empresa']
    nif_empresa = datos_empresa[0]['nif']
    years = [d['year'] for d in datos_empresa]

    accionistas_1 = datos_empresa[0]['accionistas_b2']
    accionistas_2 = datos_empresa[1]['accionistas_b2']
    accionistas_3 = datos_empresa[2]['accionistas_b2'] if len(datos_empresa) > 2 else accionistas_2
    b2_status_ok = (accionistas_1 == accionistas_2 == accionistas_3)

    hay_errores_acreedores = any(len(d['errores_acreedores']) > 0 for d in datos_empresa)

    # --- BOTONES DE CONTACTO ARRIBA ---
    st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 20px;">
            <a href="https://wa.me/34644247796" target="_blank" style="background-color: #25D366; color: white; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                💬 Contactar con el solucionador (WhatsApp)
            </a>
            <a href="mailto:cuadrarcuentas@gmail.com" style="background-color: #3b82f6; color: white; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                ✉️ Contactar con el solucionador (Email)
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.title("💼 Informe de Auditoría Financiera y Riesgo")
    st.markdown(f"**Empresa:** {nombre_empresa} | **NIF:** {nif_empresa} | **Periodo analizado:** {years[0]} - {years[-1]}")
    st.markdown("---")

    st.subheader("🔍 1. Auditoría de Estructura y Desglose")
    col_audit1, col_audit2 = st.columns(2)

    with col_audit1:
        st.markdown("### B.2. Participaciones (Accionistas)")
        if b2_status_ok:
            st.markdown('<div class="alert-success">✅ Los accionistas (B.2) se mantienen constantes.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-critical">🔴 SIRENA ROJA: Cambio de accionistas (B.2) detectado.</div>', unsafe_allow_html=True)
        
        with st.expander("Ver NIFs extraídos de B.2"):
            for d in datos_empresa:
                st.write(f"**{d['year']}:** {d['accionistas_b2']}")
            
    with col_audit2:
        st.markdown("### Sirenas Rojas (Acreedores/Proveedores)")
        
        if hay_errores_acreedores:
            for d in datos_empresa:
                if d['errores_acreedores']:
                    for error in d['errores_acreedores']:
                        st.markdown(f'<div class="alert-critical">🔴 SIRENA ROJA ({d["year"]}): {error}</div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="contact-banner">
                    <p>Los Proveedores no pueden estar a 0 y los Acreedores no pueden estar en negativo.</p>
                    <p>Por favor, <a href="mailto:cuadrarcuentas@gmail.com">contáctenos urgentemente</a> y le explicamos las soluciones.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-success">✅ Saldos de acreedores y proveedores coherentes.</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # --- GRÁFICAS DE BARRAS ---
    st.subheader("📊 2. Evolución de Existencias y Acreedores")
    
    col_chart1, col_chart2 = st.columns(2)
    years_str = [str(y) for y in years]

    with col_chart1:
        df_exist = pd.DataFrame({
            'Año': years_str,
            'Existencias': [d['existencias_00138'] if d['existencias_00138'] is not None else 0 for d in datos_empresa]
        })
        fig_exist = px.bar(df_exist, x='Año', y='Existencias', title='Evolución de Existencias (00138)', color_discrete_sequence=['#1d4ed8'])
        fig_exist.update_traces(texttemplate='%{y:.2s}', textposition='outside')
        fig_exist.update_layout(template='plotly_dark', title_font=dict(size=18, color='#1d4ed8'), xaxis_title="Año", yaxis_title="Euros")
        st.plotly_chart(fig_exist, use_container_width=True)

    with col_chart2:
        df_acreedores = pd.DataFrame({
            'Año': years_str,
            'Acreedores (00239)': [d['acreedores_00239'] if d['acreedores_00239'] is not None else 0 for d in datos_empresa],
            'Proveedores (00240)': [d['proveedores_00240'] if d['proveedores_00240'] is not None else 0 for d in datos_empresa]
        })
        df_melted = df_acreedores.melt(id_vars='Año', var_name='Cuenta', value_name='Importe')
        fig_acreedores = px.bar(df_melted, x='Año', y='Importe', color='Cuenta', barmode='group', title='Evolución de Acreedores y Proveedores', color_discrete_sequence=['#60a5fa', '#3b82f6'])
        fig_acreedores.update_traces(texttemplate='%{y:.2s}', textposition='outside')
        fig_acreedores.update_layout(template='plotly_dark', title_font=dict(size=18, color='#60a5fa'), xaxis_title="Año", yaxis_title="Euros")
        st.plotly_chart(fig_acreedores, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 3. Análisis de Masas Patrimoniales")
    ult_idx = -1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True): st.metric("Ingresos", f"{datos_empresa[ult_idx]['ingresos']:,.0f} €")
    with col2:
        with st.container(border=True): st.metric("Resultado Neto", f"{datos_empresa[ult_idx]['resultado_neto']:,.0f} €")
    with col3:
        with st.container(border=True): st.metric("Activo Total", f"{datos_empresa[ult_idx]['activo_total']:,.0f} €")
    with col4:
        with st.container(border=True): st.metric("Patrimonio Neto", f"{datos_empresa[ult_idx]['patrimonio_neto']:,.0f} €")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ingresos', x=years_str, y=[d['ingresos'] for d in datos_empresa], marker_color='#3B82F6'))
        fig.add_trace(go.Bar(name='Resultado Neto', x=years_str, y=[d['resultado_neto'] for d in datos_empresa], marker_color='#10B981'))
        fig.update_layout(title='Evolución de Ingresos y Resultados', barmode='group', template='plotly_dark', xaxis_title="Año", yaxis_title="Euros")
        st.plotly_chart(fig, use_container_width=True)
        
    with col_g2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='Activo Total', x=years_str, y=[d['activo_total'] for d in datos_empresa], mode='lines+markers', line=dict(color='#EF4444', width=3)))
        fig.add_trace(go.Scatter(name='Patrimonio Neto', x=years_str, y=[d['patrimonio_neto'] for d in datos_empresa], mode='lines+markers', line=dict(color='#3B82F6', width=3)))
        fig.update_layout(title='Evolución del Balance', template='plotly_dark', xaxis_title="Año", yaxis_title="Euros")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("🧠 4. Informe Ejecutivo redactado por IA")
    if st.button("Generar Informe Ejecutivo con IA"):
        if not api_key:
            st.error("Introduce tu API Key en la barra lateral.")
        else:
            with st.spinner("Redactando informe..."):
                summary = ""
                for d in datos_empresa:
                    summary += f"Año {d['year']}: Ingresos: {d['ingresos']}, RN: {d['resultado_neto']}, Acreedores(00239): {d['acreedores_00239']}, Proveedores(00240): {d['proveedores_00240']}.\n"
                
                rules = f"B.2 iguales: {b2_status_ok}. Errores detectados: {[e for d in datos_empresa for e in d['errores_acreedores']]}."
                
                ai_text = generate_ai_report(api_key, summary, rules)
                st.markdown(f'<div class="ai-report">{ai_text}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>TODO MODELO 200 | Desarrollado con estándares de 22 años de experiencia.</p>
        <p>Esta web no guarda ninguno de los documentos subidos. Análisis 100% anónimo.</p>
    </div>
    """, unsafe_allow_html=True)