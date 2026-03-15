import streamlit as st
from utils.supabase_client import get_client


def sign_up(email: str, password: str, first_name: str, last_name: str):
    client = get_client()
    resp = client.auth.sign_up({"email": email, "password": password})
    if resp.user and resp.session:
        client.table("users").insert({
            "id":         str(resp.user.id),
            "first_name": first_name,
            "last_name":  last_name,
            "email":      email,
        }).execute()
        _store_user(resp.user, first_name, last_name)
    return resp


def sign_in(email: str, password: str):
    client = get_client()
    resp = client.auth.sign_in_with_password({"email": email, "password": password})
    if resp.user:
        profile = (
            client.table("users")
            .select("first_name, last_name")
            .eq("id", str(resp.user.id))
            .single()
            .execute()
        )
        first_name = profile.data.get("first_name", "") if profile.data else ""
        last_name  = profile.data.get("last_name",  "") if profile.data else ""
        _store_user(resp.user, first_name, last_name)
    return resp


def sign_out():
    get_client().auth.sign_out()
    st.session_state.current_user            = None
    st.session_state.settings_loaded_from_db = False
    st.session_state.selected_belt_keys      = []
    st.session_state.unlocked_cycles         = []
    st.session_state.settings_saved          = False
    st.session_state.cards                   = []
    st.session_state.card_index              = 0
    st.session_state.show_answer             = False
    st.session_state.session_belt_keys       = []
    st.session_state.focus_gen               = 0


def get_current_user():
    return st.session_state.get("current_user")


def _store_user(auth_user, first_name: str, last_name: str):
    st.session_state.current_user            = {
        "id":         str(auth_user.id),
        "email":      auth_user.email,
        "first_name": first_name,
        "last_name":  last_name,
    }
    st.session_state.settings_loaded_from_db = False