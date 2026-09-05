import streamlit as st
import pandas as pd

from utils.formatters import *
from utils import datos

HOY_STR = "31 de agosto de 2026"

STYLE = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ font-family:'Montserrat',Arial,sans-serif; background:#fff; color:{TINTA};
         font-size:13px; line-height:1.55 }}
  .pg {{ max-width:940px; margin:0 auto; padding:34px }}
  .hd {{ display:flex; align-items:center; gap:16px; padding-bottom:16px;
        border-bottom:3px solid {TINTA}; margin-bottom:6px }}
  .hd img {{ height:46px }}
  .hd .meta {{ margin-left:auto; text-align:right; font-size:11px; color:{MUTED} }}
  .hd .meta strong {{ color:{TINTA}; font-size:13px; display:block }}
  .flag {{ height:4px; margin-bottom:22px;
          background:linear-gradient(90deg,{ROJO} 0 34%,{AZUL} 34% 64%,{ORO} 64% 82%,transparent 82%) }}
  .ttl {{ font-size:19px; font-weight:900; color:{TINTA}; margin:0 0 18px;
         padding:12px 16px; background:{SURF2}; border-left:5px solid {ROJO}; border-radius:0 10px 10px 0 }}
  .kpis {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:22px }}
  .kpi {{ background:{SURF2}; border:1px solid {BORDER}; border-radius:12px; padding:14px }}
  .kpi .l {{ font-size:9.5px; text-transform:uppercase; letter-spacing:.08em; color:{MUTED}; font-weight:800 }}
  .kpi .v {{ font-size:21px; font-weight:900; color:{TINTA}; line-height:1.15; margin-top:4px }}
  .kpi .d {{ font-size:10.5px; margin-top:3px; font-weight:700 }}
  .ok {{ color:{GOOD} }} .bad {{ color:{BAD} }}
  h3 {{ font-size:12px; font-weight:900; color:{ROJO}; margin:20px 0 8px;
       text-transform:uppercase; letter-spacing:.07em }}
  table {{ width:100%; border-collapse:collapse; font-size:11.5px; margin-bottom:14px }}
  thead th {{ background:{TINTA}; color:#fff; padding:8px 10px; text-align:left;
             font-size:10.5px; font-weight:800 }}
  tbody td {{ padding:7px 10px; border-bottom:1px solid #EEF1F5 }}
  tbody tr:nth-child(even) td {{ background:{SURF2} }}
  .note {{ background:{ORO_LT}; border:1px solid #EEDCA6; border-radius:10px; padding:12px 14px;
          margin-bottom:16px; font-size:11.5px }}
  .alert {{ background:{ROJO_LT}; border:1px solid #F3C4C6; border-radius:10px; padding:12px 14px;
           margin-bottom:16px; font-size:11.5px }}
  .print {{ background:#EAF6EF; border:1px solid #BFE3CE; border-radius:10px; padding:10px 14px;
           margin-bottom:18px; font-size:11px; color:#1F6B45 }}
  .ft {{ margin-top:28px; padding-top:14px; border-top:1px solid #EEF1F5; display:flex;
        justify-content:space-between; font-size:10px; color:{DIM} }}
  @media print {{ .print {{ display:none }} .pg {{ padding:12px }} }}
</style>"""

FT = """<div class="ft"><span>Nutramerican Pharma · Documento interno · datos simulados de demostración</span>
<span>Generado automáticamente por Calybrat · 2026</span></div>"""


def _hd():
    logo = asset_b64("logo_nutramerican.jpg")
    img = f'<img src="{logo}" alt="Nutramerican Pharma">' if logo else '<b style="font-size:22px">NUTRAMERICAN</b>'
    return f"""<div class="hd">{img}
      <div class="meta"><strong>Panel de negocio</strong>Generado: {HOY_STR}<br>
      <span style="color:{ROJO}">Powered by Calybrat</span></div></div><div class="flag"></div>"""


def _kpi(l, v, d="", ok=True):
    dd = f'<div class="d {"ok" if ok else "bad"}">{d}</div>' if d else ""
    return f'<div class="kpi"><div class="l">{l}</div><div class="v">{v}</div>{dd}</div>'


def _tabla(filas, cols):
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in fila) + "</tr>" for fila in filas)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _doc(titulo, cuerpo):
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{titulo} — Nutramerican Pharma</title>{STYLE}</head><body><div class="pg">
<div class="print">💡 Para guardarlo en PDF: abre este archivo y presiona <b>Ctrl+P</b>
(o <b>Cmd+P</b>) → «Guardar como PDF».</div>
{_hd()}<div class="ttl">{titulo}</div>{cuerpo}{FT}</div></body></html>"""


# ── Reportes ─────────────────────────────────────────────────────────────────
def rpt_ejecutivo(v, fin, car, desp, prod):
    ult, prev = fin.iloc[-1], fin.iloc[-2]
    var = (ult["ingresos_cop"] - prev["ingresos_cop"]) / prev["ingresos_cop"] * 100
    abierta = car[~car["pagada"]]
    venc = abierta[abierta["dias_mora"] > 0]["valor_cop"].sum()
    ent = desp[(desp["estado"] == "Entregado") & (desp["mes"] == ult["mes"])]
    otif = ent["otif"].mean() * 100 if len(ent) else 0
    aprob = (prod[prod["mes"] == ult["mes"]]["estado_calidad"] == "Aprobado").mean() * 100
    vm = v[v["mes"] == ult["mes"]]

    canal = vm.groupby("canal").agg(ventas=("venta_cop", "sum"), und=("unidades", "sum"),
                                    margen=("margen_cop", "sum")).reset_index()
    canal["m"] = canal["margen"] / canal["ventas"] * 100
    canal = canal.sort_values("ventas", ascending=False)
    f_canal = [(r["canal"], cop(r["ventas"], 1), f"{r['ventas']/canal['ventas'].sum()*100:.1f}%",
                f"{int(r['und']):,}", f"{r['m']:.1f}%") for _, r in canal.iterrows()]

    marca = vm.groupby("marca")["venta_cop"].sum().sort_values(ascending=False)
    f_marca = [(m, cop(x, 1), f"{x/marca.sum()*100:.1f}%") for m, x in marca.items()]

    top = vm.groupby("producto")["venta_cop"].sum().nlargest(10)
    f_top = [(p, cop(x, 1)) for p, x in top.items()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Ingresos del mes", cop(ult['ingresos_cop'],1), f"{'▲' if var>=0 else '▼'} {abs(var):.1f}% vs mes anterior", var>=0)}
      {_kpi("Margen bruto", f"{ult['margen_bruto_pct']:.1f}%", "Referencia del sector 48%", ult['margen_bruto_pct']>=48)}
      {_kpi("EBITDA", f"{ult['ebitda_pct']:.1f}%", cop(ult['ebitda_cop'],1), ult['ebitda_pct']>=12)}
      {_kpi("Unidades vendidas", f"{int(vm['unidades'].sum()):,}", "En todos los canales")}
      {_kpi("OTIF", f"{otif:.1f}%", "Meta 92%", otif>=92)}
      {_kpi("Liberación de lotes", f"{aprob:.1f}%", "Meta FSSC 22000 97%", aprob>=97)}
    </div>
    <div class="note"><b>Lectura del mes:</b> el canal propio —tiendas y web— cobra de contado y
    deja el mejor margen; los distribuidores y las cadenas dan cobertura pero pagan a 45 y 75 días.
    Hoy hay {cop(venc,1)} de cartera vencida
    ({venc/max(1,abierta['valor_cop'].sum())*100:.0f}% de lo abierto).</div>
    <h3>Resultado por canal</h3>
    {_tabla(f_canal, ["Canal", "Facturación", "Mix", "Unidades", "Margen"])}
    <h3>Facturación por marca propia</h3>
    {_tabla(f_marca, ["Marca", "Facturación", "Participación"])}
    <h3>Top 10 referencias del mes</h3>
    {_tabla(f_top, ["Producto", "Facturación"])}"""
    return _doc("📊 Reporte ejecutivo mensual", cuerpo)


def rpt_regulatorio(reg, nc, ens, fv):
    riesgo = reg[reg["estado"].isin(["Por vencer", "Vencido"])].sort_values("dias_para_vencer")
    f_reg = [(r["producto"], r["registro_invima"], r["tipo"], r["fecha_vencimiento"],
              f"{int(r['dias_para_vencer'])} días", r["estado"])
             for _, r in riesgo.iterrows()]
    abiertas = nc[nc["estado"] == "Abierta"].sort_values("fecha_deteccion")
    f_nc = [(r["nc_id"], r["fecha_deteccion"], r["clausula"], r["severidad"], r["origen"],
             "Sí" if r["vencida"] else "") for _, r in abiertas.iterrows()]
    fuera = ens[~ens["cumple_proteina"]].sort_values("fecha", ascending=False).head(15)
    f_en = [(r["lote_id"], r["fecha"], r["producto"], f"{r['proteina_declarada_g']} g",
             f"{r['proteina_medida_g']} g", r["resultado"]) for _, r in fuera.iterrows()]
    fv_ab = fv[fv["estado"] == "En análisis"]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Registros vigentes", f"{int((reg['estado']=='Vigente').sum())} de {len(reg)}", "Sin riesgo a 12 meses", (reg['estado']=='Vigente').sum()==len(reg))}
      {_kpi("Registros en riesgo", f"{len(riesgo)}", "Vencidos o por vencer", len(riesgo)==0)}
      {_kpi("NC abiertas", f"{len(abiertas)}", f"{int(nc['vencida'].sum())} fuera de plazo", nc['vencida'].sum()==0)}
      {_kpi("Cumplimiento de proteína", f"{ens['cumple_proteina'].mean()*100:.1f}%", "Sobre el rótulo declarado", ens['cumple_proteina'].mean()>=0.97)}
      {_kpi("Ensayos fuera de norma", f"{int((~ens['cumple_proteina']).sum())}", "Lotes retenidos")}
      {_kpi("Farmacovigilancia", f"{len(fv_ab)}", "Casos en análisis", len(fv_ab)<10)}
    </div>
    <div class="alert"><b>Alerta regulatoria:</b> un registro sanitario vencido saca el producto
    del mercado hasta que se renueve, y la renovación ante el INVIMA no es inmediata. La fecha que
    hay que gestionar no es la de vencimiento sino la de radicación, varios meses antes.</div>
    <h3>Registros sanitarios que exigen gestión</h3>
    {_tabla(f_reg, ["Producto", "Registro INVIMA", "Tipo", "Vence", "Faltan", "Estado"]) if f_reg else "<p>Ningún registro en riesgo.</p>"}
    <h3>No conformidades abiertas del sistema FSSC 22000</h3>
    {_tabla(f_nc, ["NC", "Detectada", "Cláusula", "Severidad", "Origen", "Fuera de plazo"]) if f_nc else "<p>Sin no conformidades abiertas.</p>"}
    <h3>Últimos lotes fuera de especificación de proteína</h3>
    {_tabla(f_en, ["Lote", "Fecha", "Producto", "Declarada", "Medida", "Resultado"]) if f_en else "<p>Sin desviaciones.</p>"}
    <div class="note">Los registros de BiPro Classic (RSA-0007428-2019) y Crea Stack
    (NSA-0015613-2024) son los números reales publicados por la compañía. Los demás son simulados
    para esta demostración.</div>"""
    return _doc("⚖️ Reporte regulatorio y de calidad", cuerpo)


def rpt_tiendas(tm, td):
    meses = sorted(tm["mes"].unique())
    f = tm[tm["mes"] == meses[-1]]
    g = f.merge(td[["tienda_id", "direccion", "anio_apertura"]], on="tienda_id")
    g["conv"] = g["tickets"] / g["visitas"] * 100
    g = g.sort_values("venta_cop", ascending=False)
    filas = [(r["tienda"], r["ciudad"], f"{int(r['area_m2'])} m²",
              cop(r["venta_cop"], 1), cop(r["venta_m2_cop"], 1), f"{int(r['visitas']):,}",
              f"{r['conv']:.1f}%", cop_full(r["ticket_promedio_cop"]),
              cop(r["contribucion_cop"], 1)) for _, r in g.iterrows()]
    total = f["venta_cop"].sum()
    conv = f["tickets"].sum() / f["visitas"].sum() * 100

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Venta del mes", cop(total,1), f"{len(g)} tiendas propias")}
      {_kpi("Visitantes", f"{int(f['visitas'].sum()):,}", "Tráfico total del mes")}
      {_kpi("Conversión", f"{conv:.1f}%", "Meta retail especializado 25%", conv>=25)}
      {_kpi("Ticket promedio", cop_full(total/f['tickets'].sum()), f"{f['unidades'].sum()/f['tickets'].sum():.2f} und por compra")}
      {_kpi("Contribución", cop(f['contribucion_cop'].sum(),1), "Margen menos arriendo y nómina", f['contribucion_cop'].sum()>0)}
      {_kpi("Mejor venta por m²", g.nlargest(1,'venta_m2_cop').iloc[0]['ciudad'], cop(g['venta_m2_cop'].max(),1))}
    </div>
    <div class="note"><b>Cómo usar este reporte:</b> la tienda con menor contribución no siempre
    es la que hay que cerrar. Si convierte bien y le falta tráfico, la solución es de mercadeo
    local; si entra gente y no compra, es de surtido, exhibición o asesoría en el punto.</div>
    <h3>Comparativo del mes · {meses[-1]}</h3>
    {_tabla(filas, ["Tienda", "Ciudad", "Área", "Venta", "Venta/m²", "Visitantes",
                    "Conversión", "Ticket", "Contribución"])}"""
    return _doc("🏪 Reporte de tiendas propias", cuerpo)


def rpt_cartera(car):
    abierta = car[~car["pagada"]]
    total = abierta["valor_cop"].sum()
    orden = ["Al día", "Vencida 1-30", "Vencida 31-60", "Vencida 61-90", "Vencida +90"]
    b = abierta.groupby("estado")["valor_cop"].sum().reindex(orden).fillna(0)
    f_b = [(k, cop(x, 1), f"{x/total*100:.1f}%") for k, x in b.items()]

    cli = abierta.groupby(["cliente", "canal"]).agg(
        valor=("valor_cop", "sum"), fact=("factura_id", "count"),
        mora=("dias_mora", "max")).reset_index().sort_values("valor", ascending=False)
    f_c = [(r["cliente"], r["canal"], f"{int(r['fact'])}", cop(r["valor"], 1),
            f"{int(r['mora'])} días") for _, r in cli.iterrows()]

    crit = abierta[abierta["dias_mora"] > 60].sort_values("dias_mora", ascending=False).head(25)
    f_x = [(r["factura_id"], r["cliente"], r["fecha_vencimiento"].strftime("%d/%m/%Y"),
            f"{int(r['dias_mora'])} días", cop(r["valor_cop"], 1)) for _, r in crit.iterrows()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Cartera abierta", cop(total,1), f"{len(abierta):,} facturas")}
      {_kpi("Vencida", cop(total-b['Al día'],1), f"{(total-b['Al día'])/total*100:.0f}% del total", (total-b['Al día'])/total<0.25)}
      {_kpi("Más de 90 días", cop(b['Vencida +90'],1), "Requiere decisión de dirección", b['Vencida +90']==0)}
    </div>
    <div class="note"><b>Flujo de caja:</b> los distribuidores pagan a 45 días y las cadenas y
    farmacias a 75. Cada punto de mix que se mueve hacia esos canales crece la venta hoy y la caja
    dos meses y medio después. El canal propio cobra de contado.</div>
    <h3>Antigüedad de la cartera</h3>
    {_tabla(f_b, ["Franja", "Valor", "Participación"])}
    <h3>Saldo por cliente</h3>
    {_tabla(f_c, ["Cliente", "Canal", "Facturas", "Saldo", "Mora máxima"])}
    <h3>Facturas con más de 60 días de mora</h3>
    {_tabla(f_x, ["Factura", "Cliente", "Vencimiento", "Mora", "Valor"]) if f_x else "<p>Sin facturas críticas.</p>"}"""
    return _doc("⏳ Reporte de cartera y cobranza", cuerpo)


def rpt_abastecimiento(comp, prov, trm, fin):
    meses = sorted(comp["mes"].unique())
    c12 = comp[comp["mes"].isin(meses[-12:])]
    usd_total = c12["valor_usd"].sum()
    dif = c12["diferencia_en_cambio_cop"].sum()
    trm_hoy = trm.iloc[-1]["trm_cop_usd"]

    g = c12.groupby(["insumo", "origen", "moneda"]).agg(
        kg=("kg", "sum"), costo=("costo_cop", "sum"), usd=("valor_usd", "sum"),
        lead=("lead_time_real_dias", "mean"), punt=("a_tiempo", "mean")).reset_index()
    g = g.sort_values("costo", ascending=False)
    filas = [(r["insumo"], r["origen"], r["moneda"], f"{r['kg']/1000:,.1f} t",
              cop(r["costo"], 1), usd(r["usd"], 1) if r["usd"] else "—",
              f"{r['lead']:.0f} d", f"{r['punt']*100:.0f}%") for _, r in g.iterrows()]

    esc = [(f"{s:+d}%", f"{trm_hoy*(1+s/100):,.0f}", cop(usd_total * trm_hoy * s / 100, 1),
            f"{-usd_total*trm_hoy*s/100/fin[fin['mes'].isin(meses[-12:])]['ebitda_cop'].sum()*100:+.1f} pp")
           for s in (-10, -5, 5, 10, 15)]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Compras 12 meses", cop(c12['costo_cop'].sum(),1), f"{c12['kg'].sum()/1000:,.0f} toneladas")}
      {_kpi("Exposición en divisa", usd(usd_total,1), f"TRM actual {trm_hoy:,.0f}")}
      {_kpi("Diferencia en cambio", cop(dif,1), "Ganancia" if dif>=0 else "Pérdida", dif>=0)}
      {_kpi("Lead time medio", f"{c12['lead_time_real_dias'].mean():.0f} días", "Insumos importados")}
      {_kpi("Entregas a tiempo", f"{c12['a_tiempo'].mean()*100:.0f}%", "Meta 85%", c12['a_tiempo'].mean()>=0.85)}
      {_kpi("Proteína de suero", f"{c12[c12['insumo'].str.startswith('Proteína')]['kg'].sum()/1000/4:,.0f} t/trim", "Escala pública ~120 t")}
    </div>
    <div class="alert"><b>Riesgo de divisa:</b> la materia prima principal se compra en dólares y
    el producto se vende en pesos. Con lead times de hasta {c12['lead_time_real_dias'].max():.0f}
    días, la producción de dentro de dos meses ya está comprometida a la tasa de hoy.</div>
    <h3>Sensibilidad a la tasa de cambio</h3>
    {_tabla(esc, ["Variación TRM", "TRM resultante", "Impacto en costo anual", "Impacto en EBITDA"])}
    <h3>Compras por insumo · últimos 12 meses</h3>
    {_tabla(filas, ["Insumo", "Origen", "Moneda", "Volumen", "Costo COP", "Valor USD",
                    "Lead time", "A tiempo"])}"""
    return _doc("🌎 Reporte de abastecimiento y divisa", cuerpo)


def rpt_clientes(cli, mkt):
    inv = mkt[mkt["inversion_cop"] > 0]
    cac = inv["inversion_cop"].sum() / inv["clientes_nuevos"].sum()
    ltv = cli["ltv_cop"].mean()
    riesgo = cli[cli["en_riesgo_fuga"]]

    seg = cli.groupby("segmento").agg(
        n=("cliente_id", "count"), ltv=("ltv_cop", "mean"),
        rec=("recurrente", "mean")).reset_index().sort_values("n", ascending=False)
    f_seg = [(r["segmento"], f"{int(r['n']):,}", cop_full(r["ltv"]), f"{r['rec']*100:.1f}%")
             for _, r in seg.iterrows()]

    cap = cli.groupby("canal_captacion").agg(
        n=("cliente_id", "count"), ltv=("ltv_cop", "mean"),
        rec=("recurrente", "mean")).reset_index().sort_values("n", ascending=False)
    f_cap = [(r["canal_captacion"], f"{int(r['n']):,}", cop_full(r["ltv"]), f"{r['rec']*100:.1f}%")
             for _, r in cap.iterrows()]

    top = riesgo.nlargest(30, "ltv_cop")
    f_r = [(r["cliente_id"], r["ciudad"], r["segmento"], f"{int(r['pedidos'])}",
            r["ultima_compra"].strftime("%d/%m/%Y"), f"{int(r['dias_sin_comprar'])} días",
            cop_full(r["ltv_cop"]), "Sí" if r["suscrito_crm"] else "No")
           for _, r in top.iterrows()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Clientes identificados", f"{len(cli):,}", "Tienda propia y e-commerce")}
      {_kpi("Tasa de recompra", f"{cli['recurrente'].mean()*100:.1f}%", "Clientes con 2+ compras", cli['recurrente'].mean()>=0.35)}
      {_kpi("Ciclo de recompra", f"{cli[cli['recurrente']]['ciclo_recompra_dias'].mean():.0f} días", "Un tarro rinde ~30 días")}
      {_kpi("LTV promedio", cop_full(ltv), f"CAC {cop_full(cac)}")}
      {_kpi("Relación LTV/CAC", f"{ltv/cac:.1f}x", "Sano por encima de 3x", ltv/cac>=3)}
      {_kpi("Reactivables", f"{len(riesgo):,}", cop(riesgo['ltv_cop'].sum(),1) + " de valor", len(riesgo)/len(cli)<0.15)}
    </div>
    <div class="note"><b>La palanca más barata:</b> mover un cliente de una a dos compras cuesta
    mucho menos que traer uno nuevo por {cop_full(cac)}. Con un ciclo medio de
    {cli[cli['recurrente']]['ciclo_recompra_dias'].mean():.0f} días, un recordatorio automático
    por WhatsApp al día 25 es la acción con mejor retorno del canal propio.</div>
    <h3>Por objetivo declarado</h3>
    {_tabla(f_seg, ["Objetivo", "Clientes", "LTV promedio", "Recompra"])}
    <h3>Por canal de captación</h3>
    {_tabla(f_cap, ["Canal", "Clientes", "LTV promedio", "Recompra"])}
    <h3>Los 30 clientes reactivables de mayor valor · 60 a 180 días sin comprar</h3>
    {_tabla(f_r, ["Cliente", "Ciudad", "Objetivo", "Compras", "Última compra", "Sin volver",
                  "Valor histórico", "Contactable"])}"""
    return _doc("🔁 Reporte de clientes y recompra", cuerpo)


def render():
    v = datos.ventas()
    fin = datos.finanzas()
    car = datos.cartera()
    desp = datos.despachos()
    prod = datos.produccion()
    reg = datos.registros_invima()
    nc = datos.no_conformidades()
    ens = datos.ensayos()
    fv = datos.farmacovigilancia()
    tm = datos.tiendas_mensual()
    td = datos.tiendas()
    comp = datos.compras()
    prov = datos.proveedores()
    trm = datos.trm()
    cli = datos.clientes()
    mkt = datos.marketing()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Reportes Automáticos",
        "Los mismos documentos que hoy toman días de Excel, listos para descargar, imprimir "
        "en PDF y llevar a junta, al banco, a una cadena o a una auditoría"),
        unsafe_allow_html=True)

    st.markdown(panel("Cómo se usa", """
    Cada reporte se arma con los datos del momento en que lo descargas. Ábrelo en el navegador y
    presiona <b>Ctrl+P</b> (o <b>Cmd+P</b> en Mac) → <b>Guardar como PDF</b>. En el producto final
    estos mismos documentos se programan: llegan solos por correo el primer día hábil del mes,
    o el día que se dispara una alerta.
    """, "📄"), unsafe_allow_html=True)

    reportes = [
        ("📊 Reporte ejecutivo mensual",
         "Ingresos, margen, EBITDA, unidades, OTIF y liberación de lotes, con el resultado abierto "
         "por canal y por marca. Es el documento de junta directiva.",
         lambda: rpt_ejecutivo(v, fin, car, desp, prod), "nutramerican_reporte_ejecutivo.html"),
        ("⚖️ Reporte regulatorio y de calidad",
         "Vigencia de registros INVIMA, no conformidades abiertas del sistema FSSC 22000, "
         "desviaciones de proteína y farmacovigilancia. Es lo que se le entrega a un auditor.",
         lambda: rpt_regulatorio(reg, nc, ens, fv), "nutramerican_reporte_regulatorio.html"),
        ("🏪 Reporte de tiendas propias",
         "Venta, tráfico, conversión, ticket y contribución de las 8 tiendas. Para la reunión "
         "mensual con los administradores de punto.",
         lambda: rpt_tiendas(tm, td), "nutramerican_reporte_tiendas.html"),
        ("🌎 Reporte de abastecimiento y divisa",
         "Compras por insumo, lead times, cumplimiento de proveedores y sensibilidad del EBITDA "
         "a la TRM. Para compras y para la conversación con el banco sobre coberturas.",
         lambda: rpt_abastecimiento(comp, prov, trm, fin), "nutramerican_reporte_abastecimiento.html"),
        ("⏳ Reporte de cartera y cobranza",
         "Antigüedad, saldo por distribuidor y cadena, y facturas críticas. Para finanzas y para "
         "la reunión de cobro.",
         lambda: rpt_cartera(car), "nutramerican_reporte_cartera.html"),
        ("🔁 Reporte de clientes y recompra",
         "Segmentos, LTV, CAC y la lista de clientes en riesgo de fuga con su valor. Para "
         "mercadeo y para el equipo de CRM y WhatsApp.",
         lambda: rpt_clientes(cli, mkt), "nutramerican_reporte_clientes.html"),
    ]

    for i, (nombre, desc, generador, archivo) in enumerate(reportes):
        with st.expander(nombre, expanded=(i == 0)):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"<p style='color:{MUTED};font-size:13px;margin:2px 0 10px'>{desc}</p>",
                            unsafe_allow_html=True)
            html = generador()
            with c2:
                st.download_button("⬇️  Descargar", data=html.encode("utf-8"), file_name=archivo,
                                   mime="text/html", key=f"dl_{i}", use_container_width=True)
            st.caption(f"Archivo: {archivo} · se genera con los datos de hoy")
