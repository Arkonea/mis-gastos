"""
pages/2_Registrar_Ingreso.py
============================
Formulario para registrar un ingreso. Solo acepta enteros positivos.
La fecha/hora se asigna automáticamente en America/Bogota.
"""

import streamlit as st

import sheets

sheets.require_conexion()
sheets.mostrar_flashes()

st.title(":material/add_circle: Registrar ingreso")
st.caption("Solo números enteros positivos (sin puntos ni comas).")

with st.form("form_ingreso", clear_on_submit=True):
    monto_txt = st.text_input(
        "Monto",
        placeholder="Ej: 1250000",
        help="Escribe solo dígitos. Ej: 1250000 = $1.250.000",
    )
    concepto = st.text_input(
        "Concepto (opcional)",
        placeholder="Ej: Salario octubre",
    )
    enviado = st.form_submit_button(
        "Guardar ingreso", type="primary", use_container_width=True
    )

if enviado:
    monto = sheets.parse_entero(monto_txt)
    if monto is None:
        st.error(
            "Monto inválido: usa solo números enteros positivos "
            "(sin puntos, comas, espacios ni signos)."
        )
    else:
        try:
            nombre = concepto.strip() or "Ingreso"
            sheets.add_movimiento("Ingreso", "Ingreso", nombre, monto)
            sheets.flash(
                f"Ingreso registrado correctamente por {sheets.fmt(monto)}."
            )
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo guardar el ingreso: {exc}")

st.divider()
st.page_link(
    "pages/3_Registrar_Gasto.py",
    label="Ir a registrar gastos",
    icon=":material/shopping_cart:",
)
