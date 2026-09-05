import streamlit as st
import pandas as pd

from utils.formatters import *
from utils import datos

CONTEXTO = """
Eres el Agente de Inteligencia de Negocio de Nutramerican Pharma, compañía colombiana de
nutrición deportiva con más de 26 años en el mercado, fundada por Richard Castiblanco y con
planta propia en Cantarrana, Palmira (Valle del Cauca).

Qué es la compañía:
  · Fabricante, no solo marca: planta de 2.500 m² con 1.000 toneladas de capacidad de
    almacenamiento, certificada FSSC 22000 desde el 28 de marzo de 2024 (una de las pocas
    plantas de alimentos certificadas del país), con habilitación FDA y registro INVIMA
    por producto. Todos los productos son libres de fructosa.
  · Marcas propias: BiPro (proteínas), Megaplex (creatina, hipercalóricos, carbohidratos),
    la línea Stacks (Crea Stack, Burner Stack, Collagen Stack, Gluta Stack, Prime W),
    la línea Nutra (Nutra Pops, Nutra Vegan, Nutra-C, Nutra Balance, Nutra Smart Baby),
    las bebidas Radical Power, Myth, Rescue y Energy X, y los alimentos Fitbar,
    Protein Cake y Protein Pancake.
  · 52 referencias en siete categorías: Módulos proteicos, Control de peso, Hipercalóricos,
    Energía y recuperación, Snacks proteicos, Nutrición general y Merch.
  · Escala: más de un millón de unidades al año, del orden de 80.000 unidades al mes en el
    mercado nacional, y cerca de 120 toneladas trimestrales de proteína de suero importada.
  · Comercializadora ELITENUT S.A.S. en Yumbo, bodega C-11 del terminal logístico.

Canales reales:
  · 8 tiendas propias: Bogotá Norte (Usaquén) y Bogotá Sur (Kennedy), Cali, Medellín,
    Barranquilla, Bucaramanga, Pereira y Cúcuta.
  · E-commerce nutramerican.com, con PSE, tarjeta, Nequi y financiación Addi y Sistecrédito.
  · Distribuidores y mayoristas, cadenas y farmacias (reconocidos como Proveedor Revelación
    en la feria de Farmatodo), gimnasios y wellness.
  · Maquila y marca propia para terceros, incluida producción de lácteos para Nestlé.
  · Exportación a Ecuador, México, Honduras y Panamá por distribuidor, más España y
    Estados Unidos (Nutramerican Pharma LLC) con operación propia.
  · Logística con MELONN en Bogotá y Medellín (mismo día o día siguiente), 1 a 3 días
    hábiles en ciudades principales y 2 a 3 en el resto del país.
  · Servicio al cliente por WhatsApp, línea gratuita #590, chat del sitio, redes y tienda.
  · Programa de embajadores Megaplex Stars con atletas de varias disciplinas.

Tensiones estructurales del negocio, que son las que importan al responder:
  1. La materia prima se compra en dólares y el producto se vende en pesos, con lead times
     de importación de más de 60 días.
  2. El canal propio deja mucho más margen y cobra de contado; los distribuidores y las
     cadenas dan cobertura pero pagan a 45 y 75 días.
  3. Cada registro sanitario INVIMA se vence y hay que renovarlo antes: sin registro, el
     producto no se puede vender.
  4. La certificación FSSC 22000 tomó años y se pierde con no conformidades sin cerrar.
  5. En suplementación un tarro rinde unos 30 días: la recompra es el pulso del negocio.

Responde SIEMPRE en español, de forma directa, breve y orientada a decisiones. Cuando des una
cifra, di qué significa para el negocio y qué habría que decidir. Nada de jerga innecesaria.
No inventes datos que no estén en el resumen que se te entrega.
"""

SUGERIDAS = [
    "¿Cómo vamos este mes?",
    "¿Qué canal me deja más margen?",
    "¿Cuánto me expone la TRM?",
    "¿Qué registros INVIMA se me vencen?",
    "¿Cómo van las tiendas propias?",
    "¿Cuánto me deben los distribuidores?",
    "¿Cómo está la recompra y el CAC?",
    "¿Cómo va la calidad en planta?",
    "¿Qué referencias debería impulsar?",
    "¿Cómo va la exportación?",
    "¿Qué se está agotando?",
    "¿De qué se quejan los clientes?",
]


def _resumen() -> str:
    """El mismo resumen que ve el modelo cuando hay API key: es lo que evita
    que el agente invente cifras."""
    try:
        v, fin = datos.ventas(), datos.finanzas()
        cli, car = datos.clientes(), datos.cartera()
        prod, comp = datos.produccion(), datos.compras()
        desp, inv = datos.despachos(), datos.inventario()
        reg, mkt = datos.registros_invima(), datos.marketing()
        pqr, tm = datos.pqr(), datos.tiendas_mensual()
        ult = fin.iloc[-1]
        abierta = car[~car["pagada"]]
        ent = desp[desp["estado"] == "Entregado"]
        mp = mkt[mkt["inversion_cop"] > 0]
        canal = v[v["mes"] == ult["mes"]].groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        pais = v.groupby("pais")["venta_cop"].sum().sort_values(ascending=False)
        c12 = comp[comp["mes"].isin(sorted(comp["mes"].unique())[-12:])]
        tmes = tm[tm["mes"] == sorted(tm["mes"].unique())[-1]]
        return f"""
=== DATOS DE NUTRAMERICAN PHARMA AL 31 DE AGOSTO DE 2026 ===
ÚLTIMO MES ({ult['mes']}): ingresos {cop(ult['ingresos_cop'],1)} · margen bruto {ult['margen_bruto_pct']:.1f}% · EBITDA {ult['ebitda_pct']:.1f}% ({cop(ult['ebitda_cop'],1)})
AÑO 2026 (ene-ago): {cop(v[v['mes'] >= '2026-01']['venta_cop'].sum(), 1)} · {int(v[v['mes'] >= '2026-01']['unidades'].sum()):,} unidades
CANALES DEL MES: {' · '.join(f'{k}: {cop(x,1)}' for k, x in canal.items())}
MARGEN POR TIPO DE CANAL: {' · '.join(f'{k}: {x:.0f}%' for k, x in (v.groupby('tipo_canal')['margen_cop'].sum()/v.groupby('tipo_canal')['venta_cop'].sum()*100).sort_values(ascending=False).items())}
TIENDAS PROPIAS ({ult['mes']}): venta {cop(tmes['venta_cop'].sum(),1)} · {int(tmes['visitas'].sum()):,} visitantes · conversión {tmes['tickets'].sum()/tmes['visitas'].sum()*100:.1f}% · ticket {cop_full(tmes['venta_cop'].sum()/tmes['tickets'].sum())} · mejor por m²: {tmes.nlargest(1,'venta_m2_cop').iloc[0]['ciudad']}
CANAL PROPIO: {len(cli):,} clientes · recompra {cli['recurrente'].mean()*100:.1f}% · ciclo {cli[cli['recurrente']]['ciclo_recompra_dias'].mean():.0f} días · LTV {cop_full(cli['ltv_cop'].mean())} · reactivables {int(cli['en_riesgo_fuga'].sum()):,} · perdidos {int(cli['perdido'].sum()):,}
MARKETING: ROAS {mp['ingresos_cop'].sum()/mp['inversion_cop'].sum():.1f}x · CAC {cop_full(mp['inversion_cop'].sum()/mp['clientes_nuevos'].sum())} · inversión 12m {cop(mp[mp['mes'].isin(sorted(mkt['mes'].unique())[-12:])]['inversion_cop'].sum(),1)}
PLANTA: liberación de lotes {(prod['estado_calidad']=='Aprobado').mean()*100:.1f}% · OEE {prod['oee_pct'].mean():.1f}% · merma {prod['merma_pct'].mean():.2f}% · {int((prod['estado_calidad']=='Cuarentena').sum())} lotes en cuarentena · {int((prod['estado_calidad']=='Rechazado').sum())} rechazados
REGULATORIO: {int((reg['estado']=='Vigente').sum())} registros INVIMA vigentes · {int((reg['estado']=='Por vencer').sum())} por vencer en menos de un año · {int((reg['estado']=='Vencido').sum())} vencidos
ABASTECIMIENTO 12m: {cop(c12['costo_cop'].sum(),1)} · {usd(c12['valor_usd'].sum(),1)} de exposición en divisa · diferencia en cambio {cop(c12['diferencia_en_cambio_cop'].sum(),1)} · entregas a tiempo {c12['a_tiempo'].mean()*100:.0f}% · lead time medio {c12['lead_time_real_dias'].mean():.0f} días
LOGÍSTICA: OTIF {ent['otif'].mean()*100:.1f}% · entrega media {ent['dias_reales'].mean():.1f} días · costo logístico {desp['costo_logistico_cop'].sum()/desp['valor_cop'].sum()*100:.1f}% de la venta
INVENTARIO: {cop(inv['valor_inventario_cop'].sum(),1)} · {int((inv['estado']=='Crítico').sum())} referencias críticas · {cop(inv[inv['estado']=='Exceso']['valor_inventario_cop'].sum(),1)} en exceso
CARTERA: abierta {cop(abierta['valor_cop'].sum(),1)} · vencida {cop(abierta[abierta['dias_mora']>0]['valor_cop'].sum(),1)} · más de 90 días {cop(abierta[abierta['dias_mora']>90]['valor_cop'].sum(),1)}
MERCADOS: {' · '.join(f'{k}: {cop(x,1)}' for k, x in pais.items())}
SERVICIO AL CLIENTE: {len(pqr):,} PQR · primera respuesta mediana {pqr['horas_primera_respuesta'].median():.1f} h · SLA 4h {pqr['cumple_sla_4h'].mean()*100:.0f}% · CSAT {pqr['csat'].mean():.2f}/5 · motivo principal: {pqr['motivo'].value_counts().index[0]}
TOP REFERENCIAS 2026: {' · '.join(f'{k}: {cop(x,1)}' for k, x in v[v['mes']>='2026-01'].groupby('producto')['venta_cop'].sum().nlargest(6).items())}
"""
    except Exception as ex:
        return f"[No se pudieron cargar los datos: {ex}]"


# ── Modo demo: respuestas calculadas sobre los datos reales del panel ────────
def responder_demo(pregunta: str) -> str:
    q = pregunta.lower()
    v, fin = datos.ventas(), datos.finanzas()
    ult, prev = fin.iloc[-1], fin.iloc[-2]

    if any(x in q for x in ["trm", "dólar", "dolar", "divisa", "cambio", "importa", "materia prima",
                            "proveedor", "abastec"]):
        comp = datos.compras()
        meses = sorted(comp["mes"].unique())
        c12 = comp[comp["mes"].isin(meses[-12:])]
        trm = datos.trm().iloc[-1]["trm_cop_usd"]
        usd_t = c12["valor_usd"].sum()
        dif = c12["diferencia_en_cambio_cop"].sum()
        ebitda12 = fin[fin["mes"].isin(meses[-12:])]["ebitda_cop"].sum()
        impacto10 = usd_t * trm * 0.10
        return (f"💱 En doce meses se compraron {usd(usd_t, 1)} en moneda extranjera, sobre todo "
                f"proteína de suero, creatina y premix de vitaminas.\n\n"
                f"• TRM actual de referencia: {trm:,.0f} COP por dólar\n"
                f"• Diferencia en cambio del período: {cop(dif, 1)}\n"
                f"• Si la TRM sube 10%: {cop(impacto10, 1)} más de costo, "
                f"equivalente a {impacto10/ebitda12*100:.1f} puntos del EBITDA anual\n"
                f"• Lead time medio de los insumos críticos: {c12['lead_time_real_dias'].mean():.0f} días\n\n"
                f"Lo importante no es la cifra sino el calendario: con más de dos meses de tránsito, "
                f"la producción de noviembre ya está comprometida a la tasa de hoy. Las tres salidas "
                f"son cubrir parte de la compra con forwards, adelantar compras cuando la tasa está "
                f"baja —lo que aprieta caja y bodega— o trasladar a precio, que tiene techo porque "
                f"la competencia también importa.")

    if any(x in q for x in ["invima", "registro", "regulator", "sanitario", "fssc", "certific",
                            "auditor"]):
        reg, nc = datos.registros_invima(), datos.no_conformidades()
        riesgo = reg[reg["estado"].isin(["Por vencer", "Vencido"])].sort_values("dias_para_vencer")
        abiertas = nc[nc["estado"] == "Abierta"]
        def _plazo(dias):
            return "VENCIDO" if dias < 0 else f"faltan {int(dias)} días"
        lineas = "\n".join(f"  • {r['producto']} — {r['registro_invima']} — "
                           f"{_plazo(r['dias_para_vencer'])}"
                           for _, r in riesgo.head(6).iterrows())
        return (f"⚖️ Situación regulatoria:\n\n"
                f"• {int((reg['estado'] == 'Vigente').sum())} registros vigentes de {len(reg)}\n"
                f"• {int((reg['estado'] == 'Por vencer').sum())} vencen en menos de un año · "
                f"{int((reg['estado'] == 'Vencido').sum())} ya están vencidos\n"
                f"• {len(abiertas)} no conformidades abiertas del sistema FSSC 22000, "
                f"{int(nc['vencida'].sum())} fuera del plazo de 30 días\n\n"
                f"Los más urgentes:\n{lineas}\n\n"
                f"Un registro vencido saca el producto del mercado hasta renovarlo, y el trámite "
                f"no es inmediato. La fecha que hay que gestionar no es la de vencimiento: es la "
                f"de radicación, varios meses antes. Y una no conformidad sin cerrar es lo primero "
                f"que mira un auditor de recertificación.")

    if any(x in q for x in ["tienda", "punto de venta", "local", "pdv", "tráfico", "trafico",
                            "conversión", "conversion"]):
        tm = datos.tiendas_mensual()
        mes = sorted(tm["mes"].unique())[-1]
        f = tm[tm["mes"] == mes]
        g = f.groupby("ciudad").agg(v=("venta_cop", "sum"), vi=("visitas", "sum"),
                                    t=("tickets", "sum"), m2=("venta_m2_cop", "sum"),
                                    c=("contribucion_cop", "sum"))
        g["conv"] = g["t"] / g["vi"] * 100
        lineas = "\n".join(f"  • {k}: {cop(r['v'], 1)} · conversión {r['conv']:.1f}% · "
                           f"contribución {cop(r['c'], 1)}"
                           for k, r in g.sort_values("v", ascending=False).iterrows())
        peor = g.nsmallest(1, "c")
        return (f"🏪 Las 8 tiendas en {mes}: {cop(f['venta_cop'].sum(), 1)} con "
                f"{int(f['visitas'].sum()):,} visitantes y "
                f"{f['tickets'].sum()/f['visitas'].sum()*100:.1f}% de conversión.\n\n{lineas}\n\n"
                f"La de menor contribución es {peor.index[0]} ({cop(peor['c'].iloc[0], 1)}). "
                f"Antes de tocar el arriendo hay que separar el diagnóstico: si convierte bien y "
                f"le falta gente, el problema es de mercadeo local; si entra gente y no compra, "
                f"es de surtido, exhibición o asesoría en el punto. Son dos decisiones distintas "
                f"y la tienda de al lado ya resolvió una de las dos.")

    if any(x in q for x in ["margen", "canal", "rentab", "utilidad", "mix"]):
        g = v.groupby("canal")[["venta_cop", "margen_cop"]].sum()
        g = pd.DataFrame({"ventas": g["venta_cop"],
                          "margen": g["margen_cop"] / g["venta_cop"] * 100}
                         ).sort_values("margen", ascending=False)
        lineas = "\n".join(f"  • {k}: {r['margen']:.0f}% de margen · {cop(r['ventas'], 1)}"
                           for k, r in g.iterrows())
        return (f"💰 Margen bruto por canal:\n\n{lineas}\n\n"
                f"Las tiendas propias y nutramerican.com encabezan porque no hay un tercero "
                f"quedándose con parte del precio, y además cobran de contado. Los distribuidores "
                f"y las cadenas dan cobertura nacional —que es lo que sostiene la marca— pero se "
                f"quedan con cerca de un tercio del precio de góndola y pagan a 45 y 75 días. "
                f"La maquila deja el margen más bajo por definición, y aun así vale la pena: "
                f"llena la planta y absorbe costo fijo que si no cargaría la marca propia.\n\n"
                f"La decisión no es abandonar ningún canal: es cuánta plata invertir en mover al "
                f"comprador que descubre la marca en la farmacia hacia la tienda propia o la web.")

    if any(x in q for x in ["deben", "cartera", "cobro", "cobranza", "caja", "pago", "dso",
                            "capital de trabajo"]):
        car = datos.cartera()
        abierta = car[~car["pagada"]]
        venc = abierta[abierta["dias_mora"] > 0]
        top = abierta.groupby("cliente")["valor_cop"].sum().sort_values(ascending=False)
        lineas = "\n".join(f"  • {k}: {cop(x, 1)}" for k, x in top.head(6).items())
        return (f"⏳ Cartera abierta: {cop(abierta['valor_cop'].sum(), 1)} en "
                f"{len(abierta):,} facturas.\n\n"
                f"• Vencida: {cop(venc['valor_cop'].sum(), 1)} "
                f"({venc['valor_cop'].sum()/abierta['valor_cop'].sum()*100:.0f}% de lo abierto)\n"
                f"• Con más de 90 días: {cop(abierta[abierta['dias_mora'] > 90]['valor_cop'].sum(), 1)}\n\n"
                f"Quién debe más:\n{lineas}\n\n"
                f"Los distribuidores pagan a 45 días y las cadenas y farmacias a 75. Mientras esos "
                f"canales crezcan, la utilidad se ve bien y la caja se aprieta: es el mismo peso "
                f"contado dos meses y medio después. Por eso cada punto de mix que se mueve al "
                f"canal propio mejora margen y flujo al mismo tiempo.")

    if any(x in q for x in ["recompra", "cac", "cliente", "ltv", "fuga", "retención", "retencion",
                            "fidel"]):
        cli, mkt = datos.clientes(), datos.marketing()
        mp = mkt[mkt["inversion_cop"] > 0]
        cac = mp["inversion_cop"].sum() / mp["clientes_nuevos"].sum()
        riesgo = cli[cli["en_riesgo_fuga"]]
        una = int((cli["pedidos"] == 1).sum())
        return (f"🔁 Canal propio: {len(cli):,} clientes identificados.\n\n"
                f"• Recompra: {cli['recurrente'].mean()*100:.1f}% (clientes con 2 o más compras)\n"
                f"• Ciclo medio de recompra: {cli[cli['recurrente']]['ciclo_recompra_dias'].mean():.0f} días\n"
                f"• LTV promedio: {cop_full(cli['ltv_cop'].mean())} · CAC {cop_full(cac)} → "
                f"relación {cli['ltv_cop'].mean()/cac:.1f}x\n"
                f"• Compraron una sola vez: {una:,} ({una/len(cli)*100:.0f}%)\n"
                f"• Reactivables (60 a 180 días sin volver): {len(riesgo):,} clientes con "
                f"{cop(riesgo['ltv_cop'].sum(), 1)} de valor histórico\n\n"
                f"Un tarro de 2 lb rinde unos 30 días. Eso hace que la retención sea casi un "
                f"problema de calendario: quien pasa de 45 días sin volver, casi siempre ya compró "
                f"en otra parte. La palanca más barata hoy no es traer gente nueva a "
                f"{cop_full(cac)} cada uno, es escribirle por WhatsApp al día 25 a los "
                f"{len(riesgo):,} que ya conocen el producto.")

    if any(x in q for x in ["calidad", "lote", "planta", "producción", "produccion", "oee",
                            "merma", "cuarentena"]):
        prod, ens = datos.produccion(), datos.ensayos()
        rech = prod[prod["estado_calidad"] == "Rechazado"]
        peor_linea = prod.groupby("linea")["oee_pct"].mean().idxmin()
        return (f"🧪 Planta de Palmira, últimos meses:\n\n"
                f"• Liberación de lotes: {(prod['estado_calidad']=='Aprobado').mean()*100:.1f}% "
                f"(meta FSSC 22000: 97%)\n"
                f"• En cuarentena: {int((prod['estado_calidad']=='Cuarentena').sum())} · "
                f"rechazados: {len(rech)} por {cop(rech['costo_lote_cop'].sum(), 1)}\n"
                f"• OEE promedio: {prod['oee_pct'].mean():.1f}% · merma {prod['merma_pct'].mean():.2f}%\n"
                f"• Cumplimiento de proteína declarada: {ens['cumple_proteina'].mean()*100:.1f}%\n"
                f"• Línea con menor OEE: {peor_linea}\n\n"
                f"El dato que más pesa es el de proteína: que cada tarro tenga lo que dice la "
                f"etiqueta es lo que sostiene el «nutrición con respaldo», y los lotes que no "
                f"cumplen se están reteniendo, que es exactamente lo que debe pasar. En OEE, cada "
                f"punto que se recupera en {peor_linea} es capacidad que no hay que comprar: "
                f"sale más barato que una máquina nueva.")

    if any(x in q for x in ["agot", "quiebre", "stock", "inventario", "bodega", "reposición",
                            "reposicion"]):
        inv = datos.inventario()
        crit = inv[inv["estado"] == "Crítico"].nsmallest(6, "dias_cobertura")
        exc = inv[inv["estado"] == "Exceso"]
        lineas = "\n".join(f"  • {r['producto']} en {r['bodega']}: "
                           f"{r['dias_cobertura']:.0f} días de cobertura"
                           for _, r in crit.iterrows())
        return (f"📦 Inventario: {cop(inv['valor_inventario_cop'].sum(), 1)} en cinco ubicaciones "
                f"(planta Palmira, CD Yumbo, MELONN Bogotá y Medellín, y las 8 tiendas).\n\n"
                f"Lo que se está agotando:\n{lineas}\n\n"
                f"• {int((inv['estado'] == 'Crítico').sum())} referencias con menos de 12 días\n"
                f"• {cop(exc['valor_inventario_cop'].sum(), 1)} en exceso "
                f"({len(exc)} referencias con más de 60 días)\n"
                f"• {int(inv['proximo_a_vencer'].sum())} lotes llevan más de 300 días en bodega\n\n"
                f"Que falte y sobre al mismo tiempo no es contradictorio: pasa cuando la reposición "
                f"se decide por bodega y no por referencia. Y con importación a más de 60 días, un "
                f"faltante de proteína no se arregla en la semana: se decidió dos meses atrás.")

    if any(x in q for x in ["export", "internacional", "país", "pais", "ecuador", "méxico",
                            "mexico", "españa", "espana", "estados unidos", "usa", "expansión",
                            "expansion"]):
        g = v.groupby("pais")[["venta_cop", "margen_cop"]].sum()
        g = pd.DataFrame({"ventas": g["venta_cop"],
                          "margen": g["margen_cop"] / g["venta_cop"] * 100}
                         ).sort_values("ventas", ascending=False)
        intl = g.drop("Colombia", errors="ignore")
        lineas = "\n".join(f"  • {k}: {cop(r['ventas'], 1)} · margen {r['margen']:.0f}%"
                           for k, r in intl.iterrows())
        return (f"🌎 La exportación pesa "
                f"{intl['ventas'].sum()/g['ventas'].sum()*100:.1f}% de la venta total.\n\n{lineas}\n\n"
                f"Ecuador y Honduras son los mercados maduros y van por distribuidor. México es el "
                f"más grande y el más competido. Panamá abrió este año como hub de Centroamérica. "
                f"España y Estados Unidos son operación propia y por eso dejan más margen por "
                f"unidad, aunque el costo de traer al cliente allá es otra historia.\n\n"
                f"El cuello de botella de la expansión no es comercial, es regulatorio: cada "
                f"referencia necesita su propio registro sanitario en cada país. Decidir el "
                f"portafolio de exportación es decidir qué referencias justifican pagar ese trámite.")

    if any(x in q for x in ["producto", "impuls", "sku", "portafolio", "referencia", "marca",
                            "bipro", "megaplex", "descontinuar"]):
        v26 = v[v["mes"] >= "2026-01"]
        g = v26.groupby("producto").agg(ventas=("venta_cop", "sum"), und=("unidades", "sum"),
                                        margen=("margen_cop", "sum"))
        g["m"] = g["margen"] / g["ventas"] * 100
        top = g.nlargest(6, "ventas")
        lineas = "\n".join(f"  • {k}: {cop(r['ventas'], 1)} · {int(r['und']):,} und · "
                           f"margen {r['m']:.0f}%" for k, r in top.iterrows())
        floja = g.nsmallest(4, "ventas")
        marca = v26.groupby("marca")["venta_cop"].sum().sort_values(ascending=False)
        acum = g.sort_values("ventas", ascending=False)["ventas"].cumsum() / g["ventas"].sum()
        n80 = int((acum <= 0.8).sum()) + 1
        return (f"💪 Las que más facturan en 2026:\n\n{lineas}\n\n"
                f"Por marca: {' · '.join(f'{k} {x/marca.sum()*100:.0f}%' for k, x in marca.items())}\n\n"
                f"Con 52 referencias, {n80} generan el 80% de la venta. Las de menor tracción son "
                f"{', '.join(floja.index)}.\n\n"
                f"La pregunta de portafolio no es qué lanzar sino qué proteger: garantizar que las "
                f"de arriba nunca se agoten vale más que un sabor nuevo. Y cada referencia de la "
                f"cola larga cuesta un registro sanitario que hay que renovar, una corrida de "
                f"planta y un renglón en la lista de precios de cada distribuidor. Ese costo no "
                f"aparece en el P&G: aparece como complejidad.")

    if any(x in q for x in ["queja", "reclamo", "pqr", "servicio", "cliente insatisf", "csat",
                            "whatsapp"]):
        pqr, desp = datos.pqr(), datos.despachos()
        top = pqr["motivo"].value_counts().head(5)
        lineas = "\n".join(f"  • {k}: {x:,} casos ({x/len(pqr)*100:.0f}%)" for k, x in top.items())
        auto = (~pqr["requiere_agente_humano"]).mean() * 100
        return (f"🎧 {len(pqr):,} PQR registrados. Primera respuesta mediana de "
                f"{pqr['horas_primera_respuesta'].median():.1f} horas y "
                f"{pqr['cumple_sla_4h'].mean()*100:.0f}% dentro de las 4 horas. "
                f"Satisfacción {pqr['csat'].mean():.2f} sobre 5.\n\n"
                f"De qué se quejan:\n{lineas}\n\n"
                f"Los reclamos de entrega no se arreglan en servicio al cliente sino en logística: "
                f"el OTIF va en {desp[desp['estado']=='Entregado']['otif'].mean()*100:.1f}% y cada "
                f"punto que sube quita reclamos de raíz.\n\n"
                f"Y hay un dato que vale plata: {auto:.0f}% de los casos no necesitan una persona "
                f"—estado del envío, dudas de uso, solicitud de factura—. Son exactamente los que "
                f"un agente conectado a los datos responde en segundos a cualquier hora, dejando "
                f"al equipo para los faltantes, las garantías y los eventos adversos.")

    if any(x in q for x in ["marketing", "pauta", "roas", "meta ads", "embajador", "megaplex stars",
                            "influencer", "evento", "feria"]):
        mkt, emb = datos.marketing(), datos.embajadores()
        mp = mkt[mkt["inversion_cop"] > 0]
        g = mp.groupby("canal").agg(i=("inversion_cop", "sum"), r=("ingresos_cop", "sum"))
        g["roas"] = g["r"] / g["i"]
        lineas = "\n".join(f"  • {k}: {r['roas']:.1f}x con {cop(r['i'], 1)} invertidos"
                           for k, r in g.sort_values("roas", ascending=False).iterrows())
        chicos = emb[emb["seguidores"] < emb["seguidores"].median()]
        roi_ch = chicos["venta_atribuida_cop"].sum() / chicos["costo_mensual_cop"].sum()
        grandes = emb[emb["seguidores"] >= emb["seguidores"].median()]
        roi_gr = grandes["venta_atribuida_cop"].sum() / grandes["costo_mensual_cop"].sum()
        return (f"⭐ Retorno de la inversión de mercadeo:\n\n{lineas}\n\n"
                f"El programa Megaplex Stars tiene {len(emb)} embajadores en "
                f"{emb['disciplina'].nunique()} disciplinas y devuelve "
                f"{emb['venta_atribuida_cop'].sum()/emb['costo_mensual_cop'].sum():.1f}x en venta "
                f"con código.\n\n"
                f"El hallazgo interesante: los perfiles con audiencia por debajo de la mediana "
                f"devuelven {roi_ch:.1f}x y los grandes {roi_gr:.1f}x. "
                f"{'El programa está pagando alcance más que ventas.' if roi_ch > roi_gr else 'Los perfiles grandes están sosteniendo el programa.'} "
                f"La métrica que decide no es el número de seguidores: es cuántos pedidos entraron "
                f"con su código, y eso ya se está midiendo.")

    if any(x in q for x in ["cómo vamos", "como vamos", "mes", "resumen", "general", "ventas",
                            "negocio", "hola"]):
        var = (ult["ingresos_cop"] - prev["ingresos_cop"]) / prev["ingresos_cop"] * 100
        canal = v[v["mes"] == ult["mes"]].groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        v26 = v[v["mes"] >= "2026-01"]
        return (f"📊 {ult['mes']} cerró en {cop(ult['ingresos_cop'], 1)}, "
                f"{'arriba' if var >= 0 else 'abajo'} {abs(var):.1f}% frente al mes anterior.\n\n"
                f"• Margen bruto: {ult['margen_bruto_pct']:.1f}%\n"
                f"• EBITDA: {ult['ebitda_pct']:.1f}% ({cop(ult['ebitda_cop'], 1)})\n"
                f"• Canal que más facturó: {canal.index[0]} con {cop(canal.iloc[0], 1)}\n"
                f"• Año corrido: {cop(v26['venta_cop'].sum(), 1)} · "
                f"{int(v26['unidades'].sum()):,} unidades\n\n"
                f"Lo que hay que vigilar este mes: el mix se está apoyando en distribuidores y "
                f"cadenas, que dan cobertura pero dejan menos margen y pagan a 45 y 75 días. "
                f"Cada punto que crezca el canal propio mejora margen y caja al tiempo. Y por el "
                f"lado del costo, la exposición en dólares de la proteína importada sigue siendo "
                f"la variable que puede mover el EBITDA sin que nadie tome una decisión comercial.")

    return (f"Te puedo ayudar con cualquiera de estos temas:\n\n"
            f"📊 Resultado del mes · 💰 Margen por canal · 🏪 Tiendas propias\n"
            f"💪 Portafolio y referencias · 🔁 Clientes y recompra · ⭐ Marketing y Megaplex Stars\n"
            f"🧪 Planta y calidad · ⚖️ Registros INVIMA y FSSC 22000 · 💱 TRM y abastecimiento\n"
            f"📦 Inventario y quiebres · ⏳ Cartera · 🌎 Exportación · 🎧 PQR\n\n"
            f"Para orientarte: {ult['mes']} cerró en {cop(ult['ingresos_cop'], 1)} con "
            f"{ult['ebitda_pct']:.1f}% de EBITDA.")


