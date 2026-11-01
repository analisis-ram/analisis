import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pdfplumber
import re
import io

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Análisis Financiero Modelo 200",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        with st.spinner(f"Procesando {file.name}..."):
            try:
                extracted = extract_data_from_pdf(file)
                if extracted['ingresos'] > 0 or extracted['activo_total'] > 0:
                    datos_empresa.append(extracted)
                else:
                    st.sidebar.warning(f"No se pudieron extraer datos válidos de {file.name}")
            except Exception as e:
                st.sidebar.error(f"Error leyendo {file.name}: {e}")
    
    if datos_empresa:
        datos_empresa = sorted(datos_empresa, key=lambda x: x['year'])
        st.sidebar.success(f"¡{len(datos_empresa)} ejercicios cargados!")
    else:
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
    fondo_maniobra.append(activo_total[i] - pasivo_no_corriente[i] - pasivo_corriente[i] - patrimonio_neto[i])
if not uploaded_files and len(datos_empresa) == 3:
    fondo_maniobra = [459340, 934553, 994129]

# ============================================
# CÁLCULO DE RATIOS
# ============================================
sector = { 'Margen Bruto %': 57.88, 'EBIT/Ventas %': 5.77, 'RN/Ventas %': 4.08, 'PMC (días)': 56.92, 'PMP (días)': 43.45, 'Endeudamiento %': 13.55, 'ROA %': 6.09, 'ROE %': 12.67, 'Liquidez General': 1.83, 'Fondo Maniobra/Activo %': 33.41, 'Autonomía Financiera': 0.50 }

def calc_ratios(i):
    ventas = ingresos[i] if ingresos[i] > 0 else 1
    ac = clientes[i] + existencias[i] + tesoreria[i]
    pc = pasivo_corriente[i]
    pn = patrimonio_neto[i]
    pnc = pasivo_no_corriente[i]
    total_pasivo = pn + pnc + pc
    
    liquidez = ac / pc if pc > 0 else 0
    endeudamiento = (pnc + pc) / total_pasivo * 100 if total_pasivo != 0 else 0
    autonomia = pn / total_pasivo if total_pasivo != 0 else 0
    pmc = clientes[i] / (ventas * 1.21) * 365 if ventas > 0 else 0
    aprox = aprovisionamientos[i] if aprovisionamientos[i] > 0 else 1
    pmp = abs(proveedores[i]) / (aprox * 1.21) * 365 if proveedores[i] != 0 else 0
    ebitda = resultado_explotacion[i] + amortizacion[i]
    
    return {
        'margen_bruto': (ventas - aprovisionamientos[i]) / ventas * 100 if ventas > 0 else 0,
        'ebit_ventas': resultado_explotacion[i] / ventas * 100 if ventas > 0 else 0,
        'rn_ventas': resultado_neto[i] / ventas * 100 if ventas > 0 else 0,
        'ebitda': ebitda,
        'ebitda_margen': ebitda / ventas * 100 if ventas > 0 else 0,
        'roa': resultado_neto[i] / activo_total[i] * 100 if activo_total[i] > 0 else 0,
        'roe': resultado_neto[i] / pn * 100 if pn > 0 else 0,
        'liquidez': liquidez,
        'autonomia': autonomia,
        'endeudamiento': endeudamiento,
        'fm_activo': fondo_maniobra[i] / activo_total[i] * 100 if activo_total[i] > 0 else 0,
        'pmc': pmc,
        'pmp': pmp,
        'clientes_activo': clientes[i] / activo_total[i] * 100 if activo_total[i] > 0 else 0,
        'existencias_activo': existencias[i] / activo_total[i] * 100 if activo_total[i] > 0 else 0,
        'deuda_ebitda': deuda_bancaria[i] / ebitda if ebitda > 0 else 0,
    }

ratios = [calc_ratios(i) for i in range(len(datos_empresa))]

# ============================================
# SIDEBAR - SELECCIÓN DE AÑO
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Seleccionar ejercicio")
if years:
    year_sel = st.sidebar.selectbox("", years, index=len(years)-1)
    idx = years.index(year_sel)
else:
    st.error("No hay datos disponibles para mostrar.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚦 Leyenda")
st.sidebar.markdown("🔴 **Crítico** - Requiere acción inmediata")
st.sidebar.markdown("🟠 **Advertencia** - Vigilar")
st.sidebar.markdown("✅ **Correcto** - Sin problemas")

# ============================================
# HEADER Y BOTONES ESTILO "SERVIPDF"
# ============================================
col_title, col_actions = st.columns([6.5, 3.5])

