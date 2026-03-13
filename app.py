import streamlit as st

st.set_page_config(
    page_title="REMA Flashcards",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.state import init_state
init_state()

# ── Sidebar navigation ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥋 REMA Flashcards")
    st.divider()
    page = st.radio(
        "Navigate",
        ["⚙️  Settings", "🃏  Flashcards"],
        index=0 if not st.session_state.get("settings_saved") else 1,
        label_visibility="collapsed",
    )
    st.divider()
    if st.session_state.get("settings_saved"):
        st.caption(f"Current belt: **{st.session_state.current_belt_name}**")
        unlocked = st.session_state.get("unlocked_cycles", [])
        if unlocked:
            st.caption(f"Cycles unlocked: **{len(unlocked)}**")

# ── Route pages ─────────────────────────────────────────────────────────────
if page == "⚙️  Settings":
    from pages.settings import render
    render()
else:
    from pages.flashcards import render
    render()
