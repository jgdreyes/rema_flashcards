import streamlit as st
from supabase import create_client, Client


def get_client() -> Client:
    """
    Returns a Supabase client scoped to the current Streamlit session.

    Stored in st.session_state (not @st.cache_resource) so each user
    gets their own client with their own auth token.
    """
    if "supabase_client" not in st.session_state:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]