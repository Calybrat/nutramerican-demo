import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.formatters import *
from utils import datos


def render():
    ens = datos.ensayos()
    nc = datos.no_conformidades()
    reg = datos.registros_invima()
    fv = datos.farmacovigilancia()
    prod = datos.produccion()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Calidad & Regulatorio",
        "FSSC 22000 desde el 28 de marzo de 2024 —una de las pocas plantas certificadas del "
        "país—, habilitación FDA y registro INVIMA por producto · lo que sostiene la promesa "
        "de «nutrición con respaldo»", adorno="fssc"), unsafe_allow_html=True)

    aprob = (prod["estado_calidad"] == "Aprobado").mean() * 100
    cuarentena = int((prod["estado_calidad"] == "Cuarentena").sum())
    rechazados = prod[prod["estado_calidad"] == "Rechazado"]
    costo_rech = int(rechazados["costo_lote_cop"].sum())
    nc_abiertas = nc[nc["estado"] == "Abierta"]
    nc_vencidas = nc[nc["vencida"]]
    reg_riesgo = reg[reg["estado"].isin(["Por vencer", "Vencido"])]
    cumple_prot = ens["cumple_proteina"].mean() * 100

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Liberación de lotes", pct(aprob), "Meta FSSC 22000: 97%", aprob >= 97,
                      "✅", "Lotes que pasaron sin cuarentena ni rechazo."), unsafe_allow_html=True)
    k[1].markdown(kpi("Proteína declarada", pct(cumple_prot),
                      "Lotes que cumplen el rótulo", cumple_prot >= 97, "🥛",
                      "Que el tarro tenga la proteína que dice la etiqueta. No es negociable."),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Lotes retenidos", f"{cuarentena + len(rechazados)}",
                      f"{cuarentena} en cuarentena · {len(rechazados)} rechazados",
                      cuarentena + len(rechazados) < 30, "🚫"), unsafe_allow_html=True)
    k[3].markdown(kpi("No conformidades abiertas", f"{len(nc_abiertas)}",
                      f"{len(nc_vencidas)} fuera del plazo de 30 días",
                      len(nc_vencidas) == 0, "📋",
                      "Una NC vencida es un hallazgo garantizado en la próxima auditoría."),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Registros en riesgo", f"{len(reg_riesgo)}",
                      "Vencidos o a menos de 12 meses", len(reg_riesgo) == 0, "⚖️",
                      "Sin registro sanitario vigente el producto no se puede vender."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Registros sanitarios INVIMA", "Ensayos de laboratorio",
                              "Sistema FSSC 22000", "Farmacovigilancia"])

    # ── Registros INVIMA ────────────────────────────────────────────────────
    with t1:
        st.markdown(panel("Por qué este es el módulo que más plata protege", """
        Un registro sanitario vencido no se nota en el P&G hasta que un distribuidor lo pide, una
        cadena lo audita o el INVIMA hace una visita. Ahí el producto sale de circulación y la
        renovación toma meses. Este tablero convierte un archivo de Excel que casi nadie abre en
        una alarma con fecha.
        """, "⚖️"), unsafe_allow_html=True)

        c1, c2 = st.columns([1, 1.6], gap="medium")
        with c1:
            est = reg["estado"].value_counts()
            fig = go.Figure(go.Pie(labels=est.index, values=est.values, hole=0.58,
                                   marker_colors=[estado_color(x) for x in est.index],
                                   texttemplate="%{value}"))
            st.plotly_chart(light(fig, 330, "Estado de los registros"), use_container_width=True)
        with c2:
            prox = reg.nsmallest(14, "dias_para_vencer").sort_values("dias_para_vencer",
                                                                     ascending=False)
            fig = go.Figure(go.Bar(
                x=prox["dias_para_vencer"], y=prox["producto"], orientation="h",
                marker_color=[estado_color(x) for x in prox["estado"]],
                hovertemplate="<b>%{y}</b><br>%{x} días<extra></extra>"))
            fig.add_vline(x=0, line_color=TINTA, line_width=1.5)
            fig.add_vline(x=365, line_dash="dot", line_color=WARN)
            fig.update_xaxes(title="Días para vencer (negativo = ya vencido)")
            st.plotly_chart(light(fig, 330, "Los 14 registros más próximos a vencer"),
                            use_container_width=True)

        c1, c2 = st.columns([1, 3])
        with c1:
            solo_riesgo = st.checkbox("Ver solo los que están en riesgo", value=True, key="cal_r")
        r = reg_riesgo if solo_riesgo else reg
        st.dataframe(pd.DataFrame({
            "Producto": r["producto"], "Marca": r["marca"], "Categoría": r["categoria"],
            "Registro INVIMA": r["registro_invima"], "Tipo": r["tipo"],
            "Expedido": r["fecha_expedicion"], "Vence": r["fecha_vencimiento"],
            "Días para vencer": r["dias_para_vencer"], "Estado": r["estado"],
            "Origen del dato": r["fuente"],
        }), hide_index=True, use_container_width=True, height=360)
        st.caption("Los registros de BiPro Classic (RSA-0007428-2019) y Crea Stack "
                   "(NSA-0015613-2024) son los números reales publicados por la compañía. "
                   "Los demás son simulados para la demostración.")

        if len(reg_riesgo):
            venta_riesgo = reg_riesgo["producto"].nunique()
            st.markdown(panel("Qué hacer con esto", f"""
            Hay <b>{len(reg_riesgo)} referencias</b> ({venta_riesgo} productos distintos) que en
            los próximos doce meses necesitan renovación. El trámite ante el INVIMA no es
            inmediato, así que la fecha que importa no es la de vencimiento: es la de radicación,
            varios meses antes. En el producto final esta lista dispara una alerta automática con
            seis meses de anticipación al responsable de Asuntos Regulatorios.
            """, "⏰", tono="alerta"), unsafe_allow_html=True)

    # ── Ensayos ─────────────────────────────────────────────────────────────
    with t2:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            e = ens.copy()
            e["desvio"] = (e["proteina_medida_g"] - e["proteina_declarada_g"]) / e["proteina_declarada_g"] * 100
            fig = go.Figure(go.Histogram(x=e["desvio"], nbinsx=50, marker_color=AZUL_DEEP))
            fig.add_vline(x=0, line_color=TINTA, line_width=1.6)
            fig.add_vline(x=-5, line_dash="dot", line_color=ROJO)
            fig.update_xaxes(title="Desviación de la proteína medida frente a la declarada (%)")
            f2 = light(fig, 350, "Distribución del cumplimiento de proteína")
            f2.update_layout(hovermode="closest")
            st.plotly_chart(f2, use_container_width=True)
        with c2:
            m = ens.groupby("metodo").size().sort_values()
            fig = go.Figure(go.Bar(x=m.values, y=m.index, orientation="h", marker_color=ORO,
                                   text=[f"{x:,}" for x in m.values], textposition="outside"))
            fig.update_xaxes(range=[0, m.max() * 1.28])
            st.plotly_chart(light(fig, 350, "Ensayos por método analítico"),
                            use_container_width=True)

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            g = ens.groupby("mes")["cumple_proteina"].mean() * 100
            fig = go.Figure(go.Scatter(x=g.index, y=g.values, mode="lines+markers",
                                       line=dict(color=AZUL_DEEP, width=3)))
            fig.add_hline(y=97, line_dash="dot", line_color=ROJO)
            fig.update_yaxes(range=[80, 102])
            st.plotly_chart(light(fig, 300, "Cumplimiento de proteína por mes (%)"),
                            use_container_width=True)
        with c2:
            fig = go.Figure(go.Box(y=ens["humedad_pct"], x=ens["linea"], marker_color=AZUL_LUM,
                                   boxpoints=False))
            f2 = light(fig, 300, "Humedad por línea (%)")
            f2.update_layout(hovermode="closest")
            st.plotly_chart(f2, use_container_width=True)
        with c3:
            g = ens.groupby("mes")["metales_pesados_ppm"].max()
            fig = go.Figure(go.Bar(x=g.index, y=g.values,
                                   marker_color=[BAD if x > 0.5 else GOOD for x in g.values]))
            fig.add_hline(y=0.5, line_dash="dot", line_color=ROJO)
            st.plotly_chart(light(fig, 300, "Metales pesados · máximo del mes (ppm)"),
                            use_container_width=True)

        fuera = ens[~ens["cumple_proteina"]]
        st.markdown(panel("Lectura de laboratorio", f"""
        · <b>{len(fuera)} ensayos</b> quedaron por debajo del 95% de la proteína declarada. Esos
          lotes no salen: es exactamente lo que debe pasar, y es el respaldo del claim de la
          marca.<br>
        · El analizador de infrarrojo cercano cubre <b>{(ens['metodo'].str.startswith('NIR')).mean()*100:.0f}%</b>
          de los ensayos. Es la inversión que permite medir cada lote en minutos en vez de mandar
          muestras afuera y esperar días.<br>
        · Cuando un desvío se repite en la misma línea y el mismo turno, deja de ser variabilidad
          y pasa a ser un problema de dosificación. Este panel lo hace visible antes de que se
          vuelva un lote rechazado.
        """, "🧪"), unsafe_allow_html=True)

    # ── FSSC 22000 ──────────────────────────────────────────────────────────
    with t3:
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            g = nc.groupby(["clausula", "estado"]).size().unstack(fill_value=0)
            g["total"] = g.sum(axis=1)
            g = g.sort_values("total")
            fig = go.Figure()
            if "Cerrada" in g.columns:
                fig.add_trace(go.Bar(x=g["Cerrada"], y=g.index, orientation="h",
                                     name="Cerrada", marker_color=GOOD))
            if "Abierta" in g.columns:
                fig.add_trace(go.Bar(x=g["Abierta"], y=g.index, orientation="h",
                                     name="Abierta", marker_color=ROJO))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 400, "No conformidades por cláusula del sistema"),
                            use_container_width=True)
        with c2:
            g = nc.groupby("origen").size().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=AZUL_DEEP,
                                   text=g.values, textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.3])
            st.plotly_chart(light(fig, 400, "Cómo se detectaron"), use_container_width=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            g = nc[nc["dias_cierre"].notna()].groupby("severidad")["dias_cierre"].mean().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h",
                                   marker_color=[GOOD if x <= 20 else WARN if x <= 35 else BAD
                                                 for x in g.values],
                                   text=[f"{x:.0f} días" for x in g.values], textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.4])
            st.plotly_chart(light(fig, 300, "Tiempo medio de cierre por severidad"),
                            use_container_width=True)
        with c2:
            g = nc.groupby("mes").size()
            fig = go.Figure(go.Bar(x=g.index, y=g.values, marker_color=ORO))
            st.plotly_chart(light(fig, 300, "No conformidades detectadas por mes"),
                            use_container_width=True)

        d = nc.sort_values(["estado", "fecha_deteccion"], ascending=[True, False])
        st.dataframe(pd.DataFrame({
            "NC": d["nc_id"], "Detectada": d["fecha_deteccion"], "Cláusula": d["clausula"],
            "Severidad": d["severidad"], "Origen": d["origen"], "Estado": d["estado"],
            "Días para cerrar": d["dias_cierre"].map(lambda x: f"{int(x)}" if pd.notna(x) else "—"),
            "Fuera de plazo": d["vencida"].map({True: "Sí", False: ""}),
        }), hide_index=True, use_container_width=True, height=330)

        criticas = nc_abiertas[nc_abiertas["severidad"] == "Alta"]
        st.markdown(panel("Lo que mira un auditor", f"""
        Un auditor de recertificación no revisa cuántas no conformidades hubo: revisa cuántas
        siguen abiertas y cuánto tardaron en cerrarse las anteriores. Hoy hay
        <b>{len(nc_abiertas)} abiertas</b>, de las cuales <b>{len(criticas)} son de severidad alta</b>,
        y <b>{len(nc_vencidas)} pasaron el plazo de 30 días</b>.
        {"Ese es el material con el que se pierde una certificación que tomó años conseguir." if len(nc_vencidas) else "El sistema está al día en plazos de cierre."}
        """, "📋", tono="alerta" if len(nc_vencidas) else "bien"), unsafe_allow_html=True)

    # ── Farmacovigilancia ───────────────────────────────────────────────────
    with t4:
        st.markdown(panel("Qué es y por qué se mide", """
        Algunos ingredientes producen efectos esperados —la beta-alanina da hormigueo, la cafeína
        puede quitar el sueño—. Otros reportes no son esperados y hay que analizarlos. Llevar el
        registro ordenado sirve para tres cosas: responder rápido a la persona, detectar si un
        lote concreto está detrás de varios reportes, y tener la evidencia lista si el INVIMA
        pregunta.
        """, "🩺"), unsafe_allow_html=True)

        k = st.columns(4, gap="small")
        k[0].markdown(kpi("Reportes recibidos", f"{len(fv)}", "Desde enero de 2025", True, "📨"),
                      unsafe_allow_html=True)
        k[1].markdown(kpi("Severidad moderada", f"{int((fv['severidad'] == 'Moderado').sum())}",
                          "Requieren análisis individual",
                          (fv["severidad"] == "Moderado").sum() < 30, "⚠️"), unsafe_allow_html=True)
        k[2].markdown(kpi("Tiempo medio de respuesta", f"{fv['dias_respuesta'].mean():.1f} días",
                          "Meta interna: 3 días", fv["dias_respuesta"].mean() <= 3, "⏱️"),
                      unsafe_allow_html=True)
        k[3].markdown(kpi("Casos en análisis", f"{int((fv['estado'] == 'En análisis').sum())}",
                          "Sin cerrar", (fv["estado"] == "En análisis").sum() < 20, "🔬"),
                      unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            g = fv.groupby(["evento", "severidad"]).size().unstack(fill_value=0)
            g["t"] = g.sum(axis=1)
            g = g.sort_values("t").drop(columns="t")
            fig = go.Figure()
            for sev, col in [("Leve", GOOD), ("Moderado", WARN)]:
                if sev in g.columns:
                    fig.add_trace(go.Bar(x=g[sev], y=g.index, orientation="h", name=sev,
                                         marker_color=col))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 360, "Eventos reportados por tipo y severidad"),
                            use_container_width=True)
        with c2:
            g = fv.groupby("canal_reporte").size().sort_values()
            fig = go.Figure(go.Bar(x=g.values, y=g.index, orientation="h", marker_color=AZUL_DEEP,
                                   text=g.values, textposition="outside"))
            fig.update_xaxes(range=[0, g.max() * 1.3])
            st.plotly_chart(light(fig, 360, "Por dónde llegan los reportes"),
                            use_container_width=True)

        d = fv.sort_values("fecha", ascending=False)
        st.dataframe(pd.DataFrame({
            "Reporte": d["reporte_id"], "Fecha": d["fecha"], "Evento": d["evento"],
            "Severidad": d["severidad"], "Producto": d["sku"], "Canal": d["canal_reporte"],
            "Días de respuesta": d["dias_respuesta"], "Estado": d["estado"],
        }).head(200), hide_index=True, use_container_width=True, height=320)
