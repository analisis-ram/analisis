import streamlit as st
import pandas as pd
import pdfplumber
import re
import openai

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
# 2. CSS MEJORADO (CAJETÍN CON SCROLL FLUIDO Y ARCHIVOS COMPACTOS)
# ============================================
st.markdown("""
<style>
    /* --- ESTILOS DE LA BARRA LATERAL --- */
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
        ESTILOS DEL CAJETÍN DE SUBIDA Y ARCHIVOS COMPACTOS
        ========================================================== */
    [data-testid="stFileUploader"] label p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #FAFAFA !important;
        margin-bottom: 8px !important;
    }

    /* Contenedor del área de arrastre */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #F8B155 !important;
        border: 3px dashed #262730 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: flex-start !important;
        min-height: 260px !important;
        max-height: 380px !important;
        overflow-y: auto !important;
    }

    /* Scroll personalizado elegante */
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar {
        width: 6px;
    }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 3px;
    }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-thumb {
        background: #262730;
        border-radius: 3px;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzone"] button svg {
        display: none !important;
    }

    /* Botón interno para añadir más archivos */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: 2px solid #1E3A8A !important;
        border-radius: 8px !important;
        padding: 0 20px !important;
        min-width: 220px !important;
        height: 42px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        white-space: nowrap !important;
        margin: 8px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4) !important;
        visibility: visible !important;
        flex-shrink: 0 !important;
    }

    [data-testid="stFileUploaderDropzone"] button div,
    [data-testid="stFileUploaderDropzone"] button span {
        font-size: 0 !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Añadir más archivos";
        font-size: 14px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        white-space: nowrap !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #2563EB !important;
        border-color: #1E3A8A !important;
    }

    /* ==========================================================
        REDUCCIÓN DE TAMAÑO DE LOS ARCHIVOS SUBIDOS (PILLS/ITEMS)
        ========================================================== */
    /* Tarjetas individuales de archivos subidos */
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"],
    section[data-testid="stFileUploader"] div[data-testid="stUploadedFile"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        margin-bottom: 6px !important;
        min-height: unset !important;
        height: auto !important;
    }

    /* Texto del nombre del archivo y tamaño en miniatura */
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] span,
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] p {
        color: #F9FAFB !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* Icono del archivo dentro de la lista muy pequeño */
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] svg {
        width: 16px !important;
        height: 16px !important;
        fill: #F8B155 !important;
    }

    /* Botón de eliminar (la "X") de cada archivo en miniatura */
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] button {
        background-color: transparent !important;
        border: none !important;
        height: 20px !important;
        min-width: 20px !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] button svg {
        width: 14px !important;
        height: 14px !important;
        fill: #EF4444 !important;
    }

    /* --- ESTILOS DEL BOTÓN DE ACCIÓN PRINCIPAL --- */
    .stButton > button {
        background-color: #F8B155 !important;
        color: #14161F !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        padding: 16px 30px !important;
        border-radius: 12px !important;
        border: 3px solid #14161F !important;
        width: 100% !important;
        box-shadow: 0 8px 20px rgba(248, 177, 85, 0.4) !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #F59E0B !important;
        transform: translateY(-2px);
    }

    .block-container { padding-top: 2rem; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    div[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; }
    h1 a { display: none !important; }
</style>
""", unsafe_allow_html=True)

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
    with pdfplumber.open(pdf_file) as pdf:
        for idx, page in enumerate(pdf.pages):
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    
    data = {
        'year': 0, 'nif': 'Desconocido', 'empresa': 'Desconocida', 
        'ingresos': 0.0, 'resultado_neto': 0.0, 'activo_total': 0.0, 'patrimonio_neto': 0.0
    }

    nif_empresa_match = re.search(r'Identificaci[oó]n[\s\S]*?NIF\s*([A-Z]\d{8})', text, re.IGNORECASE)
    if nif_empresa_match:
        data['nif'] = nif_empresa_match.group(1).strip()
    else:
        nif_empresa_match = re.search(r'\b([A-Z]\d{8})\b', text)
        if nif_empresa_match:
            data['nif'] = nif_empresa_match.group(1).strip()

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "apellidos y nombre o razón social" in line_lower or "denominación social" in line_lower:
            for offset in range(1, 6):
                if i + offset < len(lines):
                    posible = lines[i + offset].strip()
                    if not posible.isdigit() and len(posible) > 3:
                        data['empresa'] = posible
                        break
            if data['empresa'] != 'Desconocida':
                break

    patrones_anio = [r'Ejercicio[\s\.\:\-]*?(20[12]\d)\b', r'De\s+01/01/(20[12]\d)']
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
    data['resultado_neto'] = get_val('00500') or 0.0
    data['activo_total'] = get_val('00180') or 0.0
    data['patrimonio_neto'] = get_val('00185') or 0.0
    
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
        <div style="text-align: center; margin-top: 4vh; margin-bottom: 25px;">
            <h1 style="color: #F8B155; font-size: 3rem; font-weight: 800; margin-bottom: 15px;">TODO MODELO 200</h1>
            <p style="font-size: 1.2rem; color: #A0A0A0;">Sube tus Modelos 200 y Excel adjuntos para comenzar el análisis.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_files = st.file_uploader(
            "Arrastra aquí tus archivos", 
            type=["pdf", "xlsx", "xls"], 
            accept_multiple_files=True, 
            key=f"uploader_{st.session_state.uploader_key}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("COMENZAR EXTRACCIÓN DATOS MODELOS 200", key="btn_iniciar", use_container_width=True):
            if not uploaded_files:
                st.warning("Por favor, sube al menos un archivo PDF o Excel.")
            else:
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
</div>
""", unsafe_allow_html=True)