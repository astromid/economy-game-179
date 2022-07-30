import streamlit as st


def login_callback():
    st.session_state.user = st.session_state.login


def login_form():
    st.markdown(
        "<center> <h2>Необходим авторизованный доступ.</h2> </center>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form(key="login_form"):
            st.text("Corporate Portal [CP] v20.22")
            st.text_input("Логин:", key="login")
            st.text_input("Пароль:", type="password", key="password")
            if st.form_submit_button("Войти", on_click=login_callback):
                if not st.session_state.user:
                    st.error("Неверный логин или пароль")


def logout():
    st.session_state.user = None
    st.experimental_memo.clear()
    st.experimental_rerun()