def llamar_claude(api_key: str, pregunta: str) -> str:
    try:
        import anthropic
        cliente = anthropic.Anthropic(api_key=api_key)
        historial = [{"role": m["role"], "content": m["content"]}
                     for m in st.session_state.ag_msgs[:-1]]
        historial.append({"role": "user", "content": pregunta})
        r = cliente.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1400,
            system=CONTEXTO + "\n\n" + _resumen(),
            messages=historial,
        )
        return r.content[0].text
    except Exception as ex:
        return f"No se pudo conectar con Claude: {ex}"


def _procesar(pregunta, modo_demo, api_key):
    st.session_state.ag_msgs.append({"role": "user", "content": pregunta})
    resp = responder_demo(pregunta) if (modo_demo or not api_key) else llamar_claude(api_key, pregunta)
    st.session_state.ag_msgs.append({"role": "assistant", "content": resp})


def render():
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Agente IA Nutramerican",
        "Pregúntale al negocio en español, como si le escribieras a alguien del equipo que ya "
        "revisó todos los reportes"), unsafe_allow_html=True)

    if "ag_msgs" not in st.session_state:
        st.session_state.ag_msgs = []
    if "ag_pend" not in st.session_state:
        st.session_state.ag_pend = None

    c1, c2 = st.columns([3, 1])
    with c1:
        api_key = st.text_input("API Key de Anthropic (opcional)", type="password",
                                placeholder="sk-ant-…", key="ag_key",
                                help="Con una API key el agente responde cualquier pregunta libre "
                                     "sobre los datos del panel. Sin ella funciona el modo demo.")
    with c2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        modo_demo = st.toggle("Modo demo", value=True, key="ag_demo")

    st.markdown(f"<p style='font-size:13px;font-weight:900;color:{TINTA};margin:14px 0 8px'>"
                f"💡 Preguntas frecuentes</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(SUGERIDAS):
        if cols[i % 4].button(q, key=f"sug_{i}", use_container_width=True):
            st.session_state.ag_pend = q

    if st.session_state.ag_pend:
        _procesar(st.session_state.ag_pend, modo_demo, api_key)
        st.session_state.ag_pend = None

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for msg in st.session_state.ag_msgs:
        es_user = msg["role"] == "user"
        color = ROJO if es_user else AZUL_DEEP
        etiqueta = "Tú" if es_user else "🤖 Agente Nutramerican"
        fondo = ROJO_LT if es_user else SURF
        st.markdown(f"""
        <div style="background:{fondo};border:1px solid {BORDER};border-radius:14px;
          padding:14px 18px;margin:8px 0;border-left:4px solid {color}">
          <p style="font-size:10.5px;font-weight:900;color:{color};margin:0 0 8px;
            text-transform:uppercase;letter-spacing:.08em">{etiqueta}</p>
          <p style="color:{TINTA};margin:0;line-height:1.75;white-space:pre-wrap;
            font-size:13.5px">{msg['content']}</p>
        </div>""", unsafe_allow_html=True)

    pregunta = st.chat_input("Escribe tu pregunta sobre el negocio…")
    if pregunta:
        _procesar(pregunta, modo_demo, api_key)
        st.rerun()

    if st.session_state.ag_msgs:
        if st.button("🗑️  Limpiar conversación", key="ag_clear"):
            st.session_state.ag_msgs = []
            st.rerun()
    else:
        st.markdown(panel("Qué puedes preguntarle", """
        Este agente ve exactamente los mismos datos que el resto del panel. En el producto final
        se conecta a las fuentes reales de Nutramerican —el ERP, el POS de las tiendas, el
        e-commerce, los reportes de los distribuidores, el sistema de calidad de la planta— y
        responde en segundos lo que hoy toma horas de Excel y varios correos:
        <i>«¿cuánto me debe el distribuidor de Ecuador?»</i>,
        <i>«¿qué referencia se está agotando en la tienda de Cali?»</i>,
        <i>«¿qué registro INVIMA tengo que radicar este trimestre?»</i>,
        <i>«¿me conviene subir el precio de la BiPro si la TRM llega a 4.300?»</i>.
        <br><br>
        Modo demo responde con lógica precalculada sobre los datos del panel. Con una API key de
        Anthropic, responde cualquier pregunta libre usando el mismo resumen de datos.
        """, "🤖"), unsafe_allow_html=True)
