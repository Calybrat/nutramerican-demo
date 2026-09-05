import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    comp = datos.compras()
    prov = datos.proveedores()
    trm = datos.trm()
    fin = datos.finanzas()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Abastecimiento & Divisa",
        "La proteína de suero se importa —del orden de 120 toneladas por trimestre— y se paga en "
        "dólares; el producto se vende en pesos. Entre la orden de compra y el pago pueden pasar "
        "dos meses de TRM"), unsafe_allow_html=True)

    meses = sorted(comp["mes"].unique())
    ult12 = meses[-12:]
    c12 = comp[comp["mes"].isin(ult12)]

    kg_total = c12["kg"].sum()
    usd_total = c12["valor_usd"].sum()
    costo_total = c12["costo_cop"].sum()
    dif_cambio = c12["diferencia_en_cambio_cop"].sum()
    puntual = c12["a_tiempo"].mean() * 100
    lead_medio = c12["lead_time_real_dias"].mean()
    whey = c12[c12["insumo"].str.startswith("Proteína de suero")]
    whey_t_trim = whey["kg"].sum() / 1000 / 4

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Compras 12 meses", cop(costo_total, 1), f"{kg_total/1000:,.0f} toneladas",
                      True, "📥"), unsafe_allow_html=True)
    imp_cop = c12[c12["moneda"] != "COP"]["costo_cop"].sum()
    k[1].markdown(kpi("Exposición en dólares", usd(usd_total, 1),
                      f"{imp_cop/costo_total*100:.0f}% de la compra es importada",
                      True, "💵",
                      "Lo que se compra en moneda extranjera y se vende en pesos."),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Proteína de suero", f"{whey_t_trim:,.0f} t / trimestre",
                      "Escala pública: ~120 t", True, "🥛"), unsafe_allow_html=True)
    k[3].markdown(kpi("Diferencia en cambio", cop(dif_cambio, 1),
                      "Ganancia" if dif_cambio >= 0 else "Pérdida por movimiento de la TRM",
                      dif_cambio >= 0, "📉",
                      "Lo que cambió el costo entre la fecha de la orden y la del pago."),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Cumplimiento de proveedores", pct(puntual),
                      f"Meta 85% · lead time medio {lead_medio:.0f} días", puntual >= 85, "⏱️",
                      "Órdenes que llegaron dentro de los 5 días de tolerancia."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Riesgo de divisa", "Proveedores y cumplimiento",
                          "Órdenes de compra"])

    # ── Divisa ──────────────────────────────────────────────────────────────
    with t1:
        c1, c2 = st.columns([1.6, 1], gap="medium")
        with c1:
            gm = comp.groupby("mes").agg(usd=("valor_usd", "sum"),
                                         dif=("diferencia_en_cambio_cop", "sum")).reset_index()
            gm = gm.merge(trm, on="mes")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=gm["mes"], y=gm["usd"], name="Compras en USD",
                                 marker_color="#B9D3F2"))
            fig.add_trace(go.Scatter(x=gm["mes"], y=gm["trm_cop_usd"], name="TRM (COP por USD)",
                                     yaxis="y2", mode="lines+markers",
                                     line=dict(color=ROJO, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="TRM"))
            st.plotly_chart(light(fig, 380, "Compras en dólares frente a la tasa de cambio"),
                            use_container_width=True)
        with c2:
            fig = go.Figure(go.Bar(x=gm["mes"], y=gm["dif"],
                                   marker_color=[GOOD if x >= 0 else BAD for x in gm["dif"]],
                                   hovertemplate="%{x}<br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in gm["dif"]]))
            fig.add_hline(y=0, line_color=TINTA, line_width=1.2)
            st.plotly_chart(light(fig, 380, "Diferencia en cambio mensual (COP)"),
                            use_container_width=True)

        # Sensibilidad
        st.markdown(f"<p style='font-size:13px;font-weight:900;color:{TINTA};margin:14px 0 6px'>"
                    f"Qué pasa si la TRM se mueve</p>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2.4])
        with c1:
            shock = st.slider("Variación de la TRM (%)", -20, 20, 8, 1, key="ab_shock")
        usd_anual = c12["valor_usd"].sum()
        trm_actual = trm.iloc[-1]["trm_cop_usd"]
        impacto = usd_anual * trm_actual * shock / 100
        ingresos_anual = fin[fin["mes"].isin(ult12)]["ingresos_cop"].sum()
        ebitda_anual = fin[fin["mes"].isin(ult12)]["ebitda_cop"].sum()
        with c2:
            kk = st.columns(3, gap="small")
            kk[0].markdown(kpi("Mayor costo de materia prima", cop(impacto, 1),
                               f"Con TRM a {trm_actual*(1+shock/100):,.0f}", impacto <= 0, "💱"),
                           unsafe_allow_html=True)
            kk[1].markdown(kpi("Impacto sobre el EBITDA",
                               f"{-impacto/ebitda_anual*100:+.1f}%",
                               f"Sobre un EBITDA anual de {cop(ebitda_anual, 1)}",
                               impacto <= 0, "🏦",
                               "Cuánto se come del EBITDA si el costo sube y el precio no."),
                           unsafe_allow_html=True)
            kk[2].markdown(kpi("Alza de precio equivalente",
                               pct(impacto / ingresos_anual * 100),
                               "Para compensar sin tocar margen", impacto <= 0, "🏷️"),
                           unsafe_allow_html=True)

        st.markdown(panel("La decisión de fondo", f"""
        Con <b>{usd(usd_anual, 1)}</b> comprados al año en moneda extranjera, cada 100 pesos que
        se mueve la TRM cambia el costo anual en cerca de
        <b>{cop(usd_anual * 100, 1)}</b>. Hay tres formas de manejarlo y las tres se deciden
        con estos números a la vista: cubrir con forwards parte de la compra, comprar por
        adelantado cuando la tasa está baja —lo que aprieta la caja y la bodega— o trasladar al
        precio, que en un mercado con competencia importada tiene un techo.<br><br>
        Lo que no se puede es enterarse en el cierre contable. La diferencia en cambio de los
        últimos doce meses fue de <b>{cop(dif_cambio, 1)}</b>: eso es EBITDA que se ganó o se
        perdió sin que nadie tomara una decisión comercial.
        """, "💱", tono="alerta" if dif_cambio < 0 else "neutro"), unsafe_allow_html=True)

    # ── Proveedores ─────────────────────────────────────────────────────────
    with t2:
        g = c12.groupby(["proveedor_id", "insumo", "origen", "moneda", "critico"]).agg(
            kg=("kg", "sum"), costo=("costo_cop", "sum"), ordenes=("oc_id", "count"),
            lead=("lead_time_real_dias", "mean"), plan=("lead_time_plan_dias", "mean"),
            puntual=("a_tiempo", "mean"), atraso=("dias_atraso", "mean")).reset_index()
        g = g.merge(prov[["proveedor_id", "score_calidad", "score_puntualidad", "score_precio"]],
                    on="proveedor_id")
        g = g.sort_values("costo", ascending=False)

        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            gs = g.sort_values("costo").tail(12)
            fig = go.Figure(go.Bar(x=gs["costo"], y=gs["insumo"], orientation="h",
                                   marker_color=[ROJO if c else AZUL_DEEP for c in gs["critico"]],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in gs["costo"]]))
            st.plotly_chart(light(fig, 390, "Gasto por insumo · rojo = insumo crítico"),
                            use_container_width=True)
        with c2:
            gs = g.sort_values("puntual")
            fig = go.Figure(go.Bar(x=gs["puntual"] * 100, y=gs["insumo"], orientation="h",
                                   marker_color=[GOOD if x >= 0.85 else WARN if x >= 0.7 else BAD
                                                 for x in gs["puntual"]],
                                   text=[f"{x*100:.0f}%" for x in gs["puntual"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, 118])
            st.plotly_chart(light(fig, 390, "Entregas a tiempo"), use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Insumo": g["insumo"], "Origen": g["origen"], "Moneda": g["moneda"],
            "Crítico": g["critico"].map({1: "Sí", 0: ""}),
            "Toneladas": (g["kg"] / 1000).round(1),
            "Gasto 12m": g["costo"].map(lambda x: cop(x, 1)),
            "Órdenes": g["ordenes"],
            "Lead time plan": g["plan"].map(lambda x: f"{x:.0f} d"),
            "Lead time real": g["lead"].map(lambda x: f"{x:.0f} d"),
            "Atraso medio": g["atraso"].map(lambda x: f"{x:+.0f} d"),
            "A tiempo": (g["puntual"] * 100).round(0).map(lambda x: f"{x:.0f}%"),
            "Calidad": g["score_calidad"], "Precio": g["score_precio"],
        }), hide_index=True, use_container_width=True)

        criticos = g[g["critico"] == 1]
        peor = criticos.nsmallest(1, "puntual").iloc[0]
        lead_max = criticos["lead"].max()
        st.markdown(panel("Dónde está el riesgo real", f"""
        · Los insumos críticos tienen un lead time de hasta <b>{lead_max:.0f} días</b>. Eso quiere
          decir que la producción de noviembre se decide en agosto: no hay forma de reaccionar
          en el mes.<br>
        · <b>{peor['insumo']}</b> llega a tiempo solo el <b>{peor['puntual']*100:.0f}%</b> de las
          veces, con un atraso medio de {peor['atraso']:+.0f} días. Cada retraso ahí se traduce
          en una corrida de planta que se reprograma y en un quiebre de la referencia que más
          rota.<br>
        · La concentración también es riesgo: si un solo proveedor cubre la proteína de suero y
          se cae, no hay plan B a menos de dos meses. Tener un segundo proveedor homologado cuesta
          plata en el corto plazo y evita parar la planta en el largo.
        """, "⚠️", tono="alerta"), unsafe_allow_html=True)

    with t3:
        d = comp.sort_values("fecha_orden", ascending=False)
        c1, c2, c3 = st.columns(3)
        with c1:
            ins_f = st.multiselect("Insumo", sorted(comp["insumo"].unique()), key="ab_ins")
        with c2:
            mon_f = st.multiselect("Moneda", sorted(comp["moneda"].unique()), key="ab_mon")
        with c3:
            solo_atraso = st.checkbox("Solo órdenes con atraso", key="ab_atr")
        if ins_f:
            d = d[d["insumo"].isin(ins_f)]
        if mon_f:
            d = d[d["moneda"].isin(mon_f)]
        if solo_atraso:
            d = d[d["dias_atraso"] > 5]

        st.dataframe(pd.DataFrame({
            "Orden": d["oc_id"], "Fecha": d["fecha_orden"], "Insumo": d["insumo"],
            "Origen": d["origen"], "Moneda": d["moneda"],
            "Kg": d["kg"].map(lambda x: f"{x:,.0f}"),
            "USD / kg": d["precio_unitario_usd"].map(lambda x: f"{x:,.2f}"),
            "Valor USD": d["valor_usd"].map(lambda x: f"{x:,.0f}" if x else "—"),
            "TRM orden": d["trm_orden"].map(lambda x: f"{x:,.0f}"),
            "TRM pago": d["trm_pago"].map(lambda x: f"{x:,.0f}"),
            "Costo COP": d["costo_cop"].map(lambda x: cop(x, 1)),
            "Dif. en cambio": d["diferencia_en_cambio_cop"].map(
                lambda x: cop(x, 1) if x else "—"),
            "Atraso": d["dias_atraso"].map(lambda x: f"{x:+d} d"),
        }), hide_index=True, use_container_width=True, height=520)
