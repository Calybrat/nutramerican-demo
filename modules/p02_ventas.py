import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    v = datos.ventas()
    can = datos.canales()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Ventas Omnicanal",
        "Doce canales que reportan distinto y en momentos distintos: tiendas propias, "
        "nutramerican.com, distribuidores, cadenas y farmacias, gimnasios, maquila y seis mercados "
        "de exportación"), unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        rango = st.select_slider("Meses", options=meses, value=(meses[-12], meses[-1]),
                                 key="vt_rango")
    with f2:
        tipos = st.multiselect("Tipo de canal", sorted(v["tipo_canal"].unique()), key="vt_tipo")
    with f3:
        marcas = st.multiselect("Marca", sorted(v["marca"].unique()), key="vt_marca")
    with f4:
        cats = st.multiselect("Categoría", sorted(v["categoria"].unique()), key="vt_cat")

    vf = v[(v["mes"] >= rango[0]) & (v["mes"] <= rango[1])]
    if tipos:
        vf = vf[vf["tipo_canal"].isin(tipos)]
    if marcas:
        vf = vf[vf["marca"].isin(marcas)]
    if cats:
        vf = vf[vf["categoria"].isin(cats)]

    if vf.empty:
        st.warning("Ningún registro con esos filtros.")
        return

    ventas_tot = vf["venta_cop"].sum()
    unidades = int(vf["unidades"].sum())
    margen = vf["margen_cop"].sum() / ventas_tot * 100
    precio_medio = ventas_tot / unidades
    desc_medio = (vf["descuento_pct"] * vf["venta_cop"]).sum() / ventas_tot

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Facturación", cop(ventas_tot, 1), f"{rango[0]} a {rango[1]}", True, "💰"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Unidades", f"{unidades:,}", f"{unidades/max(1,len(set(vf['mes']))):,.0f} por mes",
                      True, "📦"), unsafe_allow_html=True)
    k[2].markdown(kpi("Margen bruto", pct(margen), "Sobre venta neta", margen >= 48, "📊"),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("Precio neto medio", cop_full(precio_medio), "Por unidad vendida", True, "🏷️",
                      "Lo que le queda a Nutramerican por unidad, ya descontado el margen del canal."),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Descuento medio", pct(desc_medio), "Promociones y cupón VIP",
                      desc_medio < 8, "🔻",
                      "Cada punto de descuento sale directo del margen."), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Por canal", "Por producto y marca",
                              "Por ciudad y país", "Detalle"])

    with t1:
        c1, c2 = st.columns([1.6, 1], gap="medium")
        with c1:
            piv = vf.groupby(["mes", "canal"])["venta_cop"].sum().reset_index()
            top_can = vf.groupby("canal")["venta_cop"].sum().nlargest(7).index.tolist()
            fig = go.Figure()
            for i, c in enumerate(top_can):
                sub = piv[piv["canal"] == c]
                fig.add_trace(go.Scatter(x=sub["mes"], y=sub["venta_cop"], name=c, mode="lines",
                                         line=dict(width=2.6, color=PALETTE[i % len(PALETTE)])))
            st.plotly_chart(light(fig, 360, "Evolución mensual de los 7 canales principales"),
                            use_container_width=True)
        with c2:
            g = vf.groupby("canal").agg(v=("venta_cop", "sum"), m=("margen_cop", "sum"))
            g["mg"] = g["m"] / g["v"] * 100
            g = g.sort_values("mg")
            fig = go.Figure(go.Bar(x=g["mg"], y=g.index, orientation="h",
                                   marker_color=[GOOD if x >= 50 else WARN if x >= 40 else BAD
                                                 for x in g["mg"]],
                                   text=[f"{x:.0f}%" for x in g["mg"]], textposition="outside"))
            fig.update_xaxes(range=[0, g["mg"].max() * 1.3])
            st.plotly_chart(light(fig, 360, "Margen bruto por canal"), use_container_width=True)

        resumen = vf.groupby(["canal", "tipo_canal"]).agg(
            Facturación=("venta_cop", "sum"), Unidades=("unidades", "sum"),
            Margen=("margen_cop", "sum")).reset_index()
        resumen["Margen %"] = (resumen["Margen"] / resumen["Facturación"] * 100).round(1)
        resumen["Precio neto medio"] = (resumen["Facturación"] / resumen["Unidades"])
        resumen["Mix %"] = (resumen["Facturación"] / resumen["Facturación"].sum() * 100).round(1)
        resumen = resumen.merge(can[["canal", "plazo_pago_dias"]], on="canal", how="left")
        resumen = resumen.sort_values("Facturación", ascending=False)
        st.dataframe(pd.DataFrame({
            "Canal": resumen["canal"], "Tipo": resumen["tipo_canal"],
            "Facturación": resumen["Facturación"].map(lambda x: cop(x, 1)),
            "Mix %": resumen["Mix %"], "Unidades": resumen["Unidades"].map(lambda x: f"{x:,}"),
            "Precio neto medio": resumen["Precio neto medio"].map(cop_full),
            "Margen %": resumen["Margen %"],
            "Plazo de pago": resumen["plazo_pago_dias"].map(
                lambda d: "Contado" if d == 0 else f"{int(d)} días"),
        }), hide_index=True, use_container_width=True)

        st.markdown(panel("Cómo leer esta tabla", """
        Un canal no se juzga solo por lo que factura. La tienda propia y la web facturan menos
        que los distribuidores, pero cobran de contado y dejan casi veinte puntos más de margen.
        Las cadenas y farmacias dan cobertura y marca, y pagan a 75 días: crecer ahí crece la
        venta y aprieta la caja al mismo tiempo. La maquila es el caso opuesto: margen bajo por
        definición, pero llena la planta y absorbe costo fijo.
        """, "💡"), unsafe_allow_html=True)

    with t2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            cat = vf.groupby(["mes", "categoria"])["venta_cop"].sum().reset_index()
            fig = go.Figure()
            for i, c in enumerate(sorted(vf["categoria"].unique())):
                sub = cat[cat["categoria"] == c]
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["venta_cop"], name=c,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 340, "Facturación por categoría del sitio"),
                            use_container_width=True)
        with c2:
            m = vf.groupby("marca")["venta_cop"].sum().sort_values(ascending=False)
            fig = go.Figure(go.Pie(labels=m.index, values=m.values, hole=0.55,
                                   marker_colors=PALETTE, texttemplate="%{percent:.0%}",
                                   hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in m.values]))
            st.plotly_chart(light(fig, 340, "Peso de cada marca propia"), use_container_width=True)

        top = vf.groupby(["producto", "marca", "categoria"]).agg(
            v=("venta_cop", "sum"), u=("unidades", "sum"), mg=("margen_cop", "sum")).reset_index()
        top["Margen %"] = (top["mg"] / top["v"] * 100).round(1)
        top = top.nlargest(20, "v")
        fig = go.Figure(go.Bar(x=top["v"][::-1], y=top["producto"][::-1], orientation="h",
                               marker_color=AZUL_DEEP,
                               hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in top["v"][::-1]]))
        st.plotly_chart(light(fig, 560, "Top 20 referencias por facturación"),
                        use_container_width=True)

    with t3:
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            co = vf[vf["pais"] == "Colombia"].groupby("ciudad")["venta_cop"].sum().nlargest(12).sort_values()
            fig = go.Figure(go.Bar(x=co.values, y=co.index, orientation="h", marker_color=AZUL_DEEP,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in co.values]))
            st.plotly_chart(light(fig, 400, "Colombia · facturación por ciudad"),
                            use_container_width=True)
        with c2:
            pa = vf.groupby("pais")["venta_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=pa.values, y=pa.index, orientation="h",
                                   marker_color=[ROJO if p == "Colombia" else ORO for p in pa.index],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in pa.values]))
            st.plotly_chart(light(fig, 400, "Facturación por país"), use_container_width=True)

        extranjero = vf[vf["pais"] != "Colombia"]["venta_cop"].sum() / ventas_tot * 100
        st.markdown(panel("Concentración geográfica", f"""
        Bogotá, Cali y Medellín concentran la mayor parte de la venta nacional, que es exactamente
        donde están las tiendas propias y donde MELONN entrega el mismo día. La exportación pesa
        hoy <b>{extranjero:.1f}%</b> del total: es el frente con más recorrido, pero también el
        que exige registro sanitario propio en cada país antes de poder facturar.
        """, "🌎"), unsafe_allow_html=True)

    with t4:
        det = vf.groupby(["mes", "canal", "producto"]).agg(
            Unidades=("unidades", "sum"), Facturación=("venta_cop", "sum"),
            Margen=("margen_cop", "sum")).reset_index()
        det["Margen %"] = (det["Margen"] / det["Facturación"] * 100).round(1)
        det = det.sort_values("Facturación", ascending=False).head(700)
        st.dataframe(pd.DataFrame({
            "Mes": det["mes"], "Canal": det["canal"], "Producto": det["producto"],
            "Unidades": det["Unidades"].map(lambda x: f"{x:,}"),
            "Facturación": det["Facturación"].map(lambda x: cop(x, 1)),
            "Margen %": det["Margen %"],
        }), hide_index=True, use_container_width=True, height=520)
        st.caption("Las 700 combinaciones de mes · canal · producto con mayor facturación.")
