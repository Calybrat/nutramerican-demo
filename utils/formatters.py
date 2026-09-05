"""
Identidad visual de Nutramerican Pharma.

Los colores no son inventados: salen de las variables CSS del propio sitio
(`/css/home-refresh.css`) y de los rellenos del logo oficial
(`/img/logonutramerican.svg`):

  --nutra-blue #0071e3 · --nutra-blue-dark #034a99 · --nutra-gold #e5bb47
  --nutra-ink #0b0c0f · --nutra-muted #626875 · --nutra-line #e4e7ec
  logo: estrellas #004BE0 · franjas rojas · tipografía negra

La tipografía de marca es Montserrat, la misma que el sitio precarga en los
pesos 400/500/700/800/900.
"""
import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# ── Paleta de marca ──────────────────────────────────────────────────────────
ROJO       = "#D8232A"   # rojo de la franja del logo
ROJO_DEEP  = "#A8171D"
ROJO_LT    = "#FBE9EA"
AZUL       = "#004BE0"   # azul de las estrellas del logo
AZUL_DEEP  = "#034A99"   # --nutra-blue-dark
AZUL_LUM   = "#0071E3"   # --nutra-blue
AZUL_LT    = "#E8F1FD"
ORO        = "#E5BB47"   # --nutra-gold
ORO_LUM    = "#F2C94C"   # --nutra-gold-strong
ORO_LT     = "#FBF3DC"
TINTA      = "#0B0C0F"   # --nutra-ink
CARBON     = "#15171C"   # --nutra-charcoal

# Roles de superficie (tema claro, como el sitio)
BG      = "#F7F9FC"
SURF    = "#FFFFFF"
SURF2   = "#F5F7FA"      # --nutra-surface
BORDER  = "#E4E7EC"      # --nutra-line
TEXT    = TINTA
MUTED   = "#626875"      # --nutra-muted
DIM     = "#A8AEBB"

# Semánticos
GOOD  = "#1F9D55"
WARN  = "#E0A03C"
BAD   = "#D8232A"
INFO  = "#0071E3"
GREEN, AMBER, RED, SKY = GOOD, WARN, BAD, INFO

PALETTE = [AZUL_DEEP, ROJO, ORO, AZUL_LUM, MUTED, GOOD, "#7C4DBE", WARN]
GRAD = [AZUL_DEEP, ROJO]

_ASSETS = Path(__file__).parent.parent / "assets"
_DATA = Path(__file__).parent.parent / "data"


def leer_csv(nombre: str, **kw) -> pd.DataFrame:
    """Lee un archivo de data/, esté comprimido (.csv.gz) o no."""
    kw.setdefault("low_memory", False)
    for candidato in (_DATA / nombre, _DATA / f"{nombre}.gz"):
        if candidato.exists():
            return pd.read_csv(candidato, **kw)
    raise FileNotFoundError(f"No se encontró {nombre} en {_DATA}")


_MIMES = {".svg": "image/svg+xml", ".webp": "image/webp",
          ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


def asset_b64(nombre: str) -> str:
    """Devuelve un asset de marca como data URI listo para <img src=...>."""
    ruta = _ASSETS / nombre
    if not ruta.exists():
        return ""
    mime = _MIMES.get(ruta.suffix.lower(), "image/png")
    return f"data:{mime};base64,{base64.b64encode(ruta.read_bytes()).decode()}"


def foto_producto(archivo: str) -> str:
    """Render oficial del producto (assets/productos/*.webp) como data URI."""
    if not archivo:
        return ""
    return asset_b64(f"productos/{archivo}")


# ── Formato ──────────────────────────────────────────────────────────────────
def cop(v, decimals=0) -> str:
    """Formatea pesos: $1,23B · $456M · $12,3K"""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(v) >= 1_000_000_000:
        return f"${v/1_000_000_000:,.{decimals}f}B"
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:,.{decimals}f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:,.{decimals}f}K"
    return f"${v:,.{decimals}f}"


def cop_full(v) -> str:
    """Pesos con separador de miles al estilo colombiano: $249.000"""
    try:
        return "$" + f"{float(v):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "—"


def usd(v, decimals=0) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(v) >= 1_000_000:
        return f"US${v/1_000_000:,.{decimals+1}f}M"
    if abs(v) >= 1_000:
        return f"US${v/1_000:,.{decimals}f}K"
    return f"US${v:,.{decimals}f}"


def num(v, decimals=0) -> str:
    try:
        return f"{float(v):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def pct(v, decimals=1) -> str:
    try:
        return f"{float(v):.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def ton(v, decimals=1) -> str:
    try:
        return f"{float(v):,.{decimals}f} t"
    except (TypeError, ValueError):
        return "—"


# ── Gráficas ─────────────────────────────────────────────────────────────────
def light(fig: go.Figure, height: int = 340, title: str = "") -> go.Figure:
    """Aplica el tema claro de Nutramerican a una figura de Plotly.

    La leyenda nunca va arriba: a esa altura pelea el mismo espacio que el
    título y termina tapándolo apenas hay más de un par de series. Va debajo
    del gráfico (barras/líneas) o a la derecha (donuts), con el margen
    reservado para que no se monte sobre nada.
    """
    is_pie = any(getattr(tr, "type", None) == "pie" for tr in fig.data)
    n_entries = 0
    for tr in fig.data:
        if getattr(tr, "type", None) == "pie":
            labels = tr.labels
            n_entries += len(labels) if labels is not None else 0
        elif getattr(tr, "name", None):
            n_entries += 1
    show_legend = is_pie or n_entries >= 1

    if is_pie:
        legend = dict(orientation="v", x=1.02, y=0.5, xanchor="left", yanchor="middle",
                      font=dict(color=MUTED, size=11))
        margin = dict(l=6, r=138, t=40 if title else 16, b=16)
    elif show_legend:
        rows = 1 if n_entries <= 4 else (2 if n_entries <= 8 else 3)
        legend = dict(orientation="h", y=-0.30 - 0.14 * (rows - 1), x=0.5,
                      xanchor="center", yanchor="top", font=dict(color=MUTED, size=11))
        margin = dict(l=6, r=34, t=40 if title else 16, b=64 + 30 * rows)
    else:
        legend = dict()
        margin = dict(l=6, r=34, t=40 if title else 16, b=16)

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TINTA, family="Montserrat, sans-serif"),
                   x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Montserrat, -apple-system, system-ui, sans-serif", color=MUTED, size=12),
        height=height,
        margin=margin,
        legend=legend,
        showlegend=show_legend,
        hovermode="x unified",
        colorway=PALETTE,
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="#EEF1F5", zeroline=False, tickfont=dict(color=MUTED))
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    return fig


dark = light  # alias retro-compatible


# ── Componentes ──────────────────────────────────────────────────────────────
def kpi(label: str, value: str, delta: str = "", delta_good: bool = True,
        icon: str = "", ayuda: str = "") -> str:
    """Tarjeta de KPI. `ayuda` explica en una línea cómo leer el indicador."""
    color = GOOD if delta_good else BAD
    delta_html = (f'<p style="font-size:12px;font-weight:800;color:{color};margin:5px 0 0">{delta}</p>'
                  if delta else "")
    icon_html = (f'<div style="font-size:20px;margin-bottom:6px;line-height:1">{icon}</div>'
                 if icon else "")
    ayuda_html = (f'<p style="font-size:10.5px;color:{MUTED};margin:6px 0 0;line-height:1.35">{ayuda}</p>'
                  if ayuda else "")
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:14px;padding:16px;
      min-height:152px;box-shadow:0 1px 3px rgba(11,12,15,.06)">
      {icon_html}
      <p style="font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:{MUTED};margin:0;font-weight:800">{label}</p>
      <p style="font-size:25px;font-weight:900;color:{TINTA};margin:5px 0 0;letter-spacing:-.6px;line-height:1.1">{value}</p>
      {delta_html}{ayuda_html}
    </div>"""


def panel(titulo: str, cuerpo_html: str, icono: str = "", tono: str = "neutro") -> str:
    """Panel de lectura/insight. `tono`: neutro · alerta · bien."""
    borde = {"alerta": ROJO, "bien": GOOD}.get(tono, AZUL_DEEP)
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-left:4px solid {borde};
      border-radius:14px;padding:18px 20px;margin:6px 0 2px;
      box-shadow:0 1px 3px rgba(11,12,15,.06)">
      <p style="font-size:13px;font-weight:900;color:{TINTA};margin:0 0 8px">{icono} {titulo}</p>
      <div style="font-size:12.5px;color:{MUTED};margin:0;line-height:1.75">{cuerpo_html}</div>
    </div>"""


def tarjeta_producto(nombre: str, imagen: str, lineas: list, badge: str = "") -> str:
    """Ficha visual de un SKU con su render oficial."""
    img = foto_producto(imagen)
    img_html = (f'<img src="{img}" style="height:96px;width:auto;object-fit:contain" alt="">'
                if img else '<div style="height:96px"></div>')
    badge_html = (f'<span style="position:absolute;top:10px;right:10px;background:{ROJO};color:#fff;'
                  f'font-size:9px;font-weight:900;letter-spacing:.06em;padding:3px 8px;'
                  f'border-radius:999px">{badge}</span>' if badge else "")
    cuerpo = "".join(
        f'<p style="font-size:11px;color:{MUTED};margin:2px 0">{l}</p>' for l in lineas)
    return f"""
    <div style="position:relative;background:{SURF};border:1px solid {BORDER};border-radius:14px;
      padding:14px;text-align:center;min-height:236px;box-shadow:0 1px 3px rgba(11,12,15,.06)">
      {badge_html}
      <div style="display:flex;align-items:center;justify-content:center;height:100px">{img_html}</div>
      <p style="font-size:12.5px;font-weight:800;color:{TINTA};margin:8px 0 4px;line-height:1.3">{nombre}</p>
      {cuerpo}
    </div>"""


def estado_color(estado: str) -> str:
    m = {"Crítico": BAD, "Bajo": WARN, "Normal": GOOD, "Alto": INFO, "Exceso": INFO,
         "Entregado": GOOD, "En tránsito": INFO, "En preparación": MUTED, "Devuelto": BAD,
         "Aprobado": GOOD, "Cuarentena": WARN, "Rechazado": BAD, "Liberado": GOOD,
         "Vigente": GOOD, "Por vencer": WARN, "En trámite": INFO, "Vencido": BAD,
         "Abierto": WARN, "En gestión": INFO, "Cerrado": GOOD, "Escalado": BAD,
         "Al día": GOOD, "Vencida 1-30": WARN, "Vencida 31-60": "#E08B3C",
         "Vencida 61-90": BAD, "Vencida +90": "#8F1218"}
    return m.get(estado, MUTED)


# ── Motivo gráfico: el cúmulo de estrellas del logo ──────────────────────────
def estrellas_svg(color: str = AZUL, alto: int = 26) -> str:
    """Las cuatro estrellas del logo, para usar como acento decorativo."""
    return f"""
    <svg viewBox="0 0 120 74" height="{alto}" style="display:block">
      <path fill="{color}" d="M34 0l8.5 17.6L61 20.2 47.5 33.3 50.7 52 34 43.2 17.3 52l3.2-18.7L7 20.2l18.5-2.6z"/>
      <path fill="{color}" d="M84 6l5.3 11 12.2 1.8-8.8 8.6 2.1 12.1L84 33.8 73.2 39.5l2.1-12.1-8.8-8.6L78.7 17z"/>
      <path fill="{color}" d="M64 46l3.7 7.6 8.4 1.2-6.1 5.9 1.5 8.4L64 65.2 56.5 69.1l1.5-8.4-6.1-5.9 8.4-1.2z"/>
      <path fill="{color}" d="M107 45l2.9 6 6.6 1-4.8 4.6 1.1 6.6-5.8-3-5.9 3 1.2-6.6-4.8-4.6 6.6-1z"/>
    </svg>"""


CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');
  html, body, [class*="css"] {{ font-family:'Montserrat',-apple-system,system-ui,sans-serif; }}
  .stApp {{ background:{BG}; color:{TEXT}; }}

  section[data-testid="stSidebar"] {{ background:{TINTA}; border-right:none; }}
  section[data-testid="stSidebar"] * {{ color:#E9ECF2; }}
  section[data-testid="stSidebar"] .stButton button {{
      background:rgba(255,255,255,.05); color:#E9ECF2 !important;
      border:1px solid rgba(255,255,255,.10); border-radius:10px;
      text-align:left; font-weight:700; font-size:12.5px; padding:8px 12px;
      transition:all .14s ease; }}
  section[data-testid="stSidebar"] .stButton button:hover {{
      background:{ROJO}22; border-color:{ROJO}; color:#fff !important; }}

  .block-container {{ padding-top:1.6rem !important; max-width:1500px; }}
  h1,h2,h3,h4 {{ color:{TINTA} !important; font-family:'Montserrat',sans-serif !important;
      font-weight:900 !important; letter-spacing:-.3px; }}
  div[data-testid="stMetricValue"] {{ color:{TINTA}; }}
  .stDataFrame {{ border-radius:12px; overflow:hidden; border:1px solid {BORDER}; }}
  thead tr th {{ background:{SURF2} !important; color:{TINTA} !important; font-size:11.5px !important;
      text-transform:uppercase; letter-spacing:.05em; font-weight:800 !important; }}
  tbody tr:hover td {{ background:{AZUL_LT} !important; }}
  div[data-baseweb="select"] > div {{ background:{SURF} !important; border-color:{BORDER} !important;
      border-radius:10px !important; }}
  div[data-baseweb="select"] span {{ color:{TINTA} !important; }}
  .stMultiSelect span[data-baseweb="tag"] {{ background:{AZUL_DEEP} !important; color:#fff !important; }}
  .stMultiSelect span[data-baseweb="tag"] span {{ color:#fff !important; -webkit-text-fill-color:#fff !important; }}
  button[kind="primary"] {{ background:{ROJO} !important; border:none !important; border-radius:10px !important;
      font-weight:800 !important; }}
  .stTabs [data-baseweb="tab"] {{ background:{SURF2}; border-radius:10px 10px 0 0; font-weight:800;
      color:{MUTED}; font-size:13px; }}
  .stTabs [aria-selected="true"] {{ background:{SURF} !important; color:{TINTA} !important;
      border-bottom:3px solid {ROJO}; }}
  div[data-testid="stExpander"] {{ border:1px solid {BORDER} !important; background:{SURF} !important;
      border-radius:12px !important; }}
  div[data-testid="stExpander"] summary {{ font-weight:800; color:{TINTA} !important; }}
  label, .stSelectbox label, .stSlider label {{ color:{MUTED} !important; font-weight:700 !important;
      font-size:12px !important; }}
  hr {{ border-color:{BORDER}; }}
</style>
"""

HEADER_CSS = f"""
<style>
  .nt-header {{ display:flex;align-items:center;gap:16px;padding:2px 0 }}
  .nt-logo-img {{ height:44px;width:auto }}
  .nt-title {{ font-size:23px;font-weight:900;color:{TINTA};letter-spacing:-.5px;line-height:1.15 }}
  .nt-sub {{ font-size:12.5px;color:{MUTED};margin-top:3px;font-weight:600 }}
  .nt-rule {{ height:3px;border-radius:99px;
      background:linear-gradient(90deg,{ROJO} 0%,{ROJO} 22%,{AZUL_DEEP} 22%,{AZUL_DEEP} 46%,{ORO} 46%,{ORO} 62%,transparent);
      margin:14px 0 20px }}
  .nt-badge {{ display:inline-block;background:{AZUL_LT};color:{AZUL_DEEP};
      border:1px solid #C9DEF8;border-radius:999px;
      padding:3px 12px;font-size:11px;font-weight:800;letter-spacing:.04em }}
  .nt-badge-rojo {{ display:inline-block;background:{ROJO_LT};color:{ROJO_DEEP};
      border:1px solid #F3C4C6;border-radius:999px;
      padding:3px 12px;font-size:11px;font-weight:800;letter-spacing:.04em }}
  .nt-badge-oro {{ display:inline-block;background:{ORO_LT};color:#8A6A12;
      border:1px solid #EEDCA6;border-radius:999px;
      padding:3px 12px;font-size:11px;font-weight:800;letter-spacing:.04em }}
</style>
"""


def encabezado(titulo: str, subtitulo: str, adorno: str = "estrellas") -> str:
    """Encabezado de módulo con el logo oficial de Nutramerican."""
    logo = asset_b64("logo_nutramerican.jpg")
    logo_html = (f'<img src="{logo}" class="nt-logo-img" alt="Nutramerican Pharma">'
                 if logo else f'<div class="nt-title">NUTRAMERICAN</div>')
    if adorno == "estrellas":
        extra = f'<div style="margin-left:auto;opacity:.85">{estrellas_svg(AZUL, 30)}</div>'
    elif adorno == "fssc":
        b = asset_b64("fssc22000.webp")
        extra = (f'<img src="{b}" style="height:40px;width:auto;margin-left:auto;opacity:.9" alt="FSSC 22000">'
                 if b else "")
    else:
        extra = ""
    return f"""
    <div class="nt-header">
      {logo_html}
      <div style="border-left:2px solid {BORDER};padding-left:16px">
        <div class="nt-title">{titulo}</div>
        <div class="nt-sub">{subtitulo}</div>
      </div>
      {extra}
    </div><div class="nt-rule"></div>"""
