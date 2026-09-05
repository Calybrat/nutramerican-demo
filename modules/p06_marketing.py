import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    mkt = datos.marketing()
    emb = datos.embajadores()
    ev = datos.eventos()
    cli = datos.clientes()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Marketing & Megaplex Stars",
        "Nueve redes activas, pauta en cuatro plataformas, un programa de embajadores atletas y "
        "presencia en ferias · qué de todo eso realmente trae clientes"), unsafe_allow_html=True)

    meses = sorted(mkt["mes"].unique())
    ult12 = meses[-12:]
    m12 = mkt[mkt["mes"].isin(ult12)]
    pagado = m12[m12["inversion_cop"] > 0]

    inv = pagado["inversion_cop"].sum()
    ingresos = m12["ingresos_cop"].sum()
    roas = m12["ingresos_cop"].sum() / inv if inv else 0
    nuevos = int(m12["clientes_nuevos"].sum())
    cac = inv / nuevos if nuevos else 0
    ltv = cli["ltv_cop"].mean()

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Inversión 12 meses", cop(inv, 1), "Pauta, embajadores y eventos", True, "💸"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Ingresos atribuidos", cop(ingresos, 1), "Venta del canal propio", True, "📈"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("ROAS global", f"{roas:.1f}x", "Meta: 4x", roas >= 4, "🎯",
                      "Cuántos pesos vuelven por cada peso invertido."), unsafe_allow_html=True)
    k[3].markdown(kpi("Clientes nuevos", f"{nuevos:,}", f"CAC {cop(cac)}", True, "👥"),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Relación LTV / CAC", f"{ltv/cac:.1f}x", "Sano por encima de 3x",
                      ltv / cac >= 3, "⚖️"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Rendimiento por canal", "Programa Megaplex Stars",
                          "Ferias y eventos"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            piv = mkt.groupby(["mes", "canal"])["inversion_cop"].sum().reset_index()
            fig = go.Figure()
            for i, c in enumerate(sorted(mkt["canal"].unique())):
                sub = piv[piv["canal"] == c]
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["inversion_cop"], name=c,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 380, "Inversión mensual por canal (COP)"),
                            use_container_width=True)
        with c2:
            g = pagado.groupby("canal").agg(inv=("inversion_cop", "sum"),
                                            ing=("ingresos_cop", "sum")).reset_index()
            g["roas"] = g["ing"] / g["inv"]
            g = g.sort_values("roas")
            fig = go.Figure(go.Bar(x=g["roas"], y=g["canal"], orientation="h",
                                   marker_color=[GOOD if x >= 4 else WARN if x >= 2.5 else BAD
                                                 for x in g["roas"]],
                                   text=[f"{x:.1f}x" for x in g["roas"]], textposition="outside"))
            fig.update_xaxes(range=[0, g["roas"].max() * 1.28])
            st.plotly_chart(light(fig, 380, "ROAS por canal"), use_container_width=True)

        g = m12.groupby("canal").agg(
            inv=("inversion_cop", "sum"), ing=("ingresos_cop", "sum"),
            nuevos=("clientes_nuevos", "sum"), clics=("clics", "sum"),
            impr=("impresiones", "sum")).reset_index()
        g["roas"] = np.where(g["inv"] > 0, g["ing"] / g["inv"], np.nan)
        g["cac"] = np.where(g["nuevos"] > 0, g["inv"] / g["nuevos"], np.nan)
        g["ctr"] = np.where(g["impr"] > 0, g["clics"] / g["impr"] * 100, np.nan)
        g = g.sort_values("inv", ascending=False)
        st.dataframe(pd.DataFrame({
            "Canal": g["canal"],
            "Inversión": g["inv"].map(lambda x: cop(x, 1) if x else "Sin costo directo"),
            "Ingresos atribuidos": g["ing"].map(lambda x: cop(x, 1)),
            "ROAS": g["roas"].map(lambda x: f"{x:.1f}x" if pd.notna(x) else "—"),
            "Clientes nuevos": g["nuevos"].map(lambda x: f"{int(x):,}"),
            "CAC": g["cac"].map(lambda x: cop_full(x) if pd.notna(x) else "—"),
            "CTR": g["ctr"].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "—"),
        }), hide_index=True, use_container_width=True)

        mejor = g[g["roas"].notna()].nlargest(1, "roas").iloc[0]
        peor = g[g["roas"].notna()].nsmallest(1, "roas").iloc[0]
        st.markdown(panel("Dónde mover el presupuesto", f"""
        · <b>{mejor['canal']}</b> devuelve {mejor['roas']:.1f}x. Los canales propios —correo y
          WhatsApp— siempre ganan en ROAS porque le hablan a alguien que ya compró: no son
          adquisición, son retención barata, y su techo es el tamaño de la base.<br>
        · <b>{peor['canal']}</b> está en {peor['roas']:.1f}x, por debajo del umbral de 2,5x. O se
          ajusta la creatividad y el público, o esa plata rinde más en el canal de arriba.<br>
        · El CAC promedio es de <b>{cop(cac)}</b> contra un LTV de <b>{cop(ltv)}</b>. La relación
          está en {ltv/cac:.1f}x: hay margen para invertir más, siempre que la recompra no se caiga.
        """, "🧭"), unsafe_allow_html=True)

    with t2:
        st.markdown(panel("Qué es este programa", """
        Megaplex Stars es el programa real de embajadores de la marca: atletas de distintas
        disciplinas y ciudades que crean contenido y venden con código propio. Es la línea de
        marketing más difícil de medir con una hoja de cálculo, porque el retorno no está en el
        alcance sino en cuántos pedidos entran con el código de cada uno.
        """, "⭐"), unsafe_allow_html=True)

        seg_tot = int(emb["seguidores"].sum())
        costo = int(emb["costo_mensual_cop"].sum())
        venta_at = int(emb["venta_atribuida_cop"].sum())
        roi = venta_at / costo if costo else 0
        rentables = emb[emb["roi"] >= 2]

        k = st.columns(4, gap="small")
        k[0].markdown(kpi("Embajadores activos", f"{len(emb)}",
                          f"{emb['disciplina'].nunique()} disciplinas", True, "⭐"),
                      unsafe_allow_html=True)
        k[1].markdown(kpi("Alcance combinado", f"{seg_tot/1_000_000:.2f}M",
                          "Seguidores sumados", True, "📣"), unsafe_allow_html=True)
        k[2].markdown(kpi("Costo mensual", cop(costo, 1), "Fees y producto entregado", True, "💸"),
                      unsafe_allow_html=True)
        k[3].markdown(kpi("Retorno del programa", f"{roi:.1f}x",
                          f"{len(rentables)} de {len(emb)} embajadores por encima de 2x",
                          roi >= 2, "🎯",
                          "Venta con código dividida por lo que cuesta el programa."),
                      unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            fig = go.Figure(go.Scatter(
                x=emb["seguidores"], y=emb["roi"], mode="markers",
                text=emb["disciplina"] + " · " + emb["ciudad"],
                marker=dict(size=emb["pedidos_con_codigo"] / emb["pedidos_con_codigo"].max() * 34 + 8,
                            color=emb["engagement_pct"],
                            colorscale=[[0, "#CBD5E1"], [0.5, AZUL_LUM], [1, ROJO]],
                            showscale=True, colorbar=dict(title="Engage-<br>ment %", thickness=12),
                            line=dict(color="white", width=1.4)),
                hovertemplate="<b>%{text}</b><br>%{x:,.0f} seguidores<br>ROI %{y:.1f}x<extra></extra>"))
            fig.add_hline(y=2, line_dash="dot", line_color=ROJO)
            fig.update_xaxes(title="Seguidores", type="log")
            fig.update_yaxes(title="Retorno (venta con código / costo)")
            f2 = light(fig, 400, "Tamaño de la audiencia contra retorno real")
            f2.update_layout(hovermode="closest")
            st.plotly_chart(f2, use_container_width=True)
        with c2:
            d = emb.groupby("disciplina").agg(v=("venta_atribuida_cop", "sum"),
                                              c=("costo_mensual_cop", "sum")).reset_index()
            d["roi"] = d["v"] / d["c"]
            d = d.sort_values("roi")
            fig = go.Figure(go.Bar(x=d["roi"], y=d["disciplina"], orientation="h",
                                   marker_color=[GOOD if x >= 2 else WARN if x >= 1 else BAD
                                                 for x in d["roi"]],
                                   text=[f"{x:.1f}x" for x in d["roi"]], textposition="outside"))
            fig.update_xaxes(range=[0, d["roi"].max() * 1.3])
            st.plotly_chart(light(fig, 400, "Retorno por disciplina"), use_container_width=True)

        e = emb.sort_values("roi", ascending=False)
        st.dataframe(pd.DataFrame({
            "Embajador": e["embajador_id"], "Disciplina": e["disciplina"], "Ciudad": e["ciudad"],
            "Seguidores": e["seguidores"].map(lambda x: f"{x:,}"),
            "Engagement": e["engagement_pct"].map(lambda x: f"{x:.1f}%"),
            "Contenidos / mes": e["contenidos_mes"],
            "Pedidos con código": e["pedidos_con_codigo"].map(lambda x: f"{x:,}"),
            "Venta atribuida": e["venta_atribuida_cop"].map(lambda x: cop(x, 1)),
            "Costo mensual": e["costo_mensual_cop"].map(cop_full),
            "ROI": e["roi"].map(lambda x: f"{x:.1f}x"),
        }), hide_index=True, use_container_width=True, height=380)

        chicos = emb[emb["seguidores"] < emb["seguidores"].median()]
        roi_chicos = chicos["venta_atribuida_cop"].sum() / chicos["costo_mensual_cop"].sum()
        grandes = emb[emb["seguidores"] >= emb["seguidores"].median()]
        roi_grandes = grandes["venta_atribuida_cop"].sum() / grandes["costo_mensual_cop"].sum()
        st.markdown(panel("El hallazgo que no se ve en Instagram", f"""
        Los embajadores con audiencia por debajo de la mediana devuelven
        <b>{roi_chicos:.1f}x</b>; los de audiencia grande, <b>{roi_grandes:.1f}x</b>.
        {"El programa está pagando alcance, no ventas: los perfiles grandes cuestan mucho más y no convierten proporcionalmente." if roi_chicos > roi_grandes else "Los perfiles grandes están sosteniendo el programa, pero conviene vigilar que su costo no crezca más rápido que su venta."}
        La métrica que decide no es el número de seguidores: es cuántos pedidos entraron con
        su código, y eso ya se está midiendo.
        """, "🔍"), unsafe_allow_html=True)

    with t3:
        e = ev.sort_values("fecha", ascending=False)
        e["roi"] = e["ventas_directas_cop"] / e["inversion_cop"]
        e["costo_lead"] = e["inversion_cop"] / e["leads"]

        k = st.columns(4, gap="small")
        k[0].markdown(kpi("Eventos", f"{len(e)}", "Últimos 12 meses", True, "🎪"),
                      unsafe_allow_html=True)
        k[1].markdown(kpi("Inversión", cop(e["inversion_cop"].sum(), 1), "Stand, equipo y muestras",
                          True, "💸"), unsafe_allow_html=True)
        k[2].markdown(kpi("Leads captados", f"{int(e['leads'].sum()):,}",
                          f"Costo por lead {cop_full(e['inversion_cop'].sum()/e['leads'].sum())}",
                          True, "📇"), unsafe_allow_html=True)
        k[3].markdown(kpi("Clientes nuevos", f"{int(e['nuevos_clientes'].sum()):,}",
                          "De los leads del evento", True, "👥"), unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        fig = go.Figure()
        ee = e.sort_values("roi")
        fig.add_trace(go.Bar(x=ee["roi"], y=ee["evento"], orientation="h",
                             marker_color=[GOOD if x >= 1.5 else WARN if x >= 1 else BAD
                                           for x in ee["roi"]],
                             text=[f"{x:.1f}x" for x in ee["roi"]], textposition="outside"))
        fig.update_xaxes(range=[0, ee["roi"].max() * 1.3])
        st.plotly_chart(light(fig, 340, "Retorno directo por evento"), use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Evento": e["evento"], "Ciudad": e["ciudad"], "Fecha": e["fecha"],
            "Objetivo": e["objetivo"],
            "Inversión": e["inversion_cop"].map(lambda x: cop(x, 1)),
            "Leads": e["leads"].map(lambda x: f"{int(x):,}"),
            "Costo por lead": e["costo_lead"].map(cop_full),
            "Venta directa": e["ventas_directas_cop"].map(lambda x: cop(x, 1)),
            "Clientes nuevos": e["nuevos_clientes"],
            "ROI directo": e["roi"].map(lambda x: f"{x:.1f}x"),
        }), hide_index=True, use_container_width=True)

        st.markdown(panel("Cómo juzgar una feria", """
        El retorno directo casi nunca justifica un stand: la feria no se paga con lo que se vende
        en el stand, se paga con los leads que entran a la base y con lo que se vende después.
        Por eso esta tabla muestra las dos cosas. Un evento con ROI directo bajo pero costo por
        lead barato puede ser el mejor negocio del año —siempre que alguien contacte esos leads—.
        Y ahí es donde el módulo de Clientes &amp; Recompra cierra el círculo: se puede rastrear
        cuántos de esos contactos terminaron comprando.
        """, "🎪"), unsafe_allow_html=True)
