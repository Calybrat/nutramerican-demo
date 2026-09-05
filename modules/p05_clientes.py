import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

HOY = pd.Timestamp("2026-08-31")


def render():
    cli = datos.clientes()
    mkt = datos.marketing()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Clientes & Recompra",
        "El canal propio —tiendas y nutramerican.com— es el único donde se sabe quién compra. "
        "Un tarro de 2 lb rinde cerca de 30 días: la recompra no es una métrica de marketing, "
        "es el pulso del negocio"), unsafe_allow_html=True)

    total = len(cli)
    recurrentes = cli[cli["recurrente"]]
    tasa_rec = len(recurrentes) / total * 100
    ltv = cli["ltv_cop"].mean()
    ticket = cli["ticket_promedio_cop"].mean()
    inv_mkt = mkt[mkt["inversion_cop"] > 0]
    cac = inv_mkt["inversion_cop"].sum() / inv_mkt["clientes_nuevos"].sum()
    ratio = ltv / cac
    riesgo = cli[cli["en_riesgo_fuga"]]
    ciclo = recurrentes["ciclo_recompra_dias"].mean()

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Clientes identificados", f"{total:,}", "Tienda propia + web", True, "👥",
                      "En distribuidores y cadenas el cliente final es invisible."),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Tasa de recompra", pct(tasa_rec), "Referencia sana en D2C: 35%",
                      tasa_rec >= 35, "🔁"), unsafe_allow_html=True)
    k[2].markdown(kpi("Ciclo de recompra", f"{ciclo:.0f} días", "Un tarro rinde ~30 días",
                      ciclo <= 40, "📅",
                      "Si el ciclo se alarga, el cliente está comprando en otra parte."),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("LTV / CAC", f"{ratio:.1f}x",
                      f"LTV {cop(ltv)} · CAC {cop(cac)}", ratio >= 3, "📈",
                      "Por debajo de 3x el crecimiento por pauta deja de ser rentable."),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Reactivables", f"{len(riesgo):,}",
                      f"{cop(riesgo['ltv_cop'].sum(), 1)} de valor histórico",
                      len(riesgo) / total < 0.15, "⚠️",
                      "Volvieron al menos una vez y llevan entre 60 y 180 días sin comprar."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Retención y cohortes", "Segmentos y objetivos",
                              "Medios de pago", "Clientes a reactivar"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            cli2 = cli.copy()
            cli2["cohorte"] = cli2["primera_compra"].dt.strftime("%Y-%m")
            coh = cli2.groupby("cohorte").agg(
                clientes=("cliente_id", "count"),
                recompra=("recurrente", "mean"),
                ltv=("ltv_cop", "mean")).reset_index()
            coh = coh[coh["clientes"] >= 40]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=coh["cohorte"], y=coh["clientes"], name="Clientes nuevos",
                                 marker_color=AZUL_LT))
            fig.add_trace(go.Scatter(x=coh["cohorte"], y=coh["recompra"] * 100,
                                     name="% que volvió a comprar", yaxis="y2",
                                     mode="lines+markers", line=dict(color=ROJO, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="% recompra", range=[0, 100]))
            st.plotly_chart(light(fig, 380, "Cohortes: cuántos entraron cada mes y cuántos volvieron"),
                            use_container_width=True)
        with c2:
            bins = [0, 30, 45, 60, 90, 120, 10_000]
            etiquetas = ["Al día (0-30 d)", "31-45 d", "46-60 d", "61-90 d", "91-120 d", "+120 d"]
            cli2 = cli.copy()
            cli2["franja"] = pd.cut(cli2["dias_sin_comprar"], bins=bins, labels=etiquetas,
                                    include_lowest=True)
            fr = cli2.groupby("franja", observed=True).size()
            colores = [GOOD, GOOD, WARN, WARN, BAD, "#8F1218"]
            fig = go.Figure(go.Bar(x=fr.index.astype(str), y=fr.values,
                                   marker_color=colores[:len(fr)],
                                   text=[f"{x:,}" for x in fr.values], textposition="outside"))
            st.plotly_chart(light(fig, 380, "Días desde la última compra"),
                            use_container_width=True)

        pedidos = cli["pedidos"].value_counts().sort_index()
        pedidos = pedidos[pedidos.index <= 10]
        c1, c2 = st.columns([1, 1], gap="medium")
        with c1:
            fig = go.Figure(go.Bar(x=pedidos.index.astype(str), y=pedidos.values,
                                   marker_color=AZUL_DEEP,
                                   text=[f"{x:,}" for x in pedidos.values], textposition="outside"))
            fig.update_xaxes(title="Número de compras")
            st.plotly_chart(light(fig, 320, "Distribución de clientes por número de compras"),
                            use_container_width=True)
        with c2:
            g = cli.groupby("pedidos")["ltv_cop"].mean()
            g = g[g.index <= 10]
            fig = go.Figure(go.Bar(x=g.index.astype(str), y=g.values, marker_color=ORO,
                                   hovertemplate="%{x} compras<br>%{customdata}<extra></extra>",
                                   customdata=[cop_full(x) for x in g.values]))
            fig.update_xaxes(title="Número de compras")
            st.plotly_chart(light(fig, 320, "Valor histórico promedio según cuántas veces compró"),
                            use_container_width=True)

        una_vez = (cli["pedidos"] == 1).sum()
        st.markdown(panel("Dónde está la plata", f"""
        · <b>{una_vez:,} clientes ({una_vez/total*100:.0f}%)</b> compraron una sola vez. En
          suplementación eso casi siempre significa que probaron y no volvieron: o el producto no
          les cumplió, o nadie les escribió cuando se les estaba acabando el tarro.<br>
        · El cliente que llega a la segunda compra multiplica varias veces su valor. Mover a un
          cliente de una a dos compras es más barato que traer uno nuevo por
          <b>{cop(cac)}</b> de CAC.<br>
        · El ciclo medio es de <b>{ciclo:.0f} días</b>. Un recordatorio automático al día 25 —por
          WhatsApp, que es el canal donde ya atienden— es la palanca de retención más obvia
          y la que menos cuesta.
        """, "💡"), unsafe_allow_html=True)

    with t2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            seg = cli.groupby("segmento").agg(
                clientes=("cliente_id", "count"), ltv=("ltv_cop", "mean"),
                recompra=("recurrente", "mean")).reset_index().sort_values("clientes")
            fig = go.Figure(go.Bar(x=seg["clientes"], y=seg["segmento"], orientation="h",
                                   marker_color=PALETTE[:len(seg)]))
            st.plotly_chart(light(fig, 330, "Clientes por objetivo declarado"),
                            use_container_width=True)
        with c2:
            fig = go.Figure(go.Bar(x=seg["recompra"] * 100, y=seg["segmento"], orientation="h",
                                   marker_color=[GOOD if x >= 0.4 else WARN for x in seg["recompra"]],
                                   text=[f"{x*100:.0f}%" for x in seg["recompra"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, seg["recompra"].max() * 130])
            st.plotly_chart(light(fig, 330, "Tasa de recompra por objetivo"),
                            use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Objetivo": seg["segmento"],
            "Clientes": seg["clientes"].map(lambda x: f"{x:,}"),
            "LTV promedio": seg["ltv"].map(cop_full),
            "Recompra": (seg["recompra"] * 100).round(1).map(lambda x: f"{x}%"),
        }).sort_values("Clientes", ascending=False), hide_index=True, use_container_width=True)

        cap = cli.groupby("canal_captacion").agg(
            clientes=("cliente_id", "count"), ltv=("ltv_cop", "mean"),
            recompra=("recurrente", "mean")).reset_index().sort_values("clientes", ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cap["canal_captacion"], y=cap["clientes"], name="Clientes captados",
                             marker_color=AZUL_DEEP))
        fig.add_trace(go.Scatter(x=cap["canal_captacion"], y=cap["ltv"], name="LTV promedio",
                                 yaxis="y2", mode="lines+markers", line=dict(color=ROJO, width=3)))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                      title="LTV (COP)"))
        st.plotly_chart(light(fig, 360, "Por dónde llegan y cuánto valen según de dónde vienen"),
                        use_container_width=True)

        mejor = cap.nlargest(1, "ltv").iloc[0]
        st.markdown(panel("No todos los clientes nuevos valen lo mismo", f"""
        El cliente que llega por <b>{mejor['canal_captacion']}</b> tiene el valor histórico más
        alto ({cop_full(mejor['ltv'])}) y recompra {mejor['recompra']*100:.0f}% de las veces.
        Optimizar la pauta por costo por clic lleva a comprar el cliente más barato; optimizarla
        por LTV lleva a comprar el que se queda. Son dos decisiones distintas y solo la segunda
        construye marca.
        """, "🎯"), unsafe_allow_html=True)

    with t3:
        pago = cli.groupby("medio_pago").agg(
            clientes=("cliente_id", "count"), ticket=("ticket_promedio_cop", "mean"),
            ltv=("ltv_cop", "mean")).reset_index().sort_values("clientes", ascending=False)
        c1, c2 = st.columns([1, 1.4], gap="medium")
        with c1:
            fig = go.Figure(go.Pie(labels=pago["medio_pago"], values=pago["clientes"], hole=0.56,
                                   marker_colors=PALETTE, texttemplate="%{percent:.0%}"))
            st.plotly_chart(light(fig, 340, "Cómo pagan"), use_container_width=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=pago["medio_pago"], y=pago["ticket"], name="Ticket promedio",
                                 marker_color=AZUL_DEEP))
            fig.add_trace(go.Bar(x=pago["medio_pago"], y=pago["ltv"] - pago["ticket"],
                                 name="Resto del valor histórico", marker_color=ORO))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 340, "Ticket y valor histórico por medio de pago"),
                            use_container_width=True)

        fin = pago[pago["medio_pago"].isin(["Addi", "Sistecrédito"])]
        share_fin = fin["clientes"].sum() / pago["clientes"].sum() * 100
        ticket_fin = (fin["ticket"] * fin["clientes"]).sum() / fin["clientes"].sum()
        ticket_resto = ((pago[~pago["medio_pago"].isin(["Addi", "Sistecrédito"])]["ticket"] *
                         pago[~pago["medio_pago"].isin(["Addi", "Sistecrédito"])]["clientes"]).sum()
                        / pago[~pago["medio_pago"].isin(["Addi", "Sistecrédito"])]["clientes"].sum())
        st.markdown(panel("La financiación no es un detalle de checkout", f"""
        <b>{share_fin:.0f}%</b> de los clientes paga con Addi o Sistecrédito, y su ticket promedio
        es de {cop_full(ticket_fin)} frente a {cop_full(ticket_resto)} de los demás
        ({(ticket_fin/ticket_resto-1)*100:+.0f}%). Con tarros de $249.000 esa diferencia es
        justamente la que permite que alguien se lleve el tarro de 2 lb en vez del de 0.9 lb.
        Vale la pena verlo al revés: si la financiación se cae un mes, se cae el ticket.
        """, "💳"), unsafe_allow_html=True)

    with t4:
        perdidos = cli[cli["perdido"]]
        st.markdown(panel("Lista de trabajo, no un reporte", f"""
        Estos son los <b>{len(riesgo):,} clientes</b> que ya compraron dos veces o más, se pasaron
        de su ciclo y todavía están a tiempo de volver: entre 60 y 180 días sin comprar.
        Representan <b>{cop(riesgo['ltv_cop'].sum(), 1)}</b> de valor histórico.<br><br>
        Por encima de 180 días ya no es riesgo de fuga: son <b>{len(perdidos):,} clientes perdidos</b>
        y recuperarlos cuesta casi lo mismo que traer uno nuevo. Por eso la lista de abajo es
        corta a propósito: es a quién escribirle esta semana, no un archivo para revisar algún día.
        """, "📋", tono="alerta"), unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            seg_f = st.multiselect("Objetivo", sorted(riesgo["segmento"].unique()), key="cl_seg")
        with c2:
            ciu_f = st.multiselect("Ciudad", sorted(riesgo["ciudad"].unique()), key="cl_ciu")
        with c3:
            min_ltv = st.slider("Valor histórico mínimo (COP)", 0,
                                int(riesgo["ltv_cop"].quantile(0.95)), 0, 50_000, key="cl_ltv")

        r = riesgo.copy()
        if seg_f:
            r = r[r["segmento"].isin(seg_f)]
        if ciu_f:
            r = r[r["ciudad"].isin(ciu_f)]
        r = r[r["ltv_cop"] >= min_ltv].sort_values("ltv_cop", ascending=False)

        st.markdown(f"<p style='font-size:12.5px;color:{MUTED};font-weight:700'>"
                    f"{len(r):,} clientes · {cop(r['ltv_cop'].sum(), 1)} de valor histórico "
                    f"· {r['suscrito_crm'].sum():,} tienen correo o WhatsApp registrado</p>",
                    unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Cliente": r["cliente_id"], "Ciudad": r["ciudad"], "Objetivo": r["segmento"],
            "Compras": r["pedidos"],
            "Última compra": r["ultima_compra"].dt.strftime("%d/%m/%Y"),
            "Días sin volver": r["dias_sin_comprar"],
            "Ticket promedio": r["ticket_promedio_cop"].map(cop_full),
            "Valor histórico": r["ltv_cop"].map(cop_full),
            "Contactable": r["suscrito_crm"].map({True: "Sí", False: "No"}),
        }).head(400), hide_index=True, use_container_width=True, height=440)
        st.caption("Se muestran los 400 de mayor valor. En el producto final esta lista se "
                   "exporta o se dispara directo a la herramienta de CRM y WhatsApp.")
