import streamlit as st


def render_settings_page(user):
    st.title("Configurações")
    current_theme = st.session_state.get("theme", "dark")
    current_sidebar = st.session_state.get("sidebar_position", "left")

    with st.form("settings_form"):
        theme = st.selectbox("Tema", ["dark", "light"], index=0 if current_theme == "dark" else 1)
        sidebar_position = st.selectbox("Posição do menu lateral", ["left", "right"], index=0 if current_sidebar == "left" else 1)
        save = st.form_submit_button("Salvar preferências")

    if save:
        st.session_state.theme = theme
        st.session_state.sidebar_position = sidebar_position
        st.success("Preferências salvas.")
        st.rerun()

    st.divider()
    if st.button("Sair da conta"):
        st.session_state.user_id = None
        st.session_state.app_view = "login"
        st.rerun()
