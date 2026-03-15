import streamlit as st
from utils.supabase_client import get_client


def load_settings(user_id: str):
    """
    Fetch belt and cycle selections from the DB and populate session state.
    Called once per login — guarded by the settings_loaded_from_db flag.
    """
    client = get_client()

    belts = client.table("user_belt_selections") \
        .select("belt_key") \
        .eq("user_id", user_id) \
        .execute()

    cycles = client.table("user_cycle_selections") \
        .select("cycle_key") \
        .eq("user_id", user_id) \
        .execute()

    st.session_state.selected_belt_keys  = [r["belt_key"]  for r in belts.data]
    st.session_state.unlocked_cycles     = [r["cycle_key"] for r in cycles.data]
    st.session_state.settings_saved      = bool(belts.data)
    st.session_state.settings_loaded_from_db = True


def save_settings(user_id: str, selected_belt_keys: list, unlocked_cycles: list):
    """
    Replace the user's belt and cycle selections in the DB.
    Uses delete + insert so the DB always mirrors the current selection.
    """
    client = get_client()

    client.table("user_belt_selections").delete().eq("user_id", user_id).execute()
    if selected_belt_keys:
        client.table("user_belt_selections").insert([
            {"user_id": user_id, "belt_key": k} for k in selected_belt_keys
        ]).execute()

    client.table("user_cycle_selections").delete().eq("user_id", user_id).execute()
    if unlocked_cycles:
        client.table("user_cycle_selections").insert([
            {"user_id": user_id, "cycle_key": k} for k in unlocked_cycles
        ]).execute()
