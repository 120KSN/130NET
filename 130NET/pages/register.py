import streamlit as st

from database import SessionLocal
from services.auth_service import AuthService


def render_register_page():
    st.title("Criar conta")
    with st.form("register_form"):
        full_name = st.text_input("Nome completo")
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Cadastrar")

    if submitted:
        try:
            db = SessionLocal()
            user = AuthService.register(db, full_name, username, password)
            st.success(f"Conta criada com sucesso! Seu ID é {user.id}.")
            st.session_state.user_id = user.id
            st.session_state.app_view = "chat"
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        finally:
            db.close()
