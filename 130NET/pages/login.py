import streamlit as st

from database import SessionLocal
from services.auth_service import AuthService


def render_login_page():
    st.title("Entrar na conta")
    with st.form("login_form"):
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if not username or not password:
            st.error("Preencha usuário e senha.")
            return

        db = SessionLocal()
        try:
            user = AuthService.authenticate(db, username, password)
            if user is None:
                st.error("Credenciais inválidas.")
                return
            st.session_state.user_id = user.id
            st.session_state.app_view = "chat"
            st.success("Login realizado com sucesso.")
            st.rerun()
        finally:
            db.close()
