import streamlit as st


def render_message(message, sent_by_me: bool):
    align = "right" if sent_by_me else "left"
    bg = "#0b5fff" if sent_by_me else "#2a2d32"
    style = f"text-align:{align}; background:{bg}; padding:10px; border-radius:12px; margin:8px 0; color:white;"
    st.markdown(f"<div style='{style}'>{message}</div>", unsafe_allow_html=True)
