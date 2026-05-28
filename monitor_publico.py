import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import io
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor climático · Tucumán",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS completo ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  .stApp { background-color: #0d1117 !important; }
  .main { background-color: #0d1117; }
  .block-container { padding-top: 1.5rem; background-color: #0d1117; }
  section[data-testid="stSidebar"] { background-color: #161b22 !important; }
  section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
  .stApp p, .stApp span, .stApp label, .stApp div { color: #e6edf3; }

  [data-testid="stToolbar"]                        { display: none !important; }
  [data-testid="stToolbar"] *                      { display: none !important; }
  [data-testid="stHeader"] button                  { display: none !important; }
  [data-testid="stDecoration"]                     { display: none !important; }
  [data-testid="stStatusWidget"]                   { display: none !important; }
  button[aria-label="View fullscreen"]             { display: none !important; }
  [data-testid="baseButton-headerNoPadding"]       { display: none !important; }
  .viewerBadge_container__r5tak                    { display: none !important; }
  .viewerBadge_link__qRIco                         { display: none !important; }
  [class*="viewerBadge"]                           { display: none !important; }
  [class*="badge"]                                 { display: none !important; }
  .st-emotion-cache-fplge5                         { display: none !important; }
  .st-emotion-cache-h5rgaw                         { display: none !important; }
  .st-emotion-cache-1dp5vir                        { display: none !important; }
  .st-emotion-cache-z5fcl4                         { display: none !important; }
  #root > div:last-child > div:not(.stApp)         { display: none !important; }
  .stApp [data-testid="stToolbar"]                 { opacity: 0 !important; pointer-events: none !important; }
  footer                                           { visibility: hidden !important; }
  a[target="_blank"]::after                        { display: none !important; }

  /* Ocultar botón de colapsar sidebar */
  button[data-testid="collapsedControl"],
  [data-testid="stSidebarCollapseButton"],
  button[aria-label="Close sidebar"],
  button[aria-label="Collapse sidebar"] { display: none !important; }

  .metric-card {
      background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
      border: 1px solid #30363d; border-radius: 12px;
      padding: 1.2rem 1.5rem; text-align: center;
  }
  .metric-label {
      font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;
      color: #8b949e; letter-spacing: 0.08em; text-transform: uppercase;
      margin-bottom: 0.5rem; font-weight: 500;
  }
  .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 2rem; font-weight: 600; color: #58a6ff; }
  .metric-unit  { font-size: 0.9rem; color: #8b949e; margin-left: 4px; }
  .status-dot   { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
      background: #3fb950; margin-right: 6px; animation: pulse 2s infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
  h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; color: #e6edf3 !important; }
  .streamlit-expanderHeader { background-color: #161b22 !important; color: #e6edf3 !important; border: 1px solid #30363d !important; }
  .streamlit-expanderContent { background-color: #0d1117 !important; border: 1px solid #30363d !important; }
  [data-testid="stDataFrame"] > div { background-color: #161b22 !important; }
  [data-testid="stCheckbox"] label { color: #e6edf3 !important; }
  .stSlider label { color: #e6edf3 !important; }
  div[data-testid="stHorizontalBlock"] .stButton button {
      width: 100%; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
      border-radius: 8px; border: 1px solid #30363d;
      background-color: #161b22; color: #8b949e; padding: 0.5rem 0; transition: all 0.2s;
  }
  div[data-testid="stHorizontalBlock"] .stButton button:hover { border-color: #58a6ff; color: #58a6ff; }

  .dba-card {
      border-radius: 14px; padding: 1.4rem 1.6rem;
      border: 2px solid; position: relative; overflow: hidden;
  }
  .dba-valor {
      font-family: 'IBM Plex Mono', monospace; font-size: 2.8rem;
      font-weight: 700; line-height: 1;
  }
  .dba-nivel {
      font-family: 'IBM Plex Mono', monospace; font-size: 1.0rem;
      font-weight: 600; letter-spacing: 0.05em; margin-top: 0.3rem;
  }
  .dba-desc { font-size: 0.78rem; color: #8b949e; margin-top: 0.4rem; line-height: 1.4; }
  .dba-tiempo {
      font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
      margin-top: 0.5rem; padding: 0.2rem 0.6rem; border-radius: 20px;
      display: inline-block; background: rgba(255,255,255,0.08);
  }
  .riesgo-bar-wrap { margin-top: 0.8rem; }
  .riesgo-bar-track {
      height: 8px; border-radius: 4px; width: 100%;
      background: linear-gradient(to right,
        #34d399 0%, #86efac 18%, #a3e635 28%,
        #fbbf24 40%, #fb923c 55%, #f87171 68%,
        #ef4444 80%, #dc2626 90%, #991b1b 100%);
      position: relative;
  }
  .riesgo-bar-marker {
      position: absolute; top: -4px; width: 16px; height: 16px;
      border-radius: 50%; background: white; border: 3px solid #0d1117;
      transform: translateX(-50%); box-shadow: 0 0 8px rgba(255,255,255,0.5);
  }
  .riesgo-bar-labels {
      display: flex; justify-content: space-between;
      font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: #8b949e;
      margin-top: 4px;
  }
  .uv-card {
      border-radius: 14px; padding: 1.4rem 1.6rem;
      border: 2px solid; position: relative; overflow: hidden;
  }
  .uv-valor {
      font-family: 'IBM Plex Mono', monospace; font-size: 2.8rem;
      font-weight: 700; line-height: 1;
  }
  .uv-nivel {
      font-family: 'IBM Plex Mono', monospace; font-size: 1.0rem;
      font-weight: 600; letter-spacing: 0.05em; margin-top: 0.3rem;
  }
  .uv-desc { font-size: 0.78rem; color: #8b949e; margin-top: 0.4rem; line-height: 1.4; }
  .uv-bar-track {
      height: 8px; border-radius: 4px; width: 100%; margin-top: 0.8rem;
      background: linear-gradient(to right,
        #34d399 0%, #a3e635 20%, #fbbf24 40%,
        #fb923c 60%, #f87171 75%, #991b1b 100%);
      position: relative;
  }
  .uv-bar-marker {
      position: absolute; top: -4px; width: 16px; height: 16px;
      border-radius: 50%; background: white; border: 3px solid #0d1117;
      transform: translateX(-50%); box-shadow: 0 0 8px rgba(255,255,255,0.5);
  }
  .uv-bar-labels {
      display: flex; justify-content: space-between;
      font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: #8b949e;
      margin-top: 4px;
  }

  /* Banner sin sensores propios */
  .no-sensor-banner {
      background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
      border: 1px solid #30363d; border-radius: 12px;
      padding: 2rem; text-align: center; margin: 1rem 0;
  }
  .no-sensor-icon { font-size: 3rem; margin-bottom: 0.5rem; }
  .no-sensor-title {
      font-family: 'IBM Plex Mono', monospace; font-size: 1.1rem;
      color: #8b949e; margin-bottom: 0.4rem;
  }
  .no-sensor-desc { font-size: 0.85rem; color: #6e7681; }
</style>
""", unsafe_allow_html=True)

# ── Configuración de barrios ──────────────────────────────────────────────────
BARRIOS = {
    "Villa Alem": {
        "sheet_id": "1mKNz5DF6Y9Gnolf1sLq8t8079_Oo6-VPxaNZVSJBaPw",
        "gid":      "0",
        "coords":   (-26.846204, -65.214542),
        "sensor_propio": True,
    },
    "Barrio Sur": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid":      "1907877979",
        "coords":   (-26.856000, -65.210000),
        "sensor_propio": False,
    },
    "Barrio Norte": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid":      "145148471",
        "coords":   (-26.820000, -65.210000),
        "sensor_propio": False,
    },
    "Yerba Buena": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid":      "2135910315",
        "coords":   (-26.816000, -65.260000),
        "sensor_propio": False,
    },
    "Yerba Buena Norte": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid":      "1668020872",
        "coords":   (-26.800000, -65.280000),
        "sensor_propio": False,
    },
}

# ── Niveles de riesgo auditivo ─────────────────────────────────────────────────
RIESGOS_DBA = [
    (0,   40,  "Silencio",         "#1e3a2f", "rgb( 52, 211, 153)", "🤫",
     "Ambiente silencioso. Sin riesgo.",                              "Sin límite"),
    (40,  55,  "Bajo",             "#1e3a2f", "rgb( 74, 222, 128)", "🟢",
     "Nivel confortable. Conversación normal.",                       "Sin límite"),
    (55,  70,  "Moderado",         "#2d3a1e", "rgb(163, 230,  53)", "🟡",
     "Molestia leve posible. Zonas residenciales.",                   "Sin límite"),
    (70,  80,  "Elevado",          "#3a2e1e", "rgb(251, 191,  36)", "🟠",
     "Molestia significativa. Puede afectar el sueño.",               "Sin límite"),
    (80,  85,  "Alto",             "#3a251e", "rgb(251, 146,  60)", "🔶",
     "Acción preventiva recomendada (Directiva EU: valor inferior).", "8 hs/día"),
    (85,  90,  "Muy alto",         "#3a1e1e", "rgb(248,  113, 113)","🔴",
     "Riesgo auditivo. Protección obligatoria (OMS/NIOSH).",          "2 hs/día"),
    (90,  100, "Peligroso",        "#2d1515", "rgb(239,  68,  68)", "🚨",
     "Daño auditivo irreversible en exposición prolongada.",          "30 min/día"),
    (100, 110, "Muy peligroso",    "#1f0f0f", "rgb(220,  38,  38)", "⛔",
     "Exposición debe ser mínima. Riesgo inmediato.",                 "5 min/día"),
    (110, 999, "Extremo",          "#150000", "rgb(185,  28,  28)", "💀",
     "Daño inmediato posible. Abandone el área.",                     "< 1 min"),
]

# ── Niveles de riesgo UV ───────────────────────────────────────────────────────
RIESGOS_UV = [
    (0,   3,  "Bajo",          "#1e3a2f", "rgb( 52, 211, 153)", "🟢",
     "Sin peligro para la mayoría. Usar protector si se está mucho tiempo al aire libre.", "FPS 15+"),
    (3,   6,  "Moderado",      "#2d3a1e", "rgb(163, 230,  53)", "🟡",
     "Riesgo moderado. Usar sombrero, anteojos y protector solar.",                        "FPS 30+"),
    (6,   8,  "Alto",          "#3a2e1e", "rgb(251, 191,  36)", "🟠",
     "Riesgo alto. Reducir exposición al mediodía. Protección necesaria.",                 "FPS 50+"),
    (8,   11, "Muy alto",      "#3a1e1e", "rgb(248,  113, 113)","🔴",
     "Riesgo muy alto. Evitar el sol entre 10 y 16 hs. Protección máxima.",               "FPS 50+"),
    (11,  99, "Extremo",       "#150000", "rgb(185,  28,  28)", "💀",
     "Riesgo extremo. Permanecer en interiores. Quemadura en minutos.",                    "FPS 50+"),
]

def get_riesgo_uv(valor):
    if valor is None or (isinstance(valor, float) and valor != valor):
        return ("Sin datos", "#21262d", "rgb(139,148,158)", "❓", "Sin lectura disponible.", "—")
    for vmin, vmax, nivel, chex, crgb, icono, desc, proteccion in RIESGOS_UV:
        if vmin <= valor < vmax:
            return (nivel, chex, crgb, icono, desc, proteccion)
    return ("Extremo", "#150000", "rgb(185,28,28)", "💀", "Riesgo extremo.", "FPS 50+")

def get_riesgo_dba(valor):
    if valor is None or (isinstance(valor, float) and valor != valor):
        return ("Sin datos", "#21262d", "rgb(139,148,158)", "❓", "Sin lectura disponible.", "—")
    for dmin, dmax, nivel, chex, crgb, icono, desc, tmax in RIESGOS_DBA:
        if dmin <= valor < dmax:
            return (nivel, chex, crgb, icono, desc, tmax)
    return ("Extremo", "#150000", "rgb(185,28,28)", "💀", "Daño inmediato posible.", "< 1 min")

# ── Columnas esperadas (hoja completa con sensor propio) ──────────────────────
NOMBRES_COLUMNAS_COMPLETO = [
    "Fecha_Hora", "Temperatura (°C)", "Presión (hPa)", "Humedad (%)",
    "Densidad (kg/m³)", "Humedad Abs (g/m³)", "Sensación Térmica (°C)",
    "Bulbo Húmedo (°C)", "Punto Rocío (°C)", "Presión NM (hPa)", "Altitud (m)",
    "Vel. Viento (km/h)", "Dir. Viento (°)", "Dir. Viento (texto)", "Ráfagas (km/h)",
    "Precip. hora (mm)", "Precip. acum. día (mm)",
    "Radiación Solar (W/m²)", "UV", "Nubosidad (%)",
    "Índice Acústico (I)", "dBA estimado", "Luz Visible (lux)", "IR (counts)",
]

# Columnas básicas que vienen de Wunderground (sin sensor propio)
NOMBRES_COLUMNAS_BASICO = [
    "Fecha_Hora", "Temperatura (°C)", "Presión (hPa)", "Humedad (%)",
    "Densidad (kg/m³)", "Humedad Abs (g/m³)", "Sensación Térmica (°C)",
    "Bulbo Húmedo (°C)", "Punto Rocío (°C)", "Presión NM (hPa)", "Altitud (m)",
]

# Columnas que requieren sensor propio
COLS_SENSOR_PROPIO = {
    "Radiación Solar (W/m²)", "UV", "Nubosidad (%)",
    "Índice Acústico (I)", "dBA estimado", "Luz Visible (lux)", "IR (counts)",
}

# ── Variables a graficar ──────────────────────────────────────────────────────
COLUMNAS = {
    "Temperatura (°C)":       ("Temperatura",         "°C",    "rgb(255,  99,  99)"),
    "Presión (hPa)":          ("Presión",              "hPa",   "rgb( 99, 180, 255)"),
    "Humedad (%)":            ("Humedad Relativa",     "%",     "rgb( 99, 220, 180)"),
    "Densidad (kg/m³)":       ("Densidad del Aire",    "kg/m³", "rgb(200, 150, 255)"),
    "Humedad Abs (g/m³)":     ("Humedad Absoluta",     "g/m³",  "rgb( 88, 166, 255)"),
    "Sensación Térmica (°C)": ("Sensación Térmica",    "°C",    "rgb(255, 165,  50)"),
    "Bulbo Húmedo (°C)":      ("Bulbo Húmedo",         "°C",    "rgb(100, 220, 100)"),
    "Punto Rocío (°C)":       ("Punto de Rocío",       "°C",    "rgb(100, 200, 255)"),
    "Presión NM (hPa)":       ("Presión Nivel Mar",    "hPa",   "rgb(150, 150, 255)"),
    "Altitud (m)":            ("Altitud",              "m",     "rgb(200, 200, 100)"),
    "Vel. Viento (km/h)":     ("Vel. Viento",          "km/h",  "rgb(255, 200,  80)"),
    "Ráfagas (km/h)":         ("Ráfagas",              "km/h",  "rgb(255, 140,  40)"),
    "Precip. hora (mm)":      ("Precip. hora",         "mm",    "rgb( 80, 160, 255)"),
    "Precip. acum. día (mm)": ("Precip. acumulada",    "mm",    "rgb( 50, 120, 220)"),
    "Radiación Solar (W/m²)": ("Radiación Solar",      "W/m²",  "rgb(255, 230,  80)"),
    "UV":                     ("Índice UV",            "",      "rgb(200, 100, 255)"),
    "Nubosidad (%)":          ("Nubosidad",            "%",     "rgb(160, 190, 220)"),
    "dBA estimado":           ("Nivel Sonoro",         "dBA",   "rgb(255, 100,  80)"),
    "Luz Visible (lux)":      ("Luz Visible",          "lux",   "rgb(255, 245, 100)"),
    "IR (counts)":            ("Infrarrojo",           "cnt",   "rgb(255, 120,  60)"),
}

METRICAS_PANEL = [
    ("Temperatura (°C)",       "🌡️ Temperatura",       "°C"),
    ("Presión (hPa)",          "🔵 Presión",            "hPa"),
    ("Humedad (%)",            "💧 Humedad Rel.",        "%"),
    ("Densidad (kg/m³)",       "🌫️ Densidad",            "kg/m³"),
    ("Humedad Abs (g/m³)",     "💦 Hum. Abs.",           "g/m³"),
    ("Sensación Térmica (°C)", "🔥 Sensación Térmica",  "°C"),
    ("Bulbo Húmedo (°C)",      "🌢️ Bulbo Húmedo",       "°C"),
    ("Punto Rocío (°C)",       "🌧️ Pto. Rocío",         "°C"),
    ("Radiación Solar (W/m²)", "☀️ Radiación",           "W/m²"),
    ("UV",                     "🔆 UV",                  ""),
    ("Nubosidad (%)",          "☁️ Nubosidad",           "%"),
    ("Vel. Viento (km/h)",     "💨 Viento",              "km/h"),
    ("dBA estimado",           "🔊 Nivel de Ruido",     "dBA"),
]

# ── Estado de sesión ──────────────────────────────────────────────────────────
if "modo"     not in st.session_state: st.session_state["modo"]     = "actual"
if "n_puntos" not in st.session_state: st.session_state["n_puntos"] = 500
if "barrio"   not in st.session_state: st.session_state["barrio"]   = list(BARRIOS.keys())[0]

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def cargar_datos_raw(sheet_id: str, gid: str):
    if not gid:
        return pd.DataFrame(), "GID de hoja no configurado."

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return pd.DataFrame(), str(e)

    r.encoding = "utf-8"
    texto = r.text.strip()
    if not texto or texto.startswith("<!DOCTYPE") or texto.startswith("<html"):
        return pd.DataFrame(), "Respuesta inválida de Google Sheets"

    primera_linea = texto.split("\n")[0]
    sep = ";" if primera_linea.count(";") > primera_linea.count(",") else ","

    try:
        df = pd.read_csv(io.StringIO(texto), header=0, sep=sep, decimal=",", quotechar='"')
    except Exception as e:
        return pd.DataFrame(), str(e)

    if df.empty or len(df.columns) < 2:
        return pd.DataFrame(), "Datos vacíos"

    n_cols = len(df.columns)
    if n_cols == len(NOMBRES_COLUMNAS_COMPLETO):
        df.columns = NOMBRES_COLUMNAS_COMPLETO
    elif n_cols == len(NOMBRES_COLUMNAS_BASICO):
        df.columns = NOMBRES_COLUMNAS_BASICO
    elif n_cols > len(NOMBRES_COLUMNAS_COMPLETO):
        df = df.iloc[:, :len(NOMBRES_COLUMNAS_COMPLETO)]
        df.columns = NOMBRES_COLUMNAS_COMPLETO
    elif n_cols > len(NOMBRES_COLUMNAS_BASICO):
        # entre 11 y 24 cols: asignar las que entren
        df.columns = NOMBRES_COLUMNAS_COMPLETO[:n_cols]
    else:
        # menos de 11: usar los nombres que haya
        df.columns = df.columns.str.strip()
        df = df.rename(columns={df.columns[0]: "Fecha_Hora"})

    fecha_col = df["Fecha_Hora"].astype(str).str.strip()
    df["Fecha_Hora"] = pd.to_datetime(fecha_col, dayfirst=True, errors="coerce")
    if df["Fecha_Hora"].notna().sum() < len(df) * 0.5:
        df["Fecha_Hora"] = pd.to_datetime(fecha_col, format="%d/%m/%Y %H:%M:%S", errors="coerce")

    df = df.dropna(subset=["Fecha_Hora"])

    for col in df.columns:
        if col != "Fecha_Hora" and col != "Dir. Viento (texto)":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values("Fecha_Hora").reset_index(drop=True), ""


def tiene_sensor_propio(df):
    """True si el df tiene al menos una columna de sensor propio con datos reales."""
    for col in COLS_SENSOR_PROPIO:
        if col in df.columns and df[col].dropna().shape[0] > 0:
            return True
    return False


def filtrar_actual(df):
    if df.empty: return df
    corte = datetime.now() - timedelta(hours=24)
    return df[df["Fecha_Hora"] >= corte].reset_index(drop=True)


def filtrar_historico(df, fecha_ini, fecha_fin):
    if df.empty: return df
    ini = pd.Timestamp(fecha_ini)
    fin = pd.Timestamp(fecha_fin) + timedelta(days=1) - timedelta(seconds=1)
    return df[(df["Fecha_Hora"] >= ini) & (df["Fecha_Hora"] <= fin)].reset_index(drop=True)


def calcular_rango_y(serie, margen_pct=0.10, margen_minimo=0.001):
    datos = serie.dropna()
    if datos.empty: return None, None
    v_min, v_max = datos.min(), datos.max()
    rango  = v_max - v_min
    margen = max(rango * margen_pct, margen_minimo) if rango != 0 else max(abs(v_min) * 0.05, margen_minimo)
    return v_min - margen, v_max + margen


def construir_grafico(df, col_sheet, color, titulo, unidad, n_puntos):
    if col_sheet not in df.columns: return None
    df_plot = df.tail(n_puntos).copy()
    if df_plot[col_sheet].dropna().empty: return None

    y_min, y_max = calcular_rango_y(df_plot[col_sheet])
    fill_color   = color.replace(")", ", 0.10)").replace("rgb", "rgba")
    suffix       = f" {unidad}" if unidad else ""

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["Fecha_Hora"], y=[y_min] * len(df_plot),
        mode="lines", line=dict(width=0, color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df_plot["Fecha_Hora"], y=df_plot[col_sheet],
        mode="lines", line=dict(color=color, width=2),
        fill="tonexty", fillcolor=fill_color,
        hovertemplate=f"<b>%{{x|%d/%m %H:%M:%S}}</b><br>{titulo}: %{{y:.2f}}{suffix}<extra></extra>",
    ))
    last_valid = df_plot[col_sheet].dropna()
    if not last_valid.empty:
        last_idx = last_valid.index[-1]
        fig.add_trace(go.Scatter(
            x=[df_plot.loc[last_idx, "Fecha_Hora"]], y=[last_valid.iloc[-1]],
            mode="markers",
            marker=dict(color=color, size=10, line=dict(color="white", width=2)),
            showlegend=False, hoverinfo="skip",
        ))

    tick_fmt = "%H:%M:%S" if (df_plot["Fecha_Hora"].max() - df_plot["Fecha_Hora"].min()).days < 1 else "%d/%m %H:%M"
    fig.update_layout(
        title=dict(text=titulo, font=dict(family="IBM Plex Mono", size=14, color="#8b949e"), x=0.01),
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        margin=dict(l=10, r=10, t=40, b=10), height=260,
        xaxis=dict(showgrid=True, gridcolor="#21262d",
                   tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                   tickformat=tick_fmt, color="#8b949e"),
        yaxis=dict(showgrid=True, gridcolor="#21262d",
                   tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                   ticksuffix=suffix, color="#8b949e", range=[y_min, y_max]),
        hovermode="x unified", showlegend=False,
        font=dict(color="#8b949e"),
    )
    return fig


def construir_gauge_dba(valor_dba):
    if valor_dba is None or pd.isna(valor_dba): return None
    nivel, chex, crgb, icono, desc, tmax = get_riesgo_dba(valor_dba)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_dba,
        number=dict(suffix=" dBA", font=dict(family="IBM Plex Mono", size=28, color=crgb)),
        gauge=dict(
            axis=dict(range=[30, 120], tickwidth=1, tickcolor="#30363d",
                      tickfont=dict(family="IBM Plex Mono", size=9, color="#8b949e"), dtick=10),
            bar=dict(color=crgb, thickness=0.25),
            bgcolor="#161b22", borderwidth=0,
            steps=[
                dict(range=[30,  40], color="#1e3a2f"), dict(range=[40,  55], color="#1e3a2f"),
                dict(range=[55,  70], color="#2d3a1e"), dict(range=[70,  80], color="#3a2e1e"),
                dict(range=[80,  85], color="#3a251e"), dict(range=[85,  90], color="#3a1e1e"),
                dict(range=[90, 100], color="#2d1515"), dict(range=[100,110], color="#1f0f0f"),
                dict(range=[110,120], color="#150000"),
            ],
            threshold=dict(line=dict(color="white", width=3), thickness=0.8, value=valor_dba),
        ),
        title=dict(
            text=f"{icono} {nivel}<br><span style='font-size:0.7em; color:#8b949e'>{tmax}</span>",
            font=dict(family="IBM Plex Mono", size=14, color=crgb),
        ),
    ))
    fig.update_layout(paper_bgcolor="#0d1117", margin=dict(l=20, r=20, t=60, b=10),
                      height=280, font=dict(color="#8b949e"))
    return fig


def construir_gauge_uv(valor_uv):
    if valor_uv is None or pd.isna(valor_uv): return None
    nivel, chex, crgb, icono, desc, proteccion = get_riesgo_uv(valor_uv)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_uv,
        number=dict(font=dict(family="IBM Plex Mono", size=28, color=crgb)),
        gauge=dict(
            axis=dict(range=[0, 14], tickwidth=1, tickcolor="#30363d",
                      tickfont=dict(family="IBM Plex Mono", size=9, color="#8b949e"), dtick=2),
            bar=dict(color=crgb, thickness=0.25),
            bgcolor="#161b22", borderwidth=0,
            steps=[
                dict(range=[0,  3], color="#1e3a2f"), dict(range=[3,  6], color="#2d3a1e"),
                dict(range=[6,  8], color="#3a2e1e"), dict(range=[8, 11], color="#3a1e1e"),
                dict(range=[11,14], color="#150000"),
            ],
            threshold=dict(line=dict(color="white", width=3), thickness=0.8, value=valor_uv),
        ),
        title=dict(
            text=f"{icono} {nivel}<br><span style='font-size:0.7em; color:#8b949e'>{proteccion}</span>",
            font=dict(family="IBM Plex Mono", size=14, color=crgb),
        ),
    ))
    fig.update_layout(paper_bgcolor="#0d1117", margin=dict(l=20, r=20, t=60, b=10),
                      height=280, font=dict(color="#8b949e"))
    return fig


def card_dba_html(valor_dba):
    if valor_dba is None or pd.isna(valor_dba):
        return """<div class='dba-card' style='border-color:#30363d; background:#161b22;'>
            <div class='metric-label'>🔊 Nivel de Ruido</div>
            <div class='dba-valor' style='color:#8b949e;'>—</div>
            <div class='dba-desc'>Sin datos de audio disponibles.</div></div>"""
    nivel, chex, crgb, icono, desc, tmax = get_riesgo_dba(valor_dba)
    pct = max(0.0, min(100.0, (valor_dba - 30) / (120 - 30) * 100))
    return f"""
    <div class='dba-card' style='border-color:{crgb}; background: linear-gradient(135deg, {chex} 0%, #0d1117 100%);'>
        <div class='metric-label'>🔊 Nivel de Ruido</div>
        <div style='display:flex; align-items:baseline; gap:0.5rem;'>
            <div class='dba-valor' style='color:{crgb};'>{valor_dba:.1f}</div>
            <div style='font-family:IBM Plex Mono; color:#8b949e; font-size:1rem;'>dBA</div>
        </div>
        <div class='dba-nivel' style='color:{crgb};'>{icono} {nivel}</div>
        <div class='dba-desc'>{desc}</div>
        <div class='dba-tiempo'>⏱ Exposición máxima recomendada: {tmax}</div>
        <div class='riesgo-bar-wrap'>
            <div class='riesgo-bar-track'><div class='riesgo-bar-marker' style='left:{pct}%;'></div></div>
            <div class='riesgo-bar-labels'>
                <span>30</span><span>55</span><span>70</span><span>85</span><span>100</span><span>120</span>
            </div>
        </div>
    </div>"""


def card_uv_html(valor_uv):
    if valor_uv is None or pd.isna(valor_uv):
        return """<div class='uv-card' style='border-color:#30363d; background:#161b22;'>
            <div class='metric-label'>🔆 Índice UV</div>
            <div class='uv-valor' style='color:#8b949e;'>—</div>
            <div class='uv-desc'>Sin datos UV disponibles.</div></div>"""
    nivel, chex, crgb, icono, desc, proteccion = get_riesgo_uv(valor_uv)
    pct = max(0.0, min(100.0, valor_uv / 14.0 * 100))
    return f"""
    <div class='uv-card' style='border-color:{crgb}; background: linear-gradient(135deg, {chex} 0%, #0d1117 100%);'>
        <div class='metric-label'>🔆 Índice UV</div>
        <div style='display:flex; align-items:baseline; gap:0.5rem;'>
            <div class='uv-valor' style='color:{crgb};'>{valor_uv:.1f}</div>
            <div style='font-family:IBM Plex Mono; color:#8b949e; font-size:1rem;'>UVI</div>
        </div>
        <div class='uv-nivel' style='color:{crgb};'>{icono} {nivel}</div>
        <div class='uv-desc'>{desc}</div>
        <div class='dba-tiempo'>🧴 Protección recomendada: {proteccion}</div>
        <div class='riesgo-bar-wrap'>
            <div class='uv-bar-track'><div class='uv-bar-marker' style='left:{pct}%;'></div></div>
            <div class='uv-bar-labels'>
                <span>0</span><span>3</span><span>6</span><span>8</span><span>11</span><span>14+</span>
            </div>
        </div>
    </div>"""


def banner_sin_sensor(tipo):
    iconos = {"acustico": "🔊", "radiacion": "☀️"}
    titulos = {"acustico": "Sin sensor acústico", "radiacion": "Sin sensor de radiación"}
    descs = {
        "acustico":  "Este barrio no cuenta con estación propia. Los datos acústicos (dBA, índice de ruido) solo están disponibles para Villa Alem.",
        "radiacion": "Este barrio no cuenta con estación propia. Los datos de radiación solar, UV y luz visible solo están disponibles para Villa Alem.",
    }
    return f"""<div class='no-sensor-banner'>
        <div class='no-sensor-icon'>{iconos[tipo]}</div>
        <div class='no-sensor-title'>{titulos[tipo]}</div>
        <div class='no-sensor-desc'>{descs[tipo]}</div>
    </div>"""


def tabla_referencia_riesgo():
    filas = ""
    for dmin, dmax, nivel, chex, crgb, icono, desc, tmax in RIESGOS_DBA:
        rango = f"{dmin}–{dmax if dmax < 999 else '120+'} dBA"
        filas += f"""<tr>
            <td style='color:{crgb}; font-family:IBM Plex Mono; font-weight:600;'>{icono} {nivel}</td>
            <td style='font-family:IBM Plex Mono; color:#8b949e;'>{rango}</td>
            <td style='color:#c9d1d9; font-size:0.85rem;'>{desc}</td>
            <td style='font-family:IBM Plex Mono; color:{crgb}; font-size:0.85rem;'>{tmax}</td>
        </tr>"""
    return f"""<table style='width:100%; border-collapse:collapse; font-size:0.88rem;'>
        <thead><tr style='border-bottom:1px solid #30363d;'>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Nivel</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Rango</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Descripción</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Exposición máx.</th>
        </tr></thead><tbody>{filas}</tbody></table>
    <p style='font-size:0.72rem; color:#8b949e; margin-top:0.8rem;'>
        Fuentes: OMS · NIOSH · Directiva EU 2003/10/CE · Ley de Riesgos del Trabajo (Argentina)</p>"""


def tabla_referencia_uv():
    filas = ""
    for vmin, vmax, nivel, chex, crgb, icono, desc, proteccion in RIESGOS_UV:
        rango = f"{vmin}–{vmax if vmax < 99 else '11+'}"
        filas += f"""<tr>
            <td style='color:{crgb}; font-family:IBM Plex Mono; font-weight:600;'>{icono} {nivel}</td>
            <td style='font-family:IBM Plex Mono; color:#8b949e;'>{rango}</td>
            <td style='color:#c9d1d9; font-size:0.85rem;'>{desc}</td>
            <td style='font-family:IBM Plex Mono; color:{crgb}; font-size:0.85rem;'>{proteccion}</td>
        </tr>"""
    return f"""<table style='width:100%; border-collapse:collapse; font-size:0.88rem;'>
        <thead><tr style='border-bottom:1px solid #30363d;'>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Nivel</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Índice UV</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Descripción</th>
            <th style='text-align:left; padding:0.5rem; color:#8b949e; font-family:IBM Plex Mono;'>Protección</th>
        </tr></thead><tbody>{filas}</tbody></table>
    <p style='font-size:0.72rem; color:#8b949e; margin-top:0.8rem;'>
        Fuentes: OMS · EPA · Servicio Nacional de Meteorología e Hidrología (Argentina)</p>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("### 📍 Barrio")
    barrio_sel = st.selectbox(
        "Seleccioná el barrio", options=list(BARRIOS.keys()),
        index=list(BARRIOS.keys()).index(st.session_state["barrio"]),
        label_visibility="collapsed", key="selectbox_barrio",
    )
    if barrio_sel != st.session_state["barrio"]:
        st.session_state["barrio"] = barrio_sel
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Actual" if st.session_state["modo"] == "actual" else "📡 Actual",
                     key="btn_actual", use_container_width=True):
            st.session_state["modo"] = "actual"; st.rerun()
    with col_b:
        if st.button("✅ Histórico" if st.session_state["modo"] == "historico" else "📅 Histórico",
                     key="btn_historico", use_container_width=True):
            st.session_state["modo"] = "historico"; st.rerun()

    st.markdown("---")
    modo = st.session_state["modo"]

    if modo == "actual":
        intervalo   = st.slider("Intervalo de refresco (seg)", 10, 60, 60)
        if st.session_state["n_puntos"] < 2: st.session_state["n_puntos"] = 2
        n_puntos    = st.slider("Puntos en el gráfico", 2, 500, key="n_puntos")
        auto_update = st.toggle("Auto-actualizar", value=True)
        fecha_ini_sel = fecha_fin_sel = None
    else:
        intervalo   = 60
        auto_update = False
        n_puntos    = st.session_state.get("n_puntos", 500)
        st.markdown("**Fecha inicio:**")
        fecha_ini_sel = st.date_input("ini", value=datetime.now().date() - timedelta(days=7),
                                      label_visibility="collapsed", key="fecha_ini")
        st.markdown("**Fecha fin:**")
        fecha_fin_sel = st.date_input("fin", value=datetime.now().date(),
                                      label_visibility="collapsed", key="fecha_fin")
        if fecha_ini_sel > fecha_fin_sel:
            st.warning("⚠️ La fecha inicio debe ser anterior a la fecha fin.")

    st.markdown("---")
    st.markdown("### Variables a mostrar")
    vars_seleccionadas = []
    for col_sheet, (etiqueta, unidad, color) in COLUMNAS.items():
        if st.checkbox(etiqueta, value=True, key=f"chk_{col_sheet}"):
            vars_seleccionadas.append(col_sheet)

# ── Barrio activo ─────────────────────────────────────────────────────────────
barrio_nombre = st.session_state["barrio"]
barrio_cfg    = BARRIOS[barrio_nombre]
coords        = barrio_cfg["coords"]

# ── Header ────────────────────────────────────────────────────────────────────
if modo == "actual":
    subtitulo = "Últimas 24 horas · actualización automática"
    icono_dot = "<span class='status-dot'></span>"
else:
    subtitulo = f"Histórico · {fecha_ini_sel.strftime('%d/%m/%Y')} al {fecha_fin_sel.strftime('%d/%m/%Y')}"
    icono_dot = "📅 "

if coords:
    lat, lon = coords
    link_html = (
        f'<a href="https://maps.google.com/?q={lat},{lon}" target="_blank" '
        f'style="font-size:1.6rem; font-family: IBM Plex Mono; color:#8b949e; '
        f'text-decoration:none; font-weight:400;">📍 {barrio_nombre}</a>'
    )
else:
    link_html = f'<span style="font-size:1.6rem; font-family:IBM Plex Mono; color:#8b949e; font-weight:400;">📍 {barrio_nombre}</span>'

st.markdown(
    f"""<h1 style='font-size:1.6rem; margin-bottom:0;'>
  {icono_dot}Monitor climático de Tucumán · {'Tiempo Real' if modo == 'actual' else 'Histórico'} &nbsp;
  {link_html}
</h1>
<p style='color:#8b949e; font-size:0.85rem; margin-top:0.2rem;'>{subtitulo}</p>""",
    unsafe_allow_html=True,
)

tab_monitor, tab_acustico, tab_radiacion, tab_stats = st.tabs([
    "📡 Monitor", "🔊 Acústico", "☀️ Radiación", "📊 Estadísticas"
])
ph_metricas  = tab_monitor.empty()
ph_graficos  = tab_monitor.empty()
ph_footer    = tab_monitor.empty()
ph_acustico  = tab_acustico.empty()
ph_radiacion = tab_radiacion.empty()
ph_stats     = tab_stats.empty()

# ── Loop principal ────────────────────────────────────────────────────────────
while True:
    df_raw, err = cargar_datos_raw(barrio_cfg["sheet_id"], barrio_cfg["gid"])

    if df_raw.empty:
        with ph_metricas.container():
            st.error(f"⚠️ No se pudieron cargar datos para **{barrio_nombre}**. {err}")
        if auto_update:
            time.sleep(intervalo); st.cache_data.clear(); st.rerun()
        break

    if modo == "actual":
        df = filtrar_actual(df_raw)
        if df.empty: df = df_raw.copy()
    else:
        df = filtrar_historico(df_raw, fecha_ini_sel, fecha_fin_sel) if fecha_ini_sel <= fecha_fin_sel else pd.DataFrame()

    if df.empty:
        with ph_metricas.container():
            st.warning("⚠️ No hay datos para el rango seleccionado.")
        if auto_update and modo == "actual":
            time.sleep(intervalo); st.cache_data.clear(); st.rerun()
        break

    # Detectar si este barrio tiene sensor propio con datos reales
    hay_sensor = tiene_sensor_propio(df)

    ultima_fila = df.iloc[-1]

    def get_float(col):
        if col in df.columns:
            v = ultima_fila.get(col)
            if pd.notna(v): return float(v)
        return None

    dba_actual = get_float("dBA estimado")
    uv_actual  = get_float("UV")
    rad_actual = get_float("Radiación Solar (W/m²)")
    lux_actual = get_float("Luz Visible (lux)")
    ir_actual  = get_float("IR (counts)")

    # ── Métricas ──────────────────────────────────────────────────────────────
    with ph_metricas.container():
        # Filtrar métricas que tienen datos en este barrio
        metricas_disp = [(c, l, u) for c, l, u in METRICAS_PANEL if c in df.columns and pd.notna(ultima_fila.get(c, None))]

        cols1 = st.columns(min(6, len(metricas_disp)))
        for i, (col_sheet, label, unidad) in enumerate(metricas_disp[:6]):
            val = ultima_fila[col_sheet]
            with cols1[i]:
                st.markdown(f"""<div class='metric-card'>
                  <div class='metric-label'>{label}</div>
                  <div class='metric-value'>{val:.1f}<span class='metric-unit'>{unidad}</span></div>
                </div>""", unsafe_allow_html=True)

        if len(metricas_disp) > 6:
            st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
            resto = metricas_disp[6:]
            cols2 = st.columns(min(7, len(resto)))
            for i, (col_sheet, label, unidad) in enumerate(resto):
                val = ultima_fila[col_sheet]
                with cols2[i]:
                    st.markdown(f"""<div class='metric-card'>
                      <div class='metric-label'>{label}</div>
                      <div class='metric-value'>{val:.1f}<span class='metric-unit'>{unidad}</span></div>
                    </div>""", unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    n_pts_graf = n_puntos if modo == "actual" else len(df)

    with ph_graficos.container():
        # Filtrar variables seleccionadas que existen en este df
        vars_disp = [c for c in vars_seleccionadas if c in df.columns and df[c].dropna().shape[0] > 0]

        if not vars_disp:
            st.info("Seleccioná al menos una variable en el panel izquierdo.")
        else:
            cols_graf = st.columns(2)
            for idx, col_sheet in enumerate(vars_disp):
                etiqueta, unidad, color = COLUMNAS[col_sheet]
                fig = construir_grafico(df, col_sheet, color, etiqueta, unidad, n_pts_graf)
                if fig:
                    with cols_graf[idx % 2]:
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}_{time.time()}")

        with st.expander("📋 Últimas 60 lecturas"):
            cols_tabla = ["Fecha_Hora"] + [c for c in COLUMNAS if c in df.columns]
            df_tabla = df.tail(60)[cols_tabla].copy()
            df_tabla["Fecha_Hora"] = df_tabla["Fecha_Hora"].dt.strftime("%d/%m %H:%M:%S")
            st.dataframe(df_tabla[::-1], use_container_width=True, hide_index=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    with ph_footer.container():
        if modo == "actual":
            footer_txt = f"Próximo refresco en {intervalo}s · Última actualización: {datetime.now().strftime('%H:%M:%S')} · {barrio_nombre}"
        else:
            footer_txt = f"Modo histórico · {barrio_nombre} · {len(df)} registros · {fecha_ini_sel.strftime('%d/%m/%Y')} → {fecha_fin_sel.strftime('%d/%m/%Y')}"
        st.markdown(f"""<div style='text-align:center; color:#8b949e; font-family: IBM Plex Mono;
            font-size:0.72rem; padding:1rem 0; border-top:1px solid #21262d; margin-top:1rem;'>
          {footer_txt}</div>""", unsafe_allow_html=True)

    # ── Tab Acústico ──────────────────────────────────────────────────────────
    with ph_acustico.container():
        st.markdown(f"### 🔊 Monitor Acústico · {barrio_nombre}")

        if not hay_sensor:
            st.markdown(banner_sin_sensor("acustico"), unsafe_allow_html=True)
        elif "dBA estimado" not in df.columns or df["dBA estimado"].dropna().empty:
            st.info("No hay datos acústicos disponibles para este barrio.")
        else:
            col_gauge, col_info = st.columns([1, 1])
            with col_gauge:
                fig_gauge = construir_gauge_dba(dba_actual)
                if fig_gauge:
                    st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{time.time()}")
            with col_info:
                st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
                st.markdown(card_dba_html(dba_actual), unsafe_allow_html=True)
                s_dba = df["dBA estimado"].dropna()
                if len(s_dba) >= 2:
                    st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"""<div class='metric-card'>
                          <div class='metric-label'>📉 Mínimo</div>
                          <div class='metric-value' style='font-size:1.5rem;'>{s_dba.min():.1f}<span class='metric-unit'>dBA</span></div>
                        </div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""<div class='metric-card'>
                          <div class='metric-label'>📊 Promedio</div>
                          <div class='metric-value' style='font-size:1.5rem;'>{s_dba.mean():.1f}<span class='metric-unit'>dBA</span></div>
                        </div>""", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""<div class='metric-card'>
                          <div class='metric-label'>📈 Máximo</div>
                          <div class='metric-value' style='font-size:1.5rem;'>{s_dba.max():.1f}<span class='metric-unit'>dBA</span></div>
                        </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Evolución del nivel sonoro")
            df_dba = df[["Fecha_Hora","dBA estimado"]].dropna().tail(n_pts_graf)
            if not df_dba.empty:
                fig_dba = go.Figure()
                zonas = [
                    (30,  55,  "rgba( 52,211,153,0.06)", "Seguro"),
                    (55,  70,  "rgba(163,230, 53,0.06)", "Moderado"),
                    (70,  85,  "rgba(251,191, 36,0.06)", "Elevado"),
                    (85, 100,  "rgba(248,113,113,0.06)", "Peligroso"),
                    (100,120,  "rgba(185, 28, 28,0.10)", "Muy peligroso"),
                ]
                for y0, y1, color_zona, nombre_zona in zonas:
                    fig_dba.add_hrect(y0=y0, y1=y1, fillcolor=color_zona, line_width=0,
                        annotation_text=nombre_zona, annotation_position="right",
                        annotation_font=dict(family="IBM Plex Mono", size=9, color="#8b949e"))
                fig_dba.add_hline(y=85, line_dash="dash", line_color="rgba(248,113,113,0.5)", line_width=1.5,
                    annotation_text="85 dBA · límite OMS", annotation_position="left",
                    annotation_font=dict(family="IBM Plex Mono", size=9, color="rgba(248,113,113,0.8)"))
                fig_dba.add_trace(go.Scatter(x=df_dba["Fecha_Hora"], y=[30]*len(df_dba),
                    mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
                fig_dba.add_trace(go.Scatter(x=df_dba["Fecha_Hora"], y=df_dba["dBA estimado"],
                    mode="lines", line=dict(color="rgb(255,100,80)", width=2),
                    fill="tonexty", fillcolor="rgba(255,100,80,0.10)",
                    hovertemplate="<b>%{x|%d/%m %H:%M:%S}</b><br>dBA: %{y:.1f}<extra></extra>"))
                tick_fmt = "%H:%M:%S" if (df_dba["Fecha_Hora"].max() - df_dba["Fecha_Hora"].min()).days < 1 else "%d/%m %H:%M"
                fig_dba.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                    margin=dict(l=10, r=90, t=20, b=10), height=320,
                    xaxis=dict(showgrid=True, gridcolor="#21262d",
                               tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                               tickformat=tick_fmt, color="#8b949e"),
                    yaxis=dict(showgrid=True, gridcolor="#21262d",
                               tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                               ticksuffix=" dBA", color="#8b949e", range=[30, 120]),
                    hovermode="x unified", showlegend=False, font=dict(color="#8b949e"))
                st.plotly_chart(fig_dba, use_container_width=True, key=f"dba_hist_{time.time()}")

            st.markdown("#### Distribución de tiempo por nivel de riesgo")
            s_todos = df["dBA estimado"].dropna()
            conteos = {}
            for dmin, dmax, nivel, chex, crgb, icono, desc, tmax in RIESGOS_DBA:
                c = ((s_todos >= dmin) & (s_todos < dmax)).sum()
                if c > 0: conteos[f"{icono} {nivel}"] = (c, crgb)
            if conteos:
                labels = list(conteos.keys())
                values = [v[0] for v in conteos.values()]
                colors = [v[1] for v in conteos.values()]
                fig_pie = go.Figure(go.Pie(labels=labels, values=values,
                    marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
                    textinfo="label+percent",
                    textfont=dict(family="IBM Plex Mono", size=11),
                    hovertemplate="<b>%{label}</b><br>%{value} registros (%{percent})<extra></extra>",
                    hole=0.4))
                fig_pie.update_layout(paper_bgcolor="#0d1117", margin=dict(l=10,r=10,t=20,b=10),
                    height=300, showlegend=False, font=dict(color="#8b949e"))
                st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{time.time()}")

            st.markdown("---")
            st.markdown("#### 📋 Tabla de referencia de riesgos auditivos")
            st.markdown(tabla_referencia_riesgo(), unsafe_allow_html=True)

    # ── Tab Radiación ─────────────────────────────────────────────────────────
    with ph_radiacion.container():
        st.markdown(f"### ☀️ Monitor de Radiación · {barrio_nombre}")

        if not hay_sensor:
            st.markdown(banner_sin_sensor("radiacion"), unsafe_allow_html=True)
        else:
            cols_rad_disponibles = [c for c in ["Radiación Solar (W/m²)", "UV", "Luz Visible (lux)", "IR (counts)"] if c in df.columns]
            if not cols_rad_disponibles:
                st.info("No hay datos de radiación disponibles para este barrio.")
            else:
                col_g, col_c, col_m = st.columns([1, 1, 1])
                with col_g:
                    fig_uv_gauge = construir_gauge_uv(uv_actual)
                    if fig_uv_gauge:
                        st.plotly_chart(fig_uv_gauge, use_container_width=True, key=f"uv_gauge_{time.time()}")
                with col_c:
                    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
                    st.markdown(card_uv_html(uv_actual), unsafe_allow_html=True)
                with col_m:
                    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
                    for _, label, unidad, val in [
                        ("Radiación Solar (W/m²)", "☀️ Radiación",  "W/m²", rad_actual),
                        ("Luz Visible (lux)",      "💡 Luz Visible", "lux",  lux_actual),
                        ("IR (counts)",            "🔴 Infrarrojo",  "cnt",  ir_actual),
                    ]:
                        if val is not None:
                            st.markdown(f"""<div class='metric-card' style='margin-bottom:0.5rem;'>
                              <div class='metric-label'>{label}</div>
                              <div class='metric-value' style='font-size:1.6rem;'>{val:.1f}<span class='metric-unit'>{unidad}</span></div>
                            </div>""", unsafe_allow_html=True)

                st.markdown("---")

                if "Radiación Solar (W/m²)" in df.columns and df["Radiación Solar (W/m²)"].dropna().shape[0] > 0:
                    st.markdown("#### Evolución de la Radiación Solar")
                    df_rad = df[["Fecha_Hora", "Radiación Solar (W/m²)"]].dropna().tail(n_pts_graf)
                    if not df_rad.empty:
                        fig_rad = go.Figure()
                        for y0, y1, color_zona, nombre_zona in [
                            (0,   200, "rgba(52,211,153,0.05)",  "Baja"),
                            (200, 400, "rgba(163,230,53,0.05)",  "Moderada"),
                            (400, 700, "rgba(251,191,36,0.05)",  "Alta"),
                            (700,1000, "rgba(248,113,113,0.05)", "Muy alta"),
                            (1000,1200,"rgba(185,28,28,0.08)",   "Máxima"),
                        ]:
                            fig_rad.add_hrect(y0=y0, y1=y1, fillcolor=color_zona, line_width=0,
                                annotation_text=nombre_zona, annotation_position="right",
                                annotation_font=dict(family="IBM Plex Mono", size=9, color="#8b949e"))
                        fig_rad.add_trace(go.Scatter(x=df_rad["Fecha_Hora"], y=[0]*len(df_rad),
                            mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
                        fig_rad.add_trace(go.Scatter(x=df_rad["Fecha_Hora"], y=df_rad["Radiación Solar (W/m²)"],
                            mode="lines", line=dict(color="rgb(255,230,80)", width=2),
                            fill="tonexty", fillcolor="rgba(255,230,80,0.12)",
                            hovertemplate="<b>%{x|%d/%m %H:%M:%S}</b><br>Radiación: %{y:.1f} W/m²<extra></extra>"))
                        tick_fmt_r = "%H:%M:%S" if (df_rad["Fecha_Hora"].max() - df_rad["Fecha_Hora"].min()).days < 1 else "%d/%m %H:%M"
                        fig_rad.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                            margin=dict(l=10, r=90, t=20, b=10), height=280,
                            xaxis=dict(showgrid=True, gridcolor="#21262d",
                                       tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                                       tickformat=tick_fmt_r, color="#8b949e"),
                            yaxis=dict(showgrid=True, gridcolor="#21262d",
                                       tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                                       ticksuffix=" W/m²", color="#8b949e", rangemode="tozero"),
                            hovermode="x unified", showlegend=False, font=dict(color="#8b949e"))
                        st.plotly_chart(fig_rad, use_container_width=True, key=f"rad_hist_{time.time()}")

                col_lux, col_ir = st.columns(2)
                with col_lux:
                    if "Luz Visible (lux)" in df.columns and df["Luz Visible (lux)"].dropna().shape[0] > 0:
                        st.markdown("#### Luz Visible (lux)")
                        fig_lux = construir_grafico(df, "Luz Visible (lux)", "rgb(255,245,100)", "Luz Visible", "lux", n_pts_graf)
                        if fig_lux: st.plotly_chart(fig_lux, use_container_width=True, key=f"lux_hist_{time.time()}")
                with col_ir:
                    if "IR (counts)" in df.columns and df["IR (counts)"].dropna().shape[0] > 0:
                        st.markdown("#### Infrarrojo (counts)")
                        fig_ir = construir_grafico(df, "IR (counts)", "rgb(255,120,60)", "Canal IR", "cnt", n_pts_graf)
                        if fig_ir: st.plotly_chart(fig_ir, use_container_width=True, key=f"ir_hist_{time.time()}")

                if "UV" in df.columns and df["UV"].dropna().shape[0] > 0:
                    st.markdown("#### Evolución del Índice UV")
                    df_uv = df[["Fecha_Hora", "UV"]].dropna().tail(n_pts_graf)
                    if not df_uv.empty:
                        fig_uv = go.Figure()
                        for y0, y1, color_zona, nombre_zona in [
                            (0,  3,  "rgba(52,211,153,0.06)",  "Bajo"),
                            (3,  6,  "rgba(163,230,53,0.06)",  "Moderado"),
                            (6,  8,  "rgba(251,191,36,0.06)",  "Alto"),
                            (8,  11, "rgba(248,113,113,0.06)", "Muy alto"),
                            (11, 14, "rgba(185,28,28,0.10)",   "Extremo"),
                        ]:
                            fig_uv.add_hrect(y0=y0, y1=y1, fillcolor=color_zona, line_width=0,
                                annotation_text=nombre_zona, annotation_position="right",
                                annotation_font=dict(family="IBM Plex Mono", size=9, color="#8b949e"))
                        fig_uv.add_hline(y=8, line_dash="dash", line_color="rgba(248,113,113,0.5)", line_width=1.5,
                            annotation_text="UV 8 · muy alto", annotation_position="left",
                            annotation_font=dict(family="IBM Plex Mono", size=9, color="rgba(248,113,113,0.8)"))
                        fig_uv.add_trace(go.Scatter(x=df_uv["Fecha_Hora"], y=[0]*len(df_uv),
                            mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
                        fig_uv.add_trace(go.Scatter(x=df_uv["Fecha_Hora"], y=df_uv["UV"],
                            mode="lines", line=dict(color="rgb(200,100,255)", width=2),
                            fill="tonexty", fillcolor="rgba(200,100,255,0.12)",
                            hovertemplate="<b>%{x|%d/%m %H:%M:%S}</b><br>UV: %{y:.1f}<extra></extra>"))
                        tick_fmt_uv = "%H:%M:%S" if (df_uv["Fecha_Hora"].max() - df_uv["Fecha_Hora"].min()).days < 1 else "%d/%m %H:%M"
                        fig_uv.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                            margin=dict(l=10, r=90, t=20, b=10), height=260,
                            xaxis=dict(showgrid=True, gridcolor="#21262d",
                                       tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                                       tickformat=tick_fmt_uv, color="#8b949e"),
                            yaxis=dict(showgrid=True, gridcolor="#21262d",
                                       tickfont=dict(family="IBM Plex Mono", size=10, color="#8b949e"),
                                       color="#8b949e", range=[0, 14]),
                            hovermode="x unified", showlegend=False, font=dict(color="#8b949e"))
                        st.plotly_chart(fig_uv, use_container_width=True, key=f"uv_hist_{time.time()}")

                st.markdown("---")
                st.markdown("#### Estadísticas del período")
                cols_stats_rad = [c for c in ["Radiación Solar (W/m²)", "UV", "Luz Visible (lux)", "IR (counts)"] if c in df.columns]
                if cols_stats_rad:
                    cols_sr = st.columns(len(cols_stats_rad))
                    for i, col_s in enumerate(cols_stats_rad):
                        s = df[col_s].dropna()
                        if s.empty: continue
                        etiqueta = COLUMNAS[col_s][0]; unidad = COLUMNAS[col_s][1]
                        suf = f" {unidad}" if unidad else ""
                        with cols_sr[i]:
                            st.markdown(f"""<div class='metric-card'>
                              <div class='metric-label'>{etiqueta}</div>
                              <div style='font-family:IBM Plex Mono; font-size:0.8rem; color:#8b949e; margin:0.3rem 0;'>
                                MÍN <span style='color:#58a6ff'>{s.min():.1f}{suf}</span> &nbsp;
                                MÁX <span style='color:#58a6ff'>{s.max():.1f}{suf}</span>
                              </div>
                              <div style='font-family:IBM Plex Mono; font-size:0.8rem; color:#8b949e;'>
                                PROM <span style='color:#58a6ff'>{s.mean():.1f}{suf}</span>
                              </div>
                            </div>""", unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("#### 📋 Tabla de referencia índice UV")
                st.markdown(tabla_referencia_uv(), unsafe_allow_html=True)

    # ── Estadísticas ──────────────────────────────────────────────────────────
    with ph_stats.container():
        import numpy as np
        rango_label = "últimas 24 horas" if modo == "actual" else f"{fecha_ini_sel.strftime('%d/%m/%Y')} → {fecha_fin_sel.strftime('%d/%m/%Y')}"
        st.markdown(f"### 📊 Estadísticas · {barrio_nombre} · {rango_label}")
        cols_num = [c for c in COLUMNAS if c in df.columns]

        filas = []
        for col_sheet in cols_num:
            etiqueta, unidad, _ = COLUMNAS[col_sheet]
            s = df[col_sheet].dropna()
            if s.empty: continue
            x_num = (df.loc[s.index, "Fecha_Hora"] - df["Fecha_Hora"].min()).dt.total_seconds() / 3600
            if len(x_num) >= 2:
                pendiente = float(np.polyfit(x_num, s, 1)[0])
                if abs(pendiente) < 0.001:  tendencia_txt = "▬ Estable"
                elif pendiente > 0:          tendencia_txt = f"▲ +{pendiente:.3f}/h"
                else:                        tendencia_txt = f"▼ {pendiente:.3f}/h"
            else:
                tendencia_txt = "—"
            filas.append({
                "Variable":  f"{etiqueta} ({unidad})" if unidad else etiqueta,
                "Mínimo":    f"{s.min():.3f}",
                "Máximo":    f"{s.max():.3f}",
                "Promedio":  f"{s.mean():.3f}",
                "Desvío":    f"{s.std():.3f}",
                "Tendencia": tendencia_txt,
            })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 📈 Tendencias por variable")
        cols_tend = st.columns(2)
        for idx, col_sheet in enumerate(cols_num):
            etiqueta, unidad, color = COLUMNAS[col_sheet]
            s = df[col_sheet].dropna()
            if len(s) < 2: continue
            x_dt  = df.loc[s.index, "Fecha_Hora"]
            x_num = (x_dt - x_dt.min()).dt.total_seconds() / 3600
            coef  = np.polyfit(x_num, s, 1)
            tend  = np.polyval(coef, x_num)
            y_min_t, y_max_t = calcular_rango_y(s)
            fill_color = color.replace(")", ", 0.08)").replace("rgb", "rgba")
            tick_fmt   = "%H:%M" if (x_dt.max() - x_dt.min()).days < 1 else "%d/%m %H:%M"
            suffix     = f" {unidad}" if unidad else ""
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_dt, y=[y_min_t]*len(x_dt), mode="lines",
                                     line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=x_dt, y=s.values, mode="lines", name="Datos",
                                     line=dict(color=color, width=1.5),
                                     fill="tonexty", fillcolor=fill_color,
                                     hovertemplate=f"%{{x|%d/%m %H:%M}}: %{{y:.3f}}{suffix}<extra></extra>"))
            fig.add_trace(go.Scatter(x=x_dt, y=tend, mode="lines", name="Tendencia",
                                     line=dict(color="white", width=2, dash="dash"), hoverinfo="skip"))
            fig.update_layout(
                title=dict(text=etiqueta, font=dict(family="IBM Plex Mono", size=13, color="#8b949e"), x=0.01),
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                margin=dict(l=10, r=10, t=40, b=10), height=240,
                xaxis=dict(showgrid=True, gridcolor="#21262d",
                           tickfont=dict(family="IBM Plex Mono", size=9, color="#8b949e"),
                           tickformat=tick_fmt, color="#8b949e"),
                yaxis=dict(showgrid=True, gridcolor="#21262d",
                           tickfont=dict(family="IBM Plex Mono", size=9, color="#8b949e"),
                           ticksuffix=suffix, color="#8b949e", range=[y_min_t, y_max_t]),
                hovermode="x unified", showlegend=True,
                legend=dict(font=dict(color="#8b949e", size=10), bgcolor="rgba(0,0,0,0)", x=0.01, y=0.99),
                font=dict(color="#8b949e"),
            )
            with cols_tend[idx % 2]:
                st.plotly_chart(fig, use_container_width=True, key=f"tend_{idx}_{time.time()}")

    # ── Control del loop ──────────────────────────────────────────────────────
    if not auto_update or modo == "historico":
        if modo == "actual":
            if st.button("🔄 Actualizar ahora"):
                st.cache_data.clear(); st.rerun()
        break

    time.sleep(intervalo)
    st.cache_data.clear()
    st.rerun()
