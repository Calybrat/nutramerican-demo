"""
Nutramerican Pharma — Generador de datos del demo
Corre una vez:  python3 data/generate_data.py

TODOS los datos transaccionales son SINTÉTICOS: se crearon para una
demostración comercial de Calybrat y no corresponden a cifras reales de la
compañía. Lo que NO es sintético, y se tomó de fuentes públicas para que el
panel se sienta propio:

  · Catálogo real: las 52 referencias publicadas en nutramerican.com/productos
    con su PVP y su precio promocional (consulta de septiembre de 2026).
  · Categorías reales del sitio: Módulos proteicos · Control de peso ·
    Hipercalóricos · Energía y recuperación · Snacks proteicos ·
    Nutrición general · Merch.
  · Marcas propias reales: BiPro y Megaplex, más las líneas Stacks, Nutra,
    Radical y el merch Nutramerican.
  · Las 8 tiendas propias con dirección, teléfono, horario y coordenadas
    exactas (nutramerican.com/context/INFO_TIENDAS_NUTRAMERICAN.md).
  · Planta de fabricación en Cantarrana, Palmira (Valle del Cauca) y
    comercializadora ELITENUT S.A.S. en Yumbo, bodega C-11.
  · Certificación FSSC 22000 obtenida el 28 de marzo de 2024 · registros
    INVIMA por producto · planta con habilitación FDA.
  · Escala pública: >1.000.000 de unidades vendidas al año, ~80.000
    unidades/mes en el mercado nacional, planta de 2.500 m² y 1.000 t de
    capacidad de almacenamiento, ~120 t trimestrales de proteína de suero
    importada (Forbes Colombia, Portafolio).
  · Dos registros INVIMA reales: BiPro Classic RSA-0007428-2019 y
    Crea Stack NSA-0015613-2024. Los demás números son simulados.
  · Mercados de exportación mencionados públicamente: Ecuador, Honduras,
    México y Centroamérica, con España y Estados Unidos en apertura.
  · Operador logístico MELONN para Bogotá y Medellín y los tiempos de
    entrega publicados en su guía de servicio.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

RNG = np.random.default_rng(2026)
OUT = Path(__file__).parent

HOY = date(2026, 8, 31)
INICIO = date(2025, 1, 1)

# ── CATÁLOGO REAL (nutramerican.com/productos) ───────────────────────────────
# (sku, nombre, marca, categoria, presentacion, pvp_cop, pvp_promo_cop,
#  costo_frac, imagen, lanzamiento)
PRODUCTOS = [
    # ── BiPro · módulos proteicos ────────────────────────────────────────────
    ("BIP-CLA-09V", "BiPro Classic Vainilla 0.9 lb",   "BiPro", "Módulos proteicos", "0.9 lb tarro",  119000, None,   0.40, "bipro-classic-vainilla-0-9lb.webp",                          "2019-01-15"),
    ("BIP-CLA-2V",  "BiPro Classic Vainilla 2 lb",     "BiPro", "Módulos proteicos", "2 lb tarro",    249000, None,   0.38, "bipro-classic-vainilla-2lb.webp",                            "2019-01-15"),
    ("BIP-CLA-2C",  "BiPro Classic Chocolate 2 lb",    "BiPro", "Módulos proteicos", "2 lb tarro",    249000, None,   0.38, "bipro-classic-chocolate-2lb.webp",                           "2019-01-15"),
    ("BIP-CLA-2N",  "BiPro Classic Natural 2 lb",      "BiPro", "Módulos proteicos", "2 lb tarro",    249000, None,   0.37, "bipro-classic-natural.webp",                                 "2020-06-01"),
    ("BIP-CLA-DIS", "BiPro Classic Display sachets",   "BiPro", "Módulos proteicos", "caja sachets",  124000, None,   0.44, "bipro-classic-display.webp",                                 "2023-02-01"),
    ("BIP-CLA-3CC", "BiPro Classic Cookies 3 lb",      "BiPro", "Módulos proteicos", "3 lb + regalo", 329000, None,   0.42, "bipro-classic-cookies-cream-3lb-gratis-nutra-pops-ca.webp","2026-01-15"),
    ("BIP-CLA-3V",  "BiPro Classic Vainilla 3 lb",     "BiPro", "Módulos proteicos", "3 lb + regalo", 329000, None,   0.42, "bipro-classic-vainilla-3lb-gratis-nutra-pops-caja.webp",     "2026-01-15"),
    ("BIP-CLA-3CA", "BiPro Classic Capuccino 3 lb",    "BiPro", "Módulos proteicos", "3 lb + regalo", 329000, None,   0.42, "bipro-classic-3lb-capuccino-gratis-nutra-pops-caja.webp",    "2026-01-15"),
    ("BIP-COM-21",  "BiPro Complex Vainilla 2.1 lb",   "BiPro", "Módulos proteicos", "2.1 lb tarro",  249000, 224100, 0.39, "bipro-complex-vainilla-2-1-lb.webp",                         "2024-05-01"),
    ("BIP-LIT-24",  "BiPro Lite 2.4 lb",               "BiPro", "Control de peso",   "2.4 lb tarro",  249000, None,   0.38, "bipro-lite.webp",                                            "2021-03-01"),
    ("BIP-MAS-3",   "BiPro Mass 3 lb",                 "BiPro", "Hipercalóricos",    "3 lb tarro",    249000, None,   0.41, "bipro-mass.webp",                                            "2021-09-01"),

    # ── Megaplex ─────────────────────────────────────────────────────────────
    ("MEG-CRE-2",   "Megaplex Creatine Power 2 lb",    "Megaplex", "Energía y recuperación", "2 lb tarro",  79900,  None, 0.36, "megaplex-creatine-power-2lb.webp",  "2019-05-01"),
    ("MEG-CRE-10",  "Megaplex Creatine Power 10 lb",   "Megaplex", "Energía y recuperación", "10 lb tarro", 299900, None, 0.34, "megaplex-creatine-power-10lb.webp", "2022-08-01"),
    ("MEG-GAI-3",   "Gainz 3 lb",                      "Megaplex", "Hipercalóricos",         "3 lb tarro",  114990, None, 0.43, "gainz-3lb.webp",                    "2020-02-01"),
    ("MEG-GAI-64",  "Gainz Vainilla 6.4 lb",           "Megaplex", "Hipercalóricos",         "6.4 lb tarro",219990, None, 0.44, "gainz-vainilla-6-4-lb.webp",        "2020-02-01"),
    ("MEG-CAR-COC", "Mega Carbs Limonada de Coco",     "Megaplex", "Energía y recuperación", "tarro",       79990,  None, 0.39, "mega-carbs-limonada-de-coco.webp",  "2023-04-01"),
    ("MEG-CAR-CER", "Mega Carbs Limón Cereza",         "Megaplex", "Energía y recuperación", "tarro",       79990,  None, 0.39, "mega-carbs-limon-cereza.webp",      "2023-04-01"),
    ("MEG-NIT-FR",  "Nitro Shock Frutos Rojos",        "Megaplex", "Energía y recuperación", "tarro",       94990,  None, 0.37, "nitro-shock-frutos-rojos.webp",     "2022-03-01"),
    ("MEG-SOY",     "Mega Soy",                        "Megaplex", "Módulos proteicos",      "tarro",       69990,  None, 0.35, "mega-soy.webp",                     "2021-07-01"),

    # ── Línea Stacks ─────────────────────────────────────────────────────────
    ("STK-CRE-TAR", "Crea Stack 1.3 lb",               "Stacks", "Energía y recuperación", "1.3 lb tarro",  149990, None,   0.35, "crea-stack.webp",         "2024-03-01"),
    ("STK-CRE-SAC", "Crea Stack Display sachets",      "Stacks", "Energía y recuperación", "caja sachets",  124900, None,   0.41, "crea-stack-sachets.webp", "2025-06-01"),
    ("STK-BUR-TAR", "Burner Stack 360 g",              "Stacks", "Control de peso",        "360 g tarro",   139990, None,   0.34, "burner-stack.webp",       "2021-11-01"),
    ("STK-BUR-L24", "Burner Stack Lata · paca x24",    "Stacks", "Control de peso",        "paca x24 lata", 189600, 161160, 0.56, "burner-stack-lata-paca-de-24-unidades.webp", "2025-03-01"),
    ("STK-BUR-L12", "Burner Stack Lata · paca x12",    "Stacks", "Control de peso",        "paca x12 lata", 101450, 91305,  0.56, "burner-stack-lata-paca-de-12-unidades.webp", "2025-03-01"),
    ("STK-COL",     "Collagen Stack 585 g",            "Stacks", "Nutrición general",      "585 g tarro",   99990,  None,   0.38, "collagen-stack.webp",     "2023-09-01"),
    ("STK-PRW",     "Prime W Collagen Stack",          "Stacks", "Nutrición general",      "tarro",         74500,  None,   0.37, "prime-w-collagen-stack.webp", "2026-07-15"),
    ("STK-GLU",     "Gluta Stack",                     "Stacks", "Energía y recuperación", "tarro",         64990,  None,   0.36, "gluta-stack.webp",        "2022-06-01"),
    ("STK-COMBO",   "Combo BiPro Lite + Burner Stack", "Stacks", "Control de peso",        "combo",         388990, 350091, 0.40, "bi-pro-lite-y-burner-stack.webp", "2025-09-01"),

    # ── Línea Nutra ──────────────────────────────────────────────────────────
    ("NUT-POP-CAJ", "Nutra Pops caja",                 "Nutra", "Snacks proteicos",   "caja",       59900, None, 0.46, "nutra-pops.webp",                   "2024-08-01"),
    ("NUT-POP-PK",  "Nutra Pops pack x12",             "Nutra", "Snacks proteicos",   "pack x12",   64900, None, 0.47, "nutra-pops-pack.webp",              "2024-08-01"),
    ("NUT-VEG-400", "Nutra Vegan Protein Mocaccino",   "Nutra", "Módulos proteicos",  "400 g",      64990, None, 0.42, "nutra-vegan-protein-mocaccino-400g.webp", "2023-02-01"),
    ("NUT-RX",      "Nut-Rx Vainilla 400 g",           "Nutra", "Nutrición general",  "400 g",      34990, None, 0.44, "nut-rx.webp",                       "2022-01-01"),
    ("NUT-ZOL",     "Zolé Vainilla 450 g",             "Nutra", "Nutrición general",  "450 g",      29990, None, 0.45, "zole.webp",                         "2022-01-01"),
    ("NUT-BAL",     "Nutra Balance x8 sobres",         "Nutra", "Nutrición general",  "8 sobres",   49900, None, 0.43, "nutra-balance.webp",                "2023-11-01"),
    ("NUT-C",       "Nutra-C Ácido Ascórbico 200 g",   "Nutra", "Nutrición general",  "200 g",      64990, None, 0.33, "nutra-c.webp",                      "2021-05-01"),
    ("NUT-SB",      "Nutra Smart Baby",                "Nutra", "Nutrición general",  "unidad",     18900, None, 0.48, "nutra-smart-baby.webp",             "2026-06-01"),
    ("NUT-SB-DIS",  "Nutra Smart Baby Display",        "Nutra", "Nutrición general",  "display",    32500, None, 0.49, "nutra-smart-baby-display.webp",     "2026-06-01"),

    # ── Bebidas Radical / Myth / Rescue ──────────────────────────────────────
    ("RAD-PWD-TAR", "Radical Power Drink tarro",       "Radical", "Energía y recuperación", "tarro",        119900, None,   0.38, "radical-power-drink-tarro.webp", "2023-06-01"),
    ("RAD-PWD",     "Radical Power Drink polvo",       "Radical", "Energía y recuperación", "polvo",        84900,  None,   0.37, "radical-power-drink.webp",       "2023-06-01"),
    ("RAD-ENX",     "Energy X",                        "Radical", "Energía y recuperación", "unidad",       29990,  None,   0.52, "energy-x.webp",                  "2024-04-01"),
    ("RAD-MYT-24",  "Myth Legendary Pre-Workout x24",  "Radical", "Energía y recuperación", "paca x24 lata",189600, 161160, 0.57, "myth-legendary-pre-workout-paca-por-24-unidades.webp", "2025-05-01"),
    ("RAD-MYT-12",  "Myth Legendary Pre-Workout x12",  "Radical", "Energía y recuperación", "paca x12 lata",101450, 91305,  0.57, "myth-legendary-pre-workout-paca-por-12-unidades.webp", "2025-05-01"),
    ("RAD-RES-24",  "Rescue · paca x24",               "Radical", "Energía y recuperación", "paca x24 lata",189600, 161160, 0.55, "rescue-paca-de-24-unidades.webp","2025-02-01"),
    ("RAD-RES-12",  "Rescue · paca x12",               "Radical", "Energía y recuperación", "paca x12 lata",101450, 91305,  0.55, "rescue-paca-de-12-unidades.webp","2025-02-01"),
    ("RAD-RES-4",   "Rescue · paca x4",                "Radical", "Energía y recuperación", "paca x4 lata", 31600,  28440,  0.55, "rescue-paca-de-4-unidades.webp", "2025-02-01"),

    # ── Alimentos funcionales ────────────────────────────────────────────────
    ("ALI-FIT-COC", "Fitbar Coco",                     "Nutramerican", "Snacks proteicos", "caja",   164990, 140242, 0.51, "fitbar-sabor-coco.webp",          "2024-10-01"),
    ("ALI-FIT-CHO", "Fitbar Chocolate",                "Nutramerican", "Snacks proteicos", "caja",   164990, 140242, 0.51, "fitbar-sabor-chocolate.webp",     "2024-10-01"),
    ("ALI-CAK-VAN", "Protein Cake Vainilla",           "Nutramerican", "Snacks proteicos", "mezcla", 74990,  None,   0.45, "protein-cake-vainilla.webp",      "2025-04-01"),
    ("ALI-CAK-CHO", "Protein Cake Chocolate",          "Nutramerican", "Snacks proteicos", "mezcla", 74990,  None,   0.45, "protein-cake-chocolate.webp",     "2025-04-01"),
    ("ALI-PAN-WAF", "Protein Pancake & Waffle",        "Nutramerican", "Snacks proteicos", "mezcla", 59990,  None,   0.44, "protein-pancake-waffle.webp",     "2024-03-01"),
    ("ALI-PAN-TRA", "Protein Pancake Tradicional",     "Nutramerican", "Snacks proteicos", "mezcla", 49990,  None,   0.44, "protein-pancake-tradicional.webp","2024-03-01"),

    # ── Merch ────────────────────────────────────────────────────────────────
    ("MER-BAC",     "Nutramerican Backpack",           "Nutramerican", "Merch", "unidad", 199990, None, 0.62, "nutramerican-backpack.webp", "2025-07-01"),
]
PROD_COLS = ["sku", "producto", "marca", "categoria", "presentacion", "pvp_cop",
             "pvp_promo_cop", "costo_frac", "imagen", "fecha_lanzamiento"]

# Línea de producción en la que se fabrica cada categoría/formato
def linea_de(sku: str, presentacion: str) -> str:
    if "lata" in presentacion:
        return "Bebidas RTD (lata)"
    if "sachet" in presentacion or "display" in presentacion or "sobres" in presentacion:
        return "Sachets & Display"
    if sku.startswith("ALI-FIT"):
        return "Barras & Snacks"
    if sku.startswith("ALI-"):
        return "Horneados & Mezclas"
    if sku.startswith("MER-"):
        return "Maquila externa"
    return "Polvos & Envasado"


# ── CANALES REALES ───────────────────────────────────────────────────────────
# factor_pvp   = cuánto paga el consumidor en ese canal vs. el PVP de la web
# margen_canal = qué se queda el canal sobre ese precio (0 en venta directa)
CANALES = [
    ("Tiendas Nutramerican",   "Tienda propia",  "Colombia",       1.00, 0.00,  0, 0.225),
    ("nutramerican.com",       "E-commerce",     "Colombia",       1.00, 0.00,  0, 0.140),
    ("Distribuidores",         "Mayorista",      "Colombia",       1.18, 0.30, 45, 0.235),
    ("Cadenas & Farmacias",    "Retail",         "Colombia",       1.24, 0.34, 75, 0.140),
    ("Gimnasios & Wellness",   "Especializado",  "Colombia",       1.20, 0.28, 45, 0.060),
    ("Maquila & Marca Propia", "Maquila",        "Colombia",       0.62, 0.00, 60, 0.095),
    ("Distribuidor Ecuador",   "Internacional",  "Ecuador",        1.16, 0.26, 60, 0.030),
    ("Distribuidor México",    "Internacional",  "México",         1.22, 0.28, 60, 0.025),
    ("Distribuidor Honduras",  "Internacional",  "Honduras",       1.14, 0.26, 60, 0.022),
    ("Distribuidor Panamá",    "Internacional",  "Panamá",         1.18, 0.26, 60, 0.012),
    ("Nutramerican España",    "Internacional",  "España",         1.45, 0.20, 45, 0.008),
    ("Nutramerican USA LLC",   "Internacional",  "Estados Unidos", 1.52, 0.15, 30, 0.008),
]
CAN_COLS = ["canal", "tipo_canal", "pais", "factor_pvp", "margen_canal",
            "plazo_pago_dias", "peso_mix"]

LANZAMIENTO_CANAL = {
    "Tiendas Nutramerican":   date(2025, 1, 1),
    "nutramerican.com":       date(2025, 1, 1),
    "Distribuidores":         date(2025, 1, 1),
    "Cadenas & Farmacias":    date(2025, 1, 1),
    "Gimnasios & Wellness":   date(2025, 1, 1),
    "Maquila & Marca Propia": date(2025, 1, 1),
    "Distribuidor Ecuador":   date(2025, 1, 1),
    "Distribuidor Honduras":  date(2025, 1, 1),
    "Distribuidor México":    date(2025, 7, 1),
    "Distribuidor Panamá":    date(2026, 1, 1),
    "Nutramerican España":    date(2026, 4, 1),
    "Nutramerican USA LLC":   date(2026, 6, 1),
}

# ── TIENDAS REALES (dirección, teléfono, horario y coordenadas oficiales) ────
TIENDAS = [
    ("TDA-BOGN", "Nutramerican Bogotá Norte",  "Bogotá",       "Av. Carrera 19 # 108-50, San Patricio (Usaquén)", "3115149103", 4.694927, -74.050367, "09:00–18:00", "09:00–13:00", 120, 2020, 0.185),
    ("TDA-BOGS", "Nutramerican Bogotá Kennedy","Bogotá",       "Carrera 79 Sur # 41C-43, Kennedy",                "3115149103", 4.620743, -74.160044, "09:00–18:00", "09:00–13:00",  95, 2022, 0.140),
    ("TDA-CALI", "Nutramerican Cali",          "Cali",         "Av. 6A Norte # 23N-65, Santa Mónica",             "3207582916", 3.465442,  -76.530905, "09:00–18:00", "09:00–13:00", 140, 2018, 0.195),
    ("TDA-MED",  "Nutramerican Medellín",      "Medellín",     "Calle 33 # 65B-13, Conquistadores",               "3137449069", 6.239383,  -75.584091, "09:00–18:00", "09:00–13:00", 110, 2019, 0.160),
    ("TDA-BAQ",  "Nutramerican Barranquilla",  "Barranquilla", "Carrera 46 # 76-96, El Porvenir",                 "3217483972", 10.997021, -74.810740, "08:00–18:00", "08:00–13:00",  90, 2021, 0.110),
    ("TDA-BGA",  "Nutramerican Bucaramanga",   "Bucaramanga",  "Carrera 35 # 54-70, Cabecera",                    "3165271052", 7.117497,  -73.126816, "08:00–18:00", "08:00–13:00",  78, 2022, 0.085),
    ("TDA-PEI",  "Nutramerican Pereira",       "Pereira",      "Av. 30 de Agosto # 46-145, Maraya",               "3165271052", 4.815753,  -75.717517, "09:00–18:00", "09:00–13:00",  72, 2023, 0.070),
    ("TDA-CUC",  "Nutramerican Cúcuta",        "Cúcuta",       "Avenida 0 # 18-54, Barrio Blanco",                "3165271052", 7.879300,  -72.497218, "08:00–18:00", "08:00–13:00",  68, 2024, 0.055),
]
TDA_COLS = ["tienda_id", "tienda", "ciudad", "direccion", "celular", "lat", "lon",
            "horario_lv", "horario_sab", "area_m2", "anio_apertura", "peso_venta"]

# ── BODEGAS ──────────────────────────────────────────────────────────────────
BODEGAS = [
    ("BOD-PAL", "Planta Palmira · Cantarrana",   "Palmira", "Colombia", "Planta",     0.42),
    ("BOD-YUM", "CD Yumbo · ELITENUT bodega C-11","Yumbo",  "Colombia", "Centro dist.",0.26),
    ("3PL-BOG", "3PL MELONN Bogotá",             "Bogotá",  "Colombia", "3PL",        0.14),
    ("3PL-MED", "3PL MELONN Medellín",           "Medellín","Colombia", "3PL",        0.08),
    ("BOD-TDA", "Tiendas Nutramerican (8)",      "Nacional","Colombia", "Tienda",     0.10),
]
BOD_COLS = ["bodega_id", "bodega", "ciudad", "pais", "tipo", "peso"]

CIUDADES_CO = [("Bogotá", 0.300), ("Cali", 0.150), ("Medellín", 0.145), ("Barranquilla", 0.085),
               ("Bucaramanga", 0.060), ("Cartagena", 0.045), ("Pereira", 0.042), ("Cúcuta", 0.038),
               ("Ibagué", 0.030), ("Manizales", 0.025), ("Villavicencio", 0.023), ("Santa Marta", 0.020),
               ("Armenia", 0.014), ("Neiva", 0.013), ("Pasto", 0.010)]
CIUDADES_INT = {
    "Ecuador":        [("Quito", 0.45), ("Guayaquil", 0.40), ("Cuenca", 0.15)],
    "México":         [("Ciudad de México", 0.50), ("Guadalajara", 0.28), ("Monterrey", 0.22)],
    "Honduras":       [("Tegucigalpa", 0.55), ("San Pedro Sula", 0.45)],
    "Panamá":         [("Ciudad de Panamá", 1.00)],
    "España":         [("Madrid", 0.55), ("Barcelona", 0.45)],
    "Estados Unidos": [("Miami", 0.50), ("Houston", 0.28), ("Nueva York", 0.22)],
}

# ── PROVEEDORES DE MATERIA PRIMA ─────────────────────────────────────────────
# (id, insumo, origen, moneda, lead_time_dias, critico, calidad, puntualidad, precio)
PROVEEDORES = [
    ("MP-001", "Proteína de suero WPC 80",      "Estados Unidos", "USD", 62, 1, 9.4, 8.5, 7.2),
    ("MP-002", "Proteína de suero aislada WPI", "Irlanda",        "USD", 74, 1, 9.6, 8.2, 6.8),
    ("MP-003", "Caseinato de calcio",           "Nueva Zelanda",  "USD", 68, 1, 9.2, 8.6, 7.4),
    ("MP-004", "Creatina monohidrato",          "Alemania",       "USD", 55, 1, 9.5, 8.9, 7.6),
    ("MP-005", "Colágeno hidrolizado bovino",   "Brasil",         "USD", 38, 0, 9.0, 8.8, 8.1),
    ("MP-006", "Proteína vegetal de arveja",    "Canadá",         "USD", 58, 0, 8.7, 8.4, 7.9),
    ("MP-007", "Cafeína anhidra y taurina",     "China",          "USD", 82, 0, 8.5, 7.6, 8.8),
    ("MP-008", "Vitaminas y minerales premix",  "Suiza",          "EUR", 65, 1, 9.7, 9.0, 6.5),
    ("MP-009", "Maltodextrina y carbohidratos", "Colombia",       "COP", 12, 0, 8.6, 9.2, 8.9),
    ("MP-010", "Endulzantes (sucralosa, stevia)","Colombia",      "COP", 15, 0, 8.4, 9.0, 8.7),
    ("MP-011", "Cacao y saborizantes",          "Colombia",       "COP", 18, 0, 8.8, 8.9, 8.5),
    ("MP-012", "Envases, tarros y tapas",       "Colombia",       "COP", 22, 1, 8.9, 8.3, 8.4),
    ("MP-013", "Latas y tapas para RTD",        "Colombia",       "COP", 34, 1, 8.7, 7.9, 8.0),
    ("MP-014", "Empaque flexible y sachets",    "Colombia",       "COP", 20, 0, 8.5, 8.7, 8.6),
]
PRO_COLS = ["proveedor_id", "insumo", "origen", "moneda", "lead_time_dias", "critico",
            "score_calidad", "score_puntualidad", "score_precio"]

# ── ORGANIZACIÓN (banda LinkedIn: 201-500 empleados) ─────────────────────────
AREAS = [
    ("Producción",              86, (1_423_500, 3_400_000)),
    ("Calidad & Laboratorio",   17, (2_100_000, 7_200_000)),
    ("Logística & Almacén",     34, (1_423_500, 3_900_000)),
    ("Tiendas",                 32, (1_423_500, 3_200_000)),
    ("Comercial & Trade",       29, (2_300_000, 9_500_000)),
    ("Marketing & Digital",     14, (2_500_000, 9_000_000)),
    ("Servicio al Cliente",     13, (1_423_500, 3_100_000)),
    ("Compras & Comercio Ext.",  9, (2_600_000, 8_800_000)),
    ("I+D e Innovación",         8, (3_200_000,11_000_000)),
    ("Administración & Finanzas",19, (2_200_000, 9_500_000)),
    ("Dirección",                7, (11_000_000, 28_000_000)),
]

CANALES_MKT = ["Meta Ads", "Google Ads", "TikTok Ads", "YouTube",
               "Email & CRM", "WhatsApp", "Megaplex Stars", "Orgánico / SEO", "Eventos & Ferias"]
MKT_ROAS_OBJ = {"Meta Ads": 3.4, "Google Ads": 4.8, "TikTok Ads": 2.6, "YouTube": 2.2,
                "Email & CRM": 12.0, "WhatsApp": 9.5, "Megaplex Stars": 3.1, "Eventos & Ferias": 1.9}

# Disciplinas del programa real de embajadores Megaplex Stars
DISCIPLINAS = ["Fisicoculturismo", "CrossFit", "Powerlifting", "Running", "Ciclismo",
               "Calistenia", "Fitness / Wellness", "Fútbol", "Voleibol", "Boxeo"]

MOTIVOS_PQR = [
    ("Demora en la entrega",            0.235, 1.0),
    ("Faltante en el pedido",           0.165, 1.2),
    ("Camiseta personalizada pendiente",0.120, 1.6),
    ("Producto averiado en transporte", 0.105, 1.1),
    ("Contenido incompleto del envase", 0.085, 1.9),
    ("Solicitud de factura electrónica",0.080, 0.5),
    ("Reclamo por precio o promoción",  0.075, 0.7),
    ("Cambio o garantía",               0.060, 1.5),
    ("Evento adverso reportado",        0.035, 2.6),
    ("Duda sobre uso del producto",     0.040, 0.4),
]
CANALES_PQR = [("WhatsApp", 0.44), ("Línea gratuita #590", 0.17), ("Chat del sitio", 0.15),
               ("Instagram / redes", 0.11), ("Tienda física", 0.08), ("Correo electrónico", 0.05)]
# No todos los canales responden igual de rápido: el chat y WhatsApp tienen
# respuesta asistida, el correo y las redes dependen de que alguien los revise.
VELOCIDAD_PQR = {"WhatsApp": 0.55, "Chat del sitio": 0.65, "Línea gratuita #590": 0.85,
                 "Tienda física": 1.30, "Instagram / redes": 2.10, "Correo electrónico": 3.20}

# Registros INVIMA reales publicados por la compañía
INVIMA_REALES = {"BIP-CLA-2V": "RSA-0007428-2019", "BIP-CLA-2C": "RSA-0007428-2019",
                 "BIP-CLA-2N": "RSA-0007428-2019", "BIP-CLA-09V": "RSA-0007428-2019",
                 "STK-CRE-TAR": "NSA-0015613-2024", "STK-CRE-SAC": "NSA-0015613-2024"}


# ── Helpers ──────────────────────────────────────────────────────────────────
def meses_entre(a: date, b: date):
    out, y, m = [], a.year, a.month
    while (y, m) <= (b.year, b.month):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


MESES = meses_entre(INICIO, HOY)


def estacional(mes: int) -> float:
    """Enero dispara la suplementación (propósitos de año nuevo); junio-julio
    es la segunda ola por temporada de playa; septiembre-octubre son los meses
    flojos del año."""
    return {1: 1.34, 2: 1.14, 3: 1.05, 4: 0.97, 5: 1.02, 6: 1.11,
            7: 1.08, 8: 1.00, 9: 0.90, 10: 0.93, 11: 1.06, 12: 1.16}[mes]


def rampa(d: date, lanzamiento: date, dias: int = 210) -> float:
    """Solo rampan los canales que se abren dentro de la ventana de datos.
    Los que ya existían antes de enero de 2025 arrancan a plena capacidad:
    la compañía lleva 26 años operando, no está empezando."""
    if d < lanzamiento:
        return 0.0
    if lanzamiento <= INICIO:
        return 1.0
    t = (d - lanzamiento).days
    return float(min(1.0, 0.28 + 0.72 * t / dias))


def elegir(opciones, n):
    vals = [o[0] for o in opciones]
    p = np.array([o[1] for o in opciones], dtype=float)
    return RNG.choice(vals, size=n, p=p / p.sum())


def trm_mensual() -> pd.DataFrame:
    """Tasa representativa del mercado, mes a mes. Los costos de materia prima
    están en dólares y el precio de venta en pesos: esa brecha es el riesgo."""
    base = [4390, 4310, 4180, 4225, 4160, 4090, 4045, 4120, 4210, 4165, 4090, 4020,
            3985, 4055, 4130, 4090, 4010, 3945, 3900, 3965]
    filas = []
    for i, m in enumerate(MESES):
        v = base[i] if i < len(base) else base[-1]
        filas.append({"mes": m, "trm_cop_usd": v + RNG.integers(-28, 29)})
    return pd.DataFrame(filas)


# ── MAESTROS ─────────────────────────────────────────────────────────────────
def gen_maestros():
    prods = pd.DataFrame(PRODUCTOS, columns=PROD_COLS)
    prods["costo_unitario_cop"] = (prods["pvp_cop"] * prods["costo_frac"]).round(-2).astype(int)
    prods["linea"] = [linea_de(s, p) for s, p in zip(prods["sku"], prods["presentacion"])]
    prods["precio_efectivo_cop"] = prods["pvp_promo_cop"].fillna(prods["pvp_cop"]).astype(int)
    prods["descuento_web_pct"] = ((1 - prods["precio_efectivo_cop"] / prods["pvp_cop"]) * 100).round(1)
    prods = prods.drop(columns=["costo_frac"])

    canales = pd.DataFrame(CANALES, columns=CAN_COLS)
    tiendas = pd.DataFrame(TIENDAS, columns=TDA_COLS)
    bodegas = pd.DataFrame(BODEGAS, columns=BOD_COLS)
    prov = pd.DataFrame(PROVEEDORES, columns=PRO_COLS)
    trm = trm_mensual()

    prods.to_csv(OUT / "productos.csv", index=False)
    canales.to_csv(OUT / "canales.csv", index=False)
    tiendas.to_csv(OUT / "tiendas.csv", index=False)
    bodegas.to_csv(OUT / "bodegas.csv", index=False)
    prov.to_csv(OUT / "proveedores.csv", index=False)
    trm.to_csv(OUT / "trm.csv", index=False)
    return prods, canales, tiendas, bodegas, prov, trm


def gen_precios_canal(prods: pd.DataFrame, canales: pd.DataFrame):
    """El mismo tarro cuesta distinto en la web, en la tienda propia, en la
    farmacia y en el gimnasio. Esa arquitectura de precios es lo que hay que
    poder ver de un vistazo."""
    filas = []
    for _, p in prods.iterrows():
        for _, c in canales.iterrows():
            if c["tipo_canal"] == "Maquila":
                continue
            ruido = 1 + RNG.normal(0, 0.022)
            pvp = int(round(p["pvp_cop"] * c["factor_pvp"] * ruido, -2))
            neto = int(round(pvp * (1 - c["margen_canal"]), -2))
            filas.append({
                "sku": p["sku"], "producto": p["producto"], "marca": p["marca"],
                "categoria": p["categoria"], "canal": c["canal"], "tipo_canal": c["tipo_canal"],
                "pais": c["pais"], "pvp_gondola_cop": pvp, "precio_neto_cop": neto,
                "costo_unitario_cop": int(p["costo_unitario_cop"]),
                "margen_cop": neto - int(p["costo_unitario_cop"]),
                "margen_pct": round((neto - p["costo_unitario_cop"]) / neto * 100, 1) if neto else 0.0,
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "precios_canal.csv", index=False)
    return df


# ── VENTAS ───────────────────────────────────────────────────────────────────
def gen_ventas(prods: pd.DataFrame, canales: pd.DataFrame, tiendas: pd.DataFrame):
    """Cerca de 1,1 millones de unidades al año repartidas en 12 canales.
    Se genera línea a línea para que el panel pueda cortar por SKU, marca,
    canal, ciudad, tienda y país sin depender de agregados precalculados."""
    # Peso de cada SKU dentro del mix. Dos fuerzas opuestas: la proteína en
    # tarro es el corazón de la marca, pero lo que más unidades mueve son las
    # referencias baratas de alta rotación (latas, sachets, snacks). Sin esa
    # segunda fuerza el precio promedio se dispara y el negocio se ve más
    # grande de lo que es.
    peso_sku = {}
    for _, p in prods.iterrows():
        base = {"Módulos proteicos": 1.00, "Control de peso": 0.78,
                "Energía y recuperación": 0.95, "Hipercalóricos": 0.42,
                "Snacks proteicos": 0.90, "Nutrición general": 0.62, "Merch": 0.05}[p["categoria"]]
        # Elasticidad: a menor precio, más unidades
        base *= (110_000 / max(25_000, p["pvp_cop"])) ** 0.75
        if p["marca"] == "BiPro":
            base *= 1.75
        if p["marca"] == "Megaplex":
            base *= 1.30
        if p["sku"] in ("BIP-CLA-2V", "BIP-CLA-2C", "STK-CRE-TAR", "STK-BUR-TAR"):
            base *= 1.9          # los más vendidos declarados por la compañía
        if "paca" in p["presentacion"]:
            base *= 0.55
        peso_sku[p["sku"]] = base * float(RNG.uniform(0.85, 1.15))
    sku_list = list(peso_sku)
    lanz_sku = {r["sku"]: pd.Timestamp(r["fecha_lanzamiento"]).date()
                for _, r in prods.iterrows()}

    def mix_del_mes(anio: int, m: int):
        """Solo se puede vender lo que ya está lanzado. El peso de las
        referencias que aún no existen se reparte entre las demás, en vez de
        descartarlas: si no, los meses viejos se ven artificialmente flojos y
        el crecimiento del año sale inflado."""
        fin_mes = date(anio, m, 28)
        activos = [s for s in sku_list if lanz_sku[s] <= fin_mes]
        p = np.array([peso_sku[s] for s in activos], dtype=float)
        return activos, p / p.sum()

    # Unidades por documento según el canal: en tienda y web es una canasta de
    # 1 a 4 unidades; en mayorista, retail y exportación es una orden de compra.
    UND_DOC = {"Tienda propia": 2.3, "E-commerce": 2.4, "Mayorista": 34,
               "Retail": 46, "Especializado": 22, "Maquila": 320, "Internacional": 58}
    TOPE_DOCS = {"Tienda propia": 11_000, "E-commerce": 7_500}

    prods_idx = prods.set_index("sku")
    tidx = tiendas.set_index("tienda_id")
    filas = []
    doc = 0
    # Crece ~1% al mes hasta rondar el millón de unidades al año, que es la
    # la compañía es "más de un millón de unidades al año".
    for i, mes in enumerate(MESES):
        anio, m = int(mes[:4]), int(mes[5:])
        dias_mes = (date(anio + (m == 12), (m % 12) + 1, 1) - date(anio, m, 1)).days
        crecimiento = 1.0 + 0.0100 * i
        skus_mes, p_mes = mix_del_mes(anio, m)
        for _, c in canales.iterrows():
            lanz = LANZAMIENTO_CANAL[c["canal"]]
            r = rampa(date(anio, m, 15), lanz)
            if r == 0:
                continue
            unidades_canal = 67_000 * c["peso_mix"] * crecimiento * estacional(m) * r
            unidades_canal *= float(RNG.uniform(0.94, 1.06))
            und_doc = UND_DOC[c["tipo_canal"]]
            n_docs = max(4, int(unidades_canal / und_doc))
            n_docs = min(n_docs, TOPE_DOCS.get(c["tipo_canal"], 2_600))
            und_doc = unidades_canal / n_docs      # se reajusta si topó el límite

            skus = RNG.choice(skus_mes, size=n_docs, p=p_mes)
            if c["canal"] == "Tiendas Nutramerican":
                tds = RNG.choice(tiendas["tienda_id"].tolist(), size=n_docs,
                                 p=tiendas["peso_venta"] / tiendas["peso_venta"].sum())
                ciudades = [tidx.loc[t, "ciudad"] for t in tds]
            else:
                tds = [""] * n_docs
                ciudades = (elegir(CIUDADES_CO, n_docs) if c["pais"] == "Colombia"
                            else elegir(CIUDADES_INT[c["pais"]], n_docs))

            for j in range(n_docs):
                sku = skus[j]
                p = prods_idx.loc[sku]
                if und_doc < 6:
                    # Canasta de mostrador: casi siempre 1 o 2 unidades, a veces
                    # más. La media coincide con `und_doc` para que el total del
                    # canal cuadre con lo planeado.
                    und = 1 + int(RNG.poisson(max(0.05, und_doc - 1)))
                else:
                    und = int(round(max(1, RNG.normal(und_doc, und_doc * 0.45))))

                base_precio = p["pvp_cop"] * c["factor_pvp"]
                # Promociones reales del sitio + descuento por volumen mayorista
                desc = 0.0
                if pd.notna(p["pvp_promo_cop"]) and c["tipo_canal"] in ("E-commerce", "Tienda propia"):
                    desc = 1 - p["pvp_promo_cop"] / p["pvp_cop"]
                elif c["tipo_canal"] == "E-commerce" and RNG.random() < 0.28:
                    desc = 0.15                        # cupón VIP publicado
                elif c["tipo_canal"] == "Tienda propia" and RNG.random() < 0.16:
                    desc = float(RNG.choice([0.10, 0.15]))
                precio_gondola = base_precio * (1 - desc)
                neto = precio_gondola * (1 - c["margen_canal"])
                costo = float(p["costo_unitario_cop"])
                dia = int(RNG.integers(1, dias_mes + 1))
                doc += 1
                filas.append((
                    f"{anio}{m:02d}-{doc:07d}", date(anio, m, dia).isoformat(), mes,
                    c["canal"], c["tipo_canal"], c["pais"], ciudades[j], tds[j],
                    sku, p["producto"], p["marca"], p["categoria"], p["linea"],
                    und, round(precio_gondola), round(neto), round(desc * 100, 1),
                    round(neto * und), round(costo * und), round((neto - costo) * und),
                ))

    v = pd.DataFrame(filas, columns=[
        "documento_id", "fecha", "mes", "canal", "tipo_canal", "pais", "ciudad", "tienda_id",
        "sku", "producto", "marca", "categoria", "linea", "unidades",
        "precio_gondola_cop", "precio_neto_cop", "descuento_pct",
        "venta_cop", "costo_cop", "margen_cop"])
    v["margen_pct"] = (v["margen_cop"] / v["venta_cop"] * 100).round(1)
    v.to_csv(OUT / "ventas.csv.gz", index=False, compression="gzip")
    return v


# ── TIENDAS: tráfico y conversión ────────────────────────────────────────────
def gen_trafico_tiendas(ventas: pd.DataFrame, tiendas: pd.DataFrame):
    """Sin tráfico no hay diagnóstico: una tienda puede vender poco porque
    entra poca gente o porque entra y no compra. Son dos problemas distintos
    con dos soluciones distintas."""
    vt = ventas[ventas["canal"] == "Tiendas Nutramerican"]
    agg = vt.groupby(["mes", "tienda_id"]).agg(
        venta_cop=("venta_cop", "sum"), unidades=("unidades", "sum"),
        tickets=("documento_id", "nunique"), margen_cop=("margen_cop", "sum")).reset_index()
    tidx = tiendas.set_index("tienda_id")
    filas = []
    for _, r in agg.iterrows():
        t = tidx.loc[r["tienda_id"]]
        conv = float(np.clip(RNG.normal(0.24, 0.045), 0.11, 0.42))
        visitas = int(r["tickets"] / conv)
        filas.append({
            "mes": r["mes"], "tienda_id": r["tienda_id"], "tienda": t["tienda"],
            "ciudad": t["ciudad"], "area_m2": t["area_m2"],
            "visitas": visitas, "tickets": int(r["tickets"]),
            "conversion_pct": round(conv * 100, 1),
            "venta_cop": int(r["venta_cop"]), "margen_cop": int(r["margen_cop"]),
            "unidades": int(r["unidades"]),
            "ticket_promedio_cop": int(r["venta_cop"] / r["tickets"]) if r["tickets"] else 0,
            "unidades_por_ticket": round(r["unidades"] / r["tickets"], 2) if r["tickets"] else 0,
            "venta_m2_cop": int(r["venta_cop"] / t["area_m2"]),
            "arriendo_cop": int(t["area_m2"] * RNG.integers(58_000, 86_000)),
            "nomina_cop": int(RNG.integers(3, 6) * RNG.integers(1_900_000, 2_700_000)),
        })
    df = pd.DataFrame(filas)
    df["costo_fijo_cop"] = df["arriendo_cop"] + df["nomina_cop"]
    df["contribucion_cop"] = df["margen_cop"] - df["costo_fijo_cop"]
    df.to_csv(OUT / "tiendas_mensual.csv", index=False)
    return df


# ── CLIENTES DEL CANAL PROPIO ────────────────────────────────────────────────
def gen_clientes(ventas: pd.DataFrame):
    """En suplementación el ciclo de recompra es casi un reloj: un tarro de
    2 lb rinde unos 30 días. Quien pasa de mes y medio sin volver casi siempre
    ya compró en otra parte.

    La base no se inventa por separado: se construye a partir de los pedidos
    reales del canal propio para que cuadre con la facturación. De cada pedido
    de tienda o web se asume que una parte queda identificada (quien da su
    cédula o compra con cuenta); el resto son compras anónimas de mostrador.

    El proceso es de retención, no de conteo: después de cada compra el cliente
    vuelve con probabilidad `p` dentro de su ciclo, o deja de comprar. Así la
    tasa de recompra sale del modelo y no de un número puesto a mano.
    """
    IDENTIFICADO = 0.72
    d2c = ventas[ventas["tipo_canal"].isin(["Tienda propia", "E-commerce"])]
    pedidos_mes = (d2c.groupby("mes")["documento_id"].nunique() * IDENTIFICADO).round().astype(int)

    SEGMENTOS = [("Ganar músculo", 0.31), ("Bajar de peso", 0.27), ("Fuerza", 0.13),
                 ("Tonificar", 0.16), ("Bienestar general", 0.13)]
    P_VUELVE = {"Ganar músculo": 0.47, "Fuerza": 0.45, "Tonificar": 0.38,
                "Bajar de peso": 0.34, "Bienestar general": 0.28}
    CAPTACION = [("Meta Ads", 0.24), ("Google Ads", 0.17), ("Tienda física", 0.19),
                 ("TikTok Ads", 0.09), ("Megaplex Stars", 0.11), ("Orgánico / SEO", 0.10),
                 ("Referido", 0.06), ("Eventos & Ferias", 0.04)]
    PAGOS = [("Tarjeta de crédito", 0.32), ("PSE", 0.28), ("Addi", 0.15),
             ("Sistecrédito", 0.13), ("Nequi", 0.12)]

    # Ticket por segmento: quien financia con Addi o Sistecrédito se lleva el
    # tarro grande, y eso se nota en el ticket.
    TICKET_PAGO = {"Addi": 1.34, "Sistecrédito": 1.28, "Tarjeta de crédito": 1.02,
                   "PSE": 0.92, "Nequi": 0.80}

    clientes = {}          # id → registro
    proximos = {}          # índice de mes → lista de ids que vuelven ese mes
    n = 0
    for i, mes in enumerate(MESES):
        objetivo = int(pedidos_mes.get(mes, 0))
        vuelven = proximos.pop(i, [])
        vuelven = vuelven[:objetivo]
        nuevos = max(0, objetivo - len(vuelven))

        anio, m = int(mes[:4]), int(mes[5:])
        dias_mes = (date(anio + (m == 12), (m % 12) + 1, 1) - date(anio, m, 1)).days

        # Compras repetidas
        for cid in vuelven:
            c = clientes[cid]
            f = date(anio, m, int(RNG.integers(1, dias_mes + 1)))
            c["pedidos"] += 1
            c["ultima"] = max(c["ultima"], f)
            c["ciclos"].append(int(np.clip(RNG.normal(33, 7), 18, 62)))

        # Clientes nuevos del mes
        if nuevos:
            segs = elegir(SEGMENTOS, nuevos)
            caps = elegir(CAPTACION, nuevos)
            pags = elegir(PAGOS, nuevos)
            ciuds = elegir(CIUDADES_CO, nuevos)
            for j in range(nuevos):
                n += 1
                cid = f"CL-{n:06d}"
                f = date(anio, m, int(RNG.integers(1, dias_mes + 1)))
                base = float(np.clip(RNG.normal(196_000, 74_000), 32_000, 780_000))
                clientes[cid] = {
                    "cliente_id": cid, "primera": f, "ultima": f, "pedidos": 1,
                    "segmento": segs[j], "canal_captacion": caps[j], "medio_pago": pags[j],
                    "ciudad": ciuds[j], "ciclos": [],
                    "ticket": base * TICKET_PAGO[pags[j]],
                    "suscrito_crm": bool(RNG.random() < 0.58),
                }
            vuelven = list(vuelven) + [f"CL-{k:06d}" for k in range(n - nuevos + 1, n + 1)]

        # ¿Quién vuelve, y cuándo?
        for cid in vuelven:
            c = clientes[cid]
            if RNG.random() < P_VUELVE[c["segmento"]]:
                salto = 1 if RNG.random() < 0.78 else 2   # ciclo de ~1 mes, a veces 2
                if i + salto < len(MESES):
                    proximos.setdefault(i + salto, []).append(cid)

    filas = []
    for c in clientes.values():
        dias_sin = (HOY - c["ultima"]).days
        ciclo = int(np.mean(c["ciclos"])) if c["ciclos"] else 0
        recurrente = c["pedidos"] >= 2
        filas.append({
            "cliente_id": c["cliente_id"],
            "primera_compra": c["primera"].isoformat(),
            "ultima_compra": c["ultima"].isoformat(),
            "pedidos": c["pedidos"],
            "ticket_promedio_cop": int(c["ticket"]),
            "ltv_cop": int(c["ticket"] * c["pedidos"]),
            "segmento": c["segmento"], "canal_captacion": c["canal_captacion"],
            "medio_pago": c["medio_pago"], "ciudad": c["ciudad"],
            "recurrente": recurrente,
            "dias_sin_comprar": dias_sin,
            "ciclo_recompra_dias": ciclo,
            # Reactivable: ya volvió al menos una vez, se pasó de su ciclo, pero
            # todavía se acuerda de la marca. Pasados 180 días no es riesgo de
            # fuga: ya se fue.
            "en_riesgo_fuga": bool(recurrente and 60 <= dias_sin <= 180),
            "perdido": bool(recurrente and dias_sin > 180),
            "suscrito_crm": c["suscrito_crm"],
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "clientes.csv.gz", index=False, compression="gzip")
    return df


# ── PRODUCCIÓN (planta Palmira) ──────────────────────────────────────────────
def gen_produccion(prods: pd.DataFrame, ventas: pd.DataFrame):
    """Un lote por corrida, con su rendimiento, su merma y su estado de
    liberación. La planta tiene 2.500 m² y 1.000 t de capacidad declarada."""
    demanda = ventas.groupby(["mes", "sku"])["unidades"].sum().reset_index()
    pidx = prods.set_index("sku")
    turnos = ["Turno 1 (06-14)", "Turno 2 (14-22)", "Turno 3 (22-06)"]
    filas, n = [], 0
    for _, r in demanda.iterrows():
        p = pidx.loc[r["sku"]]
        objetivo = int(r["unidades"] * float(RNG.uniform(1.02, 1.18)))
        lotes = max(1, int(np.ceil(objetivo / RNG.integers(900, 2600))))
        for _ in range(lotes):
            n += 1
            plan = int(objetivo / lotes)
            merma = float(np.clip(RNG.normal(1.9, 0.9), 0.2, 7.5))
            real = int(plan * (1 - merma / 100))
            oee = float(np.clip(RNG.normal(76, 8.5), 45, 94))
            u = RNG.random()
            estado = "Aprobado" if u < 0.955 else ("Cuarentena" if u < 0.988 else "Rechazado")
            anio, m = int(r["mes"][:4]), int(r["mes"][5:])
            dia = int(RNG.integers(1, 28))
            filas.append({
                "lote_id": f"L{anio}{m:02d}-{n:05d}", "fecha": date(anio, m, dia).isoformat(),
                "mes": r["mes"], "sku": r["sku"], "producto": p["producto"],
                "marca": p["marca"], "categoria": p["categoria"], "linea": p["linea"],
                "turno": str(RNG.choice(turnos, p=[0.42, 0.38, 0.20])),
                "unidades_plan": plan, "unidades_producidas": real,
                "merma_pct": round(merma, 2), "oee_pct": round(oee, 1),
                "estado_calidad": estado,
                "horas_paro": round(float(np.clip(RNG.exponential(1.6), 0, 11)), 1),
                "costo_lote_cop": int(real * p["costo_unitario_cop"]),
                "kg_lote": round(real * float(RNG.uniform(0.35, 1.4)), 1),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "produccion.csv.gz", index=False, compression="gzip")
    return df


# ── CALIDAD Y REGULATORIO ────────────────────────────────────────────────────
def gen_calidad(produccion: pd.DataFrame, prods: pd.DataFrame):
    """Tres tablas: ensayos de laboratorio por lote, no conformidades del
    sistema FSSC 22000 y vigencia de los registros sanitarios INVIMA."""
    # 1) Ensayos de laboratorio sobre una muestra de lotes
    muestra = produccion.sample(n=min(2600, len(produccion)), random_state=7)
    ensayos = []
    for _, r in muestra.iterrows():
        prot_decl = float(RNG.uniform(22, 27))
        prot_real = prot_decl * float(np.clip(RNG.normal(1.015, 0.035), 0.90, 1.14))
        ensayos.append({
            "ensayo_id": f"EN-{len(ensayos)+1:05d}", "lote_id": r["lote_id"],
            "fecha": r["fecha"], "mes": r["mes"], "sku": r["sku"], "producto": r["producto"],
            "linea": r["linea"],
            "proteina_declarada_g": round(prot_decl, 1),
            "proteina_medida_g": round(prot_real, 1),
            "cumple_proteina": bool(prot_real >= prot_decl * 0.95),
            "humedad_pct": round(float(np.clip(RNG.normal(3.6, 0.8), 1.2, 6.9)), 2),
            "aerobios_ufc_g": int(np.clip(RNG.lognormal(6.4, 1.0), 10, 60_000)),
            "metales_pesados_ppm": round(float(np.clip(RNG.exponential(0.09), 0, 0.95)), 3),
            "metodo": str(RNG.choice(["NIR (analizador infrarrojo)", "Kjeldahl", "Microbiología",
                                      "Absorción atómica"], p=[0.55, 0.20, 0.17, 0.08])),
            "resultado": r["estado_calidad"],
        })
    df_en = pd.DataFrame(ensayos)
    df_en.to_csv(OUT / "ensayos_calidad.csv", index=False)

    # 2) No conformidades del sistema de gestión FSSC 22000
    clausulas = [
        ("Control de alérgenos", "Alta"), ("Trazabilidad de lote", "Alta"),
        ("Limpieza y sanitización", "Media"), ("Control de proveedores", "Media"),
        ("Calibración de equipos", "Media"), ("Control de plagas", "Alta"),
        ("Capacitación del personal", "Baja"), ("Etiquetado y rotulado", "Alta"),
        ("Cadena de frío de insumos", "Media"), ("Documentación de registros", "Baja"),
    ]
    nc = []
    for i in range(74):
        cl, sev = clausulas[int(RNG.integers(0, len(clausulas)))]
        fdet = date(2025, 1, 1) + timedelta(days=int(RNG.integers(0, (HOY - date(2025, 1, 1)).days)))
        cerrada = RNG.random() < 0.80
        dias_cierre = int(np.clip(RNG.normal(21, 12), 2, 95)) if cerrada else None
        nc.append({
            "nc_id": f"NC-{i+1:03d}", "fecha_deteccion": fdet.isoformat(),
            "mes": fdet.strftime("%Y-%m"), "clausula": cl, "severidad": sev,
            "origen": str(RNG.choice(["Auditoría interna", "Auditoría de certificación",
                                      "Inspección INVIMA", "Reporte de planta", "Queja de cliente"],
                                     p=[0.34, 0.14, 0.10, 0.30, 0.12])),
            "estado": "Cerrada" if cerrada else "Abierta",
            "dias_cierre": dias_cierre,
            "vencida": bool(not cerrada and (HOY - fdet).days > 30),
        })
    df_nc = pd.DataFrame(nc)
    df_nc.to_csv(OUT / "no_conformidades.csv", index=False)

    # 3) Registros sanitarios INVIMA por producto
    reg = []
    for _, p in prods.iterrows():
        if p["categoria"] == "Merch":
            continue
        real = INVIMA_REALES.get(p["sku"])
        if real:
            numero = real
            anio_exp = int(real.split("-")[-1])
        else:
            anio_exp = int(RNG.integers(2017, 2027))
            pref = "RSA" if anio_exp < 2022 else "NSA"
            numero = f"{pref}-{int(RNG.integers(1_000, 99_999)):07d}-{anio_exp}"
        vence = date(anio_exp + 10, int(RNG.integers(1, 13)), int(RNG.integers(1, 28)))
        dias = (vence - HOY).days
        estado = "Vencido" if dias < 0 else ("Por vencer" if dias < 365 else "Vigente")
        reg.append({
            "sku": p["sku"], "producto": p["producto"], "marca": p["marca"],
            "categoria": p["categoria"], "registro_invima": numero,
            "tipo": "Registro sanitario" if numero.startswith("RSA") else "Notificación sanitaria",
            "fecha_expedicion": f"{anio_exp}-{int(RNG.integers(1,13)):02d}-15",
            "fecha_vencimiento": vence.isoformat(), "dias_para_vencer": dias,
            "estado": estado, "fuente": "Publicado por la compañía" if real else "Simulado",
        })
    df_reg = pd.DataFrame(reg).sort_values("dias_para_vencer")
    df_reg.to_csv(OUT / "registros_invima.csv", index=False)

    # 4) Farmacovigilancia: eventos adversos reportados
    eventos = [("Parestesia por beta-alanina", "Leve", 0.30), ("Molestia gastrointestinal", "Leve", 0.26),
               ("Insomnio o taquicardia por cafeína", "Moderado", 0.18),
               ("Reacción cutánea / prurito", "Moderado", 0.12),
               ("Cefalea", "Leve", 0.09), ("Retención de líquidos", "Leve", 0.05)]
    fv = []
    for i in range(96):
        e = eventos[int(RNG.choice(len(eventos), p=[x[2] for x in eventos]))]
        f = date(2025, 1, 1) + timedelta(days=int(RNG.integers(0, (HOY - date(2025, 1, 1)).days)))
        fv.append({
            "reporte_id": f"FV-{i+1:03d}", "fecha": f.isoformat(), "mes": f.strftime("%Y-%m"),
            "evento": e[0], "severidad": e[1],
            "sku": str(RNG.choice(prods[prods["categoria"] != "Merch"]["sku"])),
            "canal_reporte": str(RNG.choice(["WhatsApp", "Chat del sitio", "Tienda física",
                                             "Línea gratuita #590"], p=[0.48, 0.24, 0.16, 0.12])),
            "estado": str(RNG.choice(["Cerrado", "En análisis"], p=[0.83, 0.17])),
            "dias_respuesta": int(np.clip(RNG.normal(2.4, 1.5), 0, 14)),
        })
    pd.DataFrame(fv).to_csv(OUT / "farmacovigilancia.csv", index=False)
    return df_en, df_nc, df_reg


# ── ABASTECIMIENTO E IMPORTACIONES ───────────────────────────────────────────
def gen_compras(prov: pd.DataFrame, trm: pd.DataFrame, produccion: pd.DataFrame):
    """La compañía importa del orden de 120 toneladas trimestrales de proteína
    de suero. Se paga en dólares y se vende en pesos: cada peso que se mueve
    la TRM entre la orden y el pago cambia el costo del producto."""
    trm_idx = trm.set_index("mes")["trm_cop_usd"].to_dict()
    filas = []
    n = 0
    for mes in MESES:
        anio, m = int(mes[:4]), int(mes[5:])
        for _, p in prov.iterrows():
            # Las materias primas críticas se compran todos los meses;
            # las demás según su rotación.
            if not p["critico"] and RNG.random() > 0.55:
                continue
            n += 1
            if p["insumo"].startswith("Proteína de suero WPC"):
                kg = float(RNG.normal(26_000, 3_200))
                usd_kg = float(RNG.normal(8.4, 0.55))
            elif p["insumo"].startswith("Proteína de suero aislada"):
                kg = float(RNG.normal(9_500, 1_400))
                usd_kg = float(RNG.normal(14.2, 0.9))
            elif p["insumo"].startswith("Caseinato"):
                kg = float(RNG.normal(4_800, 800))
                usd_kg = float(RNG.normal(11.1, 0.7))
            elif p["insumo"].startswith("Creatina"):
                kg = float(RNG.normal(3_200, 500))
                usd_kg = float(RNG.normal(12.6, 1.1))
            else:
                kg = float(RNG.normal(6_500, 2_400))
                usd_kg = float(RNG.uniform(1.4, 9.0))
            kg = max(300.0, kg)
            trm_orden = trm_idx[mes]
            mes_pago_i = min(len(MESES) - 1, MESES.index(mes) + (2 if p["moneda"] != "COP" else 0))
            trm_pago = trm_idx[MESES[mes_pago_i]]
            valor_usd = kg * usd_kg if p["moneda"] != "COP" else 0.0
            if p["moneda"] == "COP":
                costo_cop = kg * usd_kg * 3_900
                dif_cambio = 0.0
            else:
                costo_cop = valor_usd * trm_orden
                dif_cambio = valor_usd * (trm_pago - trm_orden)
            # El atraso no es aleatorio parejo: depende de qué tan cumplido es
            # cada proveedor. Un premix suizo y una cafeína importada de Asia
            # no se comportan igual.
            mu = (8.8 - float(p["score_puntualidad"])) * 3.5
            atraso = int(np.clip(RNG.normal(mu, 5.5), -9, 46))
            filas.append({
                "oc_id": f"OC-{anio}{m:02d}-{n:04d}", "mes": mes,
                "fecha_orden": date(anio, m, int(RNG.integers(1, 28))).isoformat(),
                "proveedor_id": p["proveedor_id"], "insumo": p["insumo"], "origen": p["origen"],
                "moneda": p["moneda"], "critico": int(p["critico"]),
                "kg": round(kg, 1), "precio_unitario_usd": round(usd_kg, 2),
                "valor_usd": round(valor_usd, 2), "trm_orden": trm_orden, "trm_pago": trm_pago,
                "costo_cop": int(costo_cop), "diferencia_en_cambio_cop": int(dif_cambio),
                "lead_time_plan_dias": int(p["lead_time_dias"]),
                "lead_time_real_dias": int(p["lead_time_dias"] + atraso),
                "dias_atraso": atraso, "a_tiempo": bool(atraso <= 5),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "compras.csv", index=False)
    return df


# ── INVENTARIO MULTI-BODEGA ──────────────────────────────────────────────────
def gen_inventario(prods: pd.DataFrame, ventas: pd.DataFrame, bodegas: pd.DataFrame):
    ult3 = sorted(ventas["mes"].unique())[-3:]
    dem = ventas[ventas["mes"].isin(ult3)].groupby("sku")["unidades"].sum() / 90.0
    filas = []
    for _, p in prods.iterrows():
        d_total = float(dem.get(p["sku"], 1.0))
        for _, b in bodegas.iterrows():
            d = max(0.12, d_total * b["peso"])
            cobertura = float(np.clip(RNG.normal(34, 17), 2, 95))
            stock = int(d * cobertura)
            estado = ("Crítico" if cobertura < 12 else "Bajo" if cobertura < 22
                      else "Normal" if cobertura < 60 else "Exceso")
            filas.append({
                "sku": p["sku"], "producto": p["producto"], "marca": p["marca"],
                "categoria": p["categoria"], "bodega_id": b["bodega_id"], "bodega": b["bodega"],
                "ciudad": b["ciudad"], "tipo_bodega": b["tipo"],
                "stock_unidades": stock, "demanda_diaria": round(d, 2),
                "dias_cobertura": round(cobertura, 1),
                "valor_inventario_cop": int(stock * p["costo_unitario_cop"]),
                "estado": estado,
                "lote_mas_antiguo_dias": int(np.clip(RNG.normal(95, 60), 3, 420)),
            })
    df = pd.DataFrame(filas)
    df["proximo_a_vencer"] = df["lote_mas_antiguo_dias"] > 300
    df.to_csv(OUT / "inventario.csv", index=False)
    return df


# ── DESPACHOS ────────────────────────────────────────────────────────────────
def gen_despachos(ventas: pd.DataFrame):
    """Los tiempos objetivo son los que la propia compañía publica: Bogotá y
    Medellín salen por MELONN con entrega el mismo día o al siguiente; las
    ciudades principales entre 1 y 3 días hábiles; el resto del país 2 a 3."""
    base = ventas[ventas["canal"] != "Tiendas Nutramerican"].copy()
    base = base.sample(n=min(52_000, len(base)), random_state=13)
    sla = {"Bogotá": 1, "Medellín": 1, "Cali": 2, "Bucaramanga": 3, "Cúcuta": 3,
           "Barranquilla": 3, "Pereira": 3}
    # Cada transportadora cumple distinto, y esa diferencia es el insumo de la
    # negociación de tarifas. Sin ella el módulo compararía ruido.
    PUNTUALIDAD = {"MELONN": 0.960, "Flota propia (Valle)": 0.952, "Coordinadora": 0.941,
                   "Servientrega": 0.930, "TCC": 0.922, "Interrapidísimo": 0.897,
                   "Comercio exterior": 0.868}
    # Las ciudades sin operación propia dependen de un tercero para la última milla
    PENALIDAD_CIUDAD = {"Bogotá": 0.0, "Medellín": 0.0, "Cali": 0.0, "Barranquilla": 0.012,
                        "Bucaramanga": 0.015, "Pereira": 0.012, "Cúcuta": 0.030,
                        "Santa Marta": 0.035, "Pasto": 0.042, "Neiva": 0.030}
    filas = []
    for i, r in enumerate(base.itertuples(index=False)):
        if r.pais != "Colombia":
            transp, plan = "Comercio exterior", int(RNG.integers(12, 34))
        elif r.ciudad in ("Bogotá", "Medellín"):
            transp, plan = "MELONN", sla[r.ciudad]
        else:
            transp = str(RNG.choice(["Coordinadora", "Servientrega", "TCC", "Interrapidísimo",
                                     "Flota propia (Valle)"], p=[0.28, 0.24, 0.18, 0.20, 0.10]))
            plan = sla.get(r.ciudad, 3)

        p_ok = PUNTUALIDAD[transp] - PENALIDAD_CIUDAD.get(r.ciudad, 0.020)
        u = RNG.random()
        if u < p_ok:
            # Llega a tiempo, y de vez en cuando antes de lo prometido
            desv = -1 if (plan > 1 and RNG.random() < 0.22) else 0
        elif u < p_ok + 0.035:
            desv = 1
        elif u < p_ok + 0.055:
            desv = int(RNG.integers(2, 4))
        else:
            desv = int(RNG.integers(4, 13))
        real = max(1, plan + desv)
        fp = pd.Timestamp(r.fecha)
        estado = "Entregado"
        u2 = RNG.random()
        if u2 > 0.978:
            estado = "En tránsito"
        elif u2 > 0.9715:
            estado = "Devuelto"
        completo = RNG.random() < 0.978
        filas.append({
            "despacho_id": f"DES-{i+1:06d}", "documento_id": r.documento_id,
            "fecha_pedido": fp.date().isoformat(),
            "fecha_prometida": (fp + timedelta(days=plan)).date().isoformat(),
            "fecha_entrega": (fp + timedelta(days=real)).date().isoformat() if estado == "Entregado" else "",
            "mes": r.mes, "canal": r.canal, "tipo_canal": r.tipo_canal, "pais": r.pais,
            "ciudad": r.ciudad, "transportadora": transp, "estado": estado,
            "dias_plan": plan, "dias_reales": real if estado == "Entregado" else None,
            "a_tiempo": bool(estado == "Entregado" and real <= plan),
            "completo": bool(completo),
            "otif": bool(estado == "Entregado" and real <= plan and completo),
            "unidades": int(r.unidades), "valor_cop": int(r.venta_cop),
            "costo_logistico_cop": int(r.venta_cop * float(np.clip(RNG.normal(0.062, 0.02), 0.02, 0.16))),
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "despachos.csv.gz", index=False, compression="gzip")
    return df


# ── CARTERA ──────────────────────────────────────────────────────────────────
def gen_cartera(ventas: pd.DataFrame, canales: pd.DataFrame):
    """Solo se financia lo que se vende a terceros: la tienda propia y la web
    cobran de contado. Distribuidores a 45 días, cadenas y farmacias a 75."""
    plazos = canales.set_index("canal")["plazo_pago_dias"].to_dict()
    cred = ventas[ventas["canal"].map(plazos).fillna(0) > 0]
    clientes_por_canal = {
        "Distribuidores": ["Suples Colombia", "MiProteína", "Suplementos Colombia",
                           "Nutrición Total", "Distribuidora Andina", "Mundo Fitness",
                           "Vital Supplements", "Anabólicos del Valle"],
        "Cadenas & Farmacias": ["Farmatodo", "Cruz Verde", "Droguerías La Rebaja",
                                "Éxito", "Locatel", "Olímpica"],
        "Gimnasios & Wellness": ["Bodytech", "Smart Fit", "Stark Gym", "Gimnasios independientes"],
        "Maquila & Marca Propia": ["Cliente maquila lácteos", "Marca privada retail",
                                   "Marca privada gimnasios"],
    }
    agg = cred.groupby(["mes", "canal", "tipo_canal", "pais"])["venta_cop"].sum().reset_index()
    filas = []
    for i, r in enumerate(agg.itertuples(index=False)):
        nombres = clientes_por_canal.get(r.canal, [f"Distribuidor {r.pais}"])
        n_fact = len(nombres)
        for j, nombre in enumerate(nombres):
            valor = int(r.venta_cop / n_fact * float(RNG.uniform(0.55, 1.45)))
            if valor < 500_000:
                continue
            anio, m = int(r.mes[:4]), int(r.mes[5:])
            femi = date(anio, m, int(RNG.integers(1, 28)))
            plazo = plazos[r.canal]
            fven = femi + timedelta(days=plazo)
            dias_mora = max(0, (HOY - fven).days)
            # Cuanto más viejo el vencimiento, más probable que ya esté pagada
            # Cuanto más viejo el vencimiento, más probable que ya esté pagada.
            # Lo que queda arriba de 90 días es la cartera que de verdad duele.
            p_pago = 0.988 if dias_mora > 120 else 0.962 if dias_mora > 60 else \
                     0.905 if dias_mora > 20 else 0.74 if dias_mora > 0 else 0.05
            pagada = RNG.random() < p_pago
            mora = 0 if pagada else dias_mora
            estado = ("Al día" if mora == 0 else "Vencida 1-30" if mora <= 30 else
                      "Vencida 31-60" if mora <= 60 else "Vencida 61-90" if mora <= 90 else "Vencida +90")
            filas.append({
                "factura_id": f"FV-{anio}{m:02d}-{i:04d}{j}", "cliente": nombre,
                "canal": r.canal, "tipo_canal": r.tipo_canal, "pais": r.pais, "mes": r.mes,
                "fecha_factura": femi.isoformat(), "fecha_vencimiento": fven.isoformat(),
                "plazo_dias": plazo, "valor_cop": valor, "pagada": pagada,
                "dias_mora": mora, "estado": "Al día" if pagada else estado,
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "cartera.csv", index=False)
    return df


# ── MARKETING Y EMBAJADORES ──────────────────────────────────────────────────
def gen_marketing(ventas: pd.DataFrame, clientes: pd.DataFrame):
    d2c = ventas[ventas["tipo_canal"].isin(["E-commerce", "Tienda propia"])]
    ing_mes = d2c.groupby("mes")["venta_cop"].sum().to_dict()
    nuevos = clientes.copy()
    nuevos["mes"] = pd.to_datetime(nuevos["primera_compra"]).dt.strftime("%Y-%m")
    nuevos_mes = nuevos.groupby("mes").size().to_dict()

    pesos = {"Meta Ads": 0.29, "Google Ads": 0.19, "TikTok Ads": 0.12, "YouTube": 0.06,
             "Email & CRM": 0.03, "WhatsApp": 0.03, "Megaplex Stars": 0.16,
             "Orgánico / SEO": 0.0, "Eventos & Ferias": 0.12}
    filas = []
    for mes in MESES:
        ing = ing_mes.get(mes, 0)
        inv_total = ing * float(np.clip(RNG.normal(0.125, 0.018), 0.07, 0.19))
        nn = nuevos_mes.get(mes, 1)
        for c in CANALES_MKT:
            inv = inv_total * pesos[c]
            roas = MKT_ROAS_OBJ.get(c, 0) * float(np.clip(RNG.normal(1, 0.16), 0.55, 1.6))
            ingresos = inv * roas if inv > 0 else ing * 0.13 * float(RNG.uniform(0.8, 1.2))
            share = pesos[c] if pesos[c] > 0 else 0.10
            filas.append({
                "mes": mes, "canal": c, "inversion_cop": int(inv),
                "ingresos_cop": int(ingresos),
                "roas": round(ingresos / inv, 2) if inv > 0 else None,
                "clientes_nuevos": int(nn * share * float(RNG.uniform(0.75, 1.25))),
                "impresiones": int(inv / float(RNG.uniform(11, 26))) if inv > 0 else int(RNG.integers(80_000, 460_000)),
                "clics": int(inv / float(RNG.uniform(680, 1900))) if inv > 0 else int(RNG.integers(4_000, 22_000)),
            })
    df = pd.DataFrame(filas)
    df["cac_cop"] = (df["inversion_cop"] / df["clientes_nuevos"].replace(0, np.nan)).round(0)
    df.to_csv(OUT / "marketing.csv", index=False)

    # Programa de embajadores Megaplex Stars
    emb = []
    for i in range(34):
        disc = DISCIPLINAS[int(RNG.integers(0, len(DISCIPLINAS)))]
        ciudad = elegir(CIUDADES_CO, 1)[0]
        seg = int(np.clip(RNG.lognormal(10.2, 1.15), 2_500, 640_000))
        costo = int(np.clip(RNG.normal(2_400_000, 1_500_000), 400_000, 12_000_000))
        eng = float(np.clip(RNG.normal(4.1, 1.7), 0.6, 11.5))
        cod = int(np.clip(RNG.normal(seg * 0.0022, seg * 0.0016), 2, 4_200))
        emb.append({
            "embajador_id": f"MS-{i+1:03d}", "disciplina": disc, "ciudad": ciudad,
            "seguidores": seg, "engagement_pct": round(eng, 2),
            "contenidos_mes": int(np.clip(RNG.normal(5.4, 2.6), 1, 16)),
            "costo_mensual_cop": costo,
            "pedidos_con_codigo": cod,
            "venta_atribuida_cop": int(cod * float(RNG.normal(172_000, 42_000))),
            "activo_desde": (date(2025, 1, 1) + timedelta(days=int(RNG.integers(0, 560)))).isoformat(),
        })
    df_emb = pd.DataFrame(emb)
    df_emb["roi"] = (df_emb["venta_atribuida_cop"] / df_emb["costo_mensual_cop"]).round(2)
    df_emb.to_csv(OUT / "embajadores.csv", index=False)

    # Ferias y eventos reales en los que participa la compañía
    eventos = [
        ("Feria Belleza y Salud · Corferias", "Bogotá", "2026-06-12", 78_000_000, "Lanzamiento Prime W Collagen Stack"),
        ("Congreso Deportivo de Barranquilla", "Barranquilla", "2026-06-28", 26_000_000, "Alianzas con entrenadores"),
        ("Feria de Belleza y Bienestar Farmatodo", "Bogotá", "2026-07-10", 34_000_000, "Reconocimiento Proveedor Revelación"),
        ("Expo Fitness Medellín", "Medellín", "2026-03-15", 41_000_000, "Activación Megaplex Stars"),
        ("Feria del Deporte Cali", "Cali", "2025-11-08", 29_000_000, "Apertura de temporada"),
        ("Arnold Classic South America", "São Paulo", "2026-04-24", 96_000_000, "Prospección de exportación"),
    ]
    ev = []
    for i, (nom, ciu, f, inv, obj) in enumerate(eventos):
        leads = int(inv / float(RNG.uniform(24_000, 62_000)))
        ev.append({
            "evento_id": f"EV-{i+1:03d}", "evento": nom, "ciudad": ciu, "fecha": f,
            "mes": f[:7], "inversion_cop": inv, "objetivo": obj,
            "leads": leads, "ventas_directas_cop": int(inv * float(RNG.uniform(0.7, 2.6))),
            "nuevos_clientes": int(leads * float(RNG.uniform(0.12, 0.32))),
        })
    pd.DataFrame(ev).to_csv(OUT / "eventos.csv", index=False)
    return df, df_emb


# ── SERVICIO AL CLIENTE / PQR ────────────────────────────────────────────────
def gen_pqr(ventas: pd.DataFrame):
    """La compañía atiende por WhatsApp, línea gratuita #590, chat del sitio,
    redes y tienda física. Este módulo separa lo que es ruido de lo que es
    señal: un faltante repetido en un mismo SKU es un problema de picking."""
    ventas_mes = ventas.groupby("mes")["documento_id"].nunique().to_dict()
    motivos = [m[0] for m in MOTIVOS_PQR]
    pesos = np.array([m[1] for m in MOTIVOS_PQR])
    sla_factor = {m[0]: m[2] for m in MOTIVOS_PQR}
    filas, n = [], 0
    for mes in MESES:
        base = ventas_mes.get(mes, 200)
        n_pqr = int(base * float(np.clip(RNG.normal(0.028, 0.006), 0.012, 0.055)))
        for _ in range(n_pqr):
            n += 1
            mot = str(RNG.choice(motivos, p=pesos / pesos.sum()))
            canal = str(elegir(CANALES_PQR, 1)[0])
            anio, m = int(mes[:4]), int(mes[5:])
            f = date(anio, m, int(RNG.integers(1, 28)))
            resp_h = float(np.clip(RNG.exponential(2.4) * sla_factor[mot] * VELOCIDAD_PQR[canal],
                                   0.05, 96))
            cierre_h = resp_h + float(np.clip(RNG.exponential(26) * sla_factor[mot], 1, 340))
            abierto = (HOY - f).days < 6 and RNG.random() < 0.55
            escalado = mot in ("Evento adverso reportado", "Camiseta personalizada pendiente",
                               "Contenido incompleto del envase") and RNG.random() < 0.45
            csat = int(np.clip(RNG.normal(4.3 - (0.9 if cierre_h > 72 else 0), 0.8), 1, 5))
            filas.append({
                "pqr_id": f"PQR-{anio}{m:02d}-{n:05d}", "fecha": f.isoformat(), "mes": mes,
                "motivo": mot, "canal": canal,
                "ciudad": str(elegir(CIUDADES_CO, 1)[0]),
                "estado": "Abierto" if abierto else ("Escalado" if escalado else "Cerrado"),
                "horas_primera_respuesta": round(resp_h, 1),
                "horas_cierre": round(cierre_h, 1) if not abierto else None,
                "cumple_sla_4h": bool(resp_h <= 4),
                "csat": csat if not abierto else None,
                "requiere_agente_humano": bool(escalado or mot == "Evento adverso reportado"),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "pqr.csv", index=False)
    return df


# ── EMPLEADOS ────────────────────────────────────────────────────────────────
def gen_empleados():
    SMLV = 1_423_500  # salario mínimo 2026 (referencia demo)
    filas, n = [], 0
    for area, cant, (lo, hi) in AREAS:
        for _ in range(cant):
            n += 1
            sal = int(RNG.uniform(lo, hi))
            ing = date(2015, 1, 1) + timedelta(days=int(RNG.integers(0, 4_100)))
            filas.append({
                "empleado_id": f"EMP-{n:04d}", "area": area, "salario_cop": sal,
                "fecha_ingreso": ing.isoformat(),
                "antiguedad_anios": round((HOY - ing).days / 365.25, 1),
                "tipo_contrato": str(RNG.choice(["Indefinido", "Fijo", "Obra o labor"],
                                                p=[0.68, 0.22, 0.10])),
                "sede": str(RNG.choice(["Planta Palmira", "CD Yumbo", "Tiendas", "Oficina Cali"],
                                       p=[0.44, 0.16, 0.22, 0.18])),
                "ausentismo_dias_anio": int(np.clip(RNG.exponential(4.2), 0, 42)),
                "rotacion_riesgo": str(RNG.choice(["Bajo", "Medio", "Alto"], p=[0.66, 0.25, 0.09])),
                "costo_total_cop": int(sal * 1.52),  # prestaciones + seguridad social
                "sobre_smlv": round(sal / SMLV, 2),
            })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "empleados.csv", index=False)
    return df


# ── P&G MENSUAL ──────────────────────────────────────────────────────────────
def gen_finanzas(ventas, marketing, empleados, despachos, compras):
    mkt = marketing.groupby("mes")["inversion_cop"].sum().to_dict()
    log = despachos.groupby("mes")["costo_logistico_cop"].sum().to_dict()
    fx = compras.groupby("mes")["diferencia_en_cambio_cop"].sum().to_dict()
    nomina_mes = int(empleados["costo_total_cop"].sum())
    filas = []
    for mes in MESES:
        v = ventas[ventas["mes"] == mes]
        ing = int(v["venta_cop"].sum())
        cogs = int(v["costo_cop"].sum())
        bruto = ing - cogs
        g_mkt = int(mkt.get(mes, 0))
        g_log = int(log.get(mes, 0) * 1.9)     # el muestreo de despachos escala
        g_nom = int(nomina_mes * float(RNG.uniform(0.97, 1.03)))
        g_adm = int(ing * float(np.clip(RNG.normal(0.052, 0.006), 0.03, 0.08)))
        g_tda = int(ing * float(np.clip(RNG.normal(0.031, 0.004), 0.02, 0.05)))
        ebitda = bruto - g_mkt - g_log - g_nom - g_adm - g_tda
        dep = int(ing * 0.021)
        fin = int(ing * float(np.clip(RNG.normal(0.017, 0.004), 0.008, 0.03)))
        dif = int(fx.get(mes, 0))
        antes_imp = ebitda - dep - fin + dif
        filas.append({
            "mes": mes, "ingresos_cop": ing, "costo_ventas_cop": cogs,
            "margen_bruto_cop": bruto,
            "margen_bruto_pct": round(bruto / ing * 100, 1) if ing else 0,
            "gasto_marketing_cop": g_mkt, "gasto_logistica_cop": g_log,
            "gasto_nomina_cop": g_nom, "gasto_admin_cop": g_adm, "gasto_tiendas_cop": g_tda,
            "ebitda_cop": ebitda,
            "ebitda_pct": round(ebitda / ing * 100, 1) if ing else 0,
            "depreciacion_cop": dep, "gasto_financiero_cop": fin,
            "diferencia_en_cambio_cop": dif,
            "utilidad_antes_impuestos_cop": antes_imp,
            "utilidad_neta_cop": int(antes_imp * 0.65),
        })
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "finanzas_mensual.csv", index=False)
    return df


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("Generando datos del demo de Nutramerican Pharma…")
    prods, canales, tiendas, bodegas, prov, trm = gen_maestros()
    print(f"  maestros            → {len(prods)} SKU · {len(canales)} canales · {len(tiendas)} tiendas")
    precios = gen_precios_canal(prods, canales)
    print(f"  precios por canal   → {len(precios):,}")
    ventas = gen_ventas(prods, canales, tiendas)
    print(f"  ventas              → {len(ventas):,} líneas · {ventas['unidades'].sum():,} unidades")
    tmens = gen_trafico_tiendas(ventas, tiendas)
    print(f"  tiendas mensual     → {len(tmens):,}")
    clientes = gen_clientes(ventas)
    print(f"  clientes            → {len(clientes):,}")
    produccion = gen_produccion(prods, ventas)
    print(f"  producción          → {len(produccion):,} lotes")
    gen_calidad(produccion, prods)
    print("  calidad             → ensayos, no conformidades, INVIMA y farmacovigilancia")
    compras = gen_compras(prov, trm, produccion)
    print(f"  compras             → {len(compras):,} órdenes")
    gen_inventario(prods, ventas, bodegas)
    print("  inventario          → multi-bodega")
    despachos = gen_despachos(ventas)
    print(f"  despachos           → {len(despachos):,}")
    gen_cartera(ventas, canales)
    print("  cartera             → lista")
    marketing, emb = gen_marketing(ventas, clientes)
    print(f"  marketing           → {len(marketing):,} · {len(emb)} embajadores")
    pqr = gen_pqr(ventas)
    print(f"  PQR                 → {len(pqr):,}")
    empleados = gen_empleados()
    print(f"  empleados           → {len(empleados):,}")
    fin = gen_finanzas(ventas, marketing, empleados, despachos, compras)
    print(f"  finanzas            → {len(fin)} meses")
    ult = fin.iloc[-1]
    print(f"\nÚltimo mes ({ult['mes']}): ingresos {ult['ingresos_cop']/1e6:,.0f}M COP · "
          f"margen bruto {ult['margen_bruto_pct']}% · EBITDA {ult['ebitda_pct']}%")
    print(f"Unidades 2026 (ene-ago): {ventas[ventas['mes']>='2026-01']['unidades'].sum():,}")
    print("Listo.")


if __name__ == "__main__":
    main()
