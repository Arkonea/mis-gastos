"""
pages/5_Ajustes.py
==================
Ajustes de la app: edición de la lista de categorías (pestaña Categorias)
y datos básicos de configuración (pestaña Config).
"""

import streamlit as st

import sheets

sheets.require_conexion()
sheets.mostrar_flashes()

st.title(":material/settings: Ajustes")

# ---------------------------------------------------------------------------
# Categorías
# ---------------------------------------------------------------------------
st.subheader("Categorías")

if "cats_edit" not in st.session_state:
    st.session_state.cats_edit = sheets.load_categorias()

indice_a_borrar = None
for i, cat in enumerate(st.session_state.cats_edit):
    c1, c2 = st.columns([6, 1])
    with c1:
        st.session_state.cats_edit[i] = st.text_input(
            f"Categoría {i + 1}",
            value=cat,
            key=f"cat_edit_{i}",
            label_visibility="collapsed",
        )
    with c2:
        if st.button("🗑️", key=f"cat_del_{i}", help="Eliminar categoría"):
            indice_a_borrar = i

if indice_a_borrar is not None:
    st.session_state.cats_edit.pop(indice_a_borrar)
    st.rerun()

col_nueva, col_guardar = st.columns(2)
with col_nueva:
    if st.button("➕ Agregar categoría", use_container_width=True):
        st.session_state.cats_edit.append("")
        st.rerun()
with col_guardar:
    if st.button("💾 Guardar categorías", type="primary", use_container_width=True):
        limpias = [c.strip() for c in st.session_state.cats_edit if c.strip()]
        # Elimina duplicados conservando el orden.
        limpias = list(dict.fromkeys(limpias))
        if not limpias:
            st.error("Debe existir al menos una categoría.")
        else:
            try:
                sheets.save_categorias(limpias)
                st.session_state.cats_edit = limpias
                sheets.flash("Categorías guardadas correctamente.")
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudieron guardar las categorías: {exc}")

st.divider()

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
st.subheader("Configuración")
cfg = sheets.load_config()

with st.form("form_config"):
    usuario = st.text_input("Nombre de usuario", value=str(cfg.get("usuario", "")))
    moneda = st.text_input("Moneda", value=str(cfg.get("moneda", "COP")))
    guardar_cfg = st.form_submit_button("Guardar configuración", use_container_width=True)

if guardar_cfg:
    try:
        sheets.save_config({"usuario": usuario.strip(), "moneda": moneda.strip()})
        sheets.flash("Configuración guardada correctamente.")
        st.rerun()
    except Exception as exc:
        st.error(f"No se pudo guardar la configuración: {exc}")
