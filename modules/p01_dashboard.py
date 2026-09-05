import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos

HOY = pd.Timestamp("2026-08-31")


def render():
    v = datos.ventas()
    fin = datos.finanzas()
    cli = datos.clientes()
    car = datos.cartera()
    inv = datos.inventario()
    prod = datos.produccion()
    reg = datos.registros_invima()
    desp = datos.despachos()
    pqr = datos.pqr()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Dashboard Ejecutivo",
        "Todo el negocio en una pantalla · planta Palmira, 8 tiendas propias, e-commerce, "
        "distribuidores, cadenas, maquila y exportación · corte al 31 de agosto de 2026"),
        unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    c1, c2, c3 = st.columns(3)
    with c1:
        periodo = st.selectbox("Período", ["Último mes", "Últimos 3 meses", "2026 (año corrido)",
                                           "Todo el histórico"], key="db_per")
    with c2:
        pais_sel = st.selectbox("País", ["Todos"] + sorted(v["pais"].unique()), key="db_pais")
    with c3:
        tipo_sel = st.selectbox("Tipo de canal", ["Todos"] + sorted(v["tipo_canal"].unique()),
                                key="db_tipo")

    if periodo == "Último mes":
        act, ant = [meses[-1]], [meses[-2]]
    elif periodo == "Últimos 3 meses":
        act, ant = meses[-3:], meses[-6:-3]
    elif periodo == "2026 (año corrido)":
        act = [m for m in meses if m.startswith("2026")]
        ant = [m for m in meses if m.startswith("2025")][:len(act)]
    else:
        act, ant = meses, []

    vf, vp = v[v["mes"].isin(act)], v[v["mes"].isin(ant)]
    if pais_sel != "Todos":
        vf, vp = vf[vf["pais"] == pais_sel], vp[vp["pais"] == pais_sel]
    if tipo_sel != "Todos":
        vf, vp = vf[vf["tipo_canal"] == tipo_sel], vp[vp["tipo_canal"] == tipo_sel]

    ventas_act, ventas_ant = vf["venta_cop"].sum(), vp["venta_cop"].sum()
    delta = (ventas_act - ventas_ant) / ventas_ant * 100 if ventas_ant else 0
    margen = vf["margen_cop"].sum() / ventas_act * 100 if ventas_act else 0
    unidades = int(vf["unidades"].sum())

    fin_act = fin[fin["mes"].isin(act)]
    ebitda_pct = (fin_act["ebitda_cop"].sum() / fin_act["ingresos_cop"].sum() * 100
                  if fin_act["ingresos_cop"].sum() else 0)

    # Salud operativa
    aprob = (prod[prod["mes"].isin(act)]["estado_calidad"] == "Aprobado").mean() * 100
    ent = desp[(desp["estado"] == "Entregado") & (desp["mes"].isin(act))]
    otif = ent["otif"].mean() * 100 if len(ent) else 0
    abierta = car[~car["pagada"]]
    vencida = abierta[abierta["dias_mora"] > 0]["valor_cop"].sum()
    pct_venc = vencida / abierta["valor_cop"].sum() * 100 if abierta["valor_cop"].sum() else 0
    recompra = cli["recurrente"].mean() * 100

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k = st.columns(4, gap="small")
    k[0].markdown(kpi("Facturación del período", cop(ventas_act, 1),
                      f"{'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs período anterior",
                      delta >= 0, "💰",
                      "Venta neta de la compañía en los doce canales."), unsafe_allow_html=True)
    k[1].markdown(kpi("Unidades vendidas", f"{unidades:,}",
                      "Escala declarada: +1.000.000 al año", unidades > 0, "📦",
                      "Cuántos productos salieron de la planta al mercado."), unsafe_allow_html=True)
    k[2].markdown(kpi("Margen bruto", pct(margen), "Referencia del sector: 48%", margen >= 48,
                      "📊", "Precio de venta menos costo de producto."), unsafe_allow_html=True)
    k[3].markdown(kpi("EBITDA", pct(ebitda_pct), "Después de mercadeo, logística, tiendas y nómina",
                      ebitda_pct >= 12, "🏦",
                      "Lo que realmente deja la operación cada mes."), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    k2 = st.columns(4, gap="small")
    k2[0].markdown(kpi("Liberación de lotes", pct(aprob), "Meta FSSC 22000: 97%", aprob >= 97,
                       "🧪", "Lotes aprobados por Calidad sin cuarentena ni rechazo."),
                   unsafe_allow_html=True)
    k2[1].markdown(kpi("OTIF de despachos", pct(otif), "Meta interna: 92%", otif >= 92, "🚚",
                       "Pedidos entregados completos y en la fecha prometida."),
                   unsafe_allow_html=True)
    k2[2].markdown(kpi("Cartera vencida", cop(vencida, 1),
                       f"{pct_venc:.1f}% de la cartera abierta", pct_venc < 25, "⏳",
                       "Plata ya facturada a terceros que debería estar cobrada."),
                   unsafe_allow_html=True)
    k2[3].markdown(kpi("Recompra canal propio", pct(recompra), "Clientes con 2+ compras",
                       recompra > 35, "🔁",
                       "En suplementación un tarro rinde ~30 días: quien no vuelve, se fue."),
                   unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    g1, g2 = st.columns([1.7, 1], gap="medium")
    with g1:
        piv = v.groupby(["mes", "tipo_canal"])["venta_cop"].sum().reset_index()
        orden = ["Tienda propia", "Mayorista", "E-commerce", "Retail",
                 "Maquila", "Especializado", "Internacional"]
        fig = go.Figure()
        for i, t in enumerate(orden):
            sub = piv[piv["tipo_canal"] == t]
            if len(sub):
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["venta_cop"], name=t,
                                     marker_color=PALETTE[i % len(PALETTE)]))
        fig.update_layout(barmode="stack")
        st.plotly_chart(light(fig, 340, "Facturación mensual por tipo de canal (COP)"),
                        use_container_width=True)
    with g2:
        mix = vf.groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        fig = go.Figure(go.Pie(labels=mix.index, values=mix.values, hole=0.58,
                               marker_colors=PALETTE, texttemplate="%{percent:.0%}",
                               hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in mix.values]))
        st.plotly_chart(light(fig, 340, "Mix de canales del período"), use_container_width=True)

    g3, g4, g5 = st.columns(3, gap="medium")
    with g3:
        top = vf.groupby("producto")["venta_cop"].sum().nlargest(8).sort_values()
        fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=AZUL_DEEP,
                               hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in top.values]))
        st.plotly_chart(light(fig, 310, "Top 8 referencias"), use_container_width=True)
    with g4:
        marca = vf.groupby("marca")["venta_cop"].sum().sort_values()
        fig = go.Figure(go.Bar(x=marca.values, y=marca.index, orientation="h", marker_color=ROJO,
                               hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in marca.values]))
        st.plotly_chart(light(fig, 310, "Facturación por marca propia"), use_container_width=True)
    with g5:
        _a = vf.groupby("tipo_canal")[["margen_cop", "venta_cop"]].sum()
        mg = (_a["margen_cop"] / _a["venta_cop"] * 100).sort_values()
        fig = go.Figure(go.Bar(x=mg.values, y=mg.index, orientation="h",
                               marker_color=[GOOD if x >= 50 else WARN for x in mg.values],
                               text=[f"{x:.0f}%" for x in mg.values], textposition="outside"))
        fig.update_xaxes(range=[0, max(mg.values) * 1.28 if len(mg) else 100])
        st.plotly_chart(light(fig, 310, "Margen bruto por tipo de canal"), use_container_width=True)

    # ── Lectura automática y alertas ──────────────────────────────────────────
    mejor_canal = vf.groupby("canal")["venta_cop"].sum().idxmax() if len(vf) else "—"
    peor_margen = mg.idxmin() if len(mg) else "—"
    criticos = inv[inv["estado"] == "Crítico"]
    lotes_alerta = prod[prod["estado_calidad"] != "Aprobado"]
    reg_vencer = reg[reg["estado"].isin(["Por vencer", "Vencido"])]
    pqr_abiertos = pqr[pqr["estado"].isin(["Abierto", "Escalado"])]
    d2c_share = (vf[vf["tipo_canal"].isin(["Tienda propia", "E-commerce"])]["venta_cop"].sum()
                 / ventas_act * 100 if ventas_act else 0)

    l1, l2 = st.columns(2, gap="medium")
    with l1:
        st.markdown(panel("Lectura del período", f"""
        · <b>{mejor_canal}</b> es el canal que más factura.<br>
        · El canal propio —tiendas más web— pesa <b>{d2c_share:.0f}%</b> de la venta y deja el
          mejor margen: no hay un tercero quedándose con parte del precio.<br>
        · El margen más bajo está en <b>{peor_margen}</b> ({mg.min():.0f}%): es el precio de
          ganar cobertura sin poner tiendas propias.<br>
        · La recompra del canal propio va en <b>{pct(recompra)}</b>. Cada punto que suba baja
          la dependencia de pauta pagada.
        """, "🔍"), unsafe_allow_html=True)
    with l2:
        st.markdown(panel("Qué necesita atención hoy", f"""
        · <b>{len(criticos)} referencias</b> con menos de 12 días de inventario en alguna bodega.<br>
        · <b>{len(lotes_alerta)} lotes</b> en cuarentena o rechazados por Calidad.<br>
        · <b>{len(reg_vencer)} registros INVIMA</b> vencidos o a menos de un año de vencer:
          sin registro vigente el producto no se puede comercializar.<br>
        · <b>{cop(vencida, 1)}</b> de cartera vencida y <b>{len(pqr_abiertos)} PQR</b> sin cerrar.
        """, "⚠️", tono="alerta"), unsafe_allow_html=True)

    with st.expander("Ver el detalle de las alertas", expanded=False):
        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown(f"<b style='color:{BAD}'>📦 Inventario crítico</b>", unsafe_allow_html=True)
            st.dataframe(criticos.nsmallest(8, "dias_cobertura")[
                ["producto", "bodega", "stock_unidades", "dias_cobertura"]],
                hide_index=True, use_container_width=True)
        with a2:
            st.markdown(f"<b style='color:{WARN}'>🧪 Lotes retenidos por Calidad</b>",
                        unsafe_allow_html=True)
            st.dataframe(lotes_alerta.sort_values("fecha", ascending=False)[
                ["lote_id", "producto", "linea", "estado_calidad"]].head(8),
                hide_index=True, use_container_width=True)
        with a3:
            st.markdown(f"<b style='color:{BAD}'>📋 Registros sanitarios en riesgo</b>",
                        unsafe_allow_html=True)
            st.dataframe(reg_vencer[["producto", "registro_invima", "dias_para_vencer", "estado"]].head(8),
                         hide_index=True, use_container_width=True)
