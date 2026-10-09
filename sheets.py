"""
sheets.py
=========
Capa de datos y utilidades de la app "Mis Gastos".

Responsabilidades:
- Conectar con Google Sheets mediante una service account (assets/credentials.json).
- Crear automáticamente las pestañas Movimientos, Categorias y Config.
- Leer / escribir movimientos y categorías con caché de Streamlit.
- Utilidades globales: fmt(), parse_entero(), fechas en America/Bogota.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import gspread
import pandas as pd
import streamlit as st
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
ZONA = ZoneInfo("America/Bogota")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "assets", "credentials.json")

TAB_MOV = "Movimientos"
TAB_CAT = "Categorias"
TAB_CFG = "Config"

COLS_MOV = ["fecha_hora", "tipo", "categoria", "nombre", "monto"]
CATEGORIAS_DEFAULT = ["Alimentación", "Transporte", "Servicios", "Ocio", "Salud", "Otros"]
CONFIG_DEFAULT = {"usuario": "Usuario", "moneda": "COP"}

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


# ---------------------------------------------------------------------------
# Utilidades globales
# ---------------------------------------------------------------------------
def bogota_now() -> datetime:
    """Fecha/hora actual en la zona horaria America/Bogota (UTC-5)."""
    return datetime.now(ZONA)


def fmt(valor: Any) -> str:
    """Formatea un número como pesos colombianos: $1.250.000"""
    try:
        n = int(round(float(valor)))
    except (TypeError, ValueError):
        return "$0"
    signo = "-" if n < 0 else ""
    return f"{signo}${abs(n):,}".replace(",", ".")


def parse_entero(texto: Any) -> Optional[int]:
    """
    Devuelve un entero > 0 a partir de un texto, o None si es inválido.
    Rechaza puntos, comas, signos y espacios (solo dígitos).
    """
    if texto is None:
        return None
    s = str(texto).strip()
    if not s or not s.isdigit():
        return None
    n = int(s)
    return n if n > 0 else None


def mes_label(ym: str) -> str:
    """'2026-10' -> 'octubre 2026'."""
    try:
        y, m = ym.split("-")
        return f"{MESES_ES[int(m) - 1]} {y}"
    except (ValueError, IndexError):
        return ym


def require_conexion() -> None:
    """Detiene la página con un mensaje claro si no hay conexión a Sheets."""
    if not st.session_state.get("conectado", False):
        st.error("Sin conexión a Google Sheets.")
        detalle = st.session_state.get("error_conexion", "")
        if detalle:
            st.write("**Detalle del error:**")
            st.code(detalle, language="text")
        else:
            st.caption(
                "No se registró un detalle. Revisa CONFIGURACION_GOOGLE.md y los "
                "Secrets de la app."
            )
        st.stop()


def flash(mensaje: str, tipo: str = "success") -> None:
    """Guarda un mensaje para mostrarlo después del siguiente rerun."""
    st.session_state.setdefault("_flashes", []).append((tipo, mensaje))


def mostrar_flashes() -> None:
    """Muestra y limpia los mensajes pendientes."""
    for tipo, mensaje in st.session_state.pop("_flashes", []):
        getattr(st, tipo, st.info)(mensaje)


# ---------------------------------------------------------------------------
# Conexión con Google Sheets
# ---------------------------------------------------------------------------
def _spreadsheet_key() -> str:
    """Obtiene el ID de la hoja desde secrets, variable de entorno o vacío."""
    try:
        key = st.secrets["spreadsheet_key"]
        if key:
            return str(key).strip()
    except Exception:
        pass
    return os.environ.get("SPREADSHEET_KEY", "").strip()


@st.cache_resource(show_spinner=False)
def get_client() -> gspread.Client:
    """Cliente autenticado con la service account (cacheado).

    Soporta dos formas de autenticación:
    - `[gcp_service_account]` dentro de st.secrets (para Streamlit Cloud).
    - Archivo local assets/credentials.json (para ejecución en tu PC).
    """
    # 1) Desde "Secrets" (Streamlit Cloud)
    try:
        if "gcp_service_account" in st.secrets:
            return gspread.service_account_from_dict(
                dict(st.secrets["gcp_service_account"])
            )
    except Exception:
        pass

    # 2) Desde archivo local
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            "'assets/credentials.json' no existe. Genera el archivo JSON de la "
            "service account siguiendo CONFIGURACION_GOOGLE.md."
        )
    return gspread.service_account(filename=CREDENTIALS_PATH)


@st.cache_resource(show_spinner=False)
def get_spreadsheet() -> gspread.Spreadsheet:
    """Abre la hoja 'Mis Gastos' por su ID (cacheado)."""
    key = _spreadsheet_key()
    if not key or key.upper().startswith("PEGA"):
        raise ValueError(
            "Falta el ID de la hoja. Escribe 'spreadsheet_key' en "
            ".streamlit/secrets.toml (consulta CONFIGURACION_GOOGLE.md)."
        )
    try:
        return get_client().open_by_key(key)
    except SpreadsheetNotFound as exc:
        raise ValueError(
            "No se encontró la hoja. Revisa el ID y comparte la hoja con el "
            "'client_email' de la service account."
        ) from exc


def _ensure_tab(sp: gspread.Spreadsheet, titulo: str,
                headers: list[str], filas_seed: Optional[list[list]] = None):
    """Crea la pestaña si no existe y garantiza su encabezado."""
    try:
        ws = sp.worksheet(titulo)
    except WorksheetNotFound:
        ws = sp.add_worksheet(title=titulo, rows=1000, cols=max(len(headers), 2))
        ws.update([headers] + (filas_seed or []), value_input_option="RAW")
        return ws

    # La pestaña ya existe: si la primera fila está vacía, escribir encabezado.
    fila1 = ws.row_values(1)
    if not any(str(v).strip() for v in fila1):
        ws.update([headers] + (filas_seed or []), value_input_option="RAW")
    return ws


def ensure_structure() -> None:
    """Garantiza que la hoja tenga las 3 pestañas esperadas."""
    sp = get_spreadsheet()
    _ensure_tab(sp, TAB_MOV, COLS_MOV)
    _ensure_tab(sp, TAB_CAT, ["categoria"], [[c] for c in CATEGORIAS_DEFAULT])
    _ensure_tab(sp, TAB_CFG, ["clave", "valor"],
                [[k, v] for k, v in CONFIG_DEFAULT.items()])


# ---------------------------------------------------------------------------
# Movimientos
# ---------------------------------------------------------------------------
def _empty_mov() -> pd.DataFrame:
    """DataFrame vacío con los tipos correctos (evita errores con .dt)."""
    return pd.DataFrame({
        "fecha_hora": pd.Series([], dtype="datetime64[ns]"),
        "tipo": pd.Series([], dtype="object"),
        "categoria": pd.Series([], dtype="object"),
        "nombre": pd.Series([], dtype="object"),
        "monto": pd.Series([], dtype="int64"),
    })


@st.cache_data(ttl=30, show_spinner="Cargando movimientos...")
def load_movimientos() -> pd.DataFrame:
    """Carga todos los movimientos como DataFrame limpio y tipado."""
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(TAB_MOV)
    except WorksheetNotFound:
        return _empty_mov()

    valores = ws.get_all_values()
    if not valores:
        return _empty_mov()

    encabezados = [str(h).strip().lower() for h in valores[0]]
    esperado = [c.lower() for c in COLS_MOV]
    filas = valores[1:] if encabezados[:len(esperado)] == esperado else valores
    if not filas:
        return _empty_mov()

    # Rellenar filas cortas para que siempre tengan 5 columnas.
    filas = [list(r) + [""] * (len(COLS_MOV) - len(r)) for r in filas]
    df = pd.DataFrame(filas, columns=COLS_MOV)

    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")
    for col in ("tipo", "categoria", "nombre"):
        df[col] = df[col].astype(str).str.strip()

    df["monto"] = df["monto"].fillna(0).round().astype("int64")
    df = df.dropna(subset=["fecha_hora"])
    df = df[df["tipo"].isin(["Ingreso", "Gasto"])]
    return df.reset_index(drop=True)


def add_movimiento(tipo: str, categoria: str, nombre: str,
                   monto: int, fecha_hora: Optional[datetime] = None) -> None:
    """Añade un movimiento individual y refresca la caché."""
    sp = get_spreadsheet()
    ws = sp.worksheet(TAB_MOV)
    fecha = (fecha_hora or bogota_now()).strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(
        [fecha, tipo, str(categoria), str(nombre), int(monto)],
        value_input_option="RAW",
    )
    load_movimientos.clear()


def borrar_movimiento(nombre: str, monto: int,
                      tipo: Optional[str] = None) -> bool:
    """
    Elimina el primer movimiento que coincida con nombre + monto
    (opcionalmente también el tipo). Devuelve True si borró algo.
    """
    sp = get_spreadsheet()
    ws = sp.worksheet(TAB_MOV)
    valores = ws.get_all_values()

    objetivo_nombre = str(nombre).strip().lower()
    objetivo_monto = int(round(float(monto)))

    for i, fila in enumerate(valores[1:], start=2):
        if len(fila) < 5:
            continue
        f_nombre = str(fila[3]).strip().lower()
        try:
            f_monto = int(round(float(str(fila[4]).replace(",", ""))))
        except (TypeError, ValueError):
            f_monto = None

        coincide = f_nombre == objetivo_nombre and f_monto == objetivo_monto
        if coincide and tipo and str(fila[1]).strip() != tipo:
            continue
        if coincide:
            ws.delete_rows(i)
            load_movimientos.clear()
            return True
    return False


def filtrar_mes(df: pd.DataFrame, ym: str) -> pd.DataFrame:
    """Filtra un DataFrame de movimientos por mes 'YYYY-MM'."""
    if df.empty:
        return df
    mascara = df["fecha_hora"].dt.strftime("%Y-%m") == ym
    return df[mascara]


def meses_disponibles() -> list[str]:
    """Lista de meses 'YYYY-MM' presentes en los datos + el mes actual."""
    actual = bogota_now().strftime("%Y-%m")
    meses = {actual}
    try:
        df = load_movimientos()
        if not df.empty:
            meses |= set(df["fecha_hora"].dt.strftime("%Y-%m").dropna().tolist())
    except Exception:
        pass
    return sorted(meses, reverse=True)


# ---------------------------------------------------------------------------
# Categorías
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def load_categorias() -> list[str]:
    """Carga las categorías desde la pestaña Categorias."""
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(TAB_CAT)
    except WorksheetNotFound:
        return list(CATEGORIAS_DEFAULT)

    categorias: list[str] = []
    for valor in ws.col_values(1):
        s = str(valor).strip()
        if not s or s.lower() == "categoria":
            continue
        categorias.append(s)
    return categorias or list(CATEGORIAS_DEFAULT)


def save_categorias(categorias: list[str]) -> None:
    """Reescribe por completo la pestaña Categorias."""
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(TAB_CAT)
    except WorksheetNotFound:
        ws = sp.add_worksheet(title=TAB_CAT, rows=1000, cols=2)

    ws.clear()
    datos = [["categoria"]] + [[c] for c in categorias]
    ws.update(datos, value_input_option="RAW")
    load_categorias.clear()


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def load_config() -> dict:
    """Carga la configuración (clave/valor) desde la pestaña Config."""
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(TAB_CFG)
    except WorksheetNotFound:
        return dict(CONFIG_DEFAULT)

    cfg = dict(CONFIG_DEFAULT)
    for fila in ws.get_all_records():
        clave = str(fila.get("clave", "")).strip()
        if clave:
            cfg[clave] = fila.get("valor", "")
    return cfg


def save_config(cfg: dict) -> None:
    """Reescribe por completo la pestaña Config."""
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(TAB_CFG)
    except WorksheetNotFound:
        ws = sp.add_worksheet(title=TAB_CFG, rows=100, cols=2)

    ws.clear()
    datos = [["clave", "valor"]] + [[k, str(v)] for k, v in cfg.items()]
    ws.update(datos, value_input_option="RAW")
    load_config.clear()
