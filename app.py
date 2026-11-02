import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pdfplumber
import re
import openai
import time

# ============================================
# CONFIGURACIÓN DE PÁGINA (SKIN PROFESIONAL)
# ============================================
st.set_page_config(
    page_title="Auditoría Financiera Senior | Modelo 200",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS MEJORADO (ESTILOS Y ANIMACIONES)
# ============================================
st.markdown("""
<style>
    /* Estilos generales */
    .block-container { padding-top: 2rem; }
    
    /* Ocultar la flecha para cerrar la barra lateral */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarHeader"] button { display: none !important; }
    
    /* Alertas */
    .alert-critical { background-color: #EF4444; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-warning { background-color: #F59E0B; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    .alert-success { background-color: #10B981; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 500; }
    
    /* IA Report */
    .ai-report { background-color: transparent; border-left: 5px solid #3B82F6; padding: 15px 20px; border-radius: 4px; font-size: 15px; line-height: 1.6; }
    
    /* KPIs */
    div[data-testid="stMetric"] { 
        background-color: transparent !important; 
        border: 1px solid rgba(128, 128, 128, 0.3); 
        padding: 15px; 
        border-radius: 10px; 
    }

    /* Animación de la flecha de inicio */
    @keyframes pulse-arrow {
        0% { transform: translateX(0); opacity: 1; }
        50% { transform: translateX(-20px); opacity: 0.5; }
        100% { transform: translateX(0); opacity: 1; }
    }
    .start-arrow {
        font-size: 80px;
        color: #3B82F6;
        animation: pulse-arrow 1.5s infinite;
        display: inline-block;
    }

    /* Animación del Martillo */
    @keyframes smash {
        0% { transform: rotate(0deg); }
        30% { transform: rotate(-45deg); }
        50% { transform: rotate(15deg); }
        70% { transform: rotate(-10deg); }
        100% { transform: rotate(0deg); }
    }
    .animated-hammer {
        display: inline-block;
        animation: smash 0.6s infinite;
        transform-origin: bottom right;
    }
    
    /* Barra de progreso verde */
    .progress-container {
        flex-grow: 1; 
        margin-left: 20px; 
        height: 16px; 
        background-color: #333333; 
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        align-items: center;
    }
    .progress-bar-animated {
        height: 100%;
        width: 100%;
        background: repeating-linear-gradient(-45deg, #4CAF50, #4CAF50 10px, #2E7D32 10px, #2E7D32 20px);
        background-size: 28.28px 28.28px;
        animation: move-stripes 1s linear infinite;
    }
    @keyframes move-stripes {
        0% { background-position: 0 0; }
        100% { background-position: 28.28px 0; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE EXTRACCIÓN DE PDF
# ============================================
def parse_spanish_number(num_str):
    if not num_str: return 0.0
    try:
        return float(num_str.replace('.', '').replace(',', '.').strip())
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
        'pasivo_corriente': 0.0, 'clientes': 0.0, 'tesoreria': 0.0,
        'proveedores': 0.0, 'deuda_bancaria': 0.0, 'base_imponible': 0.0,
        'existencias_00138': 0.0, 'acreedores_00239': 0.0, 'accionistas_b2': []
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
    data['deuda_bancaria'] = get_val('00218')
    data['base_imponible'] = get_val('00552')
    
    data['existencias_00138'] = get_val('00138')
    data['acreedores_00239'] = get_val('00239')
    data['proveedores'] = get_val('00240')
    
    b2_match = re.search(r'B\.2\.\s+Participaciones de personas.*?(?=C\.|D\.|$)', text, re.DOTALL | re.IGNORECASE)
    if b2_match:
        b2_text = b2_match.group(0)
        nifs = re.findall(r'\b[A-Z0-9]\d{7}[A-Z0-9]\b', b2_text)
        data['accionistas_b2'] = sorted(list(set(nifs)))

    return data

# ============================================
# LÓGICA DE LA IA
# ============================================
def generate_ai_report(api_key, financial_summary, rules_audit):
    client = openai.OpenAI(api_key=api_key)
    system_prompt = """
    Eres un Analista Financiero Senior con 22 años de experiencia. Tono formal, técnico y directo.
    Aplica estas reglas:
    1. Pasivo Corriente negativo = Error contable gravísimo.
    2. Proveedores (00240-00249) a 0 con Aprovisionamientos > 0 = Alarma roja.
    3. PMC > 90 días = Tensión de caja.
    4. Cambio de accionistas (B.2) = Advertir cambio de control.
    5. Variaciones en Existencias (00138) sin cambio en ventas = Obsolescencia.
    Redacta un texto estructurado con: Resumen Ejecutivo, Sirenas Rojas y Recomendaciones.
    """
    user_prompt = f"Datos:\n{financial_summary}\n\nReglas:\n{rules_audit}"
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
# INTERFAZ SIDEBAR
# ============================================
st.sidebar.title("💼 Auditoría Senior")
st.sidebar.markdown("Sube los Modelos 200 (mínimo 2 años) para el análisis comparativo.")
uploaded_files = st.sidebar.file_uploader("Selecciona PDFs", type="pdf", accept_multiple_files=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 IA Privada (OpenAI)")
st.sidebar.markdown("Introduce tu API Key para generar el informe. *No se almacena.*")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

datos_empresa = []

# ============================================
# PROCESAMIENTO CON ANIMACIÓN (HTML EN UNA SOLA LÍNEA)
# ============================================
if uploaded_files:
    for file in uploaded_files:
        loader_placeholder = st.empty()
        
        # HTML compactado en una sola línea, sin comentarios, para que Streamlit no se confunda
        loader_html = f'<div style="display: flex; align-items: center; background-color: #262730; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #3B82F6; width: 100%; box-sizing: border-box;"><div style="position: relative; width: 60px; height: 50px; margin-right: 20px; flex-shrink: 0;"><span class="animated-hammer" style="font-size: 35px; position: absolute; top: -10px; left: 15px; z-index: 2;">🔨</span><div style="position: absolute; bottom: 0px; left: 0px; z-index: 1; width: 45px; height: 32px; background: linear-gradient(135deg, #3B82F6, #1E3A8A); color: white; font-family: sans-serif; font-size: 10px; font-weight: 900; display: flex; justify-content: center; align-items: center; border-radius: 2px 6px 6px 2px; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); border-left: 6px solid #1E3A8A; text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">MOD.<br>200</div></div><div style="flex-shrink: 0; margin-right: 20px;"><div style="color: #FAFAFA; font-size: 16px; font-weight: bold;">Auditando documento...</div><div style="color: #A0A0A0; font-size: 13px;">{file.name}</div></div><div class="progress-container"><div class="progress-bar-animated"></div></div></div>'
        
        # Mostramos el gráfico y forzamos una pausa de 1.5s para que se vea la animación
        with loader_placeholder:
            st.markdown(loader_html, unsafe_allow_html=True)
            time.sleep(1.5)
            
        try:
            extracted = extract_data_from_pdf(file)
            datos_empresa.append(extracted)
        except Exception as e:
            st.sidebar.error(f"Error con {file.name}")
        finally:
            # Borramos el loader cuando termine
            loader_placeholder.empty()
    
    if datos_empresa:
        datos_empresa = sorted(datos_empresa, key=lambda x: x['year'])
        st.sidebar.success(f"✅ Se han cargado {len(datos_empresa)} años.")
else:
    st.sidebar.info("Esperando archivos PDF...")

# ============================================
# PANTALLA DE INICIO (FLECHA ANIMADA)
# ============================================
if not datos_empresa or len(datos_empresa) < 2:
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center;">
            <h1 style="color: #3B82F6; font-size: 3rem;">Sistema de Auditoría Senior</h1>
            <p style="font-size: 1.2rem; color: gray; margin-bottom: 30px;">Sube al menos 2 Modelos 200 en el panel lateral para comenzar el análisis.</p>
            <div class="start-arrow">⬅️</div>
            <p style="font-size: 1rem; color: #A0A0A0; margin-top: 20px;">Haz clic en "Browse files" en la barra de la izquierda</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================
# RENDERIZADO PRINCIPAL (SI HAY DATOS)
# ============================================
years = [d['year'] for d in datos_empresa]

accionistas_1 = datos_empresa[0]['accionistas_b2']
accionistas_2 = datos_empresa[1]['accionistas_b2']
accionistas_3 = datos_empresa[2]['accionistas_b2'] if len(datos_empresa) > 2 else accionistas_2

b2_status_ok = (accionistas_1 == accionistas_2 == accionistas_3)

ev_existencias = []
ev_acreedores = []
sirena_acreedores = False

for d in datos_empresa:
    ev_existencias.append(f"<b>{d['year']}:</b> {d['existencias_00138']:,.2f} €")
    ev_acreedores.append(f"<b>{d['year']}:</b> Celda 00239: {d['acreedores_00239']:,.2f} € | Celda 00240: {d['proveedores']:,.2f} €")
    if d['proveedores'] == 0 and d['aprovisionamientos'] > 5000:
        sirena_acreedores = True

st.title("💼 Informe de Auditoría Financiera y Riesgo")
st.markdown(f"**Periodo analizado:** {years[0]} - {years[-1]} | Datos extraídos del Modelo 200")
st.markdown("---")

st.subheader("🔍 1. Auditoría de Estructura y Desglose")
col_audit1, col_audit2 = st.columns(2)

with col_audit1:
    st.markdown("### B.2. Participaciones (Accionistas)")
    if b2_status_ok:
        st.markdown('<div class="alert-success">✅ Los accionistas (B.2) son los mismos en todos los ejercicios.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-critical">🔴 SIRENA ROJA: Cambio de accionistas (B.2) detectado.</div>', unsafe_allow_html=True)
    
    with st.expander("Ver NIFs extraídos de B.2"):
        for d in datos_empresa:
            st.write(f"**{d['year']}:** {d['accionistas_b2']}")
        
with col_audit2:
    st.markdown("### Desglose de Existencias y Acreedores")
    if sirena_acreedores:
        st.markdown('<div class="alert-critical">🔴 SIRENA ROJA: Proveedores (00240) a cero, pero con Aprovisionamientos. Inconsistencia grave.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">✅ Saldos de acreedores coherentes.</div>', unsafe_allow_html=True)
        
    st.markdown("**Evolución de Existencias (00138):**")
    for e in ev_existencias: st.markdown(e, unsafe_allow_html=True)
    
    st.markdown("**Evolución de Acreedores (00239-00249):**")
    for a in ev_acreedores: st.caption(a, unsafe_allow_html=True)

st.markdown("---")

st.subheader("📊 2. Análisis de Masas Patrimoniales")
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
    fig.add_trace(go.Bar(name='Ingresos', x=years, y=[d['ingresos'] for d in datos_empresa], marker_color='#3B82F6'))
    fig.add_trace(go.Bar(name='Resultado Neto', x=years, y=[d['resultado_neto'] for d in datos_empresa], marker_color='#10B981'))
    fig.update_layout(title='Evolución de Ingresos y Resultados', barmode='group', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
    
with col_g2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(name='Activo Total', x=years, y=[d['activo_total'] for d in datos_empresa], mode='lines+markers', line=dict(color='#EF4444', width=3)))
    fig.add_trace(go.Scatter(name='Patrimonio Neto', x=years, y=[d['patrimonio_neto'] for d in datos_empresa], mode='lines+markers', line=dict(color='#3B82F6', width=3)))
    fig.update_layout(title='Evolución del Balance', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("🧠 3. Informe Ejecutivo redactado por IA Senior")
if st.button("Generar Informe Ejecutivo con IA"):
    if not api_key:
        st.error("Introduce tu API Key de OpenAI en la barra lateral.")
    else:
        with st.spinner("Redactando informe con 22 años de experiencia..."):
            summary = ""
            for d in datos_empresa:
                summary += f"Año {d['year']}: Ingresos: {d['ingresos']}, RN: {d['resultado_neto']}, Pasivo Corriente: {d['pasivo_corriente']}, Proveedores: {d['proveedores']}, Existencias: {d['existencias_00138']}.\n"
            rules = f"B.2 iguales: {b2_status_ok}. Sirena Proveedores: {sirena_acreedores}."
            ai_text = generate_ai_report(api_key, summary, rules)
            st.markdown(f'<div class="ai-report">{ai_text}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px;'>
    <p>Auditoría Financiera Senior | Desarrollado con estándares de 22 años de experiencia.</p>
    <p>Esta web no guarda ninguno de los documentos subidos. Análisis 100% anónimo.</p>
</div>
""", unsafe_allow_html=True)