# Nutramerican Pharma · Panel de Negocio

Demo construido por **Calybrat** para Nutramerican Pharma: un solo panel donde la dirección ve, en
tiempo real, lo que hoy vive repartido entre el ERP, el POS de las ocho tiendas, el back del
e-commerce, los reportes que mandan los distribuidores, los Excel de la planta de Palmira, la
carpeta de registros INVIMA y el WhatsApp de servicio al cliente.

---

## Por qué este panel y no un dashboard genérico

Nutramerican no es una marca de suplementos. Es **una fábrica que además tiene marcas, tiendas,
e-commerce, distribución nacional, maquila para terceros y exportación a seis países**. Cada una de
esas cosas se mide distinto, y ahí es donde un dashboard estándar se queda corto.

| Realidad del negocio | Qué problema genera | Módulo que lo resuelve |
|---|---|---|
| Vende por tienda propia, web, distribuidores, cadenas, gimnasios, maquila y seis mercados de exportación | Cada canal reporta distinto y tarde; nadie ve el total | **Ventas Omnicanal** |
| Ocho tiendas propias en siete ciudades | Una tienda puede vender poco porque entra poca gente o porque entra y no compra: son dos problemas distintos | **Tiendas Nutramerican** |
| 52 referencias en siete categorías y seis marcas propias | Cada referencia consume registro sanitario, corrida de planta e inventario, venda o no venda | **Portafolio & Precios** |
| Un tarro de 2 lb rinde unos 30 días | Quien no vuelve a los 45 días ya compró en otra marca, y nadie se entera | **Clientes & Recompra** |
| Nueve redes, pauta en cuatro plataformas y un programa de embajadores atletas | El alcance se mide solo; las ventas que produce, no | **Marketing & Megaplex Stars** |
| Planta propia de 2.500 m² con seis líneas y tres turnos | Cada punto de OEE que se recupera es capacidad que no hay que comprar | **Producción & Planta** |
| FSSC 22000, habilitación FDA y un registro INVIMA por producto | Un registro vencido saca el producto del mercado, y no se nota hasta que alguien lo pide | **Calidad & Regulatorio** |
| La proteína de suero se importa en dólares y se vende en pesos, con más de 60 días de tránsito | La TRM mueve el EBITDA sin que nadie tome una decisión comercial | **Abastecimiento & Divisa** |
| Planta en Palmira, CD en Yumbo, MELONN en Bogotá y Medellín, y ocho tiendas | Falta inventario y sobra inventario al mismo tiempo | **Logística & Inventario** |
| Distribuidores a 45 días y cadenas a 75 | Crecer en esos canales crece la venta y aprieta la caja | **Finanzas & Cartera** |
| Ecuador, México, Honduras, Panamá, España y Estados Unidos | Cada referencia necesita registro sanitario propio en cada país | **Expansión Internacional** |
| WhatsApp, línea #590, chat, redes y tienda física | Los reclamos de entrega no se arreglan en servicio al cliente | **Servicio al Cliente & PQR** |

---

## Los 15 módulos

**Vista general** — `Dashboard Ejecutivo`: el estado del negocio en una pantalla, con alertas.

**Comercial**
- `Ventas Omnicanal` — los doce canales, por marca, categoría, ciudad y país.
- `Tiendas Nutramerican` — las 8 tiendas propias: venta por m², tráfico, conversión, ticket,
  contribución y el diagnóstico que separa el problema de tráfico del problema de cierre.
- `Portafolio & Precios` — las 52 referencias con su render oficial, margen por SKU, curva de
  concentración y la arquitectura de precios canal por canal.
- `Clientes & Recompra` — cohortes, ciclo de recompra, LTV/CAC, medios de pago y la lista concreta
  de clientes reactivables.
- `Marketing & Megaplex Stars` — ROAS y CAC por canal, retorno real de cada embajador y de cada feria.

**Operación**
- `Producción & Planta` — lotes, OEE, merma y paros por línea y turno, más plan contra demanda.
- `Calidad & Regulatorio` — vigencia de registros INVIMA, no conformidades FSSC 22000, ensayos de
  laboratorio y farmacovigilancia.
- `Abastecimiento & Divisa` — compras por insumo, lead times, cumplimiento de proveedores y un
  simulador de sensibilidad del EBITDA a la TRM.
- `Logística & Inventario` — OTIF contra el SLA publicado, inventario en cinco bodegas y
  comparativo de transportadoras.

**Dirección**
- `Finanzas & Cartera` — P&G mensual, cascada de la venta al EBITDA, aging de cartera y ciclo de
  conversión de caja.
- `Expansión Internacional` — los seis mercados comparados por salud, no solo por tamaño.
- `Servicio al Cliente & PQR` — motivos, canales, SLA y qué parte de los casos se puede automatizar.
- `Reportes Automáticos` — seis documentos listos para descargar e imprimir en PDF.
- `Agente IA Nutramerican` — preguntas en español sobre los datos del negocio.

---

## Sobre los datos

Los datos transaccionales son **simulados**, generados por `data/generate_data.py`. Lo que **sí es
real**, y fue tomado de fuentes públicas de la compañía para que el demo se sienta propio:

- **Catálogo completo** — las 52 referencias publicadas en `nutramerican.com/productos`, con su
  nombre, presentación, PVP y precio promocional vigente, y **el render oficial de cada producto**
  descargado del CDN de la compañía.
- **Categorías reales del sitio** — Módulos proteicos · Control de peso · Hipercalóricos ·
  Energía y recuperación · Snacks proteicos · Nutrición general · Merch.
- **Marcas propias** — BiPro y Megaplex, más las líneas Stacks, Nutra, Radical y el merch.
- **Las 8 tiendas** — dirección, teléfono, horario de lunes a viernes y de sábado, y coordenadas
  exactas, tomadas del directorio publicado por la compañía.
- **Planta y comercializadora** — fabricación en Cantarrana, Palmira (Valle del Cauca) y
  comercializadora ELITENUT S.A.S. en Yumbo, bodega C-11 del terminal logístico.
- **Certificaciones** — FSSC 22000 obtenida el 28 de marzo de 2024, habilitación FDA y registro
  INVIMA por producto. Dos registros son los números reales publicados: BiPro Classic
  `RSA-0007428-2019` y Crea Stack `NSA-0015613-2024`; el resto están simulados y marcados como tal.
- **Escala** — más de un millón de unidades al año, del orden de 80.000 unidades mensuales en el
  mercado nacional, planta de 2.500 m² con 1.000 t de almacenamiento y cerca de 120 toneladas
  trimestrales de proteína de suero importada (Forbes Colombia y Portafolio).
- **Mercados** — Ecuador, México, Honduras y Centroamérica, con España y Estados Unidos
  (Nutramerican Pharma LLC) en apertura.
- **Logística y servicio** — MELONN para Bogotá y Medellín, los tiempos de entrega publicados en
  su guía de servicio, y los canales de atención reales incluida la línea gratuita #590.
- **Identidad de marca** — el logo oficial, la paleta tomada de las variables CSS del propio sitio
  (`--nutra-blue #0071e3`, `--nutra-gold #e5bb47`, `--nutra-ink #0b0c0f`, el rojo de la franja y el
  azul `#004BE0` de las estrellas) y Montserrat, la misma tipografía que usa la web.

Para regenerar los datos:

```bash
python3 data/generate_data.py
```

---

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

El demo es de **acceso libre**: se abre y ya, sin usuario ni clave. La idea es que el cliente entre
sin fricción. El control de acceso se implementa en el producto final.

Cada visita queda registrada (fecha, IP y ciudad aproximada) en `visit_log.json`. Para ver ese
registro, agrega `?accesos=calybrat` al final de la URL. En Streamlit Cloud el archivo se reinicia
con cada despliegue.

---

## Estructura

```
app.py                  navegación y armado del panel
utils/formatters.py     paleta de marca, helpers de formato y tema de las gráficas
utils/datos.py          carga de datos compartida y cacheada
utils/visitas.py        registro de visitas al demo
modules/p01…p15         un archivo por módulo
data/generate_data.py   generador de los datos del demo
data/*.csv(.gz)         datos generados
assets/                 logo oficial, sello FSSC 22000 y los 52 renders de producto
```

---

Construido por [Calybrat](https://calybrat.com) · 2026
