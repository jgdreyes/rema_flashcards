import streamlit as st
from st_supabase_connection import SupabaseConnection


@st.cache_resource
def get_client() -> SupabaseConnection:
    return st.connection("supabase", type=SupabaseConnection)