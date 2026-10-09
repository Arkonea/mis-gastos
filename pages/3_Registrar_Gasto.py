"""
pages/3_Registrar_Gasto.py
==========================
Registro de gastos en dos modos:

1) Gasto unitario: una categoría, un nombre y una cantidad.
2) Listado de gastos: varias filas dinámicas que se registran de una vez.

Cada fila se guarda como un registro individual en la hoja "Movimientos".
"""

from typing import Optional

import streamlit as st

import sheets

sheets.require_conexion()
sheets.mostrar_flashes()

st.title(":material/shopping_cart: Registrar gasto")

categorias = sheets.load_categorias()
OPCIONES = [""] + categorias
PLACEHOLDER = "Selecciona..."


def _linea_vacia(linea: dict) -> bool:
    return (
        not linea.get("categoria")
        and not linea.get("nombre", "").strip()
        and not str(linea.get("cantidad", "")).strip()
    )


tab_unitario, tab_listado = st.tabs(["Gasto unitario", "Listado de gastos"])

# ---------------------------------------------------------------------------
# Pestaña 1: gasto unitario
# ---------------------------------------------------------------------------
with tab_unitario:
    with st.form("form_unitario", clear_on_submit=True):
        cat = st.selectbox(
            "Categoría", OPCIONES,
            format_func=lambda x: x or PLACEHOLDER,
        )
        nombre = st.text_input("Nombre", placeholder="Ej: Almuerzo")
        cantidad = st.text_input("Cantidad (entero > 0)", value="1")
        registrar = st.form_submit_button(
            "Registrar", type="primary", use_container_width=True
        )

    if registrar:
        monto = sheets.parse_entero(cantidad)
        errores = []
        if not cat:
            errores.append("Selecciona una categoría.")
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if monto is None:
            errores.append("Cantidad inválida: debe ser un entero mayor a 0.")

        if errores:
            for e in errores:
                st.error(e)
        else:
            try:
                sheets.add_movimiento("Gasto", cat, nombre.strip(), monto)
                sheets.flash(
                    f"Gasto registrado: {nombre.strip()} — {sheets.fmt(monto)}."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo guardar el gasto: {exc}")

# ---------------------------------------------------------------------------
# Pestaña 2: listado de gastos
# ---------------------------------------------------------------------------
with tab_listado:
    if "lineas" not in st.session_state:
        st.session_state.lineas = [
            {"categoria": "", "nombre": "", "cantidad": ""}
        ]

    indices_a_borrar: Optional[int] = None

    st.caption("Completa una fila por gasto. Las filas vacías se ignoran.")

    for i, linea in enumerate(st.session_state.lineas):
        c1, c2, c3, c4 = st.columns([3, 4, 2, 1])
        with c1:
            idx = OPCIONES.index(linea["categoria"]) if linea["categoria"] in OPCIONES else 0
            linea["categoria"] = st.selectbox(
                "Categoría", OPCIONES, index=idx,
                format_func=lambda x: x or PLACEHOLDER, key=f"cat_{i}",
            )
        with c2:
            linea["nombre"] = st.text_input(
                "Nombre", value=linea["nombre"], key=f"nom_{i}"
            )
        with c3:
            linea["cantidad"] = st.text_input(
                "Cantidad", value=linea["cantidad"], key=f"cant_{i}"
            )
        with c4:
            st.write("")  # pequeño espacio para alinear el botón
            if st.button("❌", key=f"del_{i}", help="Quitar fila"):
                indices_a_borrar = i

    if indices_a_borrar is not None and len(st.session_state.lineas) > 1:
        st.session_state.lineas.pop(indices_a_borrar)
        st.rerun()

    b1, b2 = st.columns([1, 2])
    with b1:
        if st.button("➕ Agregar fila", use_container_width=True):
            st.session_state.lineas.append(
                {"categoria": "", "nombre": "", "cantidad": ""}
            )
            st.rerun()
    with b2:
        registrar_todos = st.button(
            "Registrar todos", type="primary", use_container_width=True
        )

    if registrar_todos:
        errores = []
        validos = []
        for i, linea in enumerate(st.session_state.lineas, start=1):
            if _linea_vacia(linea):
                continue
            monto = sheets.parse_entero(linea["cantidad"])
            if not linea["categoria"]:
                errores.append(f"Línea {i}: falta la categoría.")
            if not linea["nombre"].strip():
                errores.append(f"Línea {i}: el nombre es obligatorio.")
            if monto is None:
                errores.append(f"Línea {i}: cantidad inválida (entero > 0).")
            if linea["categoria"] and linea["nombre"].strip() and monto is not None:
                validos.append((linea["categoria"], linea["nombre"].strip(), monto))

        if errores:
            for e in errores:
                st.error(e)
        elif not validos:
            st.warning("No hay filas con datos para registrar.")
        else:
            total = 0
            try:
                for cat, nombre, monto in validos:
                    sheets.add_movimiento("Gasto", cat, nombre, monto)
                    total += monto
                st.session_state.lineas = [
                    {"categoria": "", "nombre": "", "cantidad": ""}
                ]
                sheets.flash(
                    f"Se registraron {len(validos)} gasto(s) por "
                    f"{sheets.fmt(total)}."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudieron guardar los gastos: {exc}")
