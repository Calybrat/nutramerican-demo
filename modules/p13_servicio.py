import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    pqr = datos.pqr()
    v = datos.ventas()
    desp = datos.despachos()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Servicio al Cliente & PQR",
        "WhatsApp, línea gratuita #590, chat del sitio, redes y tienda física · "
        "todo lo que entra, en un solo tablero, ordenado por lo que de verdad importa"),
        unsafe_allow_html=True)

    meses = sorted(pqr["mes"].unique())
    ult6 = meses[-6:]
    p6 = pqr[pqr["mes"].isin(ult6)]
    pedidos6 = v[v["mes"].isin(ult6)]["documento_id"].nunique()

    total = len(p6)
    tasa = total / pedidos6 * 100 if pedidos6 else 0
    sla = p6["cumple_sla_4h"].mean() * 100
    resp = p6["horas_primera_respuesta"].median()
    cierre = p6[p6["horas_cierre"].notna()]["horas_cierre"].median()
    csat = p6["csat"].mean()
    abiertos = p6[p6["estado"].isin(["Abierto", "Escalado"])]

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("PQR recibidos", f"{total:,}",
                      f"{tasa:.2f}% de los pedidos del período", tasa < 4, "🎧",
                      "Cuántos reclamos entran por cada 100 pedidos."), unsafe_allow_html=True)
    k[1].markdown(kpi("Primera respuesta", f"{resp:.1f} h",
                      f"{sla:.0f}% dentro de las 4 primeras horas", sla >= 80, "⚡"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Tiempo de cierre", f"{cierre:.0f} h", "Mediana hasta resolver",
                      cierre <= 48, "✅"), unsafe_allow_html=True)
    k[3].markdown(kpi("Satisfacción", f"{csat:.2f} / 5", "Encuesta al cerrar el caso",
                      csat >= 4, "⭐"), unsafe_allow_html=True)
    k[4].markdown(kpi("Sin cerrar", f"{len(abiertos)}",
                      f"{int((p6['estado'] == 'Escalado').sum())} escalados a un agente",
                      len(abiertos) < 60, "📂"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Motivos y canales", "De dónde nace el reclamo", "Casos abiertos"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            g = p6.groupby("motivo").agg(n=("pqr_id", "count"),
                                         cierre=("horas_cierre", "median")).reset_index()
            g = g.sort_values("n")
            fig = go.Figure(go.Bar(x=g["n"], y=g["motivo"], orientation="h",
                                   marker_color=[BAD if c > 90 else WARN if c > 48 else AZUL_DEEP
                                                 for c in g["cierre"].fillna(0)],
                                   text=g["n"], textposition="outside",
                                   hovertemplate="<b>%{y}</b><br>%{x} casos<extra></extra>"))
            fig.update_xaxes(range=[0, g["n"].max() * 1.2])
            st.plotly_chart(light(fig, 400,
                                  "Motivos de PQR · el color marca el tiempo de cierre"),
                            use_container_width=True)
        with c2:
            g = p6.groupby("canal").size().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=ORO,
                                   text=g.values, textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.25])
            st.plotly_chart(light(fig, 400, "Canal por el que entra el reclamo"),
                            use_container_width=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            g = pqr.groupby("mes").agg(n=("pqr_id", "count"),
                                       sla=("cumple_sla_4h", "mean")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=g["mes"], y=g["n"], name="PQR recibidos",
                                 marker_color=AZUL_LT))
            fig.add_trace(go.Scatter(x=g["mes"], y=g["sla"] * 100, name="% dentro de SLA 4 h",
                                     yaxis="y2", mode="lines+markers",
                                     line=dict(color=ROJO, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="% SLA", range=[0, 105]))
            st.plotly_chart(light(fig, 340, "Volumen mensual y cumplimiento de respuesta"),
                            use_container_width=True)
        with c2:
            g = p6.groupby("canal").agg(resp=("horas_primera_respuesta", "median"),
                                        sla=("cumple_sla_4h", "mean")).reset_index()
            g = g.sort_values("resp")
            fig = go.Figure(go.Bar(x=g["resp"], y=g["canal"], orientation="h",
                                   marker_color=[GOOD if x <= 4 else WARN if x <= 12 else BAD
                                                 for x in g["resp"]],
                                   text=[f"{x:.1f} h" for x in g["resp"]], textposition="outside"))
            fig.update_xaxes(range=[0, g["resp"].max() * 1.3])
            st.plotly_chart(light(fig, 340, "Mediana de primera respuesta por canal"),
                            use_container_width=True)

        tabla = p6.groupby("motivo").agg(
            n=("pqr_id", "count"), resp=("horas_primera_respuesta", "median"),
            cierre=("horas_cierre", "median"), csat=("csat", "mean"),
            escal=("requiere_agente_humano", "mean")).reset_index().sort_values("n", ascending=False)
        st.dataframe(pd.DataFrame({
            "Motivo": tabla["motivo"], "Casos": tabla["n"],
            "% del total": (tabla["n"] / tabla["n"].sum() * 100).round(1),
            "Primera respuesta": tabla["resp"].map(lambda x: f"{x:.1f} h"),
            "Cierre": tabla["cierre"].map(lambda x: f"{x:.0f} h" if pd.notna(x) else "—"),
            "Satisfacción": tabla["csat"].round(2),
            "Requiere agente humano": (tabla["escal"] * 100).round(0).map(lambda x: f"{x:.0f}%"),
        }), hide_index=True, use_container_width=True)

        top_motivo = tabla.iloc[0]
        lento = tabla.nlargest(1, "cierre").iloc[0]
        st.markdown(panel("Lo que dicen los motivos", f"""
        · <b>{top_motivo['motivo']}</b> es el reclamo más frecuente
          ({top_motivo['n']} casos, {top_motivo['n']/tabla['n'].sum()*100:.0f}% del total).
          Los reclamos de entrega no se resuelven en servicio al cliente: se resuelven en
          logística. El módulo de Logística &amp; Inventario muestra exactamente en qué ciudades
          se está incumpliendo la promesa.<br>
        · <b>{lento['motivo']}</b> es el que más tarda en cerrarse
          ({lento['cierre']:.0f} horas). Cada hora de más ahí cuesta puntos de satisfacción: la
          correlación entre tiempo de cierre y CSAT se ve en la columna de la derecha.<br>
        · Los casos de camiseta personalizada y de contenido incompleto son los que casi siempre
          necesitan intervención humana. Saber eso de antemano permite enrutarlos directo, sin
          hacer pasar al cliente por dos niveles de chat.
        """, "🔍"), unsafe_allow_html=True)

    with t2:
        st.markdown(panel("La pregunta que importa", """
        Un tablero de servicio al cliente que solo cuenta tickets sirve para medir al equipo de
        servicio. Este cruza los reclamos con la operación que los origina, que es lo que permite
        arreglar la causa en vez de contestar más rápido.
        """, "🧭"), unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            entrega = pqr[pqr["motivo"].isin(["Demora en la entrega", "Producto averiado en transporte"])]
            g = entrega.groupby("mes").size().rename("pqr")
            otif = desp[desp["estado"] == "Entregado"].groupby("mes")["otif"].mean() * 100
            df = pd.concat([g, otif.rename("otif")], axis=1).dropna()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df.index, y=df["pqr"], name="PQR de entrega",
                                 marker_color=ROJO))
            fig.add_trace(go.Scatter(x=df.index, y=df["otif"], name="OTIF (%)", yaxis="y2",
                                     mode="lines+markers", line=dict(color=AZUL_DEEP, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="OTIF %"))
            st.plotly_chart(light(fig, 360, "Reclamos de entrega frente al cumplimiento logístico"),
                            use_container_width=True)
        with c2:
            g = p6.groupby("ciudad").agg(n=("pqr_id", "count")).reset_index()
            vend = v[v["mes"].isin(ult6)].groupby("ciudad")["documento_id"].nunique()
            g["pedidos"] = g["ciudad"].map(vend)
            g = g[g["pedidos"] > 200].copy()
            g["tasa"] = g["n"] / g["pedidos"] * 100
            g = g.sort_values("tasa")
            fig = go.Figure(go.Bar(x=g["tasa"], y=g["ciudad"], orientation="h",
                                   marker_color=[BAD if x > 4 else WARN if x > 2.5 else GOOD
                                                 for x in g["tasa"]],
                                   text=[f"{x:.1f}%" for x in g["tasa"]], textposition="outside"))
            fig.update_xaxes(range=[0, g["tasa"].max() * 1.3],
                             title="PQR por cada 100 pedidos")
            st.plotly_chart(light(fig, 360, "Tasa de reclamo por ciudad"),
                            use_container_width=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            bins = [0, 4, 12, 24, 48, 96, 10_000]
            lab = ["≤4 h", "4-12 h", "12-24 h", "1-2 días", "2-4 días", "+4 días"]
            pp = p6[p6["csat"].notna()].copy()
            pp["franja"] = pd.cut(pp["horas_cierre"], bins=bins, labels=lab, include_lowest=True)
            g = pp.groupby("franja", observed=True)["csat"].mean()
            fig = go.Figure(go.Bar(x=g.index.astype(str), y=g.values,
                                   marker_color=[GOOD if x >= 4.2 else WARN if x >= 3.6 else BAD
                                                 for x in g.values],
                                   text=[f"{x:.2f}" for x in g.values], textposition="outside"))
            fig.update_yaxes(range=[0, 5.4], title="Satisfacción media")
            st.plotly_chart(light(fig, 340, "Cuánto cuesta cada hora de demora en satisfacción"),
                            use_container_width=True)
        with c2:
            g = p6.groupby(["motivo"])["requiere_agente_humano"].mean().sort_values()
            fig = go.Figure(go.Bar(x=g.values * 100, y=g.index, orientation="h",
                                   marker_color=[BAD if x > 0.5 else AZUL_DEEP for x in g.values],
                                   text=[f"{x*100:.0f}%" for x in g.values], textposition="outside"))
            fig.update_xaxes(range=[0, 128], title="% que necesita persona")
            st.plotly_chart(light(fig, 340, "Qué se puede automatizar y qué no"),
                            use_container_width=True)

        auto = p6[~p6["requiere_agente_humano"]]
        st.markdown(panel("Dónde está el ahorro", f"""
        <b>{len(auto)/len(p6)*100:.0f}%</b> de los casos del período no requieren una persona:
        son consultas de estado de envío, dudas de uso de producto y solicitudes de factura.
        Son exactamente el tipo de pregunta que un agente automático conectado a los datos reales
        —pedido, guía, lote— responde en segundos y a cualquier hora.<br><br>
        El equipo de servicio queda entonces para lo que sí necesita criterio: los faltantes,
        los eventos adversos y las garantías. Ahí no hay que ir más rápido, hay que ir mejor.
        """, "🤖"), unsafe_allow_html=True)

    with t3:
        ab = pqr[pqr["estado"].isin(["Abierto", "Escalado"])].copy()
        c1, c2, c3 = st.columns(3)
        with c1:
            mot_f = st.multiselect("Motivo", sorted(ab["motivo"].unique()), key="pq_mot")
        with c2:
            can_f = st.multiselect("Canal", sorted(ab["canal"].unique()), key="pq_can")
        with c3:
            solo_esc = st.checkbox("Solo escalados", key="pq_esc")
        if mot_f:
            ab = ab[ab["motivo"].isin(mot_f)]
        if can_f:
            ab = ab[ab["canal"].isin(can_f)]
        if solo_esc:
            ab = ab[ab["estado"] == "Escalado"]
        ab = ab.sort_values("fecha")

        st.markdown(f"<p style='font-size:12.5px;color:{MUTED};font-weight:700'>"
                    f"{len(ab)} casos sin cerrar · "
                    f"{int(ab['requiere_agente_humano'].sum())} necesitan un agente</p>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Caso": ab["pqr_id"], "Fecha": ab["fecha"], "Motivo": ab["motivo"],
            "Canal": ab["canal"], "Ciudad": ab["ciudad"], "Estado": ab["estado"],
            "Horas hasta la 1ª respuesta": ab["horas_primera_respuesta"],
            "Dentro de SLA": ab["cumple_sla_4h"].map({True: "Sí", False: "No"}),
            "Necesita agente": ab["requiere_agente_humano"].map({True: "Sí", False: ""}),
        }), hide_index=True, use_container_width=True, height=460)
