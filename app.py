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
# 2. CSS MEJORADO (CAJETÍN 100% NARANJA Y SIN FLECHA)
# ============================================
st.markdown("""
<style>
    /* --- ESTILOS DE LA BARRA LATERAL (NARANJA CLARITO) --- */
    [data-testid="stSidebar"] { 
        background-color: #F8B155 !important; 
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] input {
        color: #1A1A1A !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D97706 !important;
    }

    /* --- ESTILO DEL BOTÓN DE BORRAR --- */
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
       ESTILOS DEL CAJETÍN DE SUBIDA 100% NARANJA Y LIMPIO
       ========================================================== */
    [data-testid="stFileUploader"] label p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #FAFAFA !important;
        margin-bottom: 6px !important;
    }

    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #F8B155 !important;
        border: 2px dashed #262730 !important;
        border-radius: 10px !important;
        padding: 18px 22px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 80px !important;
    }

    /* Ocultar el bloque de instrucciones gris derecho por completo */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    /* Ocultar icono por defecto de Streamlit */
    [data-testid="stFileUploaderDropzone"] button svg {
        display: none !important;
    }

    /* Botón central unificado 100% naranja y sin flecha */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background-color: #14161F !important;
        color: #FFFFFF !important;
        border: 2px solid #262730 !important;
        border-radius: 8px !important;
        padding: 0 24px !important;
        height: 46px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        visibility: visible !important;
    }

    [data-testid="stFileUploaderDropzone"] button div,
    [data-testid="stFileUploaderDropzone"] button span {
        font-size: 0 !important;
    }
    
    /* Texto exacto sin flecha */
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Subir Modelos 200";
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #1F2230 !important;
        color: #FFFFFF !important;
        border-color: #262730 !important;
    }

    /* --- ESTILOS DEL BLOQUE DE CONTACTO SUPERIOR --- */
    .contact-header-title {
        font-size: 20px;
        font-weight: 800;
        color: #F8B155;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .contact-buttons-row {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 25px;
        align-items: center;
    }
    .btn-contact-wa {
        background-color: #25D366;
        color: #FFFFFF !important;
        padding: 12px 26px;
        border-radius: 40px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 17px;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.35);
        transition: transform 0.2s, background-color 0.2s;
    }
    .btn-contact-wa:hover {
        background-color: #1EBE5D;
        transform: translateY(-2px);
    }
    .btn-contact-mail {
        background-color: #3B82F6;
        color: #FFFFFF !important;
        padding: 12px 26px;
        border-radius: 40px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 17px;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        transition: transform 0.2s, background-color 0.2s;
    }
    .btn-contact-mail:hover {
        background-color: #2563EB;
        transform: translateY(-2px);
    }
    .btn-contact-gmail {
        background-color: #EA4335;
        color: #FFFFFF !important;
        padding: 12px 22px;
        border-radius: 40px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 16px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 12px rgba(234, 67, 53, 0.35);
        transition: transform 0.2s, background-color 0.2s;
    }
    .btn-contact-gmail:hover {
        background-color: #D33426;
        transform: translateY(-2px);
    }

    /* --- ESTILOS GENERALES --- */
    .block-container { padding-top: 2rem; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    div[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; }
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
        border-left: 15px solid #F8B155; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
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
    first_pages_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for idx, page in enumerate(pdf.pages):
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                if idx < 4:
                    first_pages_text += extracted + "\n"
    
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
    
    frases_excluidas = ["en calidad de", "titular", "representante", "colaborador", "nif", "teléfono", "apellidos y nombre"]
    for i, line in enumerate(lines):
        if "Apellidos y nombre o razón social" in line or "Apellidos y Nombre / Razón social" in line or "Denominación social" in line:
            for offset in range(1, 5):
                if i + offset < len(lines):
                    posible = lines[i + offset].strip()
                    es_excluida = any(excl in posible.lower() for excl in frases_excluidas)
                    if not posible.isdigit() and not es_excluida and len(posible) > 3:
                        data['empresa'] = posible
                        break
            if data['empresa'] != 'Desconocida':
                break

    patrones_anio = [
        r'Ejercicio[\s\.\:\-]*?(20[12]\d)\b',
        r'Per[ií]odo impositivo[\s\S]{0,120}?\d{2}/\d{2}/(20[12]\d)',
        r'De\s+01/01/(20[12]\d)',
        r'al\s+31/12/(20[12]\d)',
        r'EL\s+1\s+1\s+(20[12]\d)',
        r'devengo[\s\S]{0,60}?(20[12]\d)'
    ]
    for pat in patrones_anio:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            y = int(m.group(1))
            if 2010 <= y <= 2030:
                data['year'] = y
                break

    if data['year'] == 0 and hasattr(pdf_file, 'name'):
        m_file = re.search(r'(20[12]\d)', pdf_file.name)
        if m_file:
            data['year'] = int(m_file.group(1))

    if data['year'] == 0:
        fechas = [int(y) for y in re.findall(r'\d{2}/\d{2}/(20[12]\d)', first_pages_text) if 2015 <= int(y) <= 2030]
        if fechas:
            data['year'] = min(fechas)

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
            data['errores_acreedores'].append(f"La cuenta <strong>{nombre_cuenta} ({code})</strong> está en NEGATIVO ({val:,.2f} €).")
        if code == '00240' and (val is None or val == 0):
            data['errores_acreedores'].append(f"La cuenta <strong>{nombre_cuenta} ({code})</strong> está VACÍA o a CERO.")
            
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
            <h1 style="color: #F8B155; font-size: 3.5rem; font-weight: 800; margin-bottom: 20px;">TODO MODELO 200</h1>
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
    for idx, file in enumerate(uploaded_files):
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
            if extracted['year'] == 0:
                extracted['year'] = f"Ejercicio {idx + 1}"
            datos_empresa.append(extracted)
        except Exception as e:
            st.error(f"Error con {file.name}: {e}")
        finally:
            loader_placeholder.empty()
    
    if datos_empresa:
        datos_empresa = sorted(datos_empresa, key=lambda x: str(x['year']))
        vistos = {}
        for d in datos_empresa:
            yr = str(d['year'])
            if yr in vistos:
                vistos[yr] += 1
                d['year_label'] = f"{yr} ({vistos[yr]})"
            else:
                vistos[yr] = 1
                d['year_label'] = yr
        st.success(f"✅ Se han cargado {len(datos_empresa)} años: {', '.join(d['year_label'] for d in datos_empresa)}.")
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
    years_str = [d['year_label'] for d in datos_empresa]

    accionistas_1 = datos_empresa[0]['accionistas_b2']
    accionistas_2 = datos_empresa[1]['accionistas_b2']
    accionistas_3 = datos_empresa[2]['accionistas_b2'] if len(datos_empresa) > 2 else accionistas_2
    b2_status_ok = (accionistas_1 == accionistas_2 == accionistas_3)

    hay_errores_acreedores = any(len(d['errores_acreedores']) > 0 for d in datos_empresa)

    # ==========================================================
    # SECCIÓN DE CONTACTO ARRIBA
    # ==========================================================
    st.markdown("""
        <div style="margin-bottom: 25px;">
            <div class="contact-header-title">📞 Contactar con el solucionador</div>
            <div class="contact-buttons-row">
                <a href="https://wa.me/34644247796?text=Hola,%20necesito%20ayuda%20con%20el%20an%C3%A1lisis%20del%20Modelo%20200" target="_blank" rel="noopener noreferrer" class="btn-contact-wa">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.031 2C6.508 2 2.023 6.485 2.023 12.008c0 1.766.461 3.49 1.337 5.01L2 22l5.122-1.343c1.472.804 3.129 1.228 4.909 1.228 5.523 0 10.008-4.485 10.008-10.008C22.039 6.485 17.554 2 12.031 2zm5.86 14.162c-.246.693-1.428 1.326-1.996 1.411-.528.079-1.218.112-1.968-.126-.456-.145-1.04-.338-1.787-.661-3.141-1.356-5.193-4.521-5.35-4.73-.157-.209-1.278-1.701-1.278-3.245 0-1.544.808-2.303 1.095-2.617.287-.314.626-.392.835-.392.209 0 .417.002.599.011.192.009.45-.073.704.538.261.628.887 2.168.965 2.325.078.157.13.34.026.549-.104.209-.157.34-.313.523-.157.183-.329.409-.47.549-.157.156-.321.326-.138.64.183.314.812 1.34 1.744 2.171 1.199 1.069 2.21 1.4 2.523 1.557.313.157.496.131.678-.078.183-.209.782-.915.991-1.229.209-.314.417-.261.704-.157.287.105 1.825.861 2.138 1.018.313.157.522.235.599.366.079.131.079.758-.167 1.451z"/>
                    </svg>
                    <span>WhatsApp</span>
                </a>
                <a href="mailto:cuadrarcuentas@gmail.com?subject=Consulta%20Auditor%C3%ADa%20Modelo%20200" target="_top" class="btn-contact-mail">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4.25l-8 5-8-5V6l8 5 8-5v2.25z"/>
                    </svg>
                    <span>Enviar Email (cuadrarcuentas@gmail.com)</span>
                </a>
                <a href="https://mail.google.com/mail/?view=cm&fs=1&to=cuadrarcuentas@gmail.com&su=Consulta%20Auditor%C3%ADa%20Modelo%20200" target="_blank" rel="noopener noreferrer" class="btn-contact-gmail">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14h-2V8.38l-6 3.75-6-3.75V18H4V6h1.2l6.8 4.25L18.8 6H20v12z"/>
                    </svg>
                    <span>Abrir en Gmail Web</span>
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.title("💼 Informe de Auditoría Financiera y Riesgo")
    st.markdown(f"**Empresa:** {nombre_empresa} | **NIF:** {nif_empresa} | **Periodo analizado:** {years_str[0]} - {years_str[-1]}")
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
                st.write(f"**{d['year_label']}:** {d['accionistas_b2']}")
            
    with col_audit2:
        st.markdown("### Sirenas Rojas (Acreedores/Proveedores)")
        
        if hay_errores_acreedores:
            for d in datos_empresa:
                if d['errores_acreedores']:
                    for error in d['errores_acreedores']:
                        st.markdown(f'<div class="alert-critical">🔴 SIRENA ROJA ({d["year_label"]}): {error}</div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="contact-banner">
                    <p>Los Proveedores no pueden estar a 0 y los Acreedores no pueden estar en negativo.</p>
                    <p>Por favor, escríbanos a <a href="mailto:cuadrarcuentas@gmail.com" target="_top">cuadrarcuentas@gmail.com</a> o por <a href="https://wa.me/34644247796" target="_blank">WhatsApp</a> y le explicamos las soluciones.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-success">✅ Saldos de acreedores y proveedores coherentes.</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # ==========================================================
    # 2. GRÁFICAS DE BARRAS EN MILES DE EUROS (k €) Y 3 AÑOS EN X
    # ==========================================================
    st.subheader("📊 2. Evolución de Existencias y Acreedores")
    
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        existencias_k = [(d['existencias_00138'] or 0.0) / 1000.0 for d in datos_empresa]
        
        fig_exist = go.Figure()
        fig_exist.add_trace(go.Bar(
            x=years_str,
            y=existencias_k,
            name='Existencias (00138)',
            marker_color='#1d4ed8',
            text=[f"{val:,.1f}k €" for val in existencias_k],
            textposition='outside',
            hovertemplate='<b>Año %{x}</b><br>Existencias: %{y:,.2f}k €<extra></extra>'
        ))
        fig_exist.update_layout(
            title=dict(text='Evolución de Existencias (00138)', font=dict(size=18, color='#1d4ed8')),
            template='plotly_dark',
            xaxis=dict(title="Año", type='category', categoryorder='array', categoryarray=years_str),
            yaxis=dict(title="Importe (Miles de €)", ticksuffix="k €", rangemode="tozero"),
            margin=dict(t=60, b=40)
        )
        max_exist = max(existencias_k) if existencias_k else 0
        if max_exist > 0:
            fig_exist.update_yaxes(range=[0, max_exist * 1.18])
            
        st.plotly_chart(fig_exist, use_container_width=True)

    with col_chart2:
        acreedores_k = [(d['acreedores_00239'] or 0.0) / 1000.0 for d in datos_empresa]
        proveedores_k = [(d['proveedores_00240'] or 0.0) / 1000.0 for d in datos_empresa]
        
        fig_acreedores = go.Figure()
        fig_acreedores.add_trace(go.Bar(
            x=years_str,
            y=acreedores_k,
            name='Acreedores (00239)',
            marker_color='#60a5fa',
            text=[f"{val:,.1f}k €" for val in acreedores_k],
            textposition='outside',
            hovertemplate='<b>Año %{x}</b><br>Acreedores (00239): %{y:,.2f}k €<extra></extra>'
        ))
        fig_acreedores.add_trace(go.Bar(
            x=years_str,
            y=proveedores_k,
            name='Proveedores (00240)',
            marker_color='#3b82f6',
            text=[f"{val:,.1f}k €" for val in proveedores_k],
            textposition='outside',
            hovertemplate='<b>Año %{x}</b><br>Proveedores (00240): %{y:,.2f}k €<extra></extra>'
        ))
        fig_acreedores.update_layout(
            title=dict(text='Evolución de Acreedores y Proveedores', font=dict(size=18, color='#60a5fa')),
            barmode='group',
            template='plotly_dark',
            xaxis=dict(title="Año", type='category', categoryorder='array', categoryarray=years_str),
            yaxis=dict(title="Importe (Miles de €)", ticksuffix="k €", rangemode="tozero"),
            legend_title_text='Cuenta',
            margin=dict(t=60, b=40)
        )
        max_ac_pr = max(acreedores_k + proveedores_k) if (acreedores_k + proveedores_k) else 0
        min_ac_pr = min(acreedores_k + proveedores_k) if (acreedores_k + proveedores_k) else 0
        if max_ac_pr > 0 or min_ac_pr < 0:
            fig_acreedores.update_yaxes(range=[min(0, min_ac_pr * 1.18), max_ac_pr * 1.18])

        st.plotly_chart(fig_acreedores, use_container_width=True)

    st.markdown("---")

    # ==========================================================
    # 3. ANÁLISIS DE MASAS PATRIMONIALES
    # ==========================================================
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
        ingresos_k = [d['ingresos'] / 1000.0 for d in datos_empresa]
        rn_k = [d['resultado_neto'] / 1000.0 for d in datos_empresa]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ingresos', x=years_str, y=ingresos_k, marker_color='#3B82F6', text=[f"{v:,.1f}k €" for v in ingresos_k], textposition='outside'))
        fig.add_trace(go.Bar(name='Resultado Neto', x=years_str, y=rn_k, marker_color='#10B981', text=[f"{v:,.1f}k €" for v in rn_k], textposition='outside'))
        fig.update_layout(
            title='Evolución de Ingresos y Resultados',
            barmode='group',
            template='plotly_dark',
            xaxis=dict(title="Año", type='category', categoryorder='array', categoryarray=years_str),
            yaxis=dict(title="Importe (Miles de €)", ticksuffix="k €")
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_g2:
        activo_k = [d['activo_total'] / 1000.0 for d in datos_empresa]
        pn_k = [d['patrimonio_neto'] / 1000.0 for d in datos_empresa]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='Activo Total', x=years_str, y=activo_k, mode='lines+markers', line=dict(color='#EF4444', width=3)))
        fig.add_trace(go.Scatter(name='Patrimonio Neto', x=years_str, y=pn_k, mode='lines+markers', line=dict(color='#3B82F6', width=3)))
        fig.update_layout(
            title='Evolución del Balance',
            template='plotly_dark',
            xaxis=dict(title="Año", type='category', categoryorder='array', categoryarray=years_str),
            yaxis=dict(title="Importe (Miles de €)", ticksuffix="k €")
        )
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
                    summary += f"Año {d['year_label']}: Ingresos: {d['ingresos']}, RN: {d['resultado_neto']}, Acreedores(00239): {d['acreedores_00239']}, Proveedores(00240): {d['proveedores_00240']}.\n"
                
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