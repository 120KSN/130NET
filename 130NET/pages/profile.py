import streamlit as st

from database import SessionLocal
from models.user import User
from services.user_service import UserService


def render_profile_page(user_id: int):
    st.title("Perfil")
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if user is None:
            st.warning("Usuário não encontrado.")
            return

        with st.form("profile_form"):
            full_name = st.text_input("Nome completo", value=user.full_name)
            username = st.text_input("Nome de usuário", value=user.username)
            description = st.text_area("Descrição pessoal", value=user.description)
            password = st.text_input("Nova senha", type="password")
            submitted = st.form_submit_button("Salvar alterações")

        if submitted:
            try:
                UserService.update_profile(db, user.id, full_name=full_name, username=username, description=description)
                if password:
                    UserService.update_password(db, user.id, password)
                st.success("Perfil atualizado com sucesso.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    finally:
        db.close()
