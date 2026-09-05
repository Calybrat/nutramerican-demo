import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

HOY = pd.Timestamp("2026-08-31")


def render():
    fin = datos.finanzas()
    car = datos.cartera()
    v = datos.ventas()
    inv = datos.inventario()
    emp = datos.empleados()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Finanzas & Cartera",
        "El estado de resultados mes a mes, dónde se queda la plata y quién la debe · "
        "corte al 31 de agosto de 2026"), unsafe_allow_html=True)

    ult, prev = fin.iloc[-1], fin.iloc[-2]
    ytd = fin[fin["mes"] >= "2026-01"]
    ytd_prev = fin[(fin["mes"] >= "2025-01") & (fin["mes"] <= "2025-08")]
    crec = (ytd["ingresos_cop"].sum() - ytd_prev["ingresos_cop"].sum()) / ytd_prev["ingresos_cop"].sum() * 100

    abierta = car[~car["pagada"]]
    vencida = abierta[abierta["dias_mora"] > 0]
    dso = (abierta["valor_cop"].sum() /
           (ytd["ingresos_cop"].sum() / (len(ytd) * 30))) if len(ytd) else 0
    valor_inv = inv["valor_inventario_cop"].sum()

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Ingresos 2026 (ene-ago)", cop(ytd["ingresos_cop"].sum(), 1),
                      f"{'▲' if crec >= 0 else '▼'} {abs(crec):.1f}% vs mismo período 2025",
                      crec >= 0, "💰"), unsafe_allow_html=True)
    k[1].markdown(kpi("Margen bruto", pct(ytd["margen_bruto_cop"].sum() / ytd["ingresos_cop"].sum() * 100),
                      "Acumulado del año", True, "📊"), unsafe_allow_html=True)
    k[2].markdown(kpi("EBITDA", cop(ytd["ebitda_cop"].sum(), 1),
                      pct(ytd["ebitda_cop"].sum() / ytd["ingresos_cop"].sum() * 100),
                      ytd["ebitda_cop"].sum() > 0, "🏦"), unsafe_allow_html=True)
    k[3].markdown(kpi("Cartera abierta", cop(abierta["valor_cop"].sum(), 1),
                      f"{cop(vencida['valor_cop'].sum(), 1)} vencida",
                      vencida["valor_cop"].sum() / max(1, abierta["valor_cop"].sum()) < 0.25, "⏳"),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Días de cartera (DSO)", f"{dso:.0f} días",
                      "Distribuidores a 45 · cadenas a 75", dso <= 55, "📅",
                      "Cuánto tarda en volver la plata que ya se facturó."), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Estado de resultados", "Dónde se va la plata",
                              "Cartera y cobranza", "Capital de trabajo"])

    with t1:
        c1, c2 = st.columns([1.65, 1], gap="medium")
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=fin["mes"], y=fin["ingresos_cop"], name="Ingresos",
                                 marker_color=AZUL_LT))
            fig.add_trace(go.Scatter(x=fin["mes"], y=fin["margen_bruto_cop"], name="Margen bruto",
                                     mode="lines", line=dict(color=AZUL_DEEP, width=3)))
            fig.add_trace(go.Scatter(x=fin["mes"], y=fin["ebitda_cop"], name="EBITDA",
                                     mode="lines", line=dict(color=ROJO, width=3)))
            st.plotly_chart(light(fig, 380, "Ingresos, margen bruto y EBITDA (COP)"),
                            use_container_width=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=fin["mes"], y=fin["margen_bruto_pct"], name="Margen bruto %",
                                     mode="lines+markers", line=dict(color=AZUL_DEEP, width=3)))
            fig.add_trace(go.Scatter(x=fin["mes"], y=fin["ebitda_pct"], name="EBITDA %",
                                     mode="lines+markers", line=dict(color=ROJO, width=3)))
            st.plotly_chart(light(fig, 380, "Márgenes en porcentaje"), use_container_width=True)

        pyg = fin.tail(6).copy()
        filas = [
            ("Ingresos", "ingresos_cop"), ("(−) Costo de ventas", "costo_ventas_cop"),
            ("= Margen bruto", "margen_bruto_cop"), ("(−) Marketing", "gasto_marketing_cop"),
            ("(−) Logística", "gasto_logistica_cop"), ("(−) Nómina", "gasto_nomina_cop"),
            ("(−) Tiendas", "gasto_tiendas_cop"), ("(−) Administración", "gasto_admin_cop"),
            ("= EBITDA", "ebitda_cop"), ("(−) Depreciación", "depreciacion_cop"),
            ("(−) Gasto financiero", "gasto_financiero_cop"),
            ("(±) Diferencia en cambio", "diferencia_en_cambio_cop"),
            ("= Utilidad antes de impuestos", "utilidad_antes_impuestos_cop"),
            ("= Utilidad neta", "utilidad_neta_cop"),
        ]
        tabla = {"Concepto": [f[0] for f in filas]}
        for _, r in pyg.iterrows():
            tabla[r["mes"]] = [cop(r[f[1]], 1) for f in filas]
        st.dataframe(pd.DataFrame(tabla), hide_index=True, use_container_width=True)
        st.caption("Estado de resultados de los últimos seis meses.")

    with t2:
        u = ult
        conceptos = [("Costo de ventas", u["costo_ventas_cop"], ROJO),
                     ("Nómina", u["gasto_nomina_cop"], AZUL_DEEP),
                     ("Logística", u["gasto_logistica_cop"], ORO),
                     ("Marketing", u["gasto_marketing_cop"], AZUL_LUM),
                     ("Tiendas", u["gasto_tiendas_cop"], MUTED),
                     ("Administración", u["gasto_admin_cop"], "#7C4DBE")]
        c1, c2 = st.columns([1.2, 1], gap="medium")
        with c1:
            fig = go.Figure(go.Waterfall(
                orientation="v",
                measure=["absolute"] + ["relative"] * len(conceptos) + ["total"],
                x=["Ingresos"] + [c[0] for c in conceptos] + ["EBITDA"],
                y=[u["ingresos_cop"]] + [-c[1] for c in conceptos] + [None],
                decreasing=dict(marker=dict(color=ROJO)),
                increasing=dict(marker=dict(color=AZUL_DEEP)),
                totals=dict(marker=dict(color=ORO)),
                connector=dict(line=dict(color=BORDER))))
            st.plotly_chart(light(fig, 400, f"De la venta al EBITDA · {u['mes']}"),
                            use_container_width=True)
        with c2:
            g = pd.DataFrame(conceptos, columns=["c", "v", "col"])
            g["pct"] = g["v"] / u["ingresos_cop"] * 100
            g = g.sort_values("pct")
            fig = go.Figure(go.Bar(x=g["pct"], y=g["c"], orientation="h",
                                   marker_color=list(g["col"]),
                                   text=[f"{x:.1f}%" for x in g["pct"]], textposition="outside"))
            fig.update_xaxes(range=[0, g["pct"].max() * 1.28],
                             title="% de los ingresos del mes")
            st.plotly_chart(light(fig, 400, "Peso de cada gasto sobre la venta"),
                            use_container_width=True)

        nomina_anual = emp["costo_total_cop"].sum() * 12
        st.markdown(panel("Estructura de costos de un fabricante", f"""
        · El costo de ventas se lleva <b>{u['costo_ventas_cop']/u['ingresos_cop']*100:.0f}%</b> de
          la venta. En un negocio donde la materia prima principal se importa en dólares, ese
          renglón se mueve por la TRM tanto como por la eficiencia de planta.<br>
        · La nómina son <b>{len(emp)} personas</b> y cerca de <b>{cop(nomina_anual, 1)}</b> al año
          con prestaciones. Es el costo más fijo del negocio y el que hace que llenar la planta
          con maquila valga la pena aunque deje menos margen por unidad.<br>
        · Marketing pesa <b>{u['gasto_marketing_cop']/u['ingresos_cop']*100:.1f}%</b>. Es la
          palanca más rápida de mover, y también la más fácil de recortar mal: bajarlo sube el
          EBITDA este mes y baja los clientes nuevos de los tres siguientes.
        """, "🔍"), unsafe_allow_html=True)

    with t3:
        c1, c2 = st.columns([1.3, 1], gap="medium")
        with c1:
            orden = ["Al día", "Vencida 1-30", "Vencida 31-60", "Vencida 61-90", "Vencida +90"]
            g = abierta.groupby("estado")["valor_cop"].sum().reindex(orden).fillna(0)
            fig = go.Figure(go.Bar(x=g.index, y=g.values,
                                   marker_color=[estado_color(x) for x in g.index],
                                   hovertemplate="%{x}<br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in g.values]))
            st.plotly_chart(light(fig, 360, "Aging de la cartera abierta"),
                            use_container_width=True)
        with c2:
            g = abierta.groupby("tipo_canal")["valor_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=AZUL_DEEP,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in g.values]))
            st.plotly_chart(light(fig, 360, "Cartera abierta por tipo de canal"),
                            use_container_width=True)

        g = abierta.groupby(["cliente", "canal"]).agg(
            total=("valor_cop", "sum"), facturas=("factura_id", "count"),
            venc=("dias_mora", "max")).reset_index()
        gv = abierta[abierta["dias_mora"] > 0].groupby("cliente")["valor_cop"].sum()
        g["vencido"] = g["cliente"].map(gv).fillna(0)
        g["% vencido"] = (g["vencido"] / g["total"] * 100).round(1)
        g = g.sort_values("total", ascending=False)
        st.dataframe(pd.DataFrame({
            "Cliente": g["cliente"], "Canal": g["canal"],
            "Cartera abierta": g["total"].map(lambda x: cop(x, 1)),
            "Facturas": g["facturas"],
            "Vencido": g["vencido"].map(lambda x: cop(x, 1)),
            "% vencido": g["% vencido"],
            "Mora máxima": g["venc"].map(lambda x: f"{int(x)} días"),
        }), hide_index=True, use_container_width=True, height=340)

        top_deudor = g.nlargest(1, "vencido").iloc[0]
        m90 = abierta[abierta["dias_mora"] > 90]["valor_cop"].sum()
        st.markdown(panel("Lo que aprieta la caja", f"""
        · <b>{cop(vencida['valor_cop'].sum(), 1)}</b> están vencidos, de los cuales
          <b>{cop(m90, 1)}</b> pasan de 90 días. Esa última franja es la que ya no se cobra sola:
          necesita decisión de dirección.<br>
        · <b>{top_deudor['cliente']}</b> concentra el mayor saldo vencido
          ({cop(top_deudor['vencido'], 1)}). Cuando un cliente grande se atrasa, la conversación
          no es de cobranza: es comercial.<br>
        · Las cadenas y farmacias pagan a 75 días. Cada peso adicional que se venda por ese canal
          crece la venta hoy y la caja dentro de dos meses y medio. Por eso el canal propio, que
          cobra de contado, no se mide solo por margen.
        """, "⏳", tono="alerta"), unsafe_allow_html=True)

    with t4:
        ing_diario = ytd["ingresos_cop"].sum() / (len(ytd) * 30)
        cogs_diario = ytd["costo_ventas_cop"].sum() / (len(ytd) * 30)
        dio = valor_inv / cogs_diario if cogs_diario else 0
        dpo = 45
        ciclo = dso + dio - dpo

        k = st.columns(4, gap="small")
        k[0].markdown(kpi("Días de cartera (DSO)", f"{dso:.0f}", "Lo que tardan en pagarnos",
                          dso <= 55, "📥"), unsafe_allow_html=True)
        k[1].markdown(kpi("Días de inventario (DIO)", f"{dio:.0f}",
                          f"{cop(valor_inv, 1)} en bodega", dio <= 60, "🏬"), unsafe_allow_html=True)
        k[2].markdown(kpi("Días de proveedores (DPO)", f"{dpo:.0f}",
                          "Lo que tardamos en pagar", True, "📤"), unsafe_allow_html=True)
        k[3].markdown(kpi("Ciclo de conversión de caja", f"{ciclo:.0f} días",
                          "DSO + DIO − DPO", ciclo <= 90, "🔄",
                          "Cuántos días pasa la plata fuera de la caja."), unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Días de inventario", "Días de cartera"], y=[dio, dso],
                             name="Plata inmovilizada", marker_color=ROJO))
        fig.add_trace(go.Bar(x=["Días de proveedores"], y=[dpo], name="Financiación de proveedores",
                             marker_color=GOOD))
        fig.add_trace(go.Bar(x=["Ciclo neto"], y=[ciclo], name="Ciclo de caja",
                             marker_color=AZUL_DEEP))
        st.plotly_chart(light(fig, 340, "Ciclo de conversión de caja (días)"),
                        use_container_width=True)

        capital = ing_diario * ciclo
        st.markdown(panel("Cuánta plata hay que tener parada para operar", f"""
        Con un ciclo de <b>{ciclo:.0f} días</b> y una venta de <b>{cop(ing_diario)}</b> diarios, el
        negocio necesita cerca de <b>{cop(capital, 1)}</b> de capital de trabajo permanente.
        Ese es el número que define cuánto se puede crecer sin pedir plata prestada.<br><br>
        Hay tres palancas, y este panel muestra las tres: acortar la cartera (cobranza y mezcla
        de canales), bajar el inventario en exceso —hoy hay
        <b>{cop(inv[inv['estado'] == 'Exceso']['valor_inventario_cop'].sum(), 1)}</b> de más—
        y negociar plazo con proveedores, que es difícil cuando la materia prima crítica se
        importa y muchas veces se paga contra embarque.
        """, "💧"), unsafe_allow_html=True)
