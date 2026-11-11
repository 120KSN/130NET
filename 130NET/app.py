import time

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal, engine, init_db
from pages.chat import render_chat_page
from pages.login import render_login_page
from pages.profile import render_profile_page
from pages.register import render_register_page
from pages.settings import render_settings_page
from services.contact_service import ContactService
from services.user_service import UserService

st.set_page_config(page_title="130NET", page_icon="💬", layout="wide")


@st.cache_resource
def initialize_database():
    init_db()
    return engine


if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "sidebar_position" not in st.session_state:
    st.session_state.sidebar_position = "left"
if "app_view" not in st.session_state:
    st.session_state.app_view = "login"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "selected_contact_id" not in st.session_state:
    st.session_state.selected_contact_id = None
if "last_live_refresh" not in st.session_state:
    st.session_state.last_live_refresh = time.time()


def apply_theme(theme: str):
    if theme == "light":
        css = """
        <style>
        :root {
            color-scheme: light;
        }
        .stApp {
            background: #f3f5f9;
            color: #101827;
        }
        div[data-testid="stSidebar"] {
            background: #e5e7eb;
        }
        .block-container {
            padding-top: 2rem;
        }
        </style>
        """
    else:
        css = """
        <style>
        :root {
            color-scheme: dark;
        }
        .stApp {
            background: linear-gradient(135deg, #0a0f1d, #141a29);
            color: #f3f7ff;
        }
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stSidebar"] {
            background: #101822;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.35rem;
        }
        .stButton > button {
            border-radius: 12px;
            background: #0b5fff;
            color: white;
            border: none;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border-radius: 12px;
            background: #1c2433;
            color: white;
        }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


apply_theme(st.session_state.theme)

try:
    initialize_database()
except SQLAlchemyError:
    st.error(
        "Não foi possível preparar o banco de dados. Confirme se o serviço MySQL "
        "está ativo, se o banco configurado existe e se as credenciais estão corretas."
    )
    st.info("Se as tabelas ainda não existirem, execute `python database\\init_db.py` na pasta do projeto.")
    st.stop()


def auth_screen():
    st.title("130NET")
    st.caption("Rede social segura para mensagens privadas")
    tab1, tab2 = st.tabs(["Entrar", "Criar conta"])
    with tab1:
        from pages.login import render_login_page

        render_login_page()
    with tab2:
        from pages.register import render_register_page

        render_register_page()


def dashboard():
    db = SessionLocal()
    try:
        user = UserService.get_by_id(db, st.session_state.user_id)
        if user is None:
            st.session_state.user_id = None
            st.session_state.app_view = "login"
            st.rerun()

        if st.session_state.app_view == "profile":
            render_profile_page(user.id)
            return
        if st.session_state.app_view == "settings":
            render_settings_page(user)
            return

        # sidebar left/right emulation
        if st.session_state.sidebar_position == "left":
            left_col, center_col, right_col = st.columns([2, 5, 3])
        else:
            right_col, center_col, left_col = st.columns([2, 5, 3])

        with left_col:
            st.subheader("Menu")
            if st.button("Chat", use_container_width=True):
                st.session_state.app_view = "chat"
                st.rerun()
            if st.button("Perfil", use_container_width=True):
                st.session_state.app_view = "profile"
                st.rerun()
            if st.button("Configurações", use_container_width=True):
                st.session_state.app_view = "settings"
                st.rerun()
            if st.button("Sair", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.app_view = "login"
                st.rerun()

            st.divider()
            st.subheader("Adicionar contato")
            with st.form("add-contact-form"):
                target = st.text_input("ID ou nome de usuário", key="contact_identifier")
                submitted = st.form_submit_button("Enviar solicitação")
            if submitted:
                try:
                    ContactService.send_friend_request(db, user.id, target)
                    st.success("Solicitação enviada.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

            st.divider()
            st.subheader("Solicitações")
            requests = ContactService.get_requests(db, user.id, status="pending")
            if not requests:
                st.caption("Nenhuma solicitação pendente.")
            for request in requests:
                sender = request.sender
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.write(f"{sender.username}")
                with col_b:
                    if st.button("Aceitar", key=f"accept_{request.id}"):
                        ContactService.accept_friend_request(db, request.id, user.id)
                        st.success("Contato adicionado.")
                        st.rerun()
                if st.button("Recusar", key=f"reject_{request.id}"):
                    ContactService.reject_friend_request(db, request.id, user.id)
                    st.success("Solicitação recusada.")
                    st.rerun()

            st.divider()
            st.subheader("Contatos")
            contact_query = st.text_input("Pesquisar contatos", key="contact_search")
            contacts = ContactService.search_contacts(db, user.id, contact_query)
            if not contacts:
                st.caption("Nenhum contato encontrado.")
            for contact in contacts:
                if st.button(contact.username, key=f"contact_{contact.id}", use_container_width=True):
                    st.session_state.selected_contact_id = contact.id
                    st.session_state.app_view = "chat"
                    st.rerun()

        with center_col:
            st.markdown(f"## Conversas · {user.username}")
            selected_contact_id = st.session_state.selected_contact_id
            if selected_contact_id is None and contacts:
                st.session_state.selected_contact_id = contacts[0].id
                selected_contact_id = contacts[0].id

            if selected_contact_id is None:
                st.info("Selecione um contato para iniciar a conversa.")
            else:
                selected_contact = UserService.get_by_id(db, selected_contact_id)
                if selected_contact is None:
                    st.session_state.selected_contact_id = None
                    st.rerun()
                st.subheader(f"Conversa com {selected_contact.username}")

                if selected_contact is not None:
                    conversation = ContactService.get_requests(db, user.id)
                    st.write("")
                    from services.conversation_service import ConversationService
                    from services.message_service import MessageService

                    conversation = ConversationService.get_or_create_conversation(db, user.id, selected_contact.id)
                    messages = MessageService.list_messages(db, conversation.id, user.id)

                    for message in messages:
                        if message.sender_id == user.id:
                            st.markdown(
                                f"<div style='text-align:right; background:#0b5fff; padding:10px; border-radius:12px; margin:6px 0; color:#fff;'>"
                                f"<strong>Você</strong><br>{message.content}<br><small>{message.sent_at.strftime('%d/%m/%Y %H:%M')}</small>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"<div style='text-align:left; background:#1a1f2a; padding:10px; border-radius:12px; margin:6px 0; color:#fff;'>"
                                f"<strong>{selected_contact.username}</strong><br>{message.content}<br><small>{message.sent_at.strftime('%d/%m/%Y %H:%M')}</small>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                    with st.form("send-message-form"):
                        content = st.text_input("Mensagem", key="message_input")
                        sent = st.form_submit_button("Enviar")
                    if sent:
                        if content.strip():
                            MessageService.send_message(db, conversation.id, user.id, content)
                            st.session_state.message_input = ""
                            st.rerun()
                        else:
                            st.error("A mensagem não pode ficar vazia.")

        with right_col:
            if st.session_state.selected_contact_id:
                selected_contact = UserService.get_by_id(db, st.session_state.selected_contact_id)
                if selected_contact:
                    st.subheader("Contato")
                    st.write(f"Usuário: {selected_contact.username}")
                    st.write(f"ID: {selected_contact.id}")
                    st.write(f"Descrição: {selected_contact.description or 'Sem descrição.'}")
                    is_blocked = ContactService.is_blocked(db, user.id, selected_contact.id)
                    if is_blocked:
                        if st.button("Desbloquear usuário"):
                            ContactService.unblock_user(db, user.id, selected_contact.id)
                            st.success("Usuário desbloqueado.")
                            st.rerun()
                    else:
                        if st.button("Bloquear usuário"):
                            ContactService.block_user(db, user.id, selected_contact.id)
                            st.success("Usuário bloqueado.")
                            st.rerun()
                    if st.button("Remover contato"):
                        ContactService.remove_contact(db, user.id, selected_contact.id)
                        st.session_state.selected_contact_id = None
                        st.success("Contato removido.")
                        st.rerun()
    finally:
        db.close()


def main():
    if st.session_state.user_id is None:
        auth_screen()
        return

    if time.time() - st.session_state.last_live_refresh > 10:
        st.session_state.last_live_refresh = time.time()
        st.rerun()

    dashboard()


main()
