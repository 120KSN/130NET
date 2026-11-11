import streamlit as st


def render_chat_box(title: str, content):
    st.subheader(title)
    st.write(content)
