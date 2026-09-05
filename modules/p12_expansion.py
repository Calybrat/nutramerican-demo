import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

# Contexto real de cada mercado: cómo se entra y qué exige
MERCADOS = {
    "Colombia": ("🇨🇴", "Mercado base", "Planta propia, 8 tiendas, e-commerce y toda la red de "
                 "distribución. Registro INVIMA vigente por producto."),
    "Ecuador": ("🇪🇨", "Distribuidor", "Mercado andino con hábitos de consumo cercanos. "
                "Requiere registro sanitario ARCSA por referencia."),
    "México": ("🇲🇽", "Distribuidor", "El mercado de suplementación más grande de habla hispana "
               "y el más competido. Exige aviso de funcionamiento COFEPRIS."),
    "Honduras": ("🇭🇳", "Distribuidor", "Puerta de entrada a Centroamérica. Volumen pequeño, "
                 "barrera regulatoria baja."),
    "Panamá": ("🇵🇦", "Distribuidor", "Abierto en 2026. Hub logístico natural para el resto "
               "de Centroamérica."),
    "España": ("🇪🇸", "Operación propia", "Entrada a la Unión Europea, iniciada en 2026. "
               "Exige notificación por producto y cumplimiento del reglamento europeo."),
    "Estados Unidos": ("🇺🇸", "Nutramerican Pharma LLC", "La planta ya cuenta con habilitación "
                       "FDA. El reto no es regulatorio: es el costo de adquisición en el mercado "
                       "de suplementos más saturado del mundo."),
}


def render():
    v = datos.ventas()
    car = datos.cartera()
    desp = datos.despachos()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Expansión Internacional",
        "Ecuador, México, Honduras y Panamá por distribuidor; España y Estados Unidos con "
        "operación propia · la visión declarada es ser exportador competitivo de alimentos "
        "saludables"), unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    ult12 = meses[-12:]
    v12 = v[v["mes"].isin(ult12)]
    intl = v12[v12["pais"] != "Colombia"]

    total = v12["venta_cop"].sum()
    share = intl["venta_cop"].sum() / total * 100
    margen_intl = intl["margen_cop"].sum() / intl["venta_cop"].sum() * 100 if len(intl) else 0
    margen_co = (v12[v12["pais"] == "Colombia"]["margen_cop"].sum() /
                 v12[v12["pais"] == "Colombia"]["venta_cop"].sum() * 100)
    mercados = intl["pais"].nunique()

    # Crecimiento del internacional
    ult6 = v[v["mes"].isin(meses[-6:]) & (v["pais"] != "Colombia")]["venta_cop"].sum()
    prev6 = v[v["mes"].isin(meses[-12:-6]) & (v["pais"] != "Colombia")]["venta_cop"].sum()
    crec = (ult6 - prev6) / prev6 * 100 if prev6 else 0

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Venta internacional", cop(intl["venta_cop"].sum(), 1), "Últimos 12 meses",
                      True, "🌎"), unsafe_allow_html=True)
    k[1].markdown(kpi("Peso sobre el total", pct(share), "Meta razonable a 3 años: 20%",
                      share >= 8, "📊"), unsafe_allow_html=True)
    k[2].markdown(kpi("Crecimiento", f"{crec:+.1f}%", "Últimos 6 meses vs 6 anteriores",
                      crec >= 0, "📈"), unsafe_allow_html=True)
    k[3].markdown(kpi("Mercados activos", f"{mercados}", "Además de Colombia", True, "🗺️"),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Margen internacional", pct(margen_intl),
                      f"Colombia: {margen_co:.1f}%", margen_intl >= margen_co, "💰",
                      "Exportar deja más margen por unidad, pero cuesta más traer al cliente."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Comparativo de mercados", "Evolución y madurez",
                          "Qué se vende en cada país"])

    with t1:
        g = v12.groupby("pais").agg(
            venta=("venta_cop", "sum"), unidades=("unidades", "sum"),
            margen=("margen_cop", "sum"), skus=("sku", "nunique")).reset_index()
        g["margen_pct"] = g["margen"] / g["venta"] * 100
        g["precio_medio"] = g["venta"] / g["unidades"]
        # Cartera y cumplimiento por país
        carg = car[~car["pagada"]].groupby("pais")["valor_cop"].sum()
        g["cartera"] = g["pais"].map(carg).fillna(0)
        entg = desp[desp["estado"] == "Entregado"].groupby("pais")["dias_reales"].mean()
        g["dias_entrega"] = g["pais"].map(entg)
        g = g.sort_values("venta", ascending=False)

        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            gs = g[g["pais"] != "Colombia"].sort_values("venta")
            fig = go.Figure(go.Bar(x=gs["venta"], y=gs["pais"], orientation="h",
                                   marker_color=ORO,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in gs["venta"]]))
            st.plotly_chart(light(fig, 360, "Facturación por mercado de exportación"),
                            use_container_width=True)
        with c2:
            gs = g.sort_values("margen_pct")
            fig = go.Figure(go.Bar(x=gs["margen_pct"], y=gs["pais"], orientation="h",
                                   marker_color=[ROJO if p == "Colombia" else AZUL_DEEP
                                                 for p in gs["pais"]],
                                   text=[f"{x:.0f}%" for x in gs["margen_pct"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, gs["margen_pct"].max() * 1.25])
            st.plotly_chart(light(fig, 360, "Margen bruto por mercado"),
                            use_container_width=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        cols = st.columns(4, gap="small")
        for i, (_, r) in enumerate(g.iterrows()):
            bandera, modelo, nota = MERCADOS.get(r["pais"], ("🌐", "—", ""))
            cols[i % 4].markdown(f"""
            <div style="background:{SURF};border:1px solid {BORDER};border-radius:14px;
              padding:15px;margin-bottom:12px;min-height:246px;
              box-shadow:0 1px 3px rgba(11,12,15,.06);
              border-top:3px solid {ROJO if r['pais'] == 'Colombia' else ORO}">
              <p style="font-size:15px;font-weight:900;color:{TINTA};margin:0 0 2px">
                {bandera} {r['pais']}</p>
              <p style="font-size:10px;color:{MUTED};margin:0 0 10px;font-weight:800;
                text-transform:uppercase;letter-spacing:.06em">{modelo}</p>
              <p style="font-size:19px;font-weight:900;color:{AZUL_DEEP};margin:0">{cop(r['venta'], 1)}</p>
              <p style="font-size:11px;color:{MUTED};margin:4px 0 0">
                {int(r['unidades']):,} und · margen {r['margen_pct']:.0f}%</p>
              <p style="font-size:11px;color:{MUTED};margin:2px 0 0">
                {int(r['skus'])} referencias · precio medio {cop_full(r['precio_medio'])}</p>
              <p style="font-size:10.5px;color:{MUTED};margin:10px 0 0;line-height:1.5">{nota}</p>
            </div>""", unsafe_allow_html=True)

        st.dataframe(pd.DataFrame({
            "País": g["pais"],
            "Modelo": g["pais"].map(lambda p: MERCADOS.get(p, ("", "—", ""))[1]),
            "Facturación 12m": g["venta"].map(lambda x: cop(x, 1)),
            "Mix": (g["venta"] / total * 100).round(1).map(lambda x: f"{x}%"),
            "Unidades": g["unidades"].map(lambda x: f"{int(x):,}"),
            "Precio neto medio": g["precio_medio"].map(cop_full),
            "Margen %": g["margen_pct"].round(1),
            "Referencias": g["skus"],
            "Cartera abierta": g["cartera"].map(lambda x: cop(x, 1)),
            "Días de entrega": g["dias_entrega"].round(1),
        }), hide_index=True, use_container_width=True)

    with t2:
        piv = v[v["pais"] != "Colombia"].groupby(["mes", "pais"])["venta_cop"].sum().reset_index()
        c1, c2 = st.columns([1.6, 1], gap="medium")
        with c1:
            fig = go.Figure()
            for i, p in enumerate(sorted(piv["pais"].unique())):
                sub = piv[piv["pais"] == p]
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["venta_cop"], name=p,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 380, "Facturación internacional mes a mes"),
                            use_container_width=True)
        with c2:
            tot_mes = v.groupby("mes")["venta_cop"].sum()
            int_mes = v[v["pais"] != "Colombia"].groupby("mes")["venta_cop"].sum()
            sh = (int_mes / tot_mes * 100).fillna(0)
            fig = go.Figure(go.Scatter(x=sh.index, y=sh.values, mode="lines+markers",
                                       line=dict(color=ROJO, width=3), fill="tozeroy",
                                       fillcolor="rgba(216,35,42,.10)"))
            fig.update_yaxes(title="% del total")
            st.plotly_chart(light(fig, 380, "Peso del internacional sobre la venta total"),
                            use_container_width=True)

        # Madurez: primer mes con venta y ritmo actual
        prim = v[v["pais"] != "Colombia"].groupby("pais")["mes"].min()
        ultm = v[(v["pais"] != "Colombia") & (v["mes"] == meses[-1])].groupby("pais")["venta_cop"].sum()
        mad = pd.DataFrame({"Apertura": prim, "Venta del último mes": ultm}).fillna(0)
        mad["Meses activo"] = mad["Apertura"].map(
            lambda m: (int(meses[-1][:4]) - int(m[:4])) * 12 + int(meses[-1][5:]) - int(m[5:]) + 1)
        mad["Venta mensual por mes activo"] = mad["Venta del último mes"] / mad["Meses activo"]
        mad = mad.sort_values("Meses activo", ascending=False)

        fig = go.Figure(go.Scatter(
            x=mad["Meses activo"], y=mad["Venta del último mes"], mode="markers+text",
            text=mad.index, textposition="top center", textfont=dict(size=11, color=TINTA),
            marker=dict(size=26, color=ORO, line=dict(color="white", width=2)),
            hovertemplate="<b>%{text}</b><br>%{x} meses activo<br>%{customdata}<extra></extra>",
            customdata=[cop(x, 1) for x in mad["Venta del último mes"]]))
        fig.update_xaxes(title="Meses desde la apertura del mercado")
        fig.update_yaxes(title="Venta del último mes (COP)")
        f2 = light(fig, 380, "Madurez de cada mercado")
        f2.update_layout(hovermode="closest")
        st.plotly_chart(f2, use_container_width=True)

        joven = mad.nsmallest(1, "Meses activo")
        st.markdown(panel("Cómo leer la madurez", f"""
        Un mercado nuevo no se juzga por lo que factura sino por la pendiente. <b>{joven.index[0]}</b>
        lleva apenas {int(joven['Meses activo'].iloc[0])} meses: comparar su venta con la de
        Ecuador, que lleva más de año y medio, no dice nada útil.<br><br>
        Lo que sí se puede exigir a los seis meses es otra cosa: que el distribuidor haya
        colocado producto en más de un punto, que la reposición sea recurrente y no un solo
        pedido inicial, y que la cartera se esté pagando. Los tres datos ya están en este panel.
        """, "🌱"), unsafe_allow_html=True)

    with t3:
        pais_sel = st.selectbox("Mercado", sorted(v12[v12["pais"] != "Colombia"]["pais"].unique()),
                                key="ex_pais")
        vp = v12[v12["pais"] == pais_sel]
        vco = v12[v12["pais"] == "Colombia"]

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            g = vp.groupby("categoria")["venta_cop"].sum()
            g = (g / g.sum() * 100).sort_values()
            gco = vco.groupby("categoria")["venta_cop"].sum()
            gco = (gco / gco.sum() * 100).reindex(g.index)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=g.values, y=g.index, orientation="h", name=pais_sel,
                                 marker_color=ORO))
            fig.add_trace(go.Bar(x=gco.values, y=gco.index, orientation="h", name="Colombia",
                                 marker_color=AZUL_LT))
            fig.update_xaxes(title="% del mix del mercado")
            st.plotly_chart(light(fig, 380, f"Mix de categorías · {pais_sel} vs Colombia"),
                            use_container_width=True)
        with c2:
            g = vp.groupby("producto").agg(v=("venta_cop", "sum"),
                                           u=("unidades", "sum")).nlargest(10, "v").sort_values("v")
            fig = go.Figure(go.Bar(x=g["v"], y=g.index, orientation="h", marker_color=AZUL_DEEP,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in g["v"]]))
            st.plotly_chart(light(fig, 380, f"Top 10 referencias en {pais_sel}"),
                            use_container_width=True)

        det = vp.groupby(["producto", "marca", "categoria"]).agg(
            u=("unidades", "sum"), v=("venta_cop", "sum"), m=("margen_cop", "sum")).reset_index()
        det["margen_pct"] = (det["m"] / det["v"] * 100).round(1)
        det["precio"] = det["v"] / det["u"]
        det = det.sort_values("v", ascending=False)
        st.dataframe(pd.DataFrame({
            "Producto": det["producto"], "Marca": det["marca"], "Categoría": det["categoria"],
            "Unidades": det["u"].map(lambda x: f"{int(x):,}"),
            "Facturación": det["v"].map(lambda x: cop(x, 1)),
            "Precio neto medio": det["precio"].map(cop_full),
            "Margen %": det["margen_pct"],
        }), hide_index=True, use_container_width=True, height=320)

        bandera, modelo, nota = MERCADOS.get(pais_sel, ("🌐", "—", ""))
        skus_pais = det["producto"].nunique()
        skus_co = vco["producto"].nunique()
        st.markdown(panel(f"{bandera} {pais_sel} · {modelo}", f"""
        {nota}<br><br>
        Hoy se venden allí <b>{skus_pais} referencias</b> de las <b>{skus_co}</b> que se venden en
        Colombia. Esa brecha no siempre es comercial: cada referencia adicional exige su propio
        registro sanitario en el país, y ese trámite tiene costo y tiempo. La decisión de portafolio
        internacional es, en la práctica, una decisión regulatoria: qué referencias justifican
        pagar el registro y cuáles no.
        """, "🧭"), unsafe_allow_html=True)
