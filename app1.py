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
# 2. CSS MEJORADO (CAJETÍN CON SCROLL FLUIDO Y ALTURA DINÁMICA)
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
        ESTILOS DEL CAJETÍN DE SUBIDA (CONTENEDOR ADAPTABLE)
        ========================================================== */
    [data-testid="stFileUploader"] label p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #FAFAFA !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #F8B155 !important;
        border: 3px dashed #262730 !important;
        border-radius: 16px !important;
        padding: 25px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: flex-start !important;
        min-height: 280px !important;
        max-height: 420px !important;
        overflow-y: auto !important;
    }

    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar {
        width: 8px;
    }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 4px;
    }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-thumb {
        background: #262730;
        border-radius: 4px;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzone"] button svg {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: 2px solid #1E3A8A !important;
        border-radius: 10px !important;
        padding: 0 32px !important;
        min-width: 260px !important;
        height: 52px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        white-space: nowrap !important;
        margin: 10px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
        visibility: visible !important;
        flex-shrink: 0 !important;
    }

    [data-testid="stFileUploaderDropzone"] button div,
    [data-testid="stFileUploaderDropzone"] button span {
        font-size: 0 !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Subir Modelos 200 y Excel";
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        white-space: nowrap !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #2563EB !important;
        border-color: #1E3A8A !important;
    }

    /* --- ESTILOS DEL BOTÓN DE ACCIÓN PRINCIPAL --- */
    .stButton > button {
        background-color: #F8B155 !important;
        color: #14161F !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        padding: 20px 36px !important;
        border-radius: 14px !important;
        border: 4px solid #14161F !important;
        width: 100% !important;
        box-shadow: 0 10px 25px rgba(248, 177, 85, 0.4) !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #F59E0B !important;
        transform: translateY(-2px);
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
    .btn-contact-gmail {
        background-color: #EA4335;
        color: #FFFFFF !important;
        padding: 12px 26px;
        border-radius: 40px;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 17px;
        display: inline-flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(234, 67, 53, 0.35);
        transition: transform 0.2s, background-color 0.2s;
    }
    .btn-contact-gmail:hover {
        background-color: #D33426;
        transform: translateY(-2px);
    }

    .block-container { padding-top: 2rem; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    div[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; }
    h1 a { display: none !important; }

    .alert-critical { background-color: #EF4444; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-warning { background-color: #F59E0B; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-success { background-color: #10B981; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    
    .contact-banner { background-color: #FEF2F2; border: 2px solid #EF4444; color: #991B1B !important; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px; font-weight: bold; text-align: center; }
    .contact-banner a { color: #EF4444; text-decoration: underline; }

    div[data-testid="stMetric"] { 
        background-color: transparent !important; 
        border: 1px solid rgba(128, 128, 128, 0.3); 
        padding: 15px; 
        border-radius: 10px; 
    }

    /* --- ESTILOS DEL MODAL DE CARGA --- */
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
# 3. FUNCIONES DE EXTRACCIÓN DE PDF Y EXCEL
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
    
    nif_empresa_match = re.search(r'Identificaci[oó]n[\s\S]*?NIF\s*([A-Z]\d{8})', text, re.IGNORECASE)
    if nif_empresa_match:
        data['nif'] = nif_empresa_match.group(1).strip()
    else:
        nif_empresa_match = re.search(r'\b([A-Z]\d{8})\b', text)
        if nif_empresa_match:
            data['nif'] = nif_empresa_match.group(1).strip()

    frases_excluidas = [
        "vía de entrada", "presentación", "por internet", "en calidad de", "titular", 
        "representante", "colaborador", "nif", "teléfono", "apellidos y nombre", 
        "domiciliación", "ingresar", "banco", "caja", "cuenta", "entidad", "oficina", 
        "importe", "ejercicio", "declaración", "modelo 200", "página"
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "apellidos y nombre o razón social" in line_lower or "denominación social" in line_lower:
            for offset in range(1, 6):
                if i + offset < len(lines):
                    posible = lines[i + offset].strip()
                    posible_lower = posible.lower()
                    es_excluida = any(excl in posible_lower for excl in frases_excluidas)
                    if not posible.isdigit() and not es_excluida and len(posible) > 3:
                        data['empresa'] = posible
                        break
            if data['empresa'] != 'Desconocida':
                break

    patrones_anio = [
        r'Ejercicio[\s\.\:\-]*?(20[12]\d)\b',
        r'Per[ií]odo impositivo[\s\S]{0,120}?\d{2}/\d{2}/(20[12]\d)',
        r'De\s+01/01/(20[12]\d)',
        r'al\s+31/12/(20[12]\d)'
    ]
    for pat in patrones_anio:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            y = int(m.group(1))
            if 2010 <= y <= 2030:
                data['year'] = y
                break

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
    
    return data

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
# 4. GESTIÓN DE ESTADO (SESSION STATE)
# ============================================
if 'datos_empresa' not in st.session_state:
    st.session_state.datos_empresa = None
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = {}
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

st.sidebar.title("💼 TODO MODELO 200")
st.sidebar.markdown("Sube tus Modelos 200 y ficheros Excel adjuntos.")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 IA Privada")
api_key = st.sidebar.text_input("API Key (OpenAI)", type="password")

if st.session_state.datos_empresa is not None:
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Borrar documentos y empezar de nuevo", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ============================================
# 5. PANTALLA PRINCIPAL: SUBIDA DE ARCHIVOS
# ============================================
if st.session_state.datos_empresa is None:
    st.markdown("""
        <div style="text-align: center; margin-top: 5vh; margin-bottom: 30px;">
            <h1 style="color: #F8B155; font-size: 3.5rem; font-weight: 800; margin-bottom: 20px;">TODO MODELO 200</h1>
            <p style="font-size: 1.3rem; color: #A0A0A0;">Sube tus Modelos 200 (PDFs) y los Excel analíticos para cruzar la información y generar las solapas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_files = st.file_uploader(
            "Arrastra aquí tus archivos (PDFs y Excel)", 
            type=["pdf", "xlsx", "xls"], 
            accept_multiple_files=True, 
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
        if uploaded_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("COMENZAR ANÁLISIS E IMPORTACIÓN", key="btn_iniciar", use_container_width=True):
                temp_datos = []
                temp_excels = {}
                
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        try:
                            extracted = extract_data_from_pdf(file)
                            if extracted['year'] == 0:
                                extracted['year'] = "Ejercicio"
                            temp_datos.append(extracted)
                        except Exception as e:
                            st.error(f"Error procesando PDF {file.name}: {e}")
                    elif file.name.lower().endswith(('.xlsx', '.xls')):
                        try:
                            xl = pd.ExcelFile(file)
                            for sheet in xl.sheet_names:
                                temp_excels[sheet] = pd.read_excel(file, sheet_name=sheet)
                        except Exception as e:
                            st.error(f"Error procesando Excel {file.name}: {e}")
                
                if temp_datos:
                    temp_datos = sorted(temp_datos, key=lambda x: str(x['year']))
                    vistos = {}
                    for d in temp_datos:
                        yr = str(d['year'])
                        if yr in vistos:
                            vistos[yr] += 1
                            d['year_label'] = f"{yr} ({vistos[yr]})"
                        else:
                            vistos[yr] = 1
                            d['year_label'] = yr
                    st.session_state.datos_empresa = temp_datos

                if temp_excels:
                    st.session_state.excel_data = temp_excels

                st.rerun()

    st.stop()

datos_empresa = st.session_state.datos_empresa
excel_data = st.session_state.excel_data

# ============================================
# 6. CREACIÓN DINÁMICA DE SOLAPAS (WEB TABS)
# ============================================
# Solapas principales fijas + solapas de cada hoja de excel encontrada
tabs_labels = ["📊 Dashboard Financiero e Informe IA"]
if excel_data:
    for sheet_name in excel_data.keys():
        tabs_labels.append(f"📑 Excel: {sheet_name}")

creanted_tabs = st.tabs(tabs_labels)

# --------------------------------------------
# SOLAPA 1: PORTADA / DASHBOARD FINANCIERO
# --------------------------------------------
with creanted_tabs[0]:
    st.markdown("---")
    if st.button("🗑️ Borrar todos los archivos y actualizar la web", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")

    if datos_empresa and len(datos_empresa) >= 1:
        nombre_empresa = datos_empresa[0]['empresa']
        nif_empresa = datos_empresa[0]['nif']
        years_str = [d['year_label'] for d in datos_empresa]

        st.title("💼 Informe Financiero y Riesgo")
        st.markdown(f"**Empresa:** {nombre_empresa} | **NIF:** {nif_empresa} | **Periodo analizado:** {years_str[0]} - {years_str[-1]}")
        st.markdown("---")

        st.subheader("📈 Métricas y Masas Patrimoniales Recientes")
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

        st.markdown("---")
        st.subheader("🧠 Informe Ejecutivo redactado por IA")
        if st.button("Generar Informe Ejecutivo con IA"):
            if not api_key:
                st.error("Introduce tu API Key en la barra lateral.")
            else:
                with st.spinner("Redactando informe..."):
                    summary = ""
                    for d in datos_empresa:
                        summary += f"Año {d['year_label']}: Ingresos: {d['ingresos']}, RN: {d['resultado_neto']}.\n"
                    ai_text = generate_ai_report(api_key, summary, "Auditoría completada satisfactoriamente.")
                    st.markdown(f'<div class="ai-report" style="background:#1e2937; padding:20px; border-radius:10px; color:white;">{ai_text}</div>', unsafe_allow_html=True)

# --------------------------------------------
# SOLAPAS DINÁMICAS (CADA HOJA DE LOS EXCEL ADJUNTOS)
# ============================================
if excel_data:
    for idx, (sheet_name, df_sheet) in enumerate(excel_data.items(), start=1):
        with creanted_tabs[idx]:
            st.header(f"Contenido de la hoja de Excel: {sheet_name}")
            st.markdown("---")
            st.dataframe(df_sheet, use_container_width=True)

# ============================================
# PIE DE PÁGINA COMÚN
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px;'>
    <p>TODO MODELO 200 | Desarrollado con estándares profesionales de análisis financiero.</p>
    <p>Esta web no almacena ninguno de los documentos subidos. Análisis 100% anónimo.</p>
</div>
""", unsafe_allow_html=True)