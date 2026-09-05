import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

CAPACIDAD_T = 1000     # toneladas de almacenamiento declaradas
PLANTA_M2 = 2500


def render():
    prod = datos.produccion()
    v = datos.ventas()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Producción & Planta",
        "Planta propia en Cantarrana, Palmira · 2.500 m², 1.000 toneladas de capacidad de "
        "almacenamiento y certificación FSSC 22000 · seis líneas y tres turnos",
        adorno="fssc"), unsafe_allow_html=True)

    meses = sorted(prod["mes"].unique())
    c1, c2, c3 = st.columns(3)
    with c1:
        rango = st.select_slider("Meses", options=meses, value=(meses[-6], meses[-1]),
                                 key="pr_rango")
    with c2:
        lineas = st.multiselect("Línea", sorted(prod["linea"].unique()), key="pr_linea")
    with c3:
        turnos = st.multiselect("Turno", sorted(prod["turno"].unique()), key="pr_turno")

    p = prod[(prod["mes"] >= rango[0]) & (prod["mes"] <= rango[1])]
    if lineas:
        p = p[p["linea"].isin(lineas)]
    if turnos:
        p = p[p["turno"].isin(turnos)]
    if p.empty:
        st.warning("Ningún lote con esos filtros.")
        return

    lotes = len(p)
    producidas = int(p["unidades_producidas"].sum())
    plan = int(p["unidades_plan"].sum())
    cumplimiento = producidas / plan * 100 if plan else 0
    oee = p["oee_pct"].mean()
    merma = p["merma_pct"].mean()
    costo_merma = int((p["unidades_plan"] - p["unidades_producidas"]).sum() *
                      (p["costo_lote_cop"].sum() / max(1, producidas)))
    toneladas = p["kg_lote"].sum() / 1000

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Lotes fabricados", f"{lotes:,}", f"{producidas:,} unidades", True, "🏭"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Cumplimiento del plan", pct(cumplimiento), "Producido sobre planeado",
                      cumplimiento >= 97, "🎯"), unsafe_allow_html=True)
    k[2].markdown(kpi("OEE promedio", pct(oee), "Referencia de clase mundial: 85%", oee >= 75,
                      "⚙️", "Disponibilidad × rendimiento × calidad de las líneas."),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("Merma", pct(merma, 2), f"Equivale a {cop(costo_merma, 1)}", merma <= 2.5,
                      "🗑️", "Producto que se planeó y no salió: materia prima pagada y perdida."),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Volumen procesado", ton(toneladas), f"Capacidad declarada: {CAPACIDAD_T} t",
                      True, "⚖️"), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Líneas y turnos", "Plan contra demanda", "Detalle de lotes"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            piv = p.groupby(["mes", "linea"])["unidades_producidas"].sum().reset_index()
            fig = go.Figure()
            for i, l in enumerate(sorted(p["linea"].unique())):
                sub = piv[piv["linea"] == l]
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["unidades_producidas"], name=l,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 370, "Unidades producidas por línea"),
                            use_container_width=True)
        with c2:
            g = p.groupby("linea").agg(oee=("oee_pct", "mean")).reset_index().sort_values("oee")
            fig = go.Figure(go.Bar(x=g["oee"], y=g["linea"], orientation="h",
                                   marker_color=[GOOD if x >= 80 else WARN if x >= 70 else BAD
                                                 for x in g["oee"]],
                                   text=[f"{x:.0f}%" for x in g["oee"]], textposition="outside"))
            fig.update_xaxes(range=[0, 100])
            st.plotly_chart(light(fig, 370, "OEE por línea"), use_container_width=True)

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            g = p.groupby("turno").agg(oee=("oee_pct", "mean"), merma=("merma_pct", "mean"),
                                       und=("unidades_producidas", "sum")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=g["turno"], y=g["oee"], name="OEE %", marker_color=AZUL_DEEP))
            fig.add_trace(go.Scatter(x=g["turno"], y=g["merma"], name="Merma %", yaxis="y2",
                                     mode="lines+markers", line=dict(color=ROJO, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="Merma %"))
            st.plotly_chart(light(fig, 320, "Desempeño por turno"), use_container_width=True)
        with c2:
            g = p.groupby("linea")["merma_pct"].mean().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                                   marker_color=[GOOD if x <= 2 else WARN if x <= 3 else BAD
                                                 for x in g.values],
                                   text=[f"{x:.2f}%" for x in g.values], textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.35])
            st.plotly_chart(light(fig, 320, "Merma por línea"), use_container_width=True)
        with c3:
            g = p.groupby("mes")["horas_paro"].sum()
            fig = go.Figure(go.Bar(x=g.index, y=g.values, marker_color=ORO))
            st.plotly_chart(light(fig, 320, "Horas de paro acumuladas por mes"),
                            use_container_width=True)

        peor_oee = p.groupby("linea")["oee_pct"].mean().idxmin()
        peor_turno = p.groupby("turno")["merma_pct"].mean().idxmax()
        horas = p["horas_paro"].sum()
        st.markdown(panel("Lectura de planta", f"""
        · La línea con menor OEE es <b>{peor_oee}</b>. Cada punto de OEE que se recupera es
          capacidad que no hay que comprar: sale más barato que una máquina nueva.<br>
        · La merma más alta está en el <b>{peor_turno}</b>. Cuando una merma se concentra en un
          turno y no en una línea, casi nunca es la máquina: es entrenamiento, relevo o
          supervisión.<br>
        · En el período se acumularon <b>{horas:,.0f} horas de paro</b>. Al ritmo de producción
          actual eso son cerca de <b>{int(horas * producidas / max(1, (p['horas_paro'].sum() + 1)) * 0.04):,}
          unidades</b> que no se hicieron.<br>
        · La planta procesó <b>{ton(toneladas)}</b> contra {CAPACIDAD_T} t de capacidad de
          almacenamiento: hay espacio, y ese espacio es justamente lo que permite tomar maquila
          de terceros sin frenar la marca propia.
        """, "🏭"), unsafe_allow_html=True)

    with t2:
        dem = v.groupby(["mes", "sku"])["unidades"].sum().rename("vendidas").reset_index()
        fab = p.groupby(["mes", "sku"])["unidades_producidas"].sum().rename("producidas").reset_index()
        comp = dem.merge(fab, on=["mes", "sku"], how="outer").fillna(0)
        comp = comp[(comp["mes"] >= rango[0]) & (comp["mes"] <= rango[1])]

        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            g = comp.groupby("mes")[["vendidas", "producidas"]].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=g["mes"], y=g["producidas"], name="Producido",
                                 marker_color=AZUL_DEEP))
            fig.add_trace(go.Scatter(x=g["mes"], y=g["vendidas"], name="Vendido",
                                     mode="lines+markers", line=dict(color=ROJO, width=3)))
            st.plotly_chart(light(fig, 370, "Lo que se fabricó frente a lo que se vendió"),
                            use_container_width=True)
        with c2:
            sk = comp.groupby("sku")[["vendidas", "producidas"]].sum()
            sk["brecha"] = sk["producidas"] - sk["vendidas"]
            sk = sk.reindex(sk["brecha"].abs().sort_values(ascending=False).index).head(12)
            sk = sk.sort_values("brecha")
            fig = go.Figure(go.Bar(x=sk["brecha"], y=sk.index, orientation="h",
                                   marker_color=[BAD if x < 0 else INFO for x in sk["brecha"]]))
            fig.update_xaxes(title="Producido − vendido (unidades)")
            st.plotly_chart(light(fig, 370, "Referencias más desalineadas"),
                            use_container_width=True)

        faltantes = sk[sk["brecha"] < 0]
        sobrantes = sk[sk["brecha"] > 0]
        st.markdown(panel("Por qué esta comparación importa", f"""
        Producir de más inmoviliza plata en bodega y arriesga vencimiento; producir de menos deja
        de vender y, peor, deja el espacio de góndola libre para la competencia.<br><br>
        En el período hay <b>{len(faltantes)} referencias</b> donde la venta le está ganando a la
        producción y <b>{len(sobrantes)}</b> donde sobra inventario fabricado. Con el ciclo de
        importación de proteína a más de 60 días, un faltante no se resuelve en una semana: se
        decide dos meses antes, cuando se pone la orden de compra.
        """, "⚖️"), unsafe_allow_html=True)

    with t3:
        d = p.sort_values("fecha", ascending=False).head(600)
        st.dataframe(pd.DataFrame({
            "Lote": d["lote_id"], "Fecha": d["fecha"].dt.strftime("%d/%m/%Y"),
            "Producto": d["producto"], "Línea": d["linea"], "Turno": d["turno"],
            "Planeado": d["unidades_plan"].map(lambda x: f"{x:,}"),
            "Producido": d["unidades_producidas"].map(lambda x: f"{x:,}"),
            "Merma %": d["merma_pct"], "OEE %": d["oee_pct"],
            "Paro (h)": d["horas_paro"],
            "Calidad": d["estado_calidad"],
            "Costo del lote": d["costo_lote_cop"].map(lambda x: cop(x, 1)),
        }), hide_index=True, use_container_width=True, height=520)
        st.caption("Los 600 lotes más recientes del período seleccionado. La trazabilidad por "
                   "lote es un requisito de FSSC 22000 y es lo que permite responder en minutos "
                   "cuando un cliente reporta un número de lote.")
