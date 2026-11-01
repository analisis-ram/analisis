import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pdfplumber
import re
import textwrap

# ============================================
# CONFIGURACIÓN DE PÁGINA (FIJO A LA IZQUIERDA)
# ============================================
st.set_page_config(
    page_title="Análisis Financiero Modelo 200",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PARA FIJAR LA BARRA LATERAL, ANIMACIÓN Y BARRA DE PROGRESO
# ============================================
st.markdown("""
<style>
    /* Ocultar la flecha para cerrar la barra lateral */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    
    /* Darle un ancho fijo a la barra lateral */
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* Animación del martillo */
    @keyframes smash {
        0% { transform: rotate(0deg); }
        30% { transform: rotate(-40deg); }
        50% { transform: rotate(15deg); }
        70% { transform: rotate(-10deg); }
        100% { transform: rotate(0deg); }
    }
    .animated-hammer {
        display: inline-block;
        animation: smash 0.6s infinite;
        transform-origin: bottom right;
    }

    /* Contenedor de la barra de progreso */
    .progress-container {
        flex-grow: 1; 
        margin-left: 30px; 
        height: 12px; 
        background-color: #333333; 
        border-radius: 6px;
        overflow: hidden;
        position: relative;
    }

    /* Relleno animado */
    .progress-bar-animated {
        height: 100%;
        width: 100%;
        background: repeating-linear-gradient(
            -45deg,
            #4CAF50,
            #4CAF50 10px,
            #2E7D32 10px,
            #2E7D32 20px
        );
        background-size: 28.28px 28.28px; 
        animation: stripe-move 1s linear infinite; 
    }

    @keyframes stripe-move {
        0% { background-position: 0 0; }
        100% { background-position: 28.28px 0; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE EXTRACCIÓN DE PDF (MODELO 200)
# ============================================
def parse_spanish_number(num_str):
    if not num_str: return 0.0
    try:
        clean_str = num_str.replace('.', '').replace(',', '.').strip()
        return float(clean_str)
    except: return 0.0

def extract_data_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted: text += extracted + "\n"
    
    data = {
        'year': 0, 'ingresos': 0.0, 'aprovisionamientos': 0.0, 'gastos_personal': 0.0,
        'amortizacion': 0.0, 'resultado_explotacion': 0.0, 'resultado_neto': 0.0,
        'activo_total': 0.0, 'patrimonio_neto': 0.0, 'pasivo_no_corriente': 0.0,
        'pasivo_corriente': 0.0, 'clientes': 0.0, 'existencias': 0.0, 'tesoreria': 0.0,
        'proveedores': 0.0, 'deuda_bancaria': 0.0, 'base_imponible': 0.0,
    }

    year_match = re.search(r'Ejercicio\s*(\d{4})', text) or re.search(r'(20\d{2})', text)
    if year_match: data['year'] = int(year_match.group(1))

    def get_val(casilla):
        pattern = rf"{casilla}\s+(-?[\d\.]+,\d{{2}}|-?\d+)"
        match = re.search(pattern, text)
        if match: return parse_spanish_number(match.group(1))
        pattern_alt = rf"{casilla}(-?[\d\.]+,\d{{2}}|-?\d+)"
        match_alt = re.search(pattern_alt, text)
        if match_alt: return parse_spanish_number(match_alt.group(1))
        return 0.0

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
    data['proveedores'] = get_val('00240')
    data['deuda_bancaria'] = get_val('00218')
    data['base_imponible'] = get_val('00552')
    
    match_exist = re.search(r'Existencias \(N, A, P\)\s+\d+\s+([\d\.,]+)', text)
    if match_exist: data['existencias'] = parse_spanish_number(match_exist.group(1))

    return data

# ============================================
# DATOS POR DEFECTO (MODO DEMO - ITELSAT)
# ============================================
demo_data = [
    {'year': 2023, 'ingresos': 1246492.66, 'aprovisionamientos': 473328.59, 'gastos_personal': 404693.28, 'amortizacion': 52540.40, 'resultado_explotacion': 69239.77, 'resultado_neto': 67037.32, 'activo_total': 923819.82, 'patrimonio_neto': 774339.82, 'pasivo_no_corriente': 0, 'pasivo_corriente': 149480, 'clientes': 237600, 'existencias': 135900, 'tesoreria': 150319.82, 'proveedores': -52520, 'deuda_bancaria': 202000, 'base_imponible': 52032.60},
    {'year': 2024, 'ingresos': 1346718.78, 'aprovisionamientos': 457443.01, 'gastos_personal': 313418.01, 'amortizacion': 40030.55, 'resultado_explotacion': 309089.37, 'resultado_neto': 303147.69, 'activo_total': 1290129.57, 'patrimonio_neto': 1062482.79, 'pasivo_no_corriente': 205000, 'pasivo_corriente': 22647, 'clientes': 400200, 'existencias': 225000, 'tesoreria': 182000, 'proveedores': 0, 'deuda_bancaria': 227647, 'base_imponible': 53147.69},
    {'year': 2025, 'ingresos': 1356381.42, 'aprovisionamientos': 467780.14, 'gastos_personal': 381276.75, 'amortizacion': 42356.05, 'resultado_explotacion': 196002.55, 'resultado_neto': 191385.09, 'activo_total': 1365339.00, 'patrimonio_neto': 1253867.88, 'pasivo_no_corriente': 138650, 'pasivo_corriente': -27179, 'clientes': 500120, 'existencias': 160250, 'tesoreria': 226729.89, 'proveedores': 0, 'deuda_bancaria': 111471, 'base_imponible': 191385.09}
]

# ============================================
# SIDEBAR Y CARGA DE ARCHIVOS
# ============================================
st.sidebar.title("📂 Cargar Modelos 200")
st.sidebar.markdown("Sube los PDFs del Modelo 200 (puedes seleccionar varios años a la vez).")
uploaded_files = st.sidebar.file_uploader("Selecciona archivos PDF", type="pdf", accept_multiple_files=True)

datos_empresa = []

if uploaded_files:
    for file in uploaded_files:
        loader_placeholder = st.empty()
        html_loader = textwrap.dedent(f"""
            <div style="display: flex; align-items: center; background-color: #262730; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #F57C00; width: 100%; box-sizing: border-box;">
                <div style="font-size: 40px; margin-right: 20px; width: 60px; text-align: center; flex-shrink: 0;">
                    <span class="animated-hammer">🔨</span><br>
                    <span style="font-size: 26px; display: block; margin-top: -12px;">📘</span>
                </div>
                <div style="flex-shrink: 0;">
                    <span style="color: #FAFAFA; font-size: 16px; font-weight: bold;">Procesando documento...</span><br>
                    <span style="color: #A0A0A0; font-size: 14px;">{file.name}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar-animated"></div>
                </div>
            </div>
        """)
        loader_placeholder.markdown(html_loader, unsafe_allow_html=True)
        
        try:
            extracted = extract_data_from_pdf(file)
            if extracted['ingresos'] > 0 or extracted['activo_total'] > 0:
                datos_empresa.append(extracted)
            else:
                st.sidebar.warning(f"Aviso: El archivo {file.name} parece estar vacío o no tiene el formato correcto.")
        except Exception as e:
            st.sidebar.error(f"Error leyendo {file.name}: {e}")
        finally:
            loader_placeholder.empty()
    
    if datos_empresa:
        datos_empresa = sorted(datos_empresa, key=lambda x: x['year'])
        st.sidebar.success(f"¡{len(datos_empresa)} ejercicios cargados!")
    else:
        st.sidebar.warning("No se pudo extraer información de los PDFs. Mostrando Modo Demo.")
        datos_empresa = demo_data
else:
    st.sidebar.info("Modo Demo activado. Sube PDFs para analizar otras empresas.")
    datos_empresa = demo_data

# ============================================
# PREPARACIÓN DE DATOS
# ============================================
years = [d['year'] for d in datos_empresa]
ingresos = [d.get('ingresos', 0) for d in datos_empresa]
aprovisionamientos = [d.get('aprovisionamientos', 0) for d in datos_empresa]
gastos_personal = [d.get('gastos_personal', 0) for d in datos_empresa]
amortizacion = [d.get('amortizacion', 0) for d in datos_empresa]
resultado_explotacion = [d.get('resultado_explotacion', 0) for d in datos_empresa]
resultado_neto = [d.get('resultado_neto', 0) for d in datos_empresa]
activo_total = [d.get('activo_total', 0) for d in datos_empresa]
patrimonio_neto = [d.get('patrimonio_neto', 0) for d in datos_empresa]
pasivo_no_corriente = [d.get('pasivo_no_corriente', 0) for d in datos_empresa]
pasivo_corriente = [d.get('pasivo_corriente', 0) for d in datos_empresa]
clientes = [d.get('clientes', 0) for d in datos_empresa]
existencias = [d.get('existencias', 0) for d in datos_empresa]
tesoreria = [d.get('tesoreria', 0) for d in datos_empresa]
proveedores = [d.get('proveedores', 0) for d in datos_empresa]
deuda_bancaria = [d.get('deuda_bancaria', 0) for d in datos_empresa]
base_imponible = [d.get('base_imponible', 0) for d in datos_empresa]

fondo_maniobra = []
for i in range(len(datos_empresa)):
