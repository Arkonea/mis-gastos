"""
app.py
======
Punto de entrada de la app "Mis Gastos".

- Configura la página y el tema.
- Verifica la conexión con Google Sheets (crea las pestañas si faltan).
- Define el selector de MES global en la barra lateral (filtra todas las páginas).
- Registra la navegación multi-página con st.navigation / st.Page.
"""

import streamlit as st

import sheets

# ---------------------------------------------------------------------------
# Configuración de página (solo se define UNA vez, aquí)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mis Gastos",
    page_icon=":material/savings:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Conexión con Google Sheets (una sola vez por sesión)
# ---------------------------------------------------------------------------
if "estructura_ok" not in st.session_state:
    try:
        sheets.ensure_structure()
        st.session_state.conectado = True
        st.session_state.error_conexion = ""
    except Exception as exc:  # credenciales, ID o permisos
        st.session_state.conectado = False
        st.session_state.error_conexion = str(exc)
    st.session_state.estructura_ok = True

# ---------------------------------------------------------------------------
# Estado de sesión: mes seleccionado global
# ---------------------------------------------------------------------------
if "mes_sel" not in st.session_state:
    st.session_state.mes_sel = sheets.bogota_now().strftime("%Y-%m")

# ---------------------------------------------------------------------------
# Barra lateral: título + selector de mes global
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## :material/savings: Mis Gastos")

    if not st.session_state.get("conectado", False):
        st.error("No hay conexión con Google Sheets.")
        if st.session_state.get("error_conexion"):
            st.caption(st.session_state.error_conexion)
        st.caption("Revisa **CONFIGURACION_GOOGLE.md**.")
        if st.button("Reintentar conexión", use_container_width=True):
            st.session_state.pop("estructura_ok", None)
            st.cache_resource.clear()
            st.rerun()
    else:
        opciones = sheets.meses_disponibles()
        if st.session_state.mes_sel not in opciones:
            opciones = [st.session_state.mes_sel] + opciones
        st.session_state.mes_sel = st.selectbox(
            "Mes",
            options=opciones,
            index=opciones.index(st.session_state.mes_sel),
            format_func=sheets.mes_label,
            key="mes_widget",
        )

    st.divider()
    st.caption("Zona horaria: America/Bogota (UTC-5)")

# ---------------------------------------------------------------------------
# Navegación multi-página
# ---------------------------------------------------------------------------
paginas = [
    st.Page("pages/1_Dashboard.py", title="Dashboard",
            icon=":material/dashboard:", default=True),
    st.Page("pages/2_Registrar_Ingreso.py", title="Registrar ingreso",
            icon=":material/add_circle:"),
    st.Page("pages/3_Registrar_Gasto.py", title="Registrar gasto",
            icon=":material/shopping_cart:"),
    st.Page("pages/4_Historial.py", title="Historial",
            icon=":material/history:"),
    st.Page("pages/5_Ajustes.py", title="Ajustes",
            icon=":material/settings:"),
]

st.navigation(paginas).run()
