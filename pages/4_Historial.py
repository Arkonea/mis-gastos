"""
pages/4_Historial.py
====================
Tabla con todos los movimientos del mes seleccionado (orden cronológico
inverso) y opción para eliminar un registro por nombre + monto.
"""

import pandas as pd
import streamlit as st

import sheets

sheets.require_conexion()
sheets.mostrar_flashes()

mes = st.session_state.get("mes_sel")

st.title(":material/history: Historial")
st.caption(f"Movimientos de {sheets.mes_label(mes)}")

df = sheets.load_movimientos()
df_mes = sheets.filtrar_mes(df, mes)

if df_mes.empty:
    st.info("No hay movimientos registrados en este mes.")
    st.stop()

# Orden cronológico inverso (lo más reciente primero).
vista = df_mes.sort_values("fecha_hora", ascending=False).reset_index(drop=True)

tabla = pd.DataFrame({
    "Fecha/Hora": vista["fecha_hora"].dt.strftime("%Y-%m-%d %H:%M"),
    "Tipo": vista["tipo"],
    "Categoría": vista["categoria"],
    "Nombre": vista["nombre"],
    "Monto": vista["monto"].apply(sheets.fmt),
})
st.dataframe(tabla, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Eliminar un registro")


def etiqueta(i: int) -> str:
    fila = vista.iloc[i]
    fecha = fila["fecha_hora"].strftime("%Y-%m-%d %H:%M")
    return (
        f"{fecha} | {fila['tipo']} | {fila['categoria']} | "
        f"{fila['nombre']} | {sheets.fmt(fila['monto'])}"
    )


opciones = list(range(len(vista)))
seleccionado = st.selectbox(
    "Selecciona el movimiento a eliminar",
    opciones,
    format_func=etiqueta,
)

if st.button("Eliminar seleccionado", type="primary"):
    fila = vista.iloc[seleccionado]
    try:
        ok = sheets.borrar_movimiento(
            fila["nombre"], int(fila["monto"]), tipo=fila["tipo"]
        )
        if ok:
            sheets.flash("Registro eliminado correctamente.")
            st.rerun()
        else:
            st.error("No se encontró el registro en la hoja (pudo ser borrado antes).")
    except Exception as exc:
        st.error(f"No se pudo eliminar el registro: {exc}")
