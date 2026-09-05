import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    tm = datos.tiendas_mensual()
    td = datos.tiendas()
    v = datos.ventas()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Tiendas Nutramerican",
        "Las 8 tiendas propias: Bogotá Norte y Kennedy, Cali, Medellín, Barranquilla, "
        "Bucaramanga, Pereira y Cúcuta · el canal que más margen deja y el único que cobra "
        "de contado"), unsafe_allow_html=True)

    meses = sorted(tm["mes"].unique())
    c1, c2 = st.columns([1, 3])
    with c1:
        periodo = st.selectbox("Período", ["Último mes", "Últimos 3 meses", "2026 (año corrido)",
                                           "Todo el histórico"], key="td_per")
    if periodo == "Último mes":
        sel, prev = [meses[-1]], [meses[-2]]
    elif periodo == "Últimos 3 meses":
        sel, prev = meses[-3:], meses[-6:-3]
    elif periodo == "2026 (año corrido)":
        sel = [m for m in meses if m.startswith("2026")]
        prev = [m for m in meses if m.startswith("2025")][:len(sel)]
    else:
        sel, prev = meses, []

    f = tm[tm["mes"].isin(sel)]
    p = tm[tm["mes"].isin(prev)]

    venta = f["venta_cop"].sum()
    delta = (venta - p["venta_cop"].sum()) / p["venta_cop"].sum() * 100 if p["venta_cop"].sum() else 0
    visitas = int(f["visitas"].sum())
    tickets = int(f["tickets"].sum())
    conv = tickets / visitas * 100 if visitas else 0
    ticket_prom = venta / tickets if tickets else 0
    upt = f["unidades"].sum() / tickets if tickets else 0
    contrib = f["contribucion_cop"].sum()

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Venta de tiendas", cop(venta, 1),
                      f"{'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs período anterior",
                      delta >= 0, "🏪"), unsafe_allow_html=True)
    k[1].markdown(kpi("Visitantes", f"{visitas:,}", "Personas que entraron", True, "🚶",
                      "Sin tráfico no hay venta: es el primer eslabón."), unsafe_allow_html=True)
    k[2].markdown(kpi("Conversión", pct(conv), "Meta de retail especializado: 25%", conv >= 25,
                      "🎯", "De cada 100 que entran, cuántos compran."), unsafe_allow_html=True)
    k[3].markdown(kpi("Ticket promedio", cop_full(ticket_prom), f"{upt:.2f} unidades por compra",
                      ticket_prom >= 180_000, "🧾"), unsafe_allow_html=True)
    k[4].markdown(kpi("Contribución", cop(contrib, 1), "Margen menos arriendo y nómina",
                      contrib > 0, "💵",
                      "Lo que le queda a cada tienda después de sus costos fijos."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Comparativo de tiendas", "Diagnóstico: tráfico vs. conversión",
                          "Mapa y ficha de cada tienda"])

    with t1:
        g = f.groupby(["tienda_id", "tienda", "ciudad", "area_m2"]).agg(
            venta=("venta_cop", "sum"), margen=("margen_cop", "sum"),
            visitas=("visitas", "sum"), tickets=("tickets", "sum"),
            unidades=("unidades", "sum"), fijo=("costo_fijo_cop", "sum"),
            contrib=("contribucion_cop", "sum")).reset_index()
        g["conversion"] = g["tickets"] / g["visitas"] * 100
        g["ticket"] = g["venta"] / g["tickets"]
        g["venta_m2"] = g["venta"] / g["area_m2"]
        g["margen_pct"] = g["margen"] / g["venta"] * 100
        # Hay dos tiendas en Bogotá: si la etiqueta fuera solo la ciudad,
        # Plotly dibujaría las dos barras una encima de la otra.
        g["etiqueta"] = g["tienda"].str.replace("Nutramerican ", "", regex=False)
        g = g.sort_values("venta", ascending=False)

        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            gs = g.sort_values("venta")
            fig = go.Figure(go.Bar(x=gs["venta"], y=gs["etiqueta"],
                                   orientation="h", marker_color=AZUL_DEEP,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in gs["venta"]]))
            st.plotly_chart(light(fig, 360, "Venta por tienda en el período"),
                            use_container_width=True)
        with c2:
            gs = g.sort_values("venta_m2")
            fig = go.Figure(go.Bar(x=gs["venta_m2"], y=gs["etiqueta"], orientation="h",
                                   marker_color=ORO,
                                   hovertemplate="<b>%{y}</b><br>%{customdata} por m²<extra></extra>",
                                   customdata=[cop(x, 1) for x in gs["venta_m2"]]))
            st.plotly_chart(light(fig, 360, "Productividad: venta por m²"),
                            use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Tienda": g["etiqueta"], "Ciudad": g["ciudad"],
            "m²": g["area_m2"],
            "Venta": g["venta"].map(lambda x: cop(x, 1)),
            "Venta / m²": g["venta_m2"].map(lambda x: cop(x, 1)),
            "Visitantes": g["visitas"].map(lambda x: f"{int(x):,}"),
            "Conversión": g["conversion"].map(lambda x: f"{x:.1f}%"),
            "Ticket": g["ticket"].map(cop_full),
            "Margen %": g["margen_pct"].round(1),
            "Costo fijo": g["fijo"].map(lambda x: cop(x, 1)),
            "Contribución": g["contrib"].map(lambda x: cop(x, 1)),
        }), hide_index=True, use_container_width=True)

        peor = g.nsmallest(1, "contrib").iloc[0]
        mejor = g.nlargest(1, "venta_m2").iloc[0]
        st.markdown(panel("Lectura del comparativo", f"""
        · <b>{mejor['etiqueta']}</b> es la tienda más productiva por metro cuadrado
          ({cop(mejor['venta_m2'], 1)}/m²): es el formato que conviene replicar en la
          próxima apertura.<br>
        · <b>{peor['etiqueta']}</b> es la de menor contribución ({cop(peor['contrib'], 1)}).
          Antes de tocar el arriendo hay que mirar la pestaña siguiente: no es lo mismo
          que entre poca gente a que entre y no compre.<br>
        · Todas las tiendas cobran de contado, así que cada peso que se mueve del canal
          mayorista a tienda propia mejora margen <i>y</i> flujo de caja al mismo tiempo.
        """, "🔍"), unsafe_allow_html=True)

    with t2:
        g = f.groupby(["tienda_id", "tienda", "ciudad"]).agg(
            visitas=("visitas", "sum"), tickets=("tickets", "sum"),
            venta=("venta_cop", "sum")).reset_index()
        g["conversion"] = g["tickets"] / g["visitas"] * 100
        g["ticket"] = g["venta"] / g["tickets"]
        g["etiqueta"] = g["tienda"].str.replace("Nutramerican ", "", regex=False)

        fig = go.Figure(go.Scatter(
            x=g["visitas"], y=g["conversion"], mode="markers+text",
            text=g["etiqueta"], textposition="top center",
            textfont=dict(size=11, color=TINTA),
            marker=dict(size=g["venta"] / g["venta"].max() * 52 + 14,
                        color=g["ticket"], colorscale=[[0, AZUL_LT], [0.5, AZUL_LUM], [1, AZUL_DEEP]],
                        showscale=True, colorbar=dict(title="Ticket<br>promedio", thickness=12),
                        line=dict(color="white", width=2)),
            hovertemplate="<b>%{text}</b><br>Visitantes: %{x:,.0f}<br>Conversión: %{y:.1f}%<extra></extra>"))
        fig.add_hline(y=g["conversion"].mean(), line_dash="dot", line_color=MUTED)
        fig.add_vline(x=g["visitas"].mean(), line_dash="dot", line_color=MUTED)
        fig.update_xaxes(title="Visitantes en el período")
        fig.update_yaxes(title="Conversión (%)")
        f2 = light(fig, 470, "Cada tienda según cuánta gente entra y cuánta compra")
        f2.update_layout(hovermode="closest")
        st.plotly_chart(f2, use_container_width=True)

        prom_v, prom_c = g["visitas"].mean(), g["conversion"].mean()
        trafico = g[(g["visitas"] < prom_v) & (g["conversion"] >= prom_c)]["etiqueta"].tolist()
        cierre = g[(g["visitas"] >= prom_v) & (g["conversion"] < prom_c)]["etiqueta"].tolist()
        estrella = g[(g["visitas"] >= prom_v) & (g["conversion"] >= prom_c)]["etiqueta"].tolist()
        doble = g[(g["visitas"] < prom_v) & (g["conversion"] < prom_c)]["etiqueta"].tolist()

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(panel("Problema de tráfico", f"""
            <b>{', '.join(trafico) if trafico else 'Ninguna'}</b><br><br>
            Convierten bien: quien entra, compra. Lo que falta es gente en la puerta.
            La palanca es local —pauta geolocalizada, alianzas con gimnasios de la zona,
            activaciones de Megaplex Stars en esa ciudad—, no cambiar el equipo de la tienda.
            """, "🚶", tono="alerta" if trafico else "neutro"), unsafe_allow_html=True)
            st.markdown(panel("Tiendas modelo", f"""
            <b>{', '.join(estrella) if estrella else 'Ninguna'}</b><br><br>
            Traen gente y la convierten. Son la referencia de surtido, exhibición y guion de
            venta que deberían copiar las demás.
            """, "🏆", tono="bien"), unsafe_allow_html=True)
        with c2:
            st.markdown(panel("Problema de cierre de venta", f"""
            <b>{', '.join(cierre) if cierre else 'Ninguna'}</b><br><br>
            Entra gente y no compra. Aquí la plata de pauta se está desperdiciando: el problema
            está adentro —surtido agotado, asesoría, exhibición o precio percibido—, no afuera.
            """, "🎯", tono="alerta" if cierre else "neutro"), unsafe_allow_html=True)
            st.markdown(panel("Doble problema", f"""
            <b>{', '.join(doble) if doble else 'Ninguna'}</b><br><br>
            Poco tráfico y poca conversión al tiempo. Son las que hay que revisar primero,
            empezando por si el punto tiene inventario de las referencias que sí rotan.
            """, "⚠️", tono="alerta" if doble else "neutro"), unsafe_allow_html=True)

    with t3:
        mapa = td.copy()
        mapa["etiqueta"] = mapa["tienda"].str.replace("Nutramerican ", "", regex=False)
        vt = f.groupby("tienda_id")["venta_cop"].sum()
        mapa["venta"] = mapa["tienda_id"].map(vt).fillna(0)
        fig = go.Figure(go.Scattermap(
            lat=mapa["lat"], lon=mapa["lon"], mode="markers+text",
            text=mapa["etiqueta"], textposition="top center",
            textfont=dict(size=12, color=TINTA),
            marker=dict(size=mapa["venta"] / mapa["venta"].max() * 34 + 12, color=ROJO, opacity=0.85),
            hovertext=[f"{r['tienda']}<br>{r['direccion']}<br>{cop(r['venta'], 1)}"
                       for _, r in mapa.iterrows()],
            hoverinfo="text"))
        fig.update_layout(
            map=dict(style="carto-positron", center=dict(lat=5.6, lon=-74.4), zoom=4.4),
            height=470, margin=dict(l=0, r=0, t=8, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        cols = st.columns(4, gap="small")
        for i, (_, r) in enumerate(td.iterrows()):
            venta_t = vt.get(r["tienda_id"], 0)
            cols[i % 4].markdown(f"""
            <div style="background:{SURF};border:1px solid {BORDER};border-radius:14px;
              padding:14px;margin-bottom:12px;min-height:186px;
              box-shadow:0 1px 3px rgba(11,12,15,.06)">
              <p style="font-size:13px;font-weight:900;color:{TINTA};margin:0 0 2px">{r['tienda'].replace('Nutramerican ', '')}</p>
              <p style="font-size:10.5px;color:{MUTED};margin:0 0 8px;line-height:1.45">{r['direccion']}</p>
              <p style="font-size:11px;color:{MUTED};margin:0">📞 {r['celular']}</p>
              <p style="font-size:11px;color:{MUTED};margin:0">🕘 L-V {r['horario_lv']} · Sáb {r['horario_sab']}</p>
              <p style="font-size:11px;color:{MUTED};margin:0">📐 {r['area_m2']} m² · desde {r['anio_apertura']}</p>
              <p style="font-size:15px;font-weight:900;color:{AZUL_DEEP};margin:8px 0 0">{cop(venta_t, 1)}</p>
            </div>""", unsafe_allow_html=True)

        st.caption("Dirección, teléfono, horario y coordenadas son los datos reales publicados por "
                   "Nutramerican Pharma. Las cifras de venta son simuladas.")
