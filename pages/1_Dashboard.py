"""
pages/1_Dashboard.py
====================
Resumen financiero del mes seleccionado: métricas, gráfico de torta por
categoría y accesos rápidos a registrar ingreso / gasto.
"""

import plotly.express as px
import streamlit as st

import sheets

sheets.require_conexion()
sheets.mostrar_flashes()

mes = st.session_state.get("mes_sel")

st.title(":material/dashboard: Dashboard")
st.caption(f"Resumen financiero de {sheets.mes_label(mes)}")


def tarjeta(titulo: str, valor: str, color: str = "#e6edf3") -> None:
    """Tarjeta métrica con estilo oscuro minimalista."""
    st.markdown(
        f"""
        <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;
                    padding:18px 20px;margin-bottom:8px;">
            <div style="color:#8b949e;font-size:0.9rem;margin-bottom:6px;">{titulo}</div>
            <div style="color:{color};font-size:2rem;font-weight:700;line-height:1;">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Datos del mes
# ---------------------------------------------------------------------------
df = sheets.load_movimientos()
df_mes = sheets.filtrar_mes(df, mes)

if df_mes.empty:
    ingresos, gastos = 0, 0
else:
    ingresos = int(df_mes.loc[df_mes["tipo"] == "Ingreso", "monto"].sum())
    gastos = int(df_mes.loc[df_mes["tipo"] == "Gasto", "monto"].sum())
saldo = ingresos - gastos

# ---------------------------------------------------------------------------
# Tarjetas
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    tarjeta("Ingresos del mes", sheets.fmt(ingresos), "#22c55e")
with c2:
    tarjeta("Gastos del mes", sheets.fmt(gastos), "#f87171")
with c3:
    tarjeta("Saldo disponible", sheets.fmt(saldo),
            "#f87171" if saldo < 0 else "#22c55e")

if ingresos == 0:
    st.warning(
        "Aún no has registrado ingresos este mes. Puedes seguir registrando "
        "gastos, pero el saldo aparecerá en negativo."
    )

st.divider()

# ---------------------------------------------------------------------------
# Gráfico de torta + categoría con mayor gasto
# ---------------------------------------------------------------------------
df_gastos = df_mes[df_mes["tipo"] == "Gasto"] if not df_mes.empty else df_mes
agrupado = df_gastos.groupby("categoria", as_index=False)["monto"].sum()
agrupado = agrupado[agrupado["monto"] > 0]

col_graf, col_info = st.columns([2, 1])
with col_graf:
    st.subheader("Gastos por categoría")
    if agrupado.empty:
        st.info("No hay gastos registrados en este mes.")
    else:
        fig = px.pie(
            agrupado,
            names="categoria",
            values="monto",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textinfo="percent+label", textposition="outside")
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("Mayor gasto")
    if not agrupado.empty:
        top = agrupado.loc[agrupado["monto"].idxmax()]
        st.markdown(f"### {top['categoria']}")
        st.markdown(f"**{sheets.fmt(top['monto'])}**")
    else:
        st.caption("Sin datos para este mes.")

st.divider()

# ---------------------------------------------------------------------------
# Acciones rápidas
# ---------------------------------------------------------------------------
st.subheader("Acciones rápidas")
b1, b2 = st.columns(2)
with b1:
    st.page_link("pages/2_Registrar_Ingreso.py", label="Registrar ingreso",
                 icon=":material/add_circle:", use_container_width=True)
with b2:
    st.page_link("pages/3_Registrar_Gasto.py", label="Registrar gasto",
                 icon=":material/shopping_cart:", use_container_width=True)
