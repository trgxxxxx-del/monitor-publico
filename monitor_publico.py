import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import io
import requests
from datetime import datetime, timedelta

# ── Barrios ────────────────────────────────────────────────────────────────────
BARRIOS = {
    "Villa Alem": {
        "sheet_id": "1mKNz5DF6Y9Gnolf1sLq8t8079_Oo6-VPxaNZVSJBaPw",
        "gid": "0",
        "coords": (-26.846204, -65.214542),
        "emoji": "🏡",
    },
    "Barrio Sur": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid": "35635042",
        "coords": (-26.856000, -65.210000),
        "emoji": "🏘️",
    },
    "Barrio Norte": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid": "801290369",
        "coords": (-26.820000, -65.210000),
        "emoji": "🏙️",
    },
    "Yerba Buena": {
        "sheet_id": "1Qgu_M7BXpV1pT2AlVP_ZrpnqnMxksUWNOzu25J6SegQ",
        "gid": "1998468375",
        "coords": (-26.816000, -65.260000),
        "emoji": "🌿",
    },
}

# 18 columnas completas (coincide con el Apps Script)
NOMBRES_COLUMNAS = [
    "Fecha_Hora",
    "Temperatura (°C)",
    "Presión (hPa)",
    "Humedad (%)",
    "Densidad (kg/m³)",
    "Humedad Abs (g/m³)",
    "Sensación Térmica (°C)",
    "Bulbo Húmedo (°C)",
    "Punto Rocío (°C)",
    "Presión NM (hPa)",
    "Altitud (m)",
    "Radiación (W/m²)",
    "UV (índice)",
    "Nubosidad (%)",
    "Índice Acústico (I)",
    "dBA estimado",
    "Luz Visible (lux)",
    "IR (counts)",
]

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Clima en Tucumán",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Fira+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
  .stApp, .main, .block-container {
    background-color: #0f1923 !important;
    padding-top: 3rem;
  }
  section[data-testid="stSidebar"] { display: none !important; }
  [data-testid="stToolbar"]        { display: none !important; }
  [data-testid="stHeader"] button  { display: none !important; }
  #MainMenu                        { display: none !important; }
  footer                           { display: none !important; visibility: hidden !important; }
  [class*="viewerBadge"]           { display: none !important; }
  div[class*="streamlit-badge"],
  a[href*="streamlit.io"]          { display: none !important; }
  a[target="_blank"]::after        { display: none !important; }
  [data-testid="stDecoration"]     { display: none; }

  /* ── Header ── */
  .header-title { font-size:1.8rem; font-weight:800; color:#e8f4fd; margin:0; }
  .header-sub   { font-size:0.9rem; color:#6b8fa8; margin-top:0.2rem; }

  .live-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:#0d2c1a; border:1px solid #1a5c35; border-radius:20px;
    padding:6px 14px; font-size:0.82rem; font-weight:700;
    color:#3dd68c; letter-spacing:0.05em; text-transform:uppercase;
  }
  .live-dot {
    width:8px; height:8px; border-radius:50%; background:#3dd68c;
    animation:blink 1.8s ease-in-out infinite; flex-shrink:0;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

  /* ── Barrio selector ── */
  .barrio-label {
    font-size:0.78rem; font-weight:700; color:#6b8fa8;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.4rem;
  }

  /* ── Metric cards ── */
  .card-grid { display:grid; gap:1rem; margin-bottom:1.5rem; }
  .card {
    background:linear-gradient(145deg,#162032 0%,#1a2840 100%);
    border:1px solid #1e3048; border-radius:16px;
    padding:1.3rem 1.5rem; transition:transform 0.2s,border-color 0.2s;
    position:relative; overflow:hidden;
  }
  .card::before {
    content:''; position:absolute; top:0; left:0; right:0;
    height:3px; border-radius:16px 16px 0 0;
  }
  .card-temp::before  { background:linear-gradient(90deg,#ff6b6b,#ffa040); }
  .card-hum::before   { background:linear-gradient(90deg,#40d9a0,#40b8d9); }
  .card-pres::before  { background:linear-gradient(90deg,#638bff,#9a6bff); }
  .card-sens::before  { background:linear-gradient(90deg,#ffb840,#ff7a40); }
  .card-rocio::before { background:linear-gradient(90deg,#40d9e8,#4080ff); }
  .card-dens::before  { background:linear-gradient(90deg,#c040ff,#8040ff); }
  /* ── nuevas tarjetas ── */
  .card-rad::before   { background:linear-gradient(90deg,#ffe04b,#ff8c00); }
  .card-uv::before    { background:linear-gradient(90deg,#b84fff,#ff4fc8); }
  .card-dba::before   { background:linear-gradient(90deg,#00e5ff,#00b8a9); }

  .card-icon  { font-size:1.6rem; margin-bottom:0.4rem; display:block; }
  .card-label { font-size:0.75rem; font-weight:700; color:#6b8fa8; text-transform:uppercase; letter-spacing:0.1em; }
  .card-value { font-family:'Fira Mono',monospace; font-size:2.2rem; font-weight:500; color:#e8f4fd; line-height:1.1; margin-top:0.3rem; }
  .card-unit  { font-size:0.9rem; color:#6b8fa8; margin-left:3px; }
  .card-trend { font-size:0.75rem; color:#6b8fa8; margin-top:0.5rem; font-weight:600; }
  .trend-up   { color:#ff7a7a; }
  .trend-down { color:#7ac8ff; }
  .trend-ok   { color:#3dd68c; }

  /* ── UV badge ── */
  .uv-badge {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:800; letter-spacing:0.08em;
    margin-top:6px; text-transform:uppercase;
  }
  .uv-low      { background:#1a3a1a; color:#3dd68c; border:1px solid #1a5c35; }
  .uv-moderate { background:#3a3000; color:#ffd740; border:1px solid #7a6000; }
  .uv-high     { background:#3a1500; color:#ff9040; border:1px solid #7a3000; }
  .uv-vhigh    { background:#3a0000; color:#ff5050; border:1px solid #7a0000; }
  .uv-extreme  { background:#2a0030; color:#e040fb; border:1px solid #6a0080; }

  /* ── dBA badge ── */
  .dba-badge {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:800; letter-spacing:0.08em;
    margin-top:6px; text-transform:uppercase;
  }
  .dba-low    { background:#0d2535; color:#40c8ff; border:1px solid #1a5070; }
  .dba-mod    { background:#1a2a10; color:#80e060; border:1px solid #3a6020; }
  .dba-high   { background:#3a2800; color:#ffb840; border:1px solid #7a5000; }
  .dba-loud   { background:#3a0800; color:#ff6040; border:1px solid #7a2010; }

  /* ── Section titles ── */
  .section-title {
    font-size:1rem; font-weight:800; color:#6b8fa8;
    text-transform:uppercase; letter-spacing:0.12em;
    margin:1.5rem 0 0.8rem 0; padding-left:0.5rem;
    border-left:3px solid #2a4a6a;
  }

  /* ── Chart wrapper ── */
  .chart-wrap {
    background:#162032; border:1px solid #1e3048;
    border-radius:16px; padding:0.5rem; margin-bottom:0.5rem;
  }

  /* ── Footer ── */
  .footer {
    text-align:center; color:#3a5570; font-size:0.75rem;
    padding:1.5rem 0 0.5rem 0; border-top:1px solid #1e3048;
    margin-top:1.5rem; font-family:'Fira Mono',monospace;
  }

  /* ── Info chips ── */
  .info-row  { display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem; }
  .info-chip {
    background:#162032; border:1px solid #1e3048; border-radius:10px;
    padding:0.5rem 1rem; font-size:0.82rem; color:#8bb5d0; font-weight:600;
  }
  .info-chip span { color:#e8f4fd; }

  /* Streamlit overrides */
  .stSelectbox > div > div {
    background-color:#162032 !important; border:1px solid #2a4a6a !important;
    border-radius:12px !important; color:#e8f4fd !important;
  }
  .stSelectbox label { color:#6b8fa8 !important; font-weight:700 !important; font-size:0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "barrio" not in st.session_state:
    st.session_state["barrio"] = list(BARRIOS.keys())[0]

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def cargar_datos(sheet_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = "utf-8"
        texto = r.text.strip()
        if not texto or texto.startswith("<!"):
            return pd.DataFrame(), "No se pudo conectar con los datos"
        sep = ";" if texto.split("\n")[0].count(";") > texto.split("\n")[0].count(",") else ","
        df = pd.read_csv(io.StringIO(texto), header=0, sep=sep, decimal=",", quotechar='"')
        if df.empty or len(df.columns) < 2:
            return pd.DataFrame(), "Sin datos disponibles"
        # Asignar nombres según cantidad de columnas
        if len(df.columns) == len(NOMBRES_COLUMNAS):
            df.columns = NOMBRES_COLUMNAS
        elif len(df.columns) == 11:
            # hoja vieja con solo 11 cols
            df.columns = NOMBRES_COLUMNAS[:11]
        else:
            df.columns = df.columns.str.strip()
            df = df.rename(columns={df.columns[0]: "Fecha_Hora"})
        df["Fecha_Hora"] = pd.to_datetime(
            df["Fecha_Hora"].astype(str).str.strip(), dayfirst=True, errors="coerce"
        )
        df = df.dropna(subset=["Fecha_Hora"]).sort_values("Fecha_Hora").reset_index(drop=True)
        # Convertir columnas numéricas
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        # Solo últimas 24 horas
        corte = datetime.now() - timedelta(hours=24)
        df = df[df["Fecha_Hora"] >= corte].reset_index(drop=True)
        return df, ""
    except Exception as e:
        return pd.DataFrame(), str(e)


def tendencia(serie, ultimos=10):
    s = serie.dropna()
    if len(s) < ultimos:
        return "", ""
    delta = s.iloc[-1] - s.iloc[-ultimos]
    if abs(delta) < 0.2:
        return "trend-ok", "Estable"
    elif delta > 0:
        return "trend-up", f"↑ +{delta:.1f}"
    else:
        return "trend-down", f"↓ {delta:.1f}"


def uv_label(uv):
    if uv is None:
        return "", ""
    if uv < 3:
        return "uv-low", "Bajo"
    elif uv < 6:
        return "uv-moderate", "Moderado"
    elif uv < 8:
        return "uv-high", "Alto"
    elif uv < 11:
        return "uv-vhigh", "Muy alto"
    else:
        return "uv-extreme", "Extremo"


def dba_label(dba):
    if dba is None:
        return "", ""
    if dba < 50:
        return "dba-low", "Silencioso"
    elif dba < 65:
        return "dba-mod", "Normal"
    elif dba < 80:
        return "dba-high", "Ruidoso"
    else:
        return "dba-loud", "Muy ruidoso"


def mini_chart(df, col, color, unidad, titulo):
    if col not in df.columns:
        return None
    s = df[col].dropna()
    if s.empty:
        return None
    df_p = df.tail(200)
    vmin = s.min(); vmax = s.max()
    rango = vmax - vmin
    margen = max(rango * 0.12, 0.01)
    fill = color.replace("rgb(", "rgba(").replace(")", ", 0.12)")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_p["Fecha_Hora"], y=[vmin - margen] * len(df_p),
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df_p["Fecha_Hora"], y=df_p[col],
        mode="lines", line=dict(color=color, width=2.5),
        fill="tonexty", fillcolor=fill,
        hovertemplate=f"<b>%{{x|%H:%M}}</b>  {titulo}: %{{y:.1f}} {unidad}<extra></extra>",
    ))
    last = df_p[col].dropna()
    if not last.empty:
        fig.add_trace(go.Scatter(
            x=[df_p.loc[last.index[-1], "Fecha_Hora"]], y=[last.iloc[-1]],
            mode="markers",
            marker=dict(color=color, size=9, line=dict(color="white", width=2)),
            showlegend=False, hoverinfo="skip",
        ))
    fig.update_layout(
        title=dict(text=titulo, font=dict(family="Nunito", size=13, color="#8bb5d0"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=36, b=8), height=220,
        xaxis=dict(
            showgrid=True, gridcolor="#1e3048",
            tickfont=dict(family="Fira Mono", size=10, color="#6b8fa8"),
            tickformat="%H:%M", color="#6b8fa8", showline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#1e3048",
            tickfont=dict(family="Fira Mono", size=10, color="#6b8fa8"),
            ticksuffix=f" {unidad}", color="#6b8fa8",
            range=[vmin - margen, vmax + margen], showline=False,
        ),
        hovermode="x unified", showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

col_title, col_sel = st.columns([3, 1])
with col_title:
    st.markdown("""
    <div style='margin-bottom:0.3rem;'>
      <span style='font-size:1.8rem; font-weight:800; color:#e8f4fd;'>🌤️ Clima en Tucumán</span><br>
      <span style='font-size:0.88rem; color:#6b8fa8;'>Datos en tiempo real · se actualiza cada 60 segundos</span>
    </div>
    """, unsafe_allow_html=True)

with col_sel:
    st.markdown("<div class='barrio-label'>📍 Tu barrio</div>", unsafe_allow_html=True)
    barrio_opts = list(BARRIOS.keys())
    barrio_idx  = barrio_opts.index(st.session_state["barrio"])
    nuevo_barrio = st.selectbox(
        "Barrio", options=barrio_opts, index=barrio_idx,
        label_visibility="collapsed",
    )
    if nuevo_barrio != st.session_state["barrio"]:
        st.session_state["barrio"] = nuevo_barrio
        st.cache_data.clear()
        st.rerun()

st.markdown("<hr style='border:none; border-top:1px solid #1e3048; margin:0.5rem 0 1rem 0;'>",
            unsafe_allow_html=True)

# ── Carga ──────────────────────────────────────────────────────────────────────
barrio_cfg = BARRIOS[st.session_state["barrio"]]
df, err = cargar_datos(barrio_cfg["sheet_id"], barrio_cfg["gid"])

if df.empty:
    st.error(f"⚠️ No pudimos obtener los datos ahora mismo. {err}")
    st.stop()

ultima    = df.iloc[-1]
hora_str  = ultima["Fecha_Hora"].strftime("%H:%M")
fecha_str = ultima["Fecha_Hora"].strftime("%d/%m/%Y")

# ── Info chips ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='info-row'>
  <div class='info-chip'>📍 {st.session_state["barrio"]}</div>
  <div class='info-chip'>🕒 Última lectura: <span>{hora_str} · {fecha_str}</span></div>
  <div class='info-chip'>📋 Lecturas hoy: <span>{len(df)}</span></div>
  <div class='live-badge'><span class='live-dot'></span> En vivo</div>
</div>
""", unsafe_allow_html=True)


def get_val(col):
    if col in df.columns and pd.notna(ultima[col]):
        return ultima[col]
    return None

def fmt(v, dec=1):
    return f"{v:.{dec}f}" if v is not None else "—"


# Valores
temp  = get_val("Temperatura (°C)")
hum   = get_val("Humedad (%)")
pres  = get_val("Presión (hPa)")
sens  = get_val("Sensación Térmica (°C)")
rocio = get_val("Punto Rocío (°C)")
dens  = get_val("Densidad (kg/m³)")
rad   = get_val("Radiación (W/m²)")
uv    = get_val("UV (índice)")
dba   = get_val("dBA estimado")

# Tendencias
t_cls, t_txt = tendencia(df["Temperatura (°C)"]) if "Temperatura (°C)" in df.columns else ("","")
h_cls, h_txt = tendencia(df["Humedad (%)"])       if "Humedad (%)"       in df.columns else ("","")
p_cls, p_txt = tendencia(df["Presión (hPa)"])     if "Presión (hPa)"     in df.columns else ("","")
r_cls, r_txt = tendencia(df["Radiación (W/m²)"]) if "Radiación (W/m²)"  in df.columns else ("","")

uv_cls, uv_txt   = uv_label(uv)
dba_cls, dba_txt = dba_label(dba)

# ── Fila 1: temp / humedad / presión ──────────────────────────────────────────
st.markdown("<div class='section-title'>Condiciones actuales</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class='card card-temp'>
      <span class='card-icon'>🌡️</span>
      <div class='card-label'>Temperatura</div>
      <div class='card-value'>{fmt(temp)}<span class='card-unit'>°C</span></div>
      <div class='card-trend {t_cls}'>{t_txt or "Sin datos de tendencia"}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='card card-hum'>
      <span class='card-icon'>💧</span>
      <div class='card-label'>Humedad del aire</div>
      <div class='card-value'>{fmt(hum)}<span class='card-unit'>%</span></div>
      <div class='card-trend {h_cls}'>{h_txt or "Sin datos de tendencia"}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='card card-pres'>
      <span class='card-icon'>🔵</span>
      <div class='card-label'>Presión atmosférica</div>
      <div class='card-value'>{fmt(pres)}<span class='card-unit'>hPa</span></div>
      <div class='card-trend {p_cls}'>{p_txt or "Sin datos de tendencia"}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

# ── Fila 2: sensación / rocío / densidad ──────────────────────────────────────
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(f"""
    <div class='card card-sens'>
      <span class='card-icon'>🤸</span>
      <div class='card-label'>Sensación térmica</div>
      <div class='card-value'>{fmt(sens)}<span class='card-unit'>°C</span></div>
      <div class='card-trend'>Cómo se siente afuera</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class='card card-rocio'>
      <span class='card-icon'>🌧️</span>
      <div class='card-label'>Punto de rocío</div>
      <div class='card-value'>{fmt(rocio)}<span class='card-unit'>°C</span></div>
      <div class='card-trend'>Temperatura de condensación</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class='card card-dens'>
      <span class='card-icon'>🌫️</span>
      <div class='card-label'>Densidad del aire</div>
      <div class='card-value'>{fmt(dens, 3)}<span class='card-unit'>kg/m³</span></div>
      <div class='card-trend'>Masa del aire por m³</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

# ── Fila 3: radiación / UV / dBA ──────────────────────────────────────────────
st.markdown("<div class='section-title'>Radiación & ambiente sonoro</div>", unsafe_allow_html=True)

c7, c8, c9 = st.columns(3)
with c7:
    rad_trend = f"<div class='card-trend {r_cls}'>{r_txt or 'Sin datos de tendencia'}</div>"
    st.markdown(f"""
    <div class='card card-rad'>
      <span class='card-icon'>☀️</span>
      <div class='card-label'>Radiación solar</div>
      <div class='card-value'>{fmt(rad, 1)}<span class='card-unit'>W/m²</span></div>
      {rad_trend}
    </div>""", unsafe_allow_html=True)

with c8:
    uv_badge = f"<span class='uv-badge {uv_cls}'>{uv_txt}</span>" if uv_cls else ""
    st.markdown(f"""
    <div class='card card-uv'>
      <span class='card-icon'>🔆</span>
      <div class='card-label'>Índice UV</div>
      <div class='card-value'>{fmt(uv, 1)}<span class='card-unit'>UV</span></div>
      {uv_badge}
    </div>""", unsafe_allow_html=True)

with c9:
    dba_badge = f"<span class='dba-badge {dba_cls}'>{dba_txt}</span>" if dba_cls else ""
    st.markdown(f"""
    <div class='card card-dba'>
      <span class='card-icon'>🔊</span>
      <div class='card-label'>Intensidad sonora</div>
      <div class='card-value'>{fmt(dba, 1)}<span class='card-unit'>dBA</span></div>
      {dba_badge}
    </div>""", unsafe_allow_html=True)

# ── Gráficos de las últimas 24 hs ─────────────────────────────────────────────
st.markdown("<div class='section-title'>Últimas 24 horas</div>", unsafe_allow_html=True)

GRAFICOS = [
    ("Temperatura (°C)",       "rgb(255, 100, 100)",  "°C",   "Temperatura"),
    ("Humedad (%)",            "rgb(60, 220, 160)",   "%",    "Humedad"),
    ("Presión (hPa)",          "rgb(100, 160, 255)",  "hPa",  "Presión"),
    ("Sensación Térmica (°C)", "rgb(255, 170, 60)",   "°C",   "Sensación Térmica"),
    ("Radiación (W/m²)",       "rgb(255, 210, 50)",   "W/m²", "Radiación Solar"),
    ("UV (índice)",            "rgb(200, 80, 255)",   "UV",   "Índice UV"),
    ("dBA estimado",           "rgb(0, 220, 240)",    "dBA",  "Nivel Sonoro"),
]

col_g1, col_g2 = st.columns(2)
for i, (col, color, unidad, titulo) in enumerate(GRAFICOS):
    fig = mini_chart(df, col, color, unidad, titulo)
    if fig:
        target = col_g1 if i % 2 == 0 else col_g2
        with target:
            st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, key=f"g_{i}")
            st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='footer'>
  🌡️ Monitor Climático Tucumán &nbsp;·&nbsp; {st.session_state["barrio"]}
  &nbsp;·&nbsp; Actualizado: {datetime.now().strftime("%H:%M:%S")}
  &nbsp;·&nbsp; Fuente: Google Sheets / Estaciones propias
</div>
""", unsafe_allow_html=True)

# ── Auto-refresco ──────────────────────────────────────────────────────────────
time.sleep(60)
st.cache_data.clear()
st.rerun()
