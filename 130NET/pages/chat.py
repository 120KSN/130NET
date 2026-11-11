import time

import streamlit as st

from database import SessionLocal
from models.user import User
from services.contact_service import ContactService
from services.conversation_service import ConversationService
from services.message_service import MessageService


def render_chat_page(user):
    db = SessionLocal()
    try:
        current_user = db.query(User).filter_by(id=user.id).first()
        contact_query = st.text_input("Pesquisar contatos", key="contact_search")
        contacts = ContactService.search_contacts(db, current_user.id, contact_query)

        if not contacts:
            st.info("Nenhum contato encontrado.")
            return

        selected_contact = st.selectbox(
            "Contatos",
            options=contacts,
            format_func=lambda item: item.username,
            index=0,
        )

        conversation = ConversationService.get_or_create_conversation(db, current_user.id, selected_contact.id)
        st.subheader(f"Conversando com {selected_contact.username}")

        messages = MessageService.list_messages(db, conversation.id, current_user.id)
        for message in messages:
            if message.sender_id == current_user.id:
                with st.container():
                    st.markdown(f"<div style='text-align:right; background:#1f2d3d; padding:8px; border-radius:12px; margin:6px 0;'>**Você**: {message.content}<br><small>{message.sent_at.strftime('%d/%m/%Y %H:%M')}</small></div>", unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown(f"<div style='text-align:left; background:#1c1f26; padding:8px; border-radius:12px; margin:6px 0;'>**{selected_contact.username}**: {message.content}<br><small>{message.sent_at.strftime('%d/%m/%Y %H:%M')}</small></div>", unsafe_allow_html=True)

        with st.form("message_form"):
            content = st.text_input("Mensagem", placeholder="Escreva sua mensagem...")
            submitted = st.form_submit_button("Enviar")
        if submitted:
            try:
                MessageService.send_message(db, conversation.id, current_user.id, content)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    finally:
        db.close()