with col_title:
    st.title("📊 Diagnóstico Financiero Automatizado")
    st.markdown(f"### Análisis del ejercicio **{year_sel}** | Datos extraídos del Modelo 200")

with col_actions:
    # Banner superior
    st.markdown("""
    <div style="background-color: #4CAF50; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        <span style="color: #D32F2F; font-weight: 900; font-size: 15px; text-transform: uppercase;">
            Su empresa tiene solución, contacten con un profesional
        </span>
    </div>
    """, unsafe_allow_html=True)

    # HTML y CSS de los botones (Réplica exacta de la foto)
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 12px; align-items: center;">
        
        <!-- Botón WhatsApp -->
        <a href="https://wa.me/34644247796" target="_blank" style="
            display: flex; align-items: center; justify-content: center;
            background-color: #22c55e; /* Verde brillante */
            color: white; text-decoration: none;
            padding: 12px 24px; border-radius: 50px;
            font-weight: 600; font-size: 16px; font-family: sans-serif;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.1)';">
            
            <svg style="width: 22px; height: 22px; margin-right: 10px;" viewBox="0 0 24 24" fill="white">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
            Contactar con el creador
        </a>

        <!-- Botón Email (Abre Gmail en nueva pestaña) -->
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=cuadrarcuentas@gmail.com&su=Consulta%20desde%20la%20App%20de%20Análisis" target="_blank" style="
            display: flex; align-items: center; justify-content: center;
            background-color: #3b82f6; /* Azul brillante */
            color: white; text-decoration: none;
            padding: 12px 24px; border-radius: 50px;
            font-weight: 600; font-size: 16px; font-family: sans-serif;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.1)';">
            
            <svg style="width: 22px; height: 22px; margin-right: 10px;" viewBox="0 0 24 24" fill="white">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
            cuadrarcuentas@gmail.com
        </a>
        
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# KPIs PRINCIPALES
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta = (ingresos[idx] - ingresos[idx-1]) / ingresos[idx-1] * 100 if idx > 0 and ingresos[idx-1] != 0 else 0
    st.metric("💰 Ingresos", f"{ingresos[idx]:,.0f} €", f"{delta:+.1f}%")
with col2:
    delta = (resultado_neto[idx] - resultado_neto[idx-1]) / abs(resultado_neto[idx-1]) * 100 if idx > 0 and resultado_neto[idx-1] != 0 else 0
    st.metric("📈 Resultado Neto", f"{resultado_neto[idx]:,.0f} €", f"{delta:+.1f}%")
with col3:
    delta = (activo_total[idx] - activo_total[idx-1]) / activo_total[idx-1] * 100 if idx > 0 and activo_total[idx-1] != 0 else 0
    st.metric("🏢 Activo Total", f"{activo_total[idx]:,.0f} €", f"{delta:+.1f}%")
with col4:
    delta = (patrimonio_neto[idx] - patrimonio_neto[idx-1]) / patrimonio_neto[idx-1] * 100 if idx > 0 and patrimonio_neto[idx-1] != 0 else 0
    st.metric("🏦 Patrimonio Neto", f"{patrimonio_neto[idx]:,.0f} €", f"{delta:+.1f}%")
with col5:
    st.metric("👥 Empleados", "N/A", "N/A")

# ============================================
# SIRENAS ROJAS - ALERTAS DINÁMICAS
# ============================================
st.markdown("---")
st.subheader("🚨 SIRENAS ROJAS Y ALERTAS CRÍTICAS")

alertas = []
advertencias = []
fortalezas = []

if pasivo_corriente[idx] < 0:
    alertas.append(f"🔴 **PASIVO CORRIENTE NEGATIVO ({pasivo_corriente[idx]:,.0f} €)** — Error contable GRAVE. Indica que no se están registrando correctamente las obligaciones a corto plazo.")
if proveedores[idx] == 0 and aprovisionamientos[idx] > 10000:
    alertas.append(f"🔴 **PROVEEDORES Y ACREEDORES = 0 €** — Imposible que una empresa con {aprovisionamientos[idx]:,.0f} € en aprovisionamientos no tenga saldo pendiente. Indica pago al contado o error contable.")
elif proveedores[idx] < 0:
    alertas.append(f"🔴 **PROVEEDORES Y ACREEDORES NEGATIVOS ({proveedores[idx]:,.0f} €)** — Saldo anómalo que indica error contable.")

pmc_val = ratios[idx]['pmc']
if pmc_val > 100:
    alertas.append(f"🔴 **PERIODO MEDIO DE COBRO MUY ELEVADO ({pmc_val:.0f} días)** — La empresa financia a sus clientes con sus propios recursos. Clientes: {clientes[idx]:,.0f} €.")
elif pmc_val > 60:
    advertencias.append(f"🟠 **Periodo medio de cobro elevado ({pmc_val:.0f} días)** — Superior a la media del sector.")

if ratios[idx]['pmp'] == 0 and proveedores[idx] == 0:
    alertas.append(f"🔴 **PERIODO MEDIO DE PAGO = 0 DÍAS** — Paga a proveedores al contado mientras cobra a {pmc_val:.0f} días.")

if ratios[idx]['existencias_activo'] > 15:
    alertas.append(f"🔴 **EXISTENCIAS ELEVADAS ({existencias[idx]:,.0f} €)** — Verificar control físico de inventario y posible obsolescencia.")

if ratios[idx]['clientes_activo'] > 30:
    alertas.append(f"🔴 **CLIENTES > 30% DEL ACTIVO ({ratios[idx]['clientes_activo']:.1f}%)** — Alta concentración en derechos de cobro.")

if tesoreria[idx] > 150000:
    advertencias.append(f"🟠 **TESORERÍA OCIOSA ({tesoreria[idx]:,.0f} €)** — Fondos sin remuneración.")

if abs(base_imponible[idx] - resultado_neto[idx]) > 1000:
    advertencias.append(f"🟠 **BASE IMPONIBLE DIFIERE DEL RESULTADO NETO** — Hay ajustes fiscales significativos.")

if ratios[idx]['autonomia'] > 0.6:
    fortalezas.append(f"✅ **Autonomía Financiera {ratios[idx]['autonomia']:.2f}** — Empresa muy capitalizada.")
if ratios[idx]['roe'] > 10:
    fortalezas.append(f"✅ **ROE {ratios[idx]['roe']:.1f}%** — Buena rentabilidad.")
if ratios[idx]['margen_bruto'] > 50:
    fortalezas.append(f"✅ **Margen Bruto {ratios[idx]['margen_bruto']:.1f}%** — Excelente capacidad de generar valor añadido.")

if not alertas and not advertencias:
    st.success("✅ No se han detectado alertas críticas con los datos disponibles.")
for a in alertas: st.error(a)
for a in advertencias: st.warning(a)
for a in fortalezas: st.success(a)

