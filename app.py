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
        ["⚙️  Settings", "🃏  Flashcards", "📋  Curriculum"],
        index=0 if not st.session_state.get("settings_saved") else 1,
        label_visibility="collapsed",
    )
    st.divider()
    if st.session_state.get("settings_saved"):
        selected = st.session_state.get("selected_belt_keys", [])
        st.caption(f"Belts selected: **{len(selected)}**")
        unlocked = st.session_state.get("unlocked_cycles", [])
        if unlocked:
            st.caption(f"Cycles unlocked: **{len(unlocked)}**")

# ── Route pages ─────────────────────────────────────────────────────────────
if page == "⚙️  Settings":
    from pages.settings import render
    render()
elif page == "🃏  Flashcards":
    from pages.flashcards import render
    render()
else:
    from pages.curriculum import render
    render()
