import streamlit as st
from utils.auth import sign_in, sign_up, sign_out, get_current_user


def render():
    user = get_current_user()
    if user:
        _show_account(user)
    else:
        _show_auth_forms()


def _show_account(user):
    st.title("👤 Account")
    st.markdown(f"**{user['first_name']} {user['last_name']}**")
    st.caption(user["email"])
    st.divider()
    if st.button("Log Out", type="primary"):
        sign_out()
        st.rerun()


def _show_auth_forms():
    st.title("👤 Account")
    login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            email    = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)
        if submitted:
            try:
                sign_in(email, password)
                st.rerun()
            except Exception as e:
                st.error(str(e))

    with signup_tab:
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
            with col2:
                last_name  = st.text_input("Last Name")
            email     = st.text_input("Email")
            password  = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
        if submitted:
            try:
                sign_up(email, password, first_name, last_name)
                st.success("Account created! You are now logged in.")
                st.rerun()
            except Exception as e:
                st.error(str(e))