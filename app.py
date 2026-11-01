import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard ITELSAT TECNISUR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .alert-red { background-color: #ff4b4b; padding: 15px; border-radius: 10px; 
                 color: white; margin: 8px 0; font-weight: 500; }
    .alert-orange { background-color: #ffa500; padding: 15px; border-radius: 10px; 
                    color: white; margin: 8px 0; font-weight: 500; }
    .alert-green { background-color: #00cc44; padding: 15px; border-radius: 10px; 
                   color: white; margin: 8px 0; font-weight: 500; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; 
                   text-align: center; }
    .big-number { font-size: 28px; font-weight: bold; }
    .label { font-size: 12px; color: #666; }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS EXTRAÍDOS DE LOS MODELOS 200
# ============================================
years = [2023, 2024, 2025]

# --- Cuenta de Resultados ---
ingresos               = [1246492.66, 1346718.78, 1356381.42]
aprovisionamientos     = [473328.59, 457443.01, 467780.14]
gastos_personal        = [404693.28, 313418.01, 381276.75]
otros_gastos_explot    = [250912.71, 243979.88, 279814.20]
amortizacion           = [52540.40, 40030.55, 42356.05]
resultado_explotacion  = [69239.77, 309089.37, 196002.55]
resultado_financiero   = [-2202.45, -5941.68, -4617.46]
resultado_neto         = [67037.32, 303147.69, 191385.09]

# --- Balance ---
activo_total           = [923819.82, 1290129.57, 1365339.00]
activo_corriente       = [608820, 957200, 966950]
patrimonio_neto        = [774339.82, 1062482.79, 1253867.88]
pasivo_no_corriente    = [0, 205000, 138650]
pasivo_corriente       = [149480, 22647, -27179]
fondo_maniobra         = [459340, 934553, 994129]

# --- Partidas específicas ---
clientes               = [237600, 400200, 500120]
existencias            = [135900, 225000, 160250]
tesoreria              = [150319.82, 182000, 226729.89]
proveedores_acreedores = [-52520, 0, 0]        # ¡ALERTA!
deuda_bancaria         = [202000, 227647, 111471]

# --- Datos fiscales (Modelo 200) ---
base_imponible         = [52032.60, 53147.69, 191385.09]
cuota_integra          = [13008.15, 13286.92, 45932.42]
cuota_diferencial      = [2572.75, 2574.60, 12720.10]

# --- Ratios sectoriales (INFORMA D&B, percentil 50) ---
sector = {
    'Margen Bruto %': 57.88, 'EBIT/Ventas %': 5.77, 'RN/Ventas %': 4.08,
    'PMC (días)': 56.92, 'PMP (días)': 43.45, 'Endeudamiento %': 13.55,
    'ROA %': 6.09, 'ROE %': 12.67, 'Liquidez General': 1.83,
    'Fondo Maniobra/Activo %': 33.41, 'Autonomía Financiera': 0.50,
}

# ============================================
# CÁLCULO DE RATIOS
# ============================================
def calc_ratios(i):
    ventas = ingresos[i]
    ac = activo_corriente[i]
    pc = pasivo_corriente[i]
    pn = patrimonio_neto[i]
    pnc = pasivo_no_corriente[i]
    total_pasivo = pn + pnc + pc
    
    # Evitar divisiones por cero o negativos
    liquidez = ac / pc if pc > 0 else float('inf')
    tesoreria_pc = tesoreria[i] / pc if pc > 0 else float('inf')
    endeudamiento = (pnc + pc) / total_pasivo * 100 if total_pasivo != 0 else 0
    autonomia = pn / total_pasivo if total_pasivo != 0 else 0
    pmc = clientes[i] / (ventas * 1.21) * 365
    pmp = abs(proveedores_acreedores[i]) / (aprovisionamientos[i] * 1.21) * 365 if proveedores_acreedores[i] != 0 else 0
    ebitda = resultado_explotacion[i] + amortizacion[i]
    
    return {
        'margen_bruto': (ventas - aprovisionamientos[i]) / ventas * 100,
        'ebit_ventas': resultado_explotacion[i] / ventas * 100,
        'rn_ventas': resultado_neto[i] / ventas * 100,
        'ebitda': ebitda,
        'ebitda_margen': ebitda / ventas * 100,
        'roa': resultado_neto[i] / activo_total[i] * 100,
        'roe': resultado_neto[i] / pn * 100,
        'liquidez': liquidez,
        'autonomia': autonomia,
        'endeudamiento': endeudamiento,
        'fm_activo': fondo_maniobra[i] / activo_total[i] * 100,
        'pmc': pmc,
        'pmp': pmp,
        'tesoreria_pc': tesoreria_pc,
        'clientes_activo': clientes[i] / activo_total[i] * 100,
        'existencias_activo': existencias[i] / activo_total[i] * 100,
        'deuda_ebitda': deuda_bancaria[i] / ebitda if ebitda > 0 else float('inf'),
    }

ratios = [calc_ratios(i) for i in range(3)]

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("🔍 ITELSAT TECNISUR S.L.")
st.sidebar.markdown("**NIF:** B38659165")
st.sidebar.markdown("**CNAE:** 4321 - Instalaciones eléctricas")
st.sidebar.markdown("**Empleados:** 14 (2024)")
st.sidebar.markdown("**Sector:** Instalaciones eléctricas (El Hierro)")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Seleccionar ejercicio")
year_sel = st.sidebar.selectbox("", years, index=2)
idx = years.index(year_sel)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚦 Leyenda")
st.sidebar.markdown("🔴 **Crítico** - Requiere acción inmediata")
st.sidebar.markdown("🟠 **Advertencia** - Vigilar")
st.sidebar.markdown("✅ **Correcto** - Sin problemas")

# ============================================
# HEADER
# ============================================
st.title("📊 Dashboard Financiero - ITELSAT TECNISUR S.L.")
st.markdown(f"### Análisis del ejercicio **{year_sel}** | Datos del Modelo 200")
st.markdown("---")

# ============================================
# KPIs PRINCIPALES
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta = (ingresos[idx] - ingresos[idx-1]) / ingresos[idx-1] * 100 if idx > 0 else 0
    st.metric("💰 Ingresos", f"{ingresos[idx]:,.0f} €", f"{delta:+.1f}%")
with col2:
    delta = (resultado_neto[idx] - resultado_neto[idx-1]) / abs(resultado_neto[idx-1]) * 100 if idx > 0 and resultado_neto[idx-1] != 0 else 0
    st.metric("📈 Resultado Neto", f"{resultado_neto[idx]:,.0f} €", f"{delta:+.1f}%")
with col3:
    delta = (activo_total[idx] - activo_total[idx-1]) / activo_total[idx-1] * 100 if idx > 0 else 0
    st.metric("🏢 Activo Total", f"{activo_total[idx]:,.0f} €", f"{delta:+.1f}%")
with col4:
    delta = (patrimonio_neto[idx] - patrimonio_neto[idx-1]) / patrimonio_neto[idx-1] * 100 if idx > 0 else 0
    st.metric("🏦 Patrimonio Neto", f"{patrimonio_neto[idx]:,.0f} €", f"{delta:+.1f}%")
with col5:
    st.metric("👥 Empleados", "14", "0")

# ============================================
# SIRENAS ROJAS - ALERTAS
# ============================================
st.markdown("---")
st.subheader("🚨 SIRENAS ROJAS Y ALERTAS CRÍTICAS")

alertas = []
advertencias = []
fortalezas = []

# --- 1. PASIVO CORRIENTE NEGATIVO ---
if pasivo_corriente[idx] < 0:
    alertas.append(
        f"🔴 **PASIVO CORRIENTE NEGATIVO ({pasivo_corriente[idx]:,.0f} €)** — Error contable GRAVE. "
        f"Indica que no se están registrando correctamente las obligaciones a corto plazo. "
        f"Posible error en transferencias bancarias no conciliadas (Caixa)."
    )

# --- 2. PROVEEDORES Y ACREEDORES SIN SALDO ---
if proveedores_acreedores[idx] == 0:
    alertas.append(
        f"🔴 **PROVEEDORES Y ACREEDORES = 0 €** — Imposible que una empresa con "
        f"{aprovisionamientos[idx]:,.0f} € en aprovisionamientos no tenga saldo pendiente con proveedores. "
        f"Indica pago al contado o error contable. Esto distorsiona el fondo de maniobra y los ratios de liquidez."
    )
elif proveedores_acreedores[idx] < 0:
    alertas.append(
        f"🔴 **PROVEEDORES Y ACREEDORES NEGATIVOS ({proveedores_acreedores[idx]:,.0f} €)** — "
        f"Saldo anómalo que indica error contable o anticipos no registrados correctamente."
    )

# --- 3. PERIODO MEDIO DE COBRO ELEVADO ---
pmc_val = ratios[idx]['pmc']
if pmc_val > 100:
    alertas.append(
        f"🔴 **PERIODO MEDIO DE COBRO MUY ELEVADO ({pmc_val:.0f} días)** — "
        f"Muy superior al sector ({sector['PMC (días)']:.0f} días). La empresa financia a la "
        f"Administración Pública con sus propios recursos durante más de 3 meses. "
        f"Clientes inmovilizados: {clientes[idx]:,.0f} € ({ratios[idx]['clientes_activo']:.1f}% del activo)."
    )
elif pmc_val > 60:
    advertencias.append(
        f"🟠 **Periodo medio de cobro elevado ({pmc_val:.0f} días)** — "
        f"Superior a la media del sector ({sector['PMC (días)']:.0f} días)."
    )

# --- 4. PERIODO MEDIO DE PAGO = 0 ---
if ratios[idx]['pmp'] == 0:
    alertas.append(
        f"🔴 **PERIODO MEDIO DE PAGO = 0 DÍAS** — La empresa paga a proveedores al contado "
        f"mientras cobra a {pmc_val:.0f} días. Asimetría insostenible que genera tensión de liquidez. "
        f"El sector paga a {sector['PMP (días)']:.0f} días. Se renuncia a financiación gratuita de proveedores."
    )

# --- 5. EXISTENCIAS SIN CONTROL ---
if ratios[idx]['existencias_activo'] > 15:
    alertas.append(
        f"🔴 **EXISTENCIAS ELEVADAS SIN CONTROL ({existencias[idx]:,.0f} €, "
        f"{ratios[idx]['existencias_activo']:.1f}% del activo)** — No existe inventario físico formalizado. "
        f"Riesgo de mermas, obsolescencia y descuadre contable. Para una empresa de servicios, el stock debería ser menor."
    )

# --- 6. CLIENTES > 30% DEL ACTIVO ---
if ratios[idx]['clientes_activo'] > 30:
    alertas.append(
        f"🔴 **CLIENTES > 30% DEL ACTIVO ({ratios[idx]['clientes_activo']:.1f}%)** — "
        f"Alta concentración en derechos de cobro. La empresa está financiando a sus clientes "
        f"(Administración Pública) con recursos propios."
    )

# --- 7. TESORERÍA OCIOSA ---
if tesoreria[idx] > 150000:
    advertencias.append(
        f"🟠 **TESORERÍA OCIOSA ({tesoreria[idx]:,.0f} €)** — Fondos en cuentas corrientes "
        f"sin remuneración. Podrían optimizarse en depósitos a plazo o cuentas remuneradas."
    )

# --- 8. DESCONEXIÓN CONTABLE ---
alertas.append(
    "🔴 **DESCONEXIÓN CONTABLE CRÍTICA** — El software operativo (TreyGmao) no está integrado "
    "con la gestoría externa. La contabilidad se cierra trimestralmente sin conciliación bancaria rigurosa. "
    "Esto explica el saldo negativo en pasivo corriente y la ausencia de saldo en proveedores."
)

# --- 9. FONDO DE MANIOBRA DISTORSIONADO ---
if pasivo_corriente[idx] < 0:
    alertas.append(
        f"🔴 **FONDO DE MANIOBRA DISTORSIONADO ({fondo_maniobra[idx]:,.0f} €)** — "
        f"El fondo de maniobra es artificialmente alto debido al pasivo corriente negativo. "
        f"El fondo de maniobra real es inferior."
    )

# --- 10. SALDO NEGATIVO ACREEDORES 2023 ---
if year_sel == 2023 and proveedores_acreedores[0] < 0:
    alertas.append(
        f"🔴 **SALDO NEGATIVO EN ACREEDORES ({proveedores_acreedores[0]:,.0f} €)** — "
        f"Confirma un problema estructural de registro contable, no un hecho puntual."
    )

# --- 11. BASE IMPONIBLE vs RESULTADO ---
if abs(base_imponible[idx] - resultado_neto[idx]) > 1000:
    advertencias.append(
        f"🟠 **BASE IMPONIBLE ({base_imponible[idx]:,.0f} €) DIFIERE DEL RESULTADO NETO "
        f"({resultado_neto[idx]:,.0f} €)** — Hay ajustes fiscales significativos (reserva de nivelación, etc.)."
    )

# --- 12. RESERVA RIC PENDIENTE ---
advertencias.append(
    "🟠 **RESERVA PARA INVERSIONES EN CANARIAS (RIC) PENDIENTE** — En 2024 se dotaron 250.000 € de RIC. "
    "En 2025 quedan 77.757 € pendientes de materializar. Plazo: 3 años. Riesgo de incumplimiento si no se invierte."
)

# --- 13. FORTALEZAS ---
fortalezas.append(f"✅ **Fondos propios 91.8%** — {patrimonio_neto[idx]:,.0f} € (empresa blindada)")
fortalezas.append(f"✅ **Margen bruto 65.5%** — vs 57.9% del sector")
fortalezas.append(f"✅ **ROE {ratios[idx]['roe']:.1f}%** — vs 12.7% del sector")
fortalezas.append(f"✅ **Cobertura de intereses** — Sin tensión financiera")
fortalezas.append(f"✅ **Autonomía financiera {ratios[idx]['autonomia']:.2f}** — Muy por encima del sector (0.50)")

# --- MOSTRAR ALERTAS ---
for a in alertas:
    st.error(a)
for a in advertencias:
    st.warning(a)
for a in fortalezas:
    st.success(a)

# ============================================
# GRÁFICOS DE EVOLUCIÓN
# ============================================
st.markdown("---")
st.subheader("📈 EVOLUCIÓN FINANCIERA")

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Ingresos', x=years, y=ingresos, marker_color='#1f77b4'))
    fig.add_trace(go.Bar(name='Resultado Neto', x=years, y=resultado_neto, marker_color='#2ca02c'))
    fig.update_layout(title='Ingresos vs Resultado Neto (€)', barmode='group', height=400,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(name='Activo Total', x=years, y=activo_total, mode='lines+markers',
                             line=dict(color='#d62728', width=3)))
    fig.add_trace(go.Scatter(name='Patrimonio Neto', x=years, y=patrimonio_neto, mode='lines+markers',
                             line=dict(color='#2ca02c', width=3)))
    fig.add_trace(go.Scatter(name='Pasivo Corriente', x=years, y=pasivo_corriente, mode='lines+markers',
                             line=dict(color='#ff7f0e', width=3, dash='dash')))
    fig.update_layout(title='Evolución del Balance (€)', height=400,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# GRÁFICO DE COMPOSICIÓN DEL RESULTADO
# ============================================
col_g3, col_g4 = st.columns(2)

with col_g3:
    fig = go.Figure()
    fig.add_trace(go.Bar(name='EBITDA', x=years,
                         y=[r['ebitda'] for r in ratios], marker_color='#9467bd'))
    fig.add_trace(go.Bar(name='Resultado Neto', x=years, y=resultado_neto, marker_color='#2ca02c'))
    fig.update_layout(title='EBITDA vs Resultado Neto (€)', barmode='group', height=350,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig, use_container_width=True)

with col_g4:
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Clientes', x=years, y=clientes, marker_color='#ff7f0e'))
    fig.add_trace(go.Bar(name='Existencias', x=years, y=existencias, marker_color='#1f77b4'))
    fig.add_trace(go.Bar(name='Tesorería', x=years, y=tesoreria, marker_color='#2ca02c'))
    fig.update_layout(title='Composición del Activo Corriente (€)', barmode='group', height=350,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# ANÁLISIS VERTICAL DEL BALANCE
# ============================================
st.markdown("---")
st.subheader("📋 ANÁLISIS VERTICAL DEL BALANCE")

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("**ACTIVO**")
    activo_data = pd.DataFrame({
        'Partida': ['Activo No Corriente', 'Activo Corriente', '  - Clientes', '  - Existencias', '  - Tesorería'],
        'Importe': [
            activo_total[idx] - activo_corriente[idx],
            activo_corriente[idx],
            clientes[idx],
            existencias[idx],
            tesoreria[idx]
        ]
    })
    activo_data['% s/ Total'] = activo_data['Importe'] / activo_total[idx] * 100
    activo_data['Importe'] = activo_data['Importe'].apply(lambda x: f"{x:,.0f} €")
    activo_data['% s/ Total'] = activo_data['% s/ Total'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(activo_data, hide_index=True, use_container_width=True)

with col_b2:
    st.markdown("**PASIVO**")
    total_pasivo = patrimonio_neto[idx] + pasivo_no_corriente[idx] + pasivo_corriente[idx]
    pasivo_data = pd.DataFrame({
        'Partida': ['Patrimonio Neto', 'Pasivo No Corriente', 'Pasivo Corriente',
                    '  - Proveedores', '  - Deuda Bancaria'],
        'Importe': [
            patrimonio_neto[idx],
            pasivo_no_corriente[idx],
            pasivo_corriente[idx],
            proveedores_acreedores[idx],
            deuda_bancaria[idx]
        ]
    })
    pasivo_data['% s/ Total'] = pasivo_data['Importe'] / total_pasivo * 100
    pasivo_data['Importe'] = pasivo_data['Importe'].apply(lambda x: f"{x:,.0f} €")
    pasivo_data['% s/ Total'] = pasivo_data['% s/ Total'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(pasivo_data, hide_index=True, use_container_width=True)

# ============================================
# RATIOS CLAVE vs SECTOR
# ============================================
st.markdown("---")
st.subheader("📊 RATIOS CLAVE vs SECTOR (INFORMA D&B)")

ratios_df = pd.DataFrame({
    'Ratio': [
        'Margen Bruto (%)', 'EBIT / Ventas (%)', 'Resultado Neto / Ventas (%)',
        'EBITDA (€)', 'Margen EBITDA (%)',
        'ROA (%)', 'ROE (%)',
        'Liquidez General', 'Autonomía Financiera',
        'Endeudamiento (%)',
        'Fondo Maniobra / Activo (%)',
        'Periodo Medio Cobro (días)', 'Periodo Medio Pago (días)',
        'Deuda Bancaria / EBITDA (x)'
    ],
    'ITELSAT': [
        f"{ratios[idx]['margen_bruto']:.1f}",
        f"{ratios[idx]['ebit_ventas']:.1f}",
        f"{ratios[idx]['rn_ventas']:.1f}",
        f"{ratios[idx]['ebitda']:,.0f}",
        f"{ratios[idx]['ebitda_margen']:.1f}",
        f"{ratios[idx]['roa']:.1f}",
        f"{ratios[idx]['roe']:.1f}",
        f"{ratios[idx]['liquidez']:.2f}" if ratios[idx]['liquidez'] != float('inf') else 'N/A',
        f"{ratios[idx]['autonomia']:.2f}",
        f"{ratios[idx]['endeudamiento']:.1f}",
        f"{ratios[idx]['fm_activo']:.1f}",
        f"{ratios[idx]['pmc']:.0f}",
        f"{ratios[idx]['pmp']:.0f}",
        f"{ratios[idx]['deuda_ebitda']:.2f}" if ratios[idx]['deuda_ebitda'] != float('inf') else 'N/A'
    ],
    'Sector': [
        f"{sector['Margen Bruto %']:.1f}",
        f"{sector['EBIT/Ventas %']:.1f}",
        f"{sector['RN/Ventas %']:.1f}",
        '—', '—',
        f"{sector['ROA %']:.1f}",
        f"{sector['ROE %']:.1f}",
        f"{sector['Liquidez General']:.2f}",
        f"{sector['Autonomía Financiera']:.2f}",
        f"{sector['Endeudamiento %']:.1f}",
        f"{sector['Fondo Maniobra/Activo %']:.1f}",
        f"{sector['PMC (días)']:.0f}",
        f"{sector['PMP (días)']:.0f}",
        '—'
    ],
    'Evaluación': []
})

# Lógica de evaluación
for i, row in ratios_df.iterrows():
    name = row['Ratio']
    val_str = row['ITELSAT']
    sec_str = row['Sector']
    if val_str in ('N/A', '—') or sec_str in ('N/A', '—'):
        ratios_df.at[i, 'Evaluación'] = 'ℹ️'
        continue
    try:
        val = float(val_str.replace(',', ''))
        sec = float(sec_str.replace(',', ''))
    except:
        ratios_df.at[i, 'Evaluación'] = 'ℹ️'
        continue

    if 'Margen' in name or 'ROA' in name or 'ROE' in name or 'EBIT' in name or 'Resultado' in name:
        if val > sec * 1.15: ratios_df.at[i, 'Evaluación'] = '✅ Excelente'
        elif val > sec: ratios_df.at[i, 'Evaluación'] = '✅ Bien'
        else: ratios_df.at[i, 'Evaluación'] = '⚠️ Por debajo'
    elif 'Cobro' in name:
        if val > sec * 1.5: ratios_df.at[i, 'Evaluación'] = '🔴 Crítico'
        elif val > sec * 1.1: ratios_df.at[i, 'Evaluación'] = '⚠️ Elevado'
        else: ratios_df.at[i, 'Evaluación'] = '✅ Bien'
    elif 'Pago' in name:
        if val < sec * 0.5: ratios_df.at[i, 'Evaluación'] = '🔴 Crítico'
        elif val < sec: ratios_df.at[i, 'Evaluación'] = '⚠️ Bajo'
        else: ratios_df.at[i, 'Evaluación'] = '✅ Bien'
    elif 'Liquidez' in name:
        if val > 3: ratios_df.at[i, 'Evaluación'] = '⚠️ Excesiva'
        elif val > 1.5: ratios_df.at[i, 'Evaluación'] = '✅ Bien'
        else: ratios_df.at[i, 'Evaluación'] = '🔴 Baja'
    elif 'Endeudamiento' in name:
        if val > sec * 1.5: ratios_df.at[i, 'Evaluación'] = '🔴 Alto'
        elif val > sec: ratios_df.at[i, 'Evaluación'] = '⚠️ Moderado'
        else: ratios_df.at[i, 'Evaluación'] = '✅ Bajo'
    else:
        ratios_df.at[i, 'Evaluación'] = '✅'

st.dataframe(ratios_df, hide_index=True, use_container_width=True)

# ============================================
# DATOS CRUDOS
# ============================================
st.markdown("---")
with st.expander("📋 Ver datos completos del Modelo 200 (todos los años)"):
    df_mostrar = pd.DataFrame({
        'Concepto': [
            'Ingresos', 'Aprovisionamientos', 'Gastos Personal', 'Otros Gastos Explotación',
            'Amortización', 'Resultado Explotación', 'Resultado Financiero', 'Resultado Neto',
            'Activo Total', 'Activo Corriente', 'Patrimonio Neto', 'Pasivo No Corriente',
            'Pasivo Corriente', 'Fondo de Maniobra', 'Clientes', 'Existencias', 'Tesorería',
            'Proveedores y Acreedores', 'Deuda Bancaria',
            'Base Imponible', 'Cuota Íntegra', 'Cuota Diferencial'
        ],
        '2023': [
            f"{ingresos[0]:,.2f} €", f"{aprovisionamientos[0]:,.2f} €", f"{gastos_personal[0]:,.2f} €",
            f"{otros_gastos_explot[0]:,.2f} €", f"{amortizacion[0]:,.2f} €",
            f"{resultado_explotacion[0]:,.2f} €", f"{resultado_financiero[0]:,.2f} €",
            f"{resultado_neto[0]:,.2f} €", f"{activo_total[0]:,.2f} €",
            f"{activo_corriente[0]:,.2f} €", f"{patrimonio_neto[0]:,.2f} €",
            f"{pasivo_no_corriente[0]:,.2f} €", f"{pasivo_corriente[0]:,.2f} €",
            f"{fondo_maniobra[0]:,.2f} €", f"{clientes[0]:,.2f} €",
            f"{existencias[0]:,.2f} €", f"{tesoreria[0]:,.2f} €",
            f"{proveedores_acreedores[0]:,.2f} €", f"{deuda_bancaria[0]:,.2f} €",
            f"{base_imponible[0]:,.2f} €", f"{cuota_integra[0]:,.2f} €",
            f"{cuota_diferencial[0]:,.2f} €"
        ],
        '2024': [
            f"{ingresos[1]:,.2f} €", f"{aprovisionamientos[1]:,.2f} €", f"{gastos_personal[1]:,.2f} €",
            f"{otros_gastos_explot[1]:,.2f} €", f"{amortizacion[1]:,.2f} €",
            f"{resultado_explotacion[1]:,.2f} €", f"{resultado_financiero[1]:,.2f} €",
            f"{resultado_neto[1]:,.2f} €", f"{activo_total[1]:,.2f} €",
            f"{activo_corriente[1]:,.2f} €", f"{patrimonio_neto[1]:,.2f} €",
            f"{pasivo_no_corriente[1]:,.2f} €", f"{pasivo_corriente[1]:,.2f} €",
            f"{fondo_maniobra[1]:,.2f} €", f"{clientes[1]:,.2f} €",
            f"{existencias[1]:,.2f} €", f"{tesoreria[1]:,.2f} €",
            f"{proveedores_acreedores[1]:,.2f} €", f"{deuda_bancaria[1]:,.2f} €",
            f"{base_imponible[1]:,.2f} €", f"{cuota_integra[1]:,.2f} €",
            f"{cuota_diferencial[1]:,.2f} €"
        ],
        '2025': [
            f"{ingresos[2]:,.2f} €", f"{aprovisionamientos[2]:,.2f} €", f"{gastos_personal[2]:,.2f} €",
            f"{otros_gastos_explot[2]:,.2f} €", f"{amortizacion[2]:,.2f} €",
            f"{resultado_explotacion[2]:,.2f} €", f"{resultado_financiero[2]:,.2f} €",
            f"{resultado_neto[2]:,.2f} €", f"{activo_total[2]:,.2f} €",
            f"{activo_corriente[2]:,.2f} €", f"{patrimonio_neto[2]:,.2f} €",
            f"{pasivo_no_corriente[2]:,.2f} €", f"{pasivo_corriente[2]:,.2f} €",
            f"{fondo_maniobra[2]:,.2f} €", f"{clientes[2]:,.2f} €",
            f"{existencias[2]:,.2f} €", f"{tesoreria[2]:,.2f} €",
            f"{proveedores_acreedores[2]:,.2f} €", f"{deuda_bancaria[2]:,.2f} €",
            f"{base_imponible[2]:,.2f} €", f"{cuota_integra[2]:,.2f} €",
            f"{cuota_diferencial[2]:,.2f} €"
        ]
    })
    st.dataframe(df_mostrar, hide_index=True, use_container_width=True)

# ============================================
# FOOTER CON CONTACTO Y LLAMADA A LA ACCIÓN
# ============================================
st.markdown("---")

# Mensaje de advertencia final
st.error("""
### ⚠️ ESTA EMPRESA NECESITA REVISIÓN INMEDIATA POR UN EXPERTO
El análisis financiero actual revela graves incidencias contables y operativas (desconexión de software, saldos anómalos, asimetría de cobros/pagos). 
No tome decisiones de inversión o crédito sin una auditoría previa.
""")

# Botones de contacto
st.markdown("""
<div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
    <p style="font-size: 18px; font-weight: bold; color: #333;">¿Quiere reservar una consulta con nosotros?</p>
    
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 15px; flex-wrap: wrap;">
        
        <!-- Botón WhatsApp -->
        <a href="https://wa.me/34644247796" target="_blank" style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #25D366;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <svg style="width:24px;height:24px;margin-right:10px;" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
            Contactar Analista (WhatsApp)
        </a>

        <!-- Botón Email -->
        <a href="mailto:cuadrarcuentas@gmail.com" target="_blank" style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #4285F4;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <svg style="width:24px;height:24px;margin-right:10px;" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
            Contactar Analista (Email)
        </a>
        
    </div>
</div>
""", unsafe_allow_html=True)

# Pie de página estándar
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 40px;'>
    <p>Dashboard generado a partir de los Modelos 200 (2023, 2024, 2025) y el Informe de Análisis Financiero de TACTIO</p>
    <p>ITELSAT TECNISUR S.L. | NIF B38659165 | CNAE 4321 - Instalaciones eléctricas | El Hierro</p>
    <p><em>La información contenida es confidencial y para uso interno</em></p>
</div>
""", unsafe_allow_html=True)