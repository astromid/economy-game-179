import streamlit as st


def sales() -> None:
    st.markdown("## Система корпоративного управления CP/20.22")
    st.title("NoName Corporation")
    st.markdown("## Поставки")
    with st.expander("Активные поставки"):
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            st.text("Рынок 1")
            st.text("Рынок 2")
        with col2:
            st.text("50%")
            st.text("33%")
        with col3:
            st.progress(0.5)
            st.progress(0.33)
