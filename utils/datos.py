"""
Carga de datos compartida y cacheada.

Todos los módulos leen de aquí para que cada tabla se cargue UNA sola vez en
memoria: `st.cache_data` cachea por función, así que si cada módulo definiera
su propio loader se guardaría una copia por módulo. Con quince módulos leyendo
ventas eso serían quince copias de la misma tabla.

Sobre los tipos: se hace downcast de las columnas numéricas, que es seguro.
NO se convierte el texto a `category` a propósito: al agrupar por columnas
categóricas pandas devuelve también las combinaciones que no existen, lo que
metería filas en cero en las gráficas (por ejemplo, España facturando $0 en
los meses anteriores a su apertura). Preferimos gastar algo más de memoria
antes que dibujar un dato que no ocurrió.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

_DATA = Path(__file__).parent.parent / "data"


def _leer(nombre: str, **kw) -> pd.DataFrame:
    kw.setdefault("low_memory", False)
    for candidato in (_DATA / nombre, _DATA / f"{nombre}.gz"):
        if candidato.exists():
            return pd.read_csv(candidato, **kw)
    raise FileNotFoundError(f"No se encontró {nombre} en {_DATA}")


def _numerico(df: pd.DataFrame, enteros=(), flotantes=()) -> pd.DataFrame:
    for c in enteros:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="integer")
    for c in flotantes:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="float")
    return df


@st.cache_data(show_spinner="Cargando ventas…")
def ventas(con_fecha: bool = True) -> pd.DataFrame:
    df = _leer("ventas.csv")
    df = _numerico(df,
                   enteros=["unidades", "precio_gondola_cop", "precio_neto_cop",
                            "venta_cop", "costo_cop", "margen_cop"],
                   flotantes=["descuento_pct", "margen_pct"])
    if con_fecha:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


@st.cache_data(show_spinner="Cargando despachos…")
def despachos(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("despachos.csv")
    df = _numerico(df, enteros=["dias_plan", "unidades", "valor_cop", "costo_logistico_cop"],
                   flotantes=["dias_reales"])
    if con_fechas:
        for c in ("fecha_pedido", "fecha_prometida", "fecha_entrega"):
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


@st.cache_data(show_spinner="Cargando clientes…")
def clientes(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("clientes.csv")
    df = _numerico(df, enteros=["pedidos", "ticket_promedio_cop", "ltv_cop",
                                "dias_sin_comprar", "ciclo_recompra_dias"])
    if con_fechas:
        df["primera_compra"] = pd.to_datetime(df["primera_compra"])
        df["ultima_compra"] = pd.to_datetime(df["ultima_compra"])
    return df


@st.cache_data(show_spinner="Cargando producción…")
def produccion(con_fecha: bool = True) -> pd.DataFrame:
    df = _leer("produccion.csv")
    if con_fecha:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


@st.cache_data
def finanzas() -> pd.DataFrame:
    return _leer("finanzas_mensual.csv")


@st.cache_data
def cartera(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("cartera.csv")
    if con_fechas:
        for c in ("fecha_factura", "fecha_vencimiento"):
            df[c] = pd.to_datetime(df[c])
    return df


@st.cache_data
def productos() -> pd.DataFrame:
    return _leer("productos.csv")


@st.cache_data
def canales() -> pd.DataFrame:
    return _leer("canales.csv")


@st.cache_data
def tiendas() -> pd.DataFrame:
    return _leer("tiendas.csv")


@st.cache_data
def tiendas_mensual() -> pd.DataFrame:
    return _leer("tiendas_mensual.csv")


@st.cache_data
def bodegas() -> pd.DataFrame:
    return _leer("bodegas.csv")


@st.cache_data
def inventario() -> pd.DataFrame:
    return _leer("inventario.csv")


@st.cache_data
def precios_canal() -> pd.DataFrame:
    return _leer("precios_canal.csv")


@st.cache_data
def proveedores() -> pd.DataFrame:
    return _leer("proveedores.csv")


@st.cache_data
def compras() -> pd.DataFrame:
    return _leer("compras.csv")


@st.cache_data
def trm() -> pd.DataFrame:
    return _leer("trm.csv")


@st.cache_data
def marketing() -> pd.DataFrame:
    return _leer("marketing.csv")


@st.cache_data
def embajadores() -> pd.DataFrame:
    return _leer("embajadores.csv")


@st.cache_data
def eventos() -> pd.DataFrame:
    return _leer("eventos.csv")


@st.cache_data
def ensayos() -> pd.DataFrame:
    return _leer("ensayos_calidad.csv")


@st.cache_data
def no_conformidades() -> pd.DataFrame:
    return _leer("no_conformidades.csv")


@st.cache_data
def registros_invima() -> pd.DataFrame:
    return _leer("registros_invima.csv")


@st.cache_data
def farmacovigilancia() -> pd.DataFrame:
    return _leer("farmacovigilancia.csv")


@st.cache_data
def pqr() -> pd.DataFrame:
    return _leer("pqr.csv")


@st.cache_data
def empleados() -> pd.DataFrame:
    return _leer("empleados.csv")
