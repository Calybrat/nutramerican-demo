import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

# Tiempos de entrega que la propia compañía publica en su guía de servicio
SLA_PUBLICADO = {
    "Bogotá": "Mismo día o día siguiente (MELONN)",
    "Medellín": "Mismo día o día siguiente (MELONN)",
    "Cali": "1 a 3 días hábiles", "Bucaramanga": "1 a 3 días hábiles",
    "Cúcuta": "1 a 3 días hábiles", "Barranquilla": "1 a 3 días hábiles",
    "Pereira": "1 a 3 días hábiles",
}


def render():
    desp = datos.despachos()
    inv = datos.inventario()
    bod = datos.bodegas()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Logística & Inventario",
        "De la planta de Palmira al CD de Yumbo, de ahí a MELONN en Bogotá y Medellín, a las 8 "
        "tiendas y a la puerta del cliente · lo prometido contra lo cumplido"),
        unsafe_allow_html=True)

    meses = sorted(desp["mes"].unique())
    ult6 = meses[-6:]
    d6 = desp[desp["mes"].isin(ult6)]
    ent = d6[d6["estado"] == "Entregado"]

    otif = ent["otif"].mean() * 100 if len(ent) else 0
    a_tiempo = ent["a_tiempo"].mean() * 100 if len(ent) else 0
    completo = ent["completo"].mean() * 100 if len(ent) else 0
    dias = ent["dias_reales"].mean()
    costo_log = d6["costo_logistico_cop"].sum() / d6["valor_cop"].sum() * 100
    devueltos = int((d6["estado"] == "Devuelto").sum())

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("OTIF", pct(otif), "Meta interna: 92%", otif >= 92, "🎯",
                      "Entregado completo y en la fecha prometida. Las dos cosas."),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("A tiempo", pct(a_tiempo), f"Completo: {completo:.1f}%", a_tiempo >= 92,
                      "⏱️"), unsafe_allow_html=True)
    k[2].markdown(kpi("Tiempo medio de entrega", f"{dias:.1f} días", "Sobre pedidos entregados",
                      dias <= 2.5, "🚚"), unsafe_allow_html=True)
    k[3].markdown(kpi("Costo logístico", pct(costo_log), "Sobre la venta despachada",
                      costo_log <= 7, "💸",
                      "Cada punto aquí sale directo del margen operativo."), unsafe_allow_html=True)
    k[4].markdown(kpi("Devoluciones", f"{devueltos:,}",
                      f"{devueltos/len(d6)*100:.2f}% de los despachos",
                      devueltos / len(d6) < 0.01, "↩️"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Cumplimiento de entregas", "Inventario multi-bodega",
                          "Transportadoras"])

    with t1:
        c1, c2 = st.columns([1.6, 1], gap="medium")
        with c1:
            g = desp[desp["estado"] == "Entregado"].groupby("mes").agg(
                otif=("otif", "mean"), tiempo=("a_tiempo", "mean"),
                comp=("completo", "mean")).reset_index()
            fig = go.Figure()
            for nombre, col, color in [("OTIF", "otif", AZUL_DEEP),
                                       ("A tiempo", "tiempo", ORO),
                                       ("Completo", "comp", MUTED)]:
                fig.add_trace(go.Scatter(x=g["mes"], y=g[col] * 100, name=nombre,
                                         mode="lines+markers", line=dict(width=2.8, color=color)))
            fig.add_hline(y=92, line_dash="dot", line_color=ROJO)
            fig.update_yaxes(range=[60, 102])
            st.plotly_chart(light(fig, 370, "Evolución del cumplimiento (%)"),
                            use_container_width=True)
        with c2:
            g = ent[ent["pais"] == "Colombia"].groupby("ciudad").agg(
                otif=("otif", "mean"), n=("despacho_id", "count")).reset_index()
            g = g[g["n"] >= 40].sort_values("otif")
            fig = go.Figure(go.Bar(x=g["otif"] * 100, y=g["ciudad"], orientation="h",
                                   marker_color=[GOOD if x >= 0.92 else WARN if x >= 0.85 else BAD
                                                 for x in g["otif"]],
                                   text=[f"{x*100:.0f}%" for x in g["otif"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, 118])
            st.plotly_chart(light(fig, 370, "OTIF por ciudad"), use_container_width=True)

        g = ent[ent["pais"] == "Colombia"].groupby("ciudad").agg(
            plan=("dias_plan", "mean"), real=("dias_reales", "mean"),
            n=("despacho_id", "count"), otif=("otif", "mean")).reset_index()
        g = g[g["n"] >= 40].sort_values("real", ascending=False)
        g["SLA publicado"] = g["ciudad"].map(SLA_PUBLICADO).fillna("2 a 3 días hábiles")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=g["ciudad"], y=g["plan"], name="Prometido", marker_color=AZUL_LT))
        fig.add_trace(go.Bar(x=g["ciudad"], y=g["real"], name="Real", marker_color=AZUL_DEEP))
        st.plotly_chart(light(fig, 340, "Días prometidos frente a días reales, por ciudad"),
                        use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Ciudad": g["ciudad"], "SLA publicado": g["SLA publicado"],
            "Días prometidos": g["plan"].round(1), "Días reales": g["real"].round(1),
            "Desviación": (g["real"] - g["plan"]).round(1).map(lambda x: f"{x:+.1f}"),
            "OTIF": (g["otif"] * 100).round(1).map(lambda x: f"{x}%"),
            "Despachos": g["n"].map(lambda x: f"{x:,}"),
        }), hide_index=True, use_container_width=True)

        peor = g.nlargest(1, "real").iloc[0]
        st.markdown(panel("Lo que el cliente sí nota", f"""
        La compañía publica en su propia guía que Bogotá y Medellín se entregan el mismo día o al
        siguiente, y el resto del país entre uno y tres días hábiles. Esa promesa es un contrato
        con el cliente: cuando se incumple, el reclamo entra por WhatsApp y termina en el módulo
        de PQR.<br><br>
        Hoy la ciudad con mayor desviación es <b>{peor['ciudad']}</b>
        ({peor['real']:.1f} días reales contra {peor['plan']:.1f} prometidos). Antes de cambiar
        de transportadora vale la pena mirar de qué bodega se está despachando: muchas veces el
        problema no es el transporte sino que el producto salió de Yumbo en vez de la bodega
        cercana.
        """, "📦"), unsafe_allow_html=True)

    with t2:
        c1, c2, c3 = st.columns(3)
        with c1:
            bod_f = st.multiselect("Bodega", sorted(inv["bodega"].unique()), key="lo_bod")
        with c2:
            est_f = st.multiselect("Estado", ["Crítico", "Bajo", "Normal", "Exceso"], key="lo_est")
        with c3:
            marca_f = st.multiselect("Marca", sorted(inv["marca"].unique()), key="lo_mar")
        i = inv.copy()
        if bod_f:
            i = i[i["bodega"].isin(bod_f)]
        if est_f:
            i = i[i["estado"].isin(est_f)]
        if marca_f:
            i = i[i["marca"].isin(marca_f)]

        valor = i["valor_inventario_cop"].sum()
        criticos = i[i["estado"] == "Crítico"]
        exceso = i[i["estado"] == "Exceso"]
        vencer = i[i["proximo_a_vencer"]]

        k = st.columns(4, gap="small")
        k[0].markdown(kpi("Valor del inventario", cop(valor, 1),
                          f"{int(i['stock_unidades'].sum()):,} unidades", True, "🏬"),
                      unsafe_allow_html=True)
        k[1].markdown(kpi("Referencias críticas", f"{len(criticos)}",
                          "Menos de 12 días de cobertura", len(criticos) < 20, "🔴"),
                      unsafe_allow_html=True)
        k[2].markdown(kpi("Inventario en exceso", cop(exceso["valor_inventario_cop"].sum(), 1),
                          f"{len(exceso)} referencias con +60 días",
                          len(exceso) < 40, "🧊",
                          "Plata parada en bodega que podría estar en materia prima."),
                      unsafe_allow_html=True)
        k[3].markdown(kpi("Lotes añejos", f"{len(vencer)}",
                          "Más de 300 días en bodega", len(vencer) < 15, "⏳",
                          "En alimentos la fecha de vencimiento define hasta cuándo se puede vender."),
                      unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            g = i.groupby(["bodega", "estado"])["valor_inventario_cop"].sum().unstack(fill_value=0)
            fig = go.Figure()
            for est in ["Crítico", "Bajo", "Normal", "Exceso"]:
                if est in g.columns:
                    fig.add_trace(go.Bar(x=g.index, y=g[est], name=est,
                                         marker_color=estado_color(est)))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 370, "Valor del inventario por bodega y estado"),
                            use_container_width=True)
        with c2:
            g = i.groupby("bodega")["dias_cobertura"].mean().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                                   marker_color=[BAD if x < 15 else GOOD if x < 55 else INFO
                                                 for x in g.values],
                                   text=[f"{x:.0f} d" for x in g.values], textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.3])
            st.plotly_chart(light(fig, 370, "Días de cobertura promedio"),
                            use_container_width=True)

        st.markdown(f"<p style='font-size:13px;font-weight:900;color:{TINTA};margin:12px 0 6px'>"
                    f"Referencias que necesitan reposición ya</p>", unsafe_allow_html=True)
        cr = criticos.nsmallest(25, "dias_cobertura")
        st.dataframe(pd.DataFrame({
            "Producto": cr["producto"], "Marca": cr["marca"], "Bodega": cr["bodega"],
            "Stock": cr["stock_unidades"].map(lambda x: f"{x:,}"),
            "Demanda diaria": cr["demanda_diaria"],
            "Días de cobertura": cr["dias_cobertura"],
            "Valor": cr["valor_inventario_cop"].map(lambda x: cop(x, 1)),
        }), hide_index=True, use_container_width=True, height=300)

        st.markdown(panel("El costo de las dos puntas", f"""
        Hay <b>{cop(exceso['valor_inventario_cop'].sum(), 1)}</b> en inventario de más y
        <b>{len(criticos)} referencias</b> a punto de agotarse al mismo tiempo. No es
        contradictorio: es lo que pasa cuando la reposición se decide por bodega y no por
        referencia. La plata que sobra en unas referencias es exactamente la que falta para
        adelantar la importación de las otras.
        """, "⚖️", tono="alerta"), unsafe_allow_html=True)

    with t3:
        g = ent.groupby("transportadora").agg(
            n=("despacho_id", "count"), otif=("otif", "mean"), tiempo=("a_tiempo", "mean"),
            dias=("dias_reales", "mean"), costo=("costo_logistico_cop", "sum"),
            valor=("valor_cop", "sum")).reset_index()
        g["costo_pct"] = g["costo"] / g["valor"] * 100
        g["costo_envio"] = g["costo"] / g["n"]
        g = g[g["n"] >= 30].sort_values("n", ascending=False)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            gs = g.sort_values("otif")
            fig = go.Figure(go.Bar(x=gs["otif"] * 100, y=gs["transportadora"], orientation="h",
                                   marker_color=[GOOD if x >= 0.92 else WARN if x >= 0.85 else BAD
                                                 for x in gs["otif"]],
                                   text=[f"{x*100:.0f}%" for x in gs["otif"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, 118])
            st.plotly_chart(light(fig, 340, "OTIF por transportadora"), use_container_width=True)
        with c2:
            fig = go.Figure(go.Scatter(
                x=g["costo_envio"], y=g["otif"] * 100, mode="markers+text",
                text=g["transportadora"], textposition="top center",
                textfont=dict(size=11, color=TINTA),
                marker=dict(size=g["n"] / g["n"].max() * 40 + 12, color=AZUL_DEEP,
                            line=dict(color="white", width=2)),
                hovertemplate="<b>%{text}</b><br>%{customdata} por envío<br>OTIF %{y:.1f}%<extra></extra>",
                customdata=[cop_full(x) for x in g["costo_envio"]]))
            fig.update_xaxes(title="Costo medio por envío (COP)")
            fig.update_yaxes(title="OTIF %")
            f2 = light(fig, 340, "Costo contra cumplimiento")
            f2.update_layout(hovermode="closest")
            st.plotly_chart(f2, use_container_width=True)

        st.dataframe(pd.DataFrame({
            "Transportadora": g["transportadora"],
            "Despachos": g["n"].map(lambda x: f"{x:,}"),
            "OTIF": (g["otif"] * 100).round(1).map(lambda x: f"{x}%"),
            "A tiempo": (g["tiempo"] * 100).round(1).map(lambda x: f"{x}%"),
            "Días promedio": g["dias"].round(1),
            "Costo por envío": g["costo_envio"].map(cop_full),
            "Costo / venta": g["costo_pct"].round(2).map(lambda x: f"{x}%"),
        }), hide_index=True, use_container_width=True)

        mejor = g.nlargest(1, "otif").iloc[0]
        caro = g.nlargest(1, "costo_envio").iloc[0]
        st.markdown(panel("Cómo negociar con estos datos", f"""
        <b>{mejor['transportadora']}</b> es la de mejor cumplimiento ({mejor['otif']*100:.0f}% OTIF)
        y <b>{caro['transportadora']}</b> la más costosa por envío ({cop_full(caro['costo_envio'])}).
        Una negociación de tarifas sin esta tabla es una conversación sobre precio; con la tabla
        es una conversación sobre precio <i>y</i> cumplimiento —que es donde realmente se pierde
        plata, porque cada entrega tarde termina en un PQR y a veces en una devolución—.
        """, "🤝"), unsafe_allow_html=True)
