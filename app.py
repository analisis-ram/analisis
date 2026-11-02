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
# 2. CSS MEJORADO Y FORZADO
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

    /* --- ESTILOS DEL ÁREA DE SUBIDA (NARANJA CLARO FORZADO) --- */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFB03A !important; 
        border: none !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    [data-testid="stFileUploadDropzone"] div,
    [data-testid="stFileUploadDropzone"] section {
        background-color: transparent !important;
    }

    [data-testid="stFileUploadDropzone"] small {
        color: #1A1A1A !important; 
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    [data-testid="stFileUploadDropzone"] button {
        background-color: #1A1A1A !important; 
        color: #FFFFFF !important; 
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    [data-testid="stFileUploadDropzone"] button span { color: #FFFFFF !important; }
    [data-testid="stFileUploadDropzone"] button svg { fill: #FFFFFF !important; }
    [data-testid="stFileUploadDropzone"] button:hover { background-color: #333333 !important; }

    /* --- ESTILOS GENERALES --- */
    .block-container { padding-top: 2rem; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    div[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; }
    
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
# 3. FUNCIONES DE EXTRACCIÓN DE PDF (AMPLIADAS)
# ============================================
def parse_spanish_number(num_str):
    if not num_str: return None
    try:
        return float(num_str.replace('.', '').replace(',', '.').strip())
    except: return None

def extract_data_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted: text += extracted + "\n"
    
    # Inicializamos todos los campos posibles a 0 o None
    data = {
        'year': 0, 'nif': 'Desconocido', 'empresa': 'Desconocida', 
        'ingresos': 0.0, 'aprovisionamientos': 0.0, 
        'gastos_personal': 0.0, 'amortizacion': 0.0, 'resultado_explotacion': 0.0, 
        'resultado_neto': 0.0, 'activo_total': 0.0, 'patrimonio_neto': 0.0, 
        'pasivo_no_corriente': 0.0, 'pasivo_corriente': 0.0, 'clientes': 0.0, 
        'tesoreria': 0.0, 'deuda_bancaria': 0.0, 'base_imponible': 0.0,
        'existencias_00138': None, 'acreedores_00239': None, 
        'proveedores_00240': None, 'accionistas_b2': [],
        'errores_acreedores': [],
        
        # Nuevos campos para las solapas de Excel
        'inmovilizado_material': 0.0, 'inversiones_inmobiliarias': 0.0,
        'inv_fin_largo_plazo': 0.0, 'activos_imp_diferido': 0.0,
        'existencias_comerciales': 0.0, 'inv_fin_corto_plazo': 0.0,
        'deudores_varios': 0.0, 'periodificaciones_cp': 0.0,
        'capital': 0.0, 'reservas': 0.0, 'subvenciones': 0.0,
        'deuda_lp': 0.0, 'acreedores_comerciales': 0.0, 'deudas_fiscales': 0.0,
        'otras_deudas_cp': 0.0, 'deuda_bancaria_cp': 0.0,
        'gastos_personal_prod': 0.0, 'gastos_personal_est': 0.0,
        'otros_gastos_explot': 0.0, 'servicios_exteriores': 0.0,
        'tributos': 0.0, 'gastos_financieros': 0.0,
        'resultado_financiero': 0.0
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        if "Ejercicio" in line or "De 01/01/" in line or "EL 1 1 " in line:
            year_match = re.search(r'(20\d{2})', line)
            if year_match: data['year'] = int(year_match.group(1))
        
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
        if nif_empresa_match: data['nif'] = nif_empresa_match.group(1).strip()

    def get_val(casilla):
        pattern = rf"{casilla}.*?(-?[\d\.]+,\d{{2}}|-?\d+)\b"
        match = re.search(pattern, text)
        if match: 
            return parse_spanish_number(match.group(1))
        return 0.0 # Retornamos 0.0 para facilitar los DataFrames

    # --- EXTRACCIÓN DE DATOS (RESUMEN) ---
    data['ingresos'] = get_val('00255')
    data['aprovisionamientos'] = abs(get_val('00260'))
    data['gastos_personal'] = abs(get_val('00270'))
    data['amortizacion'] = abs(get_val('00284'))
    data['resultado_explotacion'] = get_val('00296')
    data['resultado_neto'] = get_val('00500')
    data['activo_total'] = get_val('00180')
    data['patrimonio_neto'] = get_val('00185')
    data['pasivo_no_corriente'] = get_val('00210')
    data['pasivo_corriente'] = get_val('00228')
    data['clientes'] = get_val('00149')
    data['tesoreria'] = get_val('00177')
    data['deuda_bancaria'] = get_val('00218')
    data['base_imponible'] = get_val('00552')
    
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

    # --- EXTRACCIÓN DE DATOS DETALLADOS (PARA TABS) ---
    data['inmovilizado_material'] = get_val('00111') # A veces 00212
    data['inversiones_inmobiliarias'] = get_val('00115')
    data['inv_fin_largo_plazo'] = get_val('00126')
    data['activos_imp_diferido'] = get_val('00134')
    
    data['existencias_comerciales'] = get_val('00138') # Usamos total existencias
    data['inv_fin_corto_plazo'] = get_val('00168')
    data['deudores_varios'] = get_val('00159')
    data['periodificaciones_cp'] = get_val('00176')
    
    data['capital'] = get_val('00187')
    data['reservas'] = get_val('00193')
    data['subvenciones'] = get_val('00209')
    data['deuda_lp'] = get_val('00218') + get_val('00219') + get_val('00222') # Suma aprox
    
    data['acreedores_comerciales'] = get_val('00239')
    data['deudas_fiscales'] = get_val('00247')
    data['otras_deudas_cp'] = get_val('00237') + get_val('00249')
    data['deuda_bancaria_cp'] = get_val('00233')
    
    data['gastos_personal_prod'] = get_val('00270') # A veces no está desglosado, ponemos el total
    data['gastos_personal_est'] = 0.0 
    data['otros_gastos_explot'] = get_val('00279')
    data['servicios_exteriores'] = get_val('00280')
    data['tributos'] = get_val('00281')
    data['gastos_financieros'] = get_val('00305')
    data['resultado_financiero'] = get_val('00324')

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

# --- BOTÓN DE BORRAR EN LA BARRA LATERAL ---
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
            <h1 style="color: #D97706; font-size: 3.5rem; margin-bottom: 20px;">TODO MODELO 200</h1>
            <p style="font-size: 1.3rem; color: #A0A0A0;">Sube al menos 2 Modelos 200 de la misma empresa para comenzar el análisis.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded = st.file_uploader("Arrastra aquí tus PDFs (mínimo 2)", type="pdf", accept_multiple_files=True, key=f"uploader_{st.session_state.uploader_key}")
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
            st.error(f"Error con {file.name}")
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
# 8. RENDERIZADO PRINCIPAL CON PESTAÑAS (TABS)
# ============================================
if datos_empresa and len(datos_empresa) >= 2:
    nombre_empresa = datos_empresa[0]['empresa']
    nif_empresa = datos_empresa[0]['nif']
    years = [d['year'] for d in datos_empresa]

    st.title("💼 Análisis Financiero - Modelo 200")
    st.markdown(f"**Empresa:** {nombre_empresa} | **NIF:** {nif_empresa} | **Periodo analizado:** {years[0]} - {years[-1]}")
    st.markdown("---")

    # --- CREACIÓN DE LAS PESTAÑAS ---
    tab_resumen, tab_balance, tab_explotacion, tab_fondo_maniobra, tab_punto_equilibrio = st.tabs([
        "📊 Resumen Ejecutivo", 
        "⚖️ Balance", 
        "📈 Explotación", 
        "💧 Fondo de Maniobra", 
        "⚖️ Punto de Equilibrio"
    ])

    # ---------------------------------------------------------
    # PESTAÑA 1: RESUMEN EJECUTIVO (La pantalla actual)
    # ---------------------------------------------------------
    with tab_resumen:
        # Botones de Contacto Arriba
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

        accionistas_1 = datos_empresa[0]['accionistas_b2']
        accionistas_2 = datos_empresa[1]['accionistas_b2']
        accionistas_3 = datos_empresa[2]['accionistas_b2'] if len(datos_empresa) > 2 else accionistas_2
        b2_status_ok = (accionistas_1 == accionistas_2 == accionistas_3)
        hay_errores_acreedores = any(len(d['errores_acreedores']) > 0 for d in datos_empresa)

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
        
        st.subheader("📊 2. Evolución de Existencias y Acreedores")
        col_chart1, col_chart2 = st.columns(2)
        
        years_str = [str(y) for y in years]
        existencias_data = [d['existencias_00138'] if d['existencias_00138'] is not None else 0 for d in datos_empresa]
        acreedores_data = [d['acreedores_00239'] if d['acreedores_00239'] is not None else 0 for d in datos_empresa]
        proveedores_data = [d['proveedores_00240'] if d['proveedores_00240'] is not None else 0 for d in datos_empresa]

        with col_chart1:
            fig_exist = go.Figure()
            fig_exist.add_trace(go.Bar(
                x=years_str, y=existencias_data, marker_color='#1d4ed8',
                text=[f"{v/1000:.1f}k" if v >= 1000 else f"{v:.0f}" for v in existencias_data], 
                textposition='outside'
            ))
            fig_exist.update_layout(
                title='Evolución de Existencias (00138)', xaxis_title='Año', yaxis_title='Euros (k)',
                template='plotly_dark', yaxis=dict(tickformat='.2s') 
            )
            st.plotly_chart(fig_exist, use_container_width=True)

        with col_chart2:
            fig_acreedores = go.Figure()
            fig_acreedores.add_trace(go.Bar(
                x=years_str, y=acreedores_data, name='Acreedores (00239)', marker_color='#60a5fa',
                text=[f"{v/1000:.1f}k" if v >= 1000 else f"{v:.0f}" for v in acreedores_data], textposition='outside'
            ))
            fig_acreedores.add_trace(go.Bar(
                x=years_str, y=proveedores_data, name='Proveedores (00240)', marker_color='#3b82f6',
                text=[f"{v/1000:.1f}k" if v >= 1000 else f"{v:.0f}" for v in proveedores_data], textposition='outside'
            ))
            fig_acreedores.update_layout(
                title='Evolución de Acreedores y Proveedores', xaxis_title='Año', yaxis_title='Euros (k)',
                barmode='group', template='plotly_dark', yaxis=dict(tickformat='.2s')
            )
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

    # ---------------------------------------------------------
    # PESTAÑA 2: BALANCE (SOLAPA EXCEL)
    # ---------------------------------------------------------
    with tab_balance:
        st.subheader("⚖️ Balance de Situación Comparado")
        
        # Construimos el DataFrame para Balance
        df_balance = pd.DataFrame({
            'Concepto': [
                'Inmovilizado Material', 'Inversiones Inmobiliarias', 'Inv. Financieras L.P.', 'Activos Imp. Diferido',
                'Existencias', 'Clientes', 'Inv. Financieras C.P.', 'Deudores Varios', 'Tesorería', 'Periodificaciones C.P.',
                'TOTAL ACTIVO',
                'Capital', 'Reservas', 'Resultado del Ejercicio', 'Subvenciones',
                'Deuda a Largo Plazo',
                'Acreedores Comerciales', 'Deudas Fiscales y Sociales', 'Otras Deudas C.P.', 'Deuda Bancaria C.P.',
                'TOTAL PASIVO'
            ],
            'Tipo': [
                'Activo', 'Activo', 'Activo', 'Activo',
                'Activo', 'Activo', 'Activo', 'Activo', 'Activo', 'Activo',
                'TOTAL',
                'Pasivo', 'Pasivo', 'Pasivo', 'Pasivo',
                'Pasivo',
                'Pasivo', 'Pasivo', 'Pasivo', 'Pasivo',
                'TOTAL'
            ]
        })

        for i, y in enumerate(years):
            d = datos_empresa[i]
            df_balance[str(y)] = [
                d['inmovilizado_material'], d['inversiones_inmobiliarias'], d['inv_fin_largo_plazo'], d['activos_imp_diferido'],
                d['existencias_comerciales'], d['clientes'], d['inv_fin_corto_plazo'], d['deudores_varios'], d['tesoreria'], d['periodificaciones_cp'],
                d['activo_total'],
                d['capital'], d['reservas'], d['resultado_neto'], d['subvenciones'],
                d['deuda_lp'],
                d['acreedores_comerciales'], d['deudas_fiscales'], d['otras_deudas_cp'], d['deuda_bancaria_cp'],
                d['patrimonio_neto'] + d['pasivo_no_corriente'] + d['pasivo_corriente']
            ]

        # Formateamos los números
        for col in df_balance.columns[2:]:
            df_balance[col] = df_balance[col].apply(lambda x: f"{x:,.2f} €")

        st.dataframe(df_balance, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # PESTAÑA 3: EXPLOTACIÓN (SOLAPA EXCEL)
    # ---------------------------------------------------------
    with tab_explotacion:
        st.subheader("📈 Cuenta de Explotación Comparada")
        
        df_explotacion = pd.DataFrame({
            'Concepto': [
                'Cifra de Negocio (Ventas)', 'Aprovisionamientos', 
                'MARGEN BRUTO',
                'Gastos de Personal', 'Otros Gastos de Explotación', 'Amortizaciones', 'Tributos',
                'RESULTADO DE EXPLOTACIÓN',
                'Gastos Financieros',
                'RESULTADO FINANCIERO',
                'RESULTADO NETO'
            ]
        })

        for i, y in enumerate(years):
            d = datos_empresa[i]
            margen_bruto = d['ingresos'] - d['aprovisionamientos']
            df_explotacion[str(y)] = [
                d['ingresos'], d['aprovisionamientos'],
                margen_bruto,
                d['gastos_personal'], d['otros_gastos_explot'], d['amortizacion'], d['tributos'],
                d['resultado_explotacion'],
                d['gastos_financieros'],
                d['resultado_financiero'],
                d['resultado_neto']
            ]

        for col in df_explotacion.columns[1:]:
            df_explotacion[col] = df_explotacion[col].apply(lambda x: f"{x:,.2f} €")

        st.dataframe(df_explotacion, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # PESTAÑA 4: FONDO DE MANIOBRA (SOLAPA EXCEL)
    # ---------------------------------------------------------
    with tab_fondo_maniobra:
        st.subheader("💧 Fondo de Maniobra")
        
        df_fm = pd.DataFrame({
            'Concepto': [
                '+ Activo Circulante',
                '- Pasivo Circulante',
                'FONDO DE MANIOBRA APARENTE',
                'FONDO DE MANIOBRA NECESARIO',
                'Días de Autonomía'
            ]
        })

        for i, y in enumerate(years):
            d = datos_empresa[i]
            ac = d['existencias_comerciales'] + d['clientes'] + d['tesoreria'] + d['inv_fin_corto_plazo'] + d['deudores_varios']
            pc = d['pasivo_corriente']
            fm_aparente = ac - pc
            
            # Aproximación al Fondo de Maniobra Necesario (Gastos diarios * Periodo de maduración) - Financiación proveedores
            # Usaremos una aproximación estándar para que la tabla no esté vacía
            gastos_diarios = (d['ingresos'] - margen_bruto) / 365
            periodo_maduracion = 60 # Días estimados
            financiacion_prov = d['proveedores_00240'] if d['proveedores_00240'] else 0
            fm_necesario = (gastos_diarios * periodo_maduracion) - financiacion_prov
            
            dias_autonomia = fm_aparente / gastos_diarios if gastos_diarios > 0 else 0

            df_fm[str(y)] = [
                ac, pc, fm_aparente, fm_necesario, f"{dias_autonomia:.1f} días"
            ]

        # Formateo selectivo
        for col in df_fm.columns[1:]:
            df_fm[col] = df_fm[col].apply(lambda x: f"{x:,.2f} €" if isinstance(x, (int, float)) else x)

        st.dataframe(df_fm, hide_index=True, use_container_width=True)

    # ---------------------------------------------------------
    # PESTAÑA 5: PUNTO DE EQUILIBRIO
    # ---------------------------------------------------------
    with tab_punto_equilibrio:
        st.subheader("⚖️ Punto de Equilibrio (Umbral de Rentabilidad)")
        
        col_pe1, col_pe2 = st.columns(2)
        
        with col_pe1:
            df_pe = pd.DataFrame({
                'Concepto': [
                    'Gastos Fijos Anuales',
                    'Gastos Variables Anuales',
                    '% Gastos Variables s/ Ventas',
                    'Facturación Anual Necesaria',
                    'Facturación Alcanzada',
                    'Diferencia (Margen de Seguridad)'
                ]
            })
            for i, y in enumerate(years):
                d = datos_empresa[i]
                gastos_fijos = d['gastos_personal'] + d['amortizacion'] + d['otros_gastos_explot']
                gastos_variables = d['aprovisionamientos']
                pct_var = gastos_variables / d['ingresos'] if d['ingresos'] > 0 else 0
                
                facturacion_necesaria = gastos_fijos / (1 - pct_var) if pct_var < 1 else 0
                diferencia = d['ingresos'] - facturacion_necesaria

                df_pe[str(y)] = [
                    gastos_fijos, gastos_variables, f"{pct_var*100:.1f}%", 
                    facturacion_necesaria, d['ingresos'], diferencia
                ]
            
            for col in df_pe.columns[1:]:
                df_pe[col] = df_pe[col].apply(lambda x: f"{x:,.2f} €" if isinstance(x, (int, float)) else x)
                
            st.dataframe(df_pe, hide_index=True, use_container_width=True)

        with col_pe2:
            # Gráfico visual del Punto de Equilibrio del último año
            ult_idx = -1
            d = datos_empresa[ult_idx]
            gastos_fijos = d['gastos_personal'] + d['amortizacion'] + d['otros_gastos_explot']
            gastos_variables = d['aprovisionamientos']
            pct_var = gastos_variables / d['ingresos'] if d['ingresos'] > 0 else 0
            facturacion_necesaria = gastos_fijos / (1 - pct_var) if pct_var < 1 else 0
            
            x_vals = [0, d['ingresos'] * 1.2]
            y_ventas = x_vals
            y_costes = [gastos_fijos + (x * pct_var) for x in x_vals]
            
            fig_pe = go.Figure()
            fig_pe.add_trace(go.Scatter(x=x_vals, y=y_ventas, mode='lines', name='Ventas', line=dict(color='#3B82F6', width=3)))
            fig_pe.add_trace(go.Scatter(x=x_vals, y=y_costes, mode='lines', name='Costes Totales', line=dict(color='#EF4444', width=3)))
            fig_pe.add_hline(y=gastos_fijos, line_dash="dash", line_color="#F59E0B", annotation_text="Gastos Fijos")
            
            # Punto de corte
            fig_pe.add_trace(go.Scatter(x=[facturacion_necesaria], y=[facturacion_necesaria], mode='markers', name='Punto de Equilibrio', marker=dict(color='#10B981', size=12)))
            
            fig_pe.update_layout(
                title=f'Gráfico Punto de Equilibrio {years[ult_idx]}',
                xaxis_title='Facturación (€)',
                yaxis_title='Euros (€)',
                template='plotly_dark',
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            st.plotly_chart(fig_pe, use_container_width=True)

    # Footer final
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>TODO MODELO 200 | Desarrollado con estándares de 22 años de experiencia.</p>
        <p>Esta web no guarda ninguno de los documentos subidos. Análisis 100% anónimo.</p>
    </div>
    """, unsafe_allow_html=True)