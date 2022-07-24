import streamlit as st


def main_page():
    if st.session_state.user is not None:
        st.markdown("# Main page 🎈")
        st.markdown("# Page 1 🎉")
        st.markdown("Hello, %s!" % st.session_state.user)
        with st.sidebar:
            st.markdown("SIDEBAR!")
