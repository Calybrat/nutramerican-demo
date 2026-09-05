import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from utils.formatters import (CSS, HEADER_CSS, asset_b64, estrellas_svg,
                              ROJO, ORO, AZUL, TINTA)
from utils.visitas import registrar_visita, panel_solicitado, render_panel_visitas

st.set_page_config(
    page_title="Nutramerican Pharma · Panel de Negocio | Calybrat",
    page_icon="⭐",
    layout="wide",
)

# El demo es de acceso libre: solo se deja constancia de la visita.
registrar_visita()

st.markdown(CSS + HEADER_CSS, unsafe_allow_html=True)

# Secciones agrupadas para que el panel sea fácil de recorrer
GRUPOS = [
    ("Vista general", [
        ("🏠  Dashboard Ejecutivo",        "p01_dashboard"),
    ]),
    ("Comercial", [
        ("🛒  Ventas Omnicanal",           "p02_ventas"),
        ("🏪  Tiendas Nutramerican",       "p03_tiendas"),
        ("💪  Portafolio & Precios",       "p04_portafolio"),
        ("🔁  Clientes & Recompra",        "p05_clientes"),
        ("⭐  Marketing & Megaplex Stars", "p06_marketing"),
    ]),
    ("Operación", [
        ("🏭  Producción & Planta",        "p07_produccion"),
        ("🧪  Calidad & Regulatorio",      "p08_calidad"),
        ("🌎  Abastecimiento & Divisa",    "p09_abastecimiento"),
        ("🚚  Logística & Inventario",     "p10_logistica"),
    ]),
    ("Dirección", [
        ("💰  Finanzas & Cartera",         "p11_finanzas"),
        ("✈️  Expansión Internacional",    "p12_expansion"),
        ("🎧  Servicio al Cliente & PQR",  "p13_servicio"),
        ("📄  Reportes Automáticos",       "p14_reportes"),
        ("🤖  Agente IA Nutramerican",     "p15_agente"),
    ]),
]
PAGES = {label: mod for _, items in GRUPOS for label, mod in items}

with st.sidebar:
    logo = asset_b64("logo_dark.svg")
    logo_html = (f'<img src="{logo}" style="width:190px;height:auto" alt="Nutramerican Pharma">'
                 if logo else
                 '<div style="font-size:20px;font-weight:900;color:#fff">NUTRAMERICAN</div>')
    st.markdown(f"""
    <div style="padding:12px 4px 6px">
      {logo_html}
      <div style="font-size:10px;color:#9AA2B1;margin-top:8px;font-weight:800;
        letter-spacing:.14em;text-transform:uppercase">Panel de negocio</div>
      <div style="height:3px;border-radius:99px;margin:12px 0 4px;
        background:linear-gradient(90deg,{ROJO} 0%,{ROJO} 34%,{AZUL} 34%,{AZUL} 64%,{ORO} 64%,{ORO} 82%,transparent)"></div>
    </div>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = list(PAGES.keys())[0]

    for grupo, items in GRUPOS:
        st.markdown(
            f'<div style="font-size:9.5px;font-weight:900;letter-spacing:.16em;'
            f'text-transform:uppercase;color:#7D8593;margin:14px 0 5px 4px">{grupo}</div>',
            unsafe_allow_html=True)
        for label, _mod in items:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:16px 16px 10px;text-align:center;border-top:1px solid rgba(255,255,255,.10)">
      <div style="display:flex;justify-content:center;margin-bottom:8px;opacity:.9">
        {estrellas_svg("#5B84E8", 22)}
      </div>
      <div style="font-size:10.5px;color:#7D8593;margin-bottom:2px">Construido por</div>
      <div style="font-size:15px;font-weight:900;color:#fff;letter-spacing:.5px">Calybrat</div>
      <div style="font-size:9.5px;color:#6B7280;margin-top:4px;line-height:1.5">
        © 2026 · Demo con datos simulados
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Panel interno de accesos (solo con ?accesos=… en la URL) ──────────────────
if panel_solicitado():
    render_panel_visitas()
    st.stop()

# ── Módulo activo ─────────────────────────────────────────────────────────────
module_name = PAGES[st.session_state.page]
try:
    mod = __import__(f"modules.{module_name}", fromlist=[module_name])
    mod.render()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    import traceback
    st.code(traceback.format_exc())