# ============================================
# GRÁFICOS
# ============================================
if len(years) > 0:
    st.markdown("---")
    st.subheader("📈 EVOLUCIÓN FINANCIERA")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ingresos', x=years, y=ingresos, marker_color='#1f77b4'))
        fig.add_trace(go.Bar(name='Resultado Neto', x=years, y=resultado_neto, marker_color='#2ca02c'))
        fig.update_layout(title='Ingresos vs Resultado Neto (€)', barmode='group', height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02))
        st.plotly_chart(fig, use_container_width=True)
    with col_g2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='Activo Total', x=years, y=activo_total, mode='lines+markers', line=dict(color='#d62728', width=3)))
        fig.add_trace(go.Scatter(name='Patrimonio Neto', x=years, y=patrimonio_neto, mode='lines+markers', line=dict(color='#2ca02c', width=3)))
        fig.add_trace(go.Scatter(name='Pasivo Corriente', x=years, y=pasivo_corriente, mode='lines+markers', line=dict(color='#ff7f0e', width=3, dash='dash')))
        fig.update_layout(title='Evolución del Balance (€)', height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02))
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# ANÁLISIS VERTICAL Y RATIOS
# ============================================
st.markdown("---")
st.subheader("📋 ANÁLISIS VERTICAL DEL BALANCE")
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown("**ACTIVO**")
    activo_nc = activo_total[idx] - (clientes[idx] + existencias[idx] + tesoreria[idx])
    activo_data = pd.DataFrame({'Partida': ['Activo No Corriente', 'Clientes', 'Existencias', 'Tesorería'], 'Importe': [activo_nc, clientes[idx], existencias[idx], tesoreria[idx]]})
    activo_data['% s/ Total'] = activo_data['Importe'] / activo_total[idx] * 100
    activo_data['Importe'] = activo_data['Importe'].apply(lambda x: f"{x:,.0f} €")
    activo_data['% s/ Total'] = activo_data['% s/ Total'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(activo_data, hide_index=True, use_container_width=True)
with col_b2:
    st.markdown("**PASIVO**")
    total_pasivo = patrimonio_neto[idx] + pasivo_no_corriente[idx] + pasivo_corriente[idx]
    pasivo_data = pd.DataFrame({'Partida': ['Patrimonio Neto', 'Pasivo No Corriente', 'Pasivo Corriente', '  - Proveedores', '  - Deuda Bancaria'], 'Importe': [patrimonio_neto[idx], pasivo_no_corriente[idx], pasivo_corriente[idx], proveedores[idx], deuda_bancaria[idx]]})
    pasivo_data['% s/ Total'] = pasivo_data['Importe'] / total_pasivo * 100
    pasivo_data['Importe'] = pasivo_data['Importe'].apply(lambda x: f"{x:,.0f} €")
    pasivo_data['% s/ Total'] = pasivo_data['% s/ Total'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(pasivo_data, hide_index=True, use_container_width=True)

st.markdown("---")
st.subheader("📊 RATIOS CLAVE")
ratios_df = pd.DataFrame({
    'Ratio': ['Margen Bruto (%)', 'EBIT / Ventas (%)', 'Resultado Neto / Ventas (%)', 'EBITDA (€)', 'Margen EBITDA (%)', 'ROA (%)', 'ROE (%)', 'Liquidez General', 'Autonomía Financiera', 'Endeudamiento (%)', 'Fondo Maniobra / Activo (%)', 'Periodo Medio Cobro (días)', 'Periodo Medio Pago (días)'],
    'Valor': [f"{ratios[idx]['margen_bruto']:.1f}", f"{ratios[idx]['ebit_ventas']:.1f}", f"{ratios[idx]['rn_ventas']:.1f}", f"{ratios[idx]['ebitda']:,.0f}", f"{ratios[idx]['ebitda_margen']:.1f}", f"{ratios[idx]['roa']:.1f}", f"{ratios[idx]['roe']:.1f}", f"{ratios[idx]['liquidez']:.2f}", f"{ratios[idx]['autonomia']:.2f}", f"{ratios[idx]['endeudamiento']:.1f}", f"{ratios[idx]['fm_activo']:.1f}", f"{ratios[idx]['pmc']:.0f}", f"{ratios[idx]['pmp']:.0f}"],
    'Sector (INFORMA)': ["57.9", "5.8", "4.1", "—", "—", "6.1", "12.7", "1.83", "0.50", "13.6", "33.4", "57", "43"]
})
def eval_ratio(name, val_str):
    try:
        val = float(val_str)
        if 'Margen' in name or 'ROA' in name or 'ROE' in name: return '✅ Bien' if val > 5 else '⚠️ Bajo'
        elif 'Cobro' in name: return '🔴 Crítico' if val > 90 else '✅ Bien'
        elif 'Pago' in name: return '🔴 Crítico' if val == 0 else '✅ Bien'
        elif 'Liquidez' in name: return '✅ Bien' if val > 1.5 else '🔴 Bajo'
        elif 'Endeudamiento' in name: return '✅ Bajo' if val < 30 else '⚠️ Alto'
        else: return '✅'
    except: return 'ℹ️'
ratios_df['Evaluación'] = [eval_ratio(row['Ratio'], row['Valor']) for _, row in ratios_df.iterrows()]
st.dataframe(ratios_df, hide_index=True, use_container_width=True)

# ============================================
# DATOS CRUDOS
# ============================================
with st.expander("📋 Ver datos extraídos (Modelo 200)"):
    if datos_empresa:
        df_mostrar = pd.DataFrame(datos_empresa).T
        df_mostrar.columns = years
        df_mostrar.index = ['Año', 'Ingresos', 'Aprovisionamientos', 'Gastos Personal', 'Amortización', 'Resultado Explotación', 'Resultado Neto', 'Activo Total', 'Patrimonio Neto', 'Pasivo No Corriente', 'Pasivo Corriente', 'Clientes', 'Existencias', 'Tesorería', 'Proveedores', 'Deuda Bancaria', 'Base Imponible']
        for col in df_mostrar.columns:
            df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:,.2f} €" if isinstance(x, (int, float)) else x)
        st.dataframe(df_mostrar, use_container_width=True)

# ============================================
# FOOTER (AVISO DE PRIVACIDAD ACTUALIZADO)
# ============================================
st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #333; font-size: 13px; margin-top: 40px; padding: 20px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;'>
    <h4 style="color: #0056b3; margin-bottom: 15px;">🔒 Política de Privacidad y Tratamiento de Datos</h4>
    <p><b>Esta web no guarda ninguno de los documentos subidos.</b></p>
    <p>El modelo está diseñado para extraer los datos de forma <b>anónima</b> y no almacenamos ningún dato en ningún servidor.</p>
    <p>Solo si usted desea puede contactar con nosotros para obtener opiniones y recomendaciones personalizadas y adaptadas a su empresa.</p>
    <hr style="border-top: 1px solid #ccc; width: 50%; margin: 20px auto;">
    <p style="color: #777;"><em>La información contenida es confidencial y para uso interno.</em></p>
</div>
""", unsafe_allow_html=True)