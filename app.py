import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pdfplumber
import re
import time
import io
import unicodedata

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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
# 2. CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* --- SIDEBAR --- */
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
    [data-testid="stSidebar"] button[kind="primary"], .main button[kind="primary"] {
        font-weight: 900 !important; 
        font-size: 16px !important;  
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* --- FILE UPloader COMPACTO --- */
    [data-testid="stFileUploader"] label p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #FAFAFA !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #14161F !important;
        border: 2px dashed #F8B155 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: flex-start !important;
        min-height: 240px !important;
        max-height: 350px !important;
        overflow-y: auto !important;
    }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar { width: 6px; }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); border-radius: 3px; }
    [data-testid="stFileUploaderDropzone"]::-webkit-scrollbar-thumb { background: #F8B155; border-radius: 3px; }
    [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
    [data-testid="stFileUploaderDropzone"] button svg { display: none !important; }
    
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background-color: #F8B155 !important;
        color: #14161F !important;
        border: 2px solid #D97706 !important;
        border-radius: 8px !important;
        padding: 0 16px !important;
        min-width: 140px !important;
        height: 38px !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        margin: 6px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 6px rgba(248, 177, 85, 0.3) !important;
    }
    [data-testid="stFileUploaderDropzone"] button div,
    [data-testid="stFileUploaderDropzone"] button span { font-size: 0 !important; }
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "+ Añadir más";
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #14161F !important;
    }

    /* --- MINIATURAS DE ARCHIVOS --- */
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        margin-bottom: 5px !important;
        height: auto !important;
    }
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] span,
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] p {
        color: #F9FAFB !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] [data-testid="stUploadedFile"] svg {
        width: 14px !important;
        height: 14px !important;
        fill: #F8B155 !important;
    }

    /* --- BOTÓN PRINCIPAL --- */
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

    /* --- ANIMACIÓN DE CARGA --- */
    @keyframes pulseText {
        0% { opacity: 0.55; }
        50% { opacity: 1; }
        100% { opacity: 0.55; }
    }
    .loading-text {
        color: #F8B155 !important;
        font-weight: 800 !important;
        animation: pulseText 1.2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 3. UTILIDADES
# ============================================
NUMERIC_KEYS = [
    "ingresos", "ventas", "servicios", "resultado_explotacion",
    "gastos_personal", "amortizaciones", "otros_gastos",
    "ingresos_financieros", "gastos_financieros", "resultado_neto",
    "activo_total", "patrimonio_neto", "pasivo_total", "pasivo_corriente",
    "clientes", "deudores", "proveedores", "existencias", "tesoreria",
    "base_imponible", "cuota_integra", "resultado_autoliquidacion"
]

EXPECTED_COLUMNS = ["year", "year_label", "nif", "empresa"] + NUMERIC_KEYS


def normalize_text(s):
    if s is None:
        return ""
    return unicodedata.normalize("NFKD", str(s)).encode("ASCII", "ignore").decode().lower()


def safe_float(x, default=0.0):
    try:
        if x is None or x == "":
            return float(default)
        return float(x)
    except Exception:
        return float(default)


def parse_spanish_number(value):
    if value is None:
        return 0.0

    s = str(value).strip().replace("€", "").replace(" ", "")
    if not s or s in {"-", "—", "--"}:
        return 0.0

    negative = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("()").lstrip("-")

    if "," in s and "." in s:
        if s.rfind(",") > s.find("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts[-1]) <= 2:
            s = ".".join(parts)
        else:
            s = "".join(parts)
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3:
            s = "".join(parts)

    try:
        v = float(s)
        return -v if negative else v
    except Exception:
        return 0.0


def clean_company_name(name):
    if not name:
        return "Desconocida"
    name = re.sub(r"\s+", " ", str(name)).strip(" .,-:")
    name = re.sub(r"^(NIF|Apellidos|razón social|Identificación)\s*", "", name, flags=re.IGNORECASE)
    return name if name else "Desconocida"


# ============================================
# 4. EXTRACCIÓN MODELO 200
# ============================================
DECIMAL_NUM = r"(?:-?\d{1,3}(?:\.\d{3})+,\d{2}|-?\d+,\d{2})"


def detect_global_year(text):
    patterns = [
        r"MOD\.?\s*200[^\n]{0,160}?\b(20[12]\d)\b",
        r"\b(20[12]\d)\b[^\n]{0,160}?MOD\.?\s*200",
        r"Impuesto sobre Sociedades[^\n]{0,160}?\b(20[12]\d)\b",
        r"Modelo\s*200[^\n]{0,160}?\b(20[12]\d)\b",
        r"\b(20[12]\d)\b[^\n]{0,160}?Modelo\s*200",
        r"Declaración relativa al período impositivo[^\n]{0,220}?\b(20[12]\d)\b",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass

    m = re.search(r"\b(20[12]\d)\b", text)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            pass
    return 0


def split_text_by_decl_year(full_text):
    markers = []

    patterns = [
        r"(?:MOD\.?\s*200|Impuesto sobre Sociedades|Modelo\s*200)[^\n]{0,160}?\b(20[12]\d)\b",
        r"\b(20[12]\d)\b[^\n]{0,160}?(?:MOD\.?\s*200|Impuesto sobre Sociedades|Modelo\s*200)",
        r"Declaración relativa al período impositivo[^\n]{0,220}?\b(20[12]\d)\b",
    ]

    for p in patterns:
        for m in re.finditer(p, full_text, flags=re.IGNORECASE | re.DOTALL):
            try:
                year = int(m.group(1))
                markers.append((m.start(), year))
            except Exception:
                pass

    markers = sorted(markers, key=lambda x: x[0])

    unique_markers = []
    seen_starts = set()
    for start, year in markers:
        if start not in seen_starts:
            seen_starts.add(start)
            unique_markers.append((start, year))
    markers = unique_markers

    if not markers:
        y = detect_global_year(full_text)
        return [(y, full_text)] if full_text.strip() else []

    segments = []
    for i, (start, year) in enumerate(markers):
        end = markers[i + 1][0] if i + 1 < len(markers) else len(full_text)
        seg = full_text[start:end]

        if segments and segments[-1][0] == year:
            segments[-1] = (year, segments[-1][1] + "\n" + seg)
        else:
            segments.append((year, seg))

    return segments


def extract_full_text_from_pdf(pdf_file):
    pdf_file.seek(0)
    texts = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    return "\n".join(texts)


def get_case_value(text, codes):
    if isinstance(codes, str):
        codes = [codes]

    for code in codes:
        # Valor con decimales españoles: 1.265,00 o 140,70
        pattern = rf"\b{code}\b[^\d]{{0,250}}?({DECIMAL_NUM})"
        m = re.search(pattern, text, flags=re.DOTALL)
        if m:
            return parse_spanish_number(m.group(1))

        # Fallback entero, evitando casillas de 5 dígitos tipo 00255
        pattern2 = rf"\b{code}\b[^\d]{{0,250}}?(-?\d+)(?![,\.\d])"
        for mm in re.finditer(pattern2, text, flags=re.DOTALL):
            token = mm.group(1)
            clean_token = token.lstrip("-")
            if len(clean_token) == 5 and clean_token.startswith("0"):
                continue
            if len(clean_token) > 7:
                continue
            return parse_spanish_number(token)

    return 0.0


def extract_identity(text, default_nif=None, default_empresa=None):
    nifs = re.findall(r"\b[A-Z]\d{8}\b", text)
    presenter_match = re.search(r"NIF\s*Presentador[:\s]*([A-Z]\d{8})", text, flags=re.IGNORECASE)
    exclude = {presenter_match.group(1)} if presenter_match else set()

    candidates = [n for n in nifs if n not in exclude]
    if candidates:
        nif = max(set(candidates), key=candidates.count)
    else:
        nif = default_nif or "Desconocido"

    empresa = "Desconocida"

    if nif and nif != "Desconocido":
        m = re.search(
            rf"{nif}\s+([A-ZÁÉÍÓÚÑ0-9\.,\s\-]{{3,90}}?)(?=\s+\d{{1,3}}(?:\.\d{{3}})*,\d{{2}}|\s+[A-Z]\d{{8}}|\n|$)",
            text,
            flags=re.DOTALL
        )
        if m:
            empresa = clean_company_name(m.group(1))

    if empresa == "Desconocida":
        m = re.search(
            r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\.,\s\-]{2,90}?,\s*S\.?\s*L\.?[U]?\.?)",
            text,
            flags=re.DOTALL
        )
        if m:
            empresa = clean_company_name(m.group(1))

    if empresa == "Desconocida":
        m = re.search(
            r"Apellidos y nombre o razón social\s*[:\s]*([^\n]{3,90})",
            text,
            flags=re.IGNORECASE
        )
        if m:
            empresa = clean_company_name(m.group(1))

    if empresa == "Desconocida" and default_empresa:
        empresa = default_empresa

    return nif, empresa


def extract_declaration_data(chunk, year, default_nif=None, default_empresa=None):
    nif, empresa = extract_identity(chunk, default_nif=default_nif, default_empresa=default_empresa)

    d = {
        "year": year,
        "year_label": str(year) if year else "Sin ejercicio",
        "nif": nif,
        "empresa": empresa,
    }

    d["ingresos"] = get_case_value(chunk, ["00255"])
    d["ventas"] = get_case_value(chunk, ["00256"])
    d["servicios"] = get_case_value(chunk, ["00257"])

    d["resultado_explotacion"] = get_case_value(chunk, ["00280", "00296", "00450"])
    d["gastos_personal"] = get_case_value(chunk, ["00265", "00270"])
    d["amortizaciones"] = get_case_value(chunk, ["00270", "00275"])
    d["otros_gastos"] = get_case_value(chunk, ["00275", "00285"])

    d["ingresos_financieros"] = get_case_value(chunk, ["00285", "00297"])
    d["gastos_financieros"] = abs(get_case_value(chunk, ["00290", "00305"]))

    d["resultado_neto"] = get_case_value(chunk, ["00500", "00320", "00450"])

    d["activo_total"] = get_case_value(chunk, ["00180"])
    d["patrimonio_neto"] = get_case_value(chunk, ["00185"])

    pasivo_extracted = get_case_value(chunk, ["00250"])
    if pasivo_extracted == 0 and d["activo_total"] and d["patrimonio_neto"]:
        d["pasivo_total"] = max(d["activo_total"] - d["patrimonio_neto"], 0.0)
    else:
        d["pasivo_total"] = pasivo_extracted

    d["pasivo_corriente"] = get_case_value(chunk, ["00228"])

    d["clientes"] = get_case_value(chunk, ["00150", "00152"])
    d["deudores"] = get_case_value(chunk, ["00149"])
    d["proveedores"] = get_case_value(chunk, ["00175", "00176", "00177"])
    d["existencias"] = get_case_value(chunk, ["00140", "00141", "00142"])
    d["tesoreria"] = get_case_value(chunk, ["00145", "00146", "00147"])

    d["base_imponible"] = get_case_value(chunk, ["00552"])
    d["cuota_integra"] = get_case_value(chunk, ["00562"])
    d["resultado_autoliquidacion"] = get_case_value(chunk, ["01586", "02485", "02489"])

    # Fallbacks lógicos
    if d["resultado_neto"] == 0 and d["resultado_explotacion"] != 0:
        d["resultado_neto"] = d["resultado_explotacion"]

    if d["resultado_explotacion"] == 0 and d["resultado_neto"] != 0:
        d["resultado_explotacion"] = d["resultado_neto"]

    if d["ventas"] == 0 and d["ingresos"] != 0:
        d["ventas"] = d["ingresos"]

    return d


def is_meaningful_declaration(d):
    if d.get("nif", "Desconocido") != "Desconocido":
        return True
    return any(abs(safe_float(d.get(k, 0.0))) > 0.0 for k in NUMERIC_KEYS)


def extract_all_from_pdf(pdf_file):
    full_text = extract_full_text_from_pdf(pdf_file)
    segments = split_text_by_decl_year(full_text)

    results = []
    default_nif = None
    default_empresa = None

    for year, text in segments:
        if not text.strip():
            continue

        d = extract_declaration_data(
            text,
            year=year,
            default_nif=default_nif,
            default_empresa=default_empresa
        )

        if d["nif"] != "Desconocido":
            default_nif = d["nif"]

        if d["empresa"] != "Desconocida":
            default_empresa = d["empresa"]

        if is_meaningful_declaration(d):
            results.append(d)

    if not results and full_text.strip():
        d = extract_declaration_data(full_text, year=detect_global_year(full_text))
        if is_meaningful_declaration(d):
            results.append(d)

    def sort_key(x):
        try:
            return (0, int(x["year"]))
        except Exception:
            return (1, str(x["year"]))

    return sorted(results, key=sort_key)


# ============================================
# 5. EXCEL
# ============================================
def load_excel_files(uploaded_files):
    excel_data = {}

    for file in uploaded_files:
        if not file.name.lower().endswith((".xlsx", ".xls")):
            continue

        try:
            file.seek(0)
            bytes_data = file.getvalue()
            xls = pd.ExcelFile(io.BytesIO(bytes_data))

            sheets = {}
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(io.BytesIO(bytes_data), sheet_name=sheet_name, header=None)
                sheets[sheet_name] = df

            excel_data[file.name] = sheets
        except Exception as e:
            st.error(f"Error leyendo Excel {file.name}: {e}")

    return excel_data


# ============================================
# 6. DATAFRAME MODELO 200
# ============================================
def build_model_df(datos_empresa):
    if not datos_empresa:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = pd.DataFrame(datos_empresa)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0 if col in NUMERIC_KEYS else ""

    for col in NUMERIC_KEYS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["year_num"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.sort_values(["year_num", "year_label"], na_position="last").reset_index(drop=True)

    return df


# ============================================
# 7. IA
# ============================================
def generate_ai_report(api_key, financial_summary, rules_audit):
    if not OPENAI_AVAILABLE:
        return (
            "No se ha podido generar el informe IA porque la librería `openai` no está instalada. "
            "Instálala con: `pip install openai`."
        )

    if not api_key:
        return "Introduce tu API Key de OpenAI en la barra lateral."

    try:
        client = openai.OpenAI(api_key=api_key)
        system_prompt = (
            "Eres un Analista Financiero Senior con 22 años de experiencia. "
            "Tono formal, técnico, directo y ejecutivo. No inventes datos."
        )
        user_prompt = f"Datos financieros extraídos de Modelos 200:\n\n{financial_summary}\n\nCriterios de análisis:\n{rules_audit}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al conectar con la IA: {e}"


# ============================================
# 8. GRÁFICOS
# ============================================
def infer_sheet_focus(sheet_name):
    s = normalize_text(sheet_name)

    if any(k in s for k in ["umbral", "punto muerto", "breakeven", "break even"]):
        return "umbral"

    if any(k in s for k in ["maduracion", "ciclo", "lucro", "fon.man", "tesoreria", "cash", "working capital"]):
        return "ciclo"

    if any(k in s for k in ["balance", "situacion", "activo", "pasivo", "patrimonio"]):
        return "balance"

    if any(k in s for k in [
        "resultado", "cuenta", "pyg", "explotacion", "ventas", "margen",
        "coste", "personal", "diversos", "financieros", "amortiz",
        "neto", "potencial", "extraordinarios", "impuesto", "reembolso",
        " deficit", "superavit"
    ]):
        return "pnl"

    if any(k in s for k in ["ratio", "indicador", "evolucion", "resumen", "analisis"]):
        return "evolucion"

    return "generico"


def render_line_evolution(model_df, columns, title):
    available = [c for c in columns if c in model_df.columns and model_df[c].abs().sum() > 0]
    if not available:
        st.info("No hay datos suficientes en los Modelos 200 para representar este gráfico.")
        return

    plot_df = model_df[["year_label"] + available].copy()
    long_df = plot_df.melt(id_vars="year_label", var_name="Métrica", value_name="Importe")

    fig = px.line(
        long_df,
        x="year_label",
        y="Importe",
        color="Métrica",
        markers=True,
        title=title
    )
    fig.update_layout(
        template="plotly_dark",
        yaxis_tickformat=",.0f",
        xaxis_title="Ejercicio",
        yaxis_title="Importe (€)",
        legend_title_text="Métrica"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_balance_charts(model_df):
    st.subheader(" Balance desde Modelo 200")

    df = model_df.copy()
    df["pasivo_total_calc"] = df["activo_total"] - df["patrimonio_neto"]
    df.loc[(df["pasivo_total"] == 0) & (df["pasivo_total_calc"] > 0), "pasivo_total"] = df["pasivo_total_calc"]

    fig = go.Figure()
    series = [
        ("activo_total", "Activo total", "#3B82F6"),
        ("patrimonio_neto", "Patrimonio neto", "#10B981"),
        ("pasivo_total", "Pasivo total", "#F8B155"),
    ]

    for col, name, color in series:
        if col in df.columns and df[col].abs().sum() > 0:
            fig.add_bar(x=df["year_label"], y=df[col], name=name, marker_color=color)

    if not fig.data:
        st.info("No se han detectado masas patrimoniales en los Modelos 200.")
        return

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Evolución de masas patrimoniales",
        xaxis_title="Ejercicio",
        yaxis_title="Importe (€)",
        yaxis_tickformat=",.0f"
    )
    st.plotly_chart(fig, use_container_width=True)

    latest = df.iloc[-1]

    activo_parts = {
        "Existencias": safe_float(latest.get("existencias")),
        "Clientes / Deudores": max(safe_float(latest.get("clientes")), safe_float(latest.get("deudores"))),
        "Tesorería": safe_float(latest.get("tesoreria")),
    }

    suma_parts = sum(v for v in activo_parts.values() if v > 0)
    otros_activos = safe_float(latest.get("activo_total")) - suma_parts
    if otros_activos > 0:
        activo_parts["Otros activos"] = otros_activos

    activo_parts = {k: v for k, v in activo_parts.items() if v > 0}

    if activo_parts:
        fig2 = px.bar(
            x=list(activo_parts.keys()),
            y=list(activo_parts.values()),
            title="Composición estimada del activo último ejercicio",
            labels={"x": "Partida", "y": "Importe (€)"}
        )
        fig2.update_layout(template="plotly_dark", yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)

    financiacion = {
        "Patrimonio neto": safe_float(latest.get("patrimonio_neto")),
        "Pasivo corriente": safe_float(latest.get("pasivo_corriente")),
        "Pasivo no corriente": max(
            safe_float(latest.get("pasivo_total")) - safe_float(latest.get("pasivo_corriente")),
            0.0
        ),
    }
    financiacion = {k: v for k, v in financiacion.items() if v > 0}

    if financiacion:
        fig3 = px.bar(
            x=list(financiacion.keys()),
            y=list(financiacion.values()),
            title="Estructura de financiación último ejercicio",
            labels={"x": "Fuente", "y": "Importe (€)"}
        )
        fig3.update_layout(template="plotly_dark", yaxis_tickformat=",.0f")
        st.plotly_chart(fig3, use_container_width=True)


def render_pnl_charts(model_df):
    st.subheader("📈 Cuenta de resultados desde Modelo 200")

    render_line_evolution(
        model_df,
        ["ingresos", "resultado_explotacion", "resultado_neto"],
        "Evolución de ingresos y resultado"
    )

    latest = model_df.iloc[-1]

    items = [
        ("Ingresos", safe_float(latest.get("ingresos"))),
        ("Ventas", safe_float(latest.get("ventas"))),
        ("Servicios", safe_float(latest.get("servicios"))),
        ("Gastos personal", -abs(safe_float(latest.get("gastos_personal")))),
        ("Amortizaciones", -abs(safe_float(latest.get("amortizaciones")))),
        ("Otros gastos", -abs(safe_float(latest.get("otros_gastos")))),
        ("Gastos financieros", -abs(safe_float(latest.get("gastos_financieros")))),
        ("Resultado neto", safe_float(latest.get("resultado_neto"))),
    ]

    items = [(k, v) for k, v in items if abs(v) > 0]

    if items:
        fig = go.Figure()
        fig.add_bar(
            x=[k for k, _ in items],
            y=[v for _, v in items],
            marker_color=["#10B981" if v >= 0 else "#EF4444" for _, v in items]
        )
        fig.update_layout(
            template="plotly_dark",
            title="Desglose estimado último ejercicio",
            xaxis_title="Partida",
            yaxis_title="Importe (€)",
            yaxis_tickformat=",.0f"
        )
        st.plotly_chart(fig, use_container_width=True)

    ingresos = safe_float(latest.get("ingresos"))
    resultado_exp = safe_float(latest.get("resultado_explotacion")) or safe_float(latest.get("resultado_neto"))

    if ingresos > 0:
        costes_estimados = max(ingresos - resultado_exp, 0.0)

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Ingresos", "Costes estimados", "Resultado"],
            y=[ingresos, -costes_estimados, resultado_exp],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig_wf.update_layout(
            template="plotly_dark",
            title="Waterfall simplificado último ejercicio",
            yaxis_title="Importe (€)",
            yaxis_tickformat=",.0f"
        )
        st.plotly_chart(fig_wf, use_container_width=True)


def render_breakeven_chart(model_df):
    st.subheader("⚖️ Umbral de rentabilidad estimado desde Modelo 200")

    latest = model_df.iloc[-1]
    ingresos = safe_float(latest.get("ingresos"))
    resultado_exp = safe_float(latest.get("resultado_explotacion")) or safe_float(latest.get("resultado_neto"))

    if ingresos <= 0:
        st.info("No hay ingresos suficientes en el Modelo 200 para calcular el umbral de rentabilidad.")
        return

    costes_totales = max(ingresos - resultado_exp, 0.0)
    fixed_ratio = 0.60
    fixed_costs = costes_totales * fixed_ratio
    variable_costs = costes_totales * (1 - fixed_ratio)

    monthly_rev = ingresos / 12.0
    variable_month = variable_costs / 12.0
    contribution = monthly_rev - variable_month

    months = list(range(1, 13))
    cum_rev = [monthly_rev * m for m in months]
    cum_costs = [fixed_costs + variable_month * m for m in months]

    fig = go.Figure()
    fig.add_scatter(x=months, y=cum_rev, mode="lines+markers", name="Ventas acumuladas", line=dict(color="#3B82F6", width=3))
    fig.add_scatter(x=months, y=cum_costs, mode="lines", name="Costes acumulados estimados", line=dict(color="#EF4444", width=2, dash="dash"))

    if contribution > 0:
        be_month = fixed_costs / contribution
        if 1 <= be_month <= 12:
            fig.add_vline(x=be_month, line_dash="dot", line_color="#F8B155", annotation_text="Punto muerto")
            st.metric("Mes de equilibrio estimado", f"{be_month:.1f} meses")
        else:
            st.info("El punto muerto estimado queda fuera del horizonte de 12 meses.")
    else:
        st.warning("Con los datos extraídos, la contribución mensual estimada es cero o negativa.")

    fig.update_layout(
        template="plotly_dark",
        title="Umbral de rentabilidad a 12 meses",
        xaxis_title="Mes",
        yaxis_title="Importe (€)",
        yaxis_tickformat=",.0f"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cash_cycle_chart(model_df):
    st.subheader("🔄 Ciclo operativo y lucro cesante estimado")

    latest = model_df.iloc[-1]

    ingresos = safe_float(latest.get("ingresos"))
    resultado_exp = safe_float(latest.get("resultado_explotacion")) or safe_float(latest.get("resultado_neto"))
    coste_ventas = max(ingresos - resultado_exp, 0.0)

    existencias = safe_float(latest.get("existencias"))
    clientes = max(safe_float(latest.get("clientes")), safe_float(latest.get("deudores")))
    proveedores = safe_float(latest.get("proveedores"))

    days_inv = (existencias / coste_ventas * 365) if coste_ventas > 0 else 0
    days_rec = (clientes / ingresos * 365) if ingresos > 0 else 0
    days_pay = (proveedores / coste_ventas * 365) if coste_ventas > 0 else 0
    cash_cycle = days_inv + days_rec - days_pay

    working_capital = existencias + clientes - proveedores
    lucro_diario = working_capital / 365 if working_capital > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Días existencias", f"{days_inv:.0f}")
    with col2:
        st.metric("Días clientes", f"{days_rec:.0f}")
    with col3:
        st.metric("Días proveedores", f"{days_pay:.0f}")
    with col4:
        st.metric("Ciclo caja", f"{cash_cycle:.0f} días")

    fases = ["Existencias", "Clientes", "Proveedores", "Ciclo caja"]
    valores = [days_inv, days_rec, -days_pay, cash_cycle]

    fig = px.bar(
        x=fases,
        y=valores,
        title="Ciclo medio de maduración estimado",
        labels={"x": "Fase", "y": "Días"},
        color=valores,
        color_continuous_scale=["#EF4444", "#F8B155", "#10B981", "#3B82F6"]
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    if lucro_diario > 0:
        st.metric("Lucro cesante diario estimado", f"{lucro_diario:,.0f} €/día")

    df_wc = model_df.copy()
    df_wc["clientes_efectivos"] = df_wc[["clientes", "deudores"]].max(axis=1)
    df_wc["capital_operativo"] = df_wc["existencias"] + df_wc["clientes_efectivos"] - df_wc["proveedores"]

    if df_wc["capital_operativo"].abs().sum() > 0:
        fig2 = px.line(
            df_wc,
            x="year_label",
            y="capital_operativo",
            markers=True,
            title="Evolución estimada del capital operativo"
        )
        fig2.update_layout(template="plotly_dark", yaxis_tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)


def render_evolution_charts(model_df):
    st.subheader("📊 Evolución financiera global")

    options = [
        "ingresos", "ventas", "servicios", "resultado_explotacion",
        "resultado_neto", "activo_total", "patrimonio_neto",
        "pasivo_total", "gastos_financieros", "base_imponible",
        "resultado_autoliquidacion"
    ]

    available = [c for c in options if c in model_df.columns and model_df[c].abs().sum() > 0]
    if not available:
        st.info("No hay series financieras disponibles para evolución.")
        return

    selected = st.multiselect(
        "Selecciona métricas a visualizar",
        available,
        default=available[:3]
    )

    if selected:
        render_line_evolution(model_df, selected, "Evolución seleccionada")

    growth_df = model_df.copy()
    growth_df = growth_df.sort_values("year_num", na_position="last")

    for col in selected:
        growth_df[f"{col}_var_%"] = growth_df[col].pct_change() * 100

    show_cols = ["year_label"] + [f"{c}_var_%" for c in selected]
    show_cols = [c for c in show_cols if c in growth_df.columns]

    if len(show_cols) > 1:
        st.markdown("#### Variación interanual estimada")
        st.dataframe(growth_df[show_cols].round(2), use_container_width=True)


def render_generic_charts(model_df):
    st.subheader(" Vista financiera general desde Modelo 200")

    render_line_evolution(
        model_df,
        ["ingresos", "resultado_neto", "activo_total", "patrimonio_neto"],
        "Principales magnitudes"
    )

    latest = model_df.iloc[-1]
    metrics = {
        "Ingresos": safe_float(latest.get("ingresos")),
        "Resultado neto": safe_float(latest.get("resultado_neto")),
        "Activo total": safe_float(latest.get("activo_total")),
        "Patrimonio neto": safe_float(latest.get("patrimonio_neto")),
    }
    metrics = {k: v for k, v in metrics.items() if abs(v) > 0}

    if metrics:
        fig = px.bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            title="Último ejercicio: magnitudes clave",
            labels={"x": "Magnitud", "y": "Importe (€)"}
        )
        fig.update_layout(template="plotly_dark", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)


def render_excel_sheet(sheet_name, df_sheet, model_df):
    st.markdown(f"### 📑 Hoja: {sheet_name}")
    st.markdown("---")

    focus = infer_sheet_focus(sheet_name)

    if model_df.empty:
        st.warning("No se han extraído datos válidos de Modelos 200. Se muestra únicamente el contenido del Excel subido.")
    else:
        if focus == "balance":
            render_balance_charts(model_df)
        elif focus == "pnl":
            render_pnl_charts(model_df)
        elif focus == "umbral":
            render_breakeven_chart(model_df)
        elif focus == "ciclo":
            render_cash_cycle_chart(model_df)
        elif focus == "evolucion":
            render_evolution_charts(model_df)
        else:
            render_generic_charts(model_df)

        st.markdown("---")

    with st.expander("Ver datos del fichero Excel subido", expanded=False):
        st.dataframe(df_sheet, use_container_width=True, height=380)


# ============================================
# 9. DASHBOARD PRINCIPAL
# ============================================
def render_dashboard(model_df, api_key):
    st.title("💼 Informe Financiero y Riesgo")

    if model_df.empty:
        st.warning("No se han encontrado datos válidos de Modelos 200 en los PDF subidos.")
        st.info("Puedes subir uno o varios PDF del Modelo 200. Si un PDF contiene varios ejercicios, el sistema intentará separarlos automáticamente.")
        return

    latest = model_df.iloc[-1]
    first = model_df.iloc[0]

    empresa = latest.get("empresa") or first.get("empresa") or "Empresa"
    nif = latest.get("nif") or first.get("nif") or "Desconocido"
    period = f"{first.get('year_label')} - {latest.get('year_label')}"

    st.markdown(f"**Empresa:** {empresa} | **NIF:** {nif} | **Periodo analizado:** {period}")
    st.markdown("---")

    st.subheader("📈 Métricas recientes")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric("Ingresos", f"{safe_float(latest.get('ingresos')):,.0f} €")

    with col2:
        with st.container(border=True):
            st.metric("Resultado neto", f"{safe_float(latest.get('resultado_neto')):,.0f} €")

    with col3:
        with st.container(border=True):
            st.metric("Activo total", f"{safe_float(latest.get('activo_total')):,.0f} €")

    with col4:
        with st.container(border=True):
            st.metric("Patrimonio neto", f"{safe_float(latest.get('patrimonio_neto')):,.0f} €")

    st.markdown("---")

    st.subheader("📉 Evolución financiera")
    render_line_evolution(
        model_df,
        ["ingresos", "resultado_explotacion", "resultado_neto"],
        "Ingresos y resultado por ejercicio"
    )

    st.markdown("---")

    st.subheader("🏦 Balance y estructura patrimonial")
    render_balance_charts(model_df)

    st.markdown("---")

    st.subheader("📊 Cuenta de resultados")
    render_pnl_charts(model_df)

    st.markdown("---")

    st.subheader("🧠 Informe ejecutivo con IA")

    if not OPENAI_AVAILABLE:
        st.info("Para activar el informe IA instala la librería: `pip install openai`.")
    else:
        if st.button("Generar informe ejecutivo con IA", use_container_width=True):
            if not api_key:
                st.error("Introduce tu API Key de OpenAI en la barra lateral.")
            else:
                with st.spinner("Redactando informe ejecutivo..."):
                    summary = model_df[
                        ["year_label", "empresa", "nif"] +
                        [c for c in NUMERIC_KEYS if c in model_df.columns]
                    ].to_string(index=False)

                    rules = (
                        "Analiza evolución de ingresos, margen operativo, resultado neto, "
                        "estructura patrimonial, endeudamiento y riesgos financieros. "
                        "Redacta un informe ejecutivo breve, técnico y accionable."
                    )

                    ai_text = generate_ai_report(api_key, summary, rules)
                    st.markdown(
                        f"""
                        <div style="background:#1E2937; padding:20px; border-radius:12px; color:white; line-height:1.6;">
                        {ai_text.replace(chr(10), '<br>')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# ============================================
# 10. SESSION STATE
# ============================================
if "datos_empresa" not in st.session_state:
    st.session_state.datos_empresa = None

if "excel_data" not in st.session_state:
    st.session_state.excel_data = {}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# ============================================
# 11. SIDEBAR
# ============================================
st.sidebar.title("💼 TODO MODELO 200")
st.sidebar.markdown("Sube Modelos 200 en PDF y ficheros Excel de apoyo.")
st.sidebar.markdown("---")

st.sidebar.subheader("🤖 IA privada")
api_key = st.sidebar.text_input("API Key (OpenAI)", type="password")

if st.session_state.datos_empresa is not None:
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Borrar documentos y empezar de nuevo", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ============================================
# 12. PANTALLA DE CARGA INICIAL
# ============================================
if st.session_state.datos_empresa is None:
    st.markdown("""
        <div style="text-align: center; margin-top: 4vh; margin-bottom: 25px;">
            <h1 style="color: #F8B155; font-size: 3rem; font-weight: 800; margin-bottom: 15px;">TODO MODELO 200</h1>
            <p style="font-size: 1.2rem; color: #A0A0A0;">
                Sube tus Modelos 200 y Excel adjuntos para comenzar el análisis.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_files = st.file_uploader(
            "Selecciona archivos PDF y Excel",
            type=["pdf", "xlsx", "xls"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("COMENZAR EXTRACCIÓN DATOS MODELOS 200", key="btn_iniciar", use_container_width=True):
            if not uploaded_files:
                st.warning("Por favor, sube al menos un archivo PDF o Excel.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.markdown('<p class="loading-text">🔄 Inicializando motores de lectura y análisis contable...</p>', unsafe_allow_html=True)
                time.sleep(0.4)
                progress_bar.progress(15)

                pdf_files = [f for f in uploaded_files if f.name.lower().endswith(".pdf")]
                excel_files = [f for f in uploaded_files if f.name.lower().endswith((".xlsx", ".xls"))]

                temp_datos = []

                if pdf_files:
                    for idx, file in enumerate(pdf_files, start=1):
                        status_text.markdown(
                            f'<p class="loading-text">📄 Extrayendo Modelo 200 {idx}/{len(pdf_files)}: {file.name}</p>',
                            unsafe_allow_html=True
                        )
                        pct = 20 + int(55 * idx / max(len(pdf_files), 1))
                        progress_bar.progress(min(pct, 80))

                        try:
                            extracted = extract_all_from_pdf(file)
                            temp_datos.extend(extracted)
                        except Exception as e:
                            st.error(f"Error procesando PDF {file.name}: {e}")

                        time.sleep(0.25)

                temp_excels = {}

                if excel_files:
                    status_text.markdown('<p class="loading-text">📑 Leyendo pestañas y hojas de los ficheros Excel...</p>', unsafe_allow_html=True)
                    progress_bar.progress(88)
                    temp_excels = load_excel_files(excel_files)
                    time.sleep(0.3)

                status_text.markdown('<p class="loading-text">📊 Sincronizando datos y preparando gráficos financieros...</p>', unsafe_allow_html=True)
                progress_bar.progress(100)
                time.sleep(0.6)

                status_text.empty()
                progress_bar.empty()

                if temp_datos:
                    temp_datos = sorted(temp_datos, key=lambda x: str(x.get("year", "")))
                    counters = {}
                    for d in temp_datos:
                        yr = str(d.get("year", "Sin ejercicio"))
                        counters[yr] = counters.get(yr, 0) + 1
                        d["year_label"] = yr if counters[yr] == 1 else f"{yr} ({counters[yr]})"

                st.session_state.datos_empresa = temp_datos
                st.session_state.excel_data = temp_excels
                st.session_state.uploader_key += 1
                st.rerun()

    st.stop()


# ============================================
# 13. APP PRINCIPAL
# ============================================
datos_empresa = st.session_state.datos_empresa
excel_data = st.session_state.excel_data

model_df = build_model_df(datos_empresa)

tab_labels = ["📊 Dashboard Financiero e Informe IA"]
if excel_data:
    tab_labels += [f"📑 Excel: {fname}" for fname in excel_data.keys()]

main_tabs = st.tabs(tab_labels)

# --------------------------------------------
# TAB 1: DASHBOARD
# --------------------------------------------
with main_tabs[0]:
    st.markdown("---")
    if st.button("🗑️ Borrar todos los archivos y actualizar la web", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")

    render_dashboard(model_df, api_key)

# --------------------------------------------
# TABS DINÁMICAS POR FICHERO EXCEL
# --------------------------------------------
if excel_data:
    for tab_idx, (fname, sheets) in enumerate(excel_data.items(), start=1):
        with main_tabs[tab_idx]:
            st.header(f"📁 {fname}")
            st.markdown("---")

            if not sheets:
                st.info("Este fichero Excel no contiene hojas legibles.")
                continue

            sheet_names = list(sheets.keys())
            sheet_tabs = st.tabs(sheet_names)

            for sheet_idx, sheet_name in enumerate(sheet_names):
                with sheet_tabs[sheet_idx]:
                    render_excel_sheet(sheet_name, sheets[sheet_name], model_df)


# ============================================
# 14. PIE
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px;'>
    <p>TODO MODELO 200 | Análisis Financiero Profesional e Inteligencia Artificial.</p>
</div>
""", unsafe_allow_html=True)