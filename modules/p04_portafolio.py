import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    v = datos.ventas()
    prods = datos.productos()
    precios = datos.precios_canal()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Portafolio & Precios",
        "Las 52 referencias del catálogo, sus seis marcas propias y lo que realmente aporta cada "
        "una · qué proteger, qué impulsar y qué está costando más de lo que deja"),
        unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    ult12 = meses[-12:]
    vf = v[v["mes"].isin(ult12)]

    g = vf.groupby("sku").agg(venta=("venta_cop", "sum"), unidades=("unidades", "sum"),
                              margen=("margen_cop", "sum")).reset_index()
    g = prods.merge(g, on="sku", how="left").fillna({"venta": 0, "unidades": 0, "margen": 0})
    g["margen_pct"] = np.where(g["venta"] > 0, g["margen"] / g["venta"] * 100, 0)
    g["precio_neto_medio"] = np.where(g["unidades"] > 0, g["venta"] / g["unidades"], 0)

    activos = int((g["unidades"] > 0).sum())
    venta_total = g["venta"].sum()
    g_ord = g.sort_values("venta", ascending=False)
    g_ord["acum"] = g_ord["venta"].cumsum() / venta_total * 100
    n_80 = int((g_ord["acum"] <= 80).sum()) + 1
    margen_medio = g["margen"].sum() / venta_total * 100
    colas = g[(g["venta"] > 0) & (g["venta"] < venta_total * 0.005)]

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Referencias activas", f"{activos} de {len(g)}", "Con venta en 12 meses",
                      True, "💪"), unsafe_allow_html=True)
    k[1].markdown(kpi("Marcas propias", f"{g['marca'].nunique()}",
                      " · ".join(sorted(g["marca"].unique())[:3]) + "…", True, "🏷️"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Concentración", f"{n_80} SKU", "generan el 80% de la venta", n_80 >= 10,
                      "🎯", "Si son muy pocos, el negocio depende de que nunca se agoten."),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("Margen del portafolio", pct(margen_medio), "Promedio ponderado",
                      margen_medio >= 48, "📊"), unsafe_allow_html=True)
    k[4].markdown(kpi("Cola larga", f"{len(colas)} SKU", "Menos de 0,5% de la venta cada una",
                      len(colas) < 15, "🪫",
                      "Cada referencia ocupa registro sanitario, inventario y espacio en góndola."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Catálogo visual", "Qué aporta cada referencia",
                              "Arquitectura de precios por canal", "Promociones y descuentos"])

    # ── Catálogo visual con los renders oficiales ────────────────────────────
    with t1:
        c1, c2, c3 = st.columns([1.2, 1.2, 1.6])
        with c1:
            marca_sel = st.selectbox("Marca", ["Todas"] + sorted(g["marca"].unique()), key="pf_marca")
        with c2:
            cat_sel = st.selectbox("Categoría", ["Todas"] + sorted(g["categoria"].unique()),
                                   key="pf_cat")
        with c3:
            orden = st.radio("Ordenar por", ["Facturación", "Unidades", "Margen %", "Precio"],
                             horizontal=True, key="pf_ord")

        gv = g.copy()
        if marca_sel != "Todas":
            gv = gv[gv["marca"] == marca_sel]
        if cat_sel != "Todas":
            gv = gv[gv["categoria"] == cat_sel]
        col_orden = {"Facturación": "venta", "Unidades": "unidades",
                     "Margen %": "margen_pct", "Precio": "pvp_cop"}[orden]
        gv = gv.sort_values(col_orden, ascending=False)

        cols = st.columns(5, gap="small")
        for i, (_, r) in enumerate(gv.iterrows()):
            badge = ""
            if pd.notna(r["pvp_promo_cop"]):
                badge = f"-{r['descuento_web_pct']:.0f}%"
            elif r["fecha_lanzamiento"] >= "2026-01-01":
                badge = "NUEVO"
            precio = (f"<s style='color:{DIM}'>{cop_full(r['pvp_cop'])}</s> "
                      f"<b style='color:{ROJO}'>{cop_full(r['pvp_promo_cop'])}</b>"
                      if pd.notna(r["pvp_promo_cop"]) else
                      f"<b style='color:{TINTA};font-size:12.5px'>{cop_full(r['pvp_cop'])}</b>")
            cols[i % 5].markdown(tarjeta_producto(
                r["producto"], r["imagen"],
                [precio,
                 f"{r['marca']} · {r['presentacion']}",
                 f"{int(r['unidades']):,} und · {cop(r['venta'], 1)}",
                 f"Margen {r['margen_pct']:.0f}%"],
                badge), unsafe_allow_html=True)
            if i % 5 == 4:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        st.caption("Los renders, nombres y precios son los publicados en nutramerican.com. "
                   "Las unidades, la facturación y el margen son simulados.")

    # ── Aporte de cada referencia ────────────────────────────────────────────
    with t2:
        c1, c2 = st.columns([1.45, 1], gap="medium")
        with c1:
            top = g_ord.head(22).iloc[::-1]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=top["venta"], y=top["producto"], orientation="h",
                                 marker_color=[ROJO if m == "BiPro" else AZUL_DEEP if m == "Megaplex"
                                               else ORO if m == "Stacks" else MUTED
                                               for m in top["marca"]],
                                 hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                 customdata=[cop(x, 1) for x in top["venta"]],
                                 name="Facturación"))
            st.plotly_chart(light(fig, 560, "Top 22 · facturación de los últimos 12 meses"),
                            use_container_width=True)
        with c2:
            acum = g_ord.reset_index(drop=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(range(1, len(acum) + 1)), y=acum["acum"],
                                     mode="lines", line=dict(color=AZUL_DEEP, width=3),
                                     name="Facturación acumulada"))
            fig.add_hline(y=80, line_dash="dot", line_color=ROJO)
            fig.add_vline(x=n_80, line_dash="dot", line_color=ROJO)
            fig.update_xaxes(title="Referencias ordenadas de mayor a menor")
            fig.update_yaxes(title="% acumulado de la facturación", range=[0, 102])
            st.plotly_chart(light(fig, 270, "Curva de concentración del portafolio"),
                            use_container_width=True)

            fig = go.Figure(go.Scatter(
                x=g[g["unidades"] > 0]["unidades"], y=g[g["unidades"] > 0]["margen_pct"],
                mode="markers", text=g[g["unidades"] > 0]["producto"],
                marker=dict(size=10, color=g[g["unidades"] > 0]["venta"],
                            colorscale=[[0, "#CBD5E1"], [1, AZUL_DEEP]], showscale=False,
                            line=dict(color="white", width=1)),
                hovertemplate="<b>%{text}</b><br>%{x:,.0f} und · margen %{y:.0f}%<extra></extra>"))
            fig.update_xaxes(title="Unidades (12 meses)", type="log")
            fig.update_yaxes(title="Margen %")
            f2 = light(fig, 270, "Rotación contra margen")
            f2.update_layout(hovermode="closest")
            st.plotly_chart(f2, use_container_width=True)

        g["Estrategia"] = np.select(
            [(g["unidades"] >= g["unidades"].median()) & (g["margen_pct"] >= margen_medio),
             (g["unidades"] >= g["unidades"].median()) & (g["margen_pct"] < margen_medio),
             (g["unidades"] < g["unidades"].median()) & (g["margen_pct"] >= margen_medio)],
            ["Proteger — no puede agotarse", "Revisar precio o costo", "Impulsar con pauta"],
            default="Candidata a descontinuar")

        tabla = g.sort_values("venta", ascending=False)
        st.dataframe(pd.DataFrame({
            "Producto": tabla["producto"], "Marca": tabla["marca"],
            "Categoría": tabla["categoria"], "Presentación": tabla["presentacion"],
            "PVP web": tabla["pvp_cop"].map(cop_full),
            "Unidades 12m": tabla["unidades"].map(lambda x: f"{int(x):,}"),
            "Facturación": tabla["venta"].map(lambda x: cop(x, 1)),
            "Margen %": tabla["margen_pct"].round(1),
            "Qué hacer": tabla["Estrategia"],
        }), hide_index=True, use_container_width=True, height=420)

        proteger = g[g["Estrategia"] == "Proteger — no puede agotarse"]
        descont = g[g["Estrategia"] == "Candidata a descontinuar"]
        st.markdown(panel("La decisión de portafolio", f"""
        · <b>{len(proteger)} referencias</b> rotan por encima de la mediana y dejan más margen que
          el promedio. Son el motor: garantizar que nunca se agoten vale más que lanzar un sabor
          nuevo.<br>
        · <b>{len(descont)} referencias</b> rotan poco y dejan poco. Cada una consume un registro
          sanitario que hay que renovar, una corrida de planta, un espacio en bodega y un renglón
          en la lista de precios de cada distribuidor.<br>
        · La cola larga cuesta más de lo que se ve en el P&G: no aparece como gasto, aparece como
          complejidad.
        """, "🧭"), unsafe_allow_html=True)

    # ── Arquitectura de precios ──────────────────────────────────────────────
    with t3:
        st.markdown(panel("Por qué esto importa", """
        El mismo tarro no cuesta lo mismo en la tienda de Cali, en nutramerican.com, en una
        farmacia o en un gimnasio. Si la brecha se abre demasiado, el cliente que ve el precio
        en la web deja de comprar en la farmacia —y la farmacia deja de pedir—. Aquí se ve la
        brecha real de cada referencia, canal por canal.
        """, "🏷️"), unsafe_allow_html=True)

        sku_sel = st.selectbox("Referencia", g_ord["producto"].tolist(), key="pf_sku")
        row = g[g["producto"] == sku_sel].iloc[0]
        pc = precios[precios["sku"] == row["sku"]].sort_values("pvp_gondola_cop")

        c1, c2 = st.columns([1, 2.1], gap="medium")
        with c1:
            img = foto_producto(row["imagen"])
            if img:
                st.markdown(
                    f'<div style="background:{SURF};border:1px solid {BORDER};border-radius:14px;'
                    f'padding:20px;text-align:center">'
                    f'<img src="{img}" style="height:190px;width:auto;object-fit:contain">'
                    f'<p style="font-size:14px;font-weight:900;color:{TINTA};margin:12px 0 2px">'
                    f'{row["producto"]}</p>'
                    f'<p style="font-size:11.5px;color:{MUTED};margin:0">{row["marca"]} · '
                    f'{row["categoria"]}</p>'
                    f'<p style="font-size:11.5px;color:{MUTED};margin:2px 0 0">'
                    f'{row["presentacion"]} · costo unitario {cop_full(row["costo_unitario_cop"])}</p>'
                    f'</div>', unsafe_allow_html=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=pc["canal"], y=pc["precio_neto_cop"],
                                 name="Le queda a Nutramerican", marker_color=AZUL_DEEP))
            fig.add_trace(go.Bar(x=pc["canal"], y=pc["pvp_gondola_cop"] - pc["precio_neto_cop"],
                                 name="Se queda el canal", marker_color=ORO))
            fig.add_trace(go.Scatter(x=pc["canal"], y=[row["costo_unitario_cop"]] * len(pc),
                                     name="Costo de producir", mode="lines",
                                     line=dict(color=ROJO, width=2.4, dash="dot")))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 400, f"Precio al público por canal · {sku_sel}"),
                            use_container_width=True)

        brecha = (pc["pvp_gondola_cop"].max() - pc["pvp_gondola_cop"].min()) / pc["pvp_gondola_cop"].min() * 100
        st.dataframe(pd.DataFrame({
            "Canal": pc["canal"], "Tipo": pc["tipo_canal"], "País": pc["pais"],
            "Precio al público": pc["pvp_gondola_cop"].map(cop_full),
            "Le queda a Nutramerican": pc["precio_neto_cop"].map(cop_full),
            "Costo": pc["costo_unitario_cop"].map(cop_full),
            "Margen unitario": pc["margen_cop"].map(cop_full),
            "Margen %": pc["margen_pct"],
        }), hide_index=True, use_container_width=True)
        st.markdown(panel("Brecha de precio de esta referencia", f"""
        Entre el canal más barato y el más caro hay <b>{brecha:.0f}%</b> de diferencia para el
        mismo producto. Una brecha de hasta un 20–25% es normal y la explica el servicio de cada
        canal; por encima de eso el consumidor la nota, compara y termina comprando donde más
        barato esté —normalmente la web—, mientras el canal caro se queda con el inventario.
        """, "📐", tono="alerta" if brecha > 30 else "neutro"), unsafe_allow_html=True)

    # ── Promociones ──────────────────────────────────────────────────────────
    with t4:
        promo = g[g["pvp_promo_cop"].notna()].copy()
        # Agregación vectorizada en vez de groupby().apply(): el descuento del
        # mes es el promedio ponderado por facturación, no el promedio simple
        # de las líneas. Además evita `include_groups`, que cambia de
        # comportamiento entre pandas 2 y 3.
        vd = v[v["mes"].isin(ult12)].copy()
        vd["_desc_ponderado"] = vd["descuento_pct"] * vd["venta_cop"]
        _m = vd.groupby("mes")[["_desc_ponderado", "venta_cop", "margen_cop"]].sum()
        desc_mes = _m["_desc_ponderado"] / _m["venta_cop"]
        margen_mes = _m["margen_cop"] / _m["venta_cop"] * 100

        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=desc_mes.index, y=desc_mes.values, name="Descuento medio (%)",
                                 marker_color=ROJO))
            fig.add_trace(go.Scatter(x=margen_mes.index, y=margen_mes.values, name="Margen bruto (%)",
                                     mode="lines+markers", yaxis="y2",
                                     line=dict(color=AZUL_DEEP, width=3)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                          title="Margen %"))
            st.plotly_chart(light(fig, 360, "Descuento aplicado frente a margen obtenido"),
                            use_container_width=True)
        with c2:
            por_canal = vd[vd["descuento_pct"] > 0].groupby("canal")["venta_cop"].sum()
            total_canal = vd.groupby("canal")["venta_cop"].sum()
            share = (por_canal / total_canal * 100).dropna().sort_values()
            fig = go.Figure(go.Bar(x=share.values, y=share.index, orientation="h",
                                   marker_color=[BAD if x > 40 else WARN if x > 20 else GOOD
                                                 for x in share.values],
                                   text=[f"{x:.0f}%" for x in share.values], textposition="outside"))
            fig.update_xaxes(range=[0, max(share.values) * 1.3 if len(share) else 100])
            st.plotly_chart(light(fig, 360, "% de la venta hecha con descuento, por canal"),
                            use_container_width=True)

        if len(promo):
            st.markdown(f"<p style='font-size:13px;font-weight:900;color:{TINTA};margin:12px 0 8px'>"
                        f"Referencias con precio promocional vigente en el sitio</p>",
                        unsafe_allow_html=True)
            cols = st.columns(min(5, len(promo)), gap="small")
            for i, (_, r) in enumerate(promo.iterrows()):
                cols[i % len(cols)].markdown(tarjeta_producto(
                    r["producto"], r["imagen"],
                    [f"<s style='color:{DIM}'>{cop_full(r['pvp_cop'])}</s> "
                     f"<b style='color:{ROJO}'>{cop_full(r['pvp_promo_cop'])}</b>",
                     f"Deja de entrar {cop_full(r['pvp_cop'] - r['pvp_promo_cop'])} por unidad",
                     f"{int(r['unidades']):,} und en 12 meses"],
                    f"-{r['descuento_web_pct']:.0f}%"), unsafe_allow_html=True)

        cedido = (vd["precio_gondola_cop"] * vd["unidades"] * vd["descuento_pct"] / 100).sum()
        st.markdown(panel("Lo que cuesta la promoción", f"""
        En los últimos doce meses se cedieron cerca de <b>{cop(cedido, 1)}</b> en descuentos entre
        el cupón VIP del sitio, las promociones del catálogo y los descuentos de tienda.
        Eso no es malo por sí solo: el descuento compra volumen y compra prueba de producto nuevo.
        La pregunta que este panel permite responder es otra —<i>¿el mes con más descuento trajo
        más clientes nuevos, o solo le hizo rebaja a los que igual iban a comprar?</i>—
        cruzando esta pestaña con Clientes &amp; Recompra.
        """, "💸"), unsafe_allow_html=True)
