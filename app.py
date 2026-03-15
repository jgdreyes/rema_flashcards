import streamlit as st

st.set_page_config(
    page_title="REMA Flashcards",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.state import init_state
from utils.data import get_belt_order

init_state()

# ── Page callables (settings / flashcards / curriculum grid) ──────────────────

def _render_settings():
    from pages.settings import render
    render()


def _render_flashcards():
    from pages.flashcards import render
    render()


def _render_curriculum():
    from pages.curriculum_page import _show_grid
    _show_grid()


def _render_auth():
    from pages.auth_page import render
    render()


# ── Page objects ──────────────────────────────────────────────────────────────

settings_page   = st.Page(_render_settings,   title="Settings",   url_path="settings",   default=True)
flashcards_page = st.Page(_render_flashcards, title="Flashcards", url_path="flashcards")
curriculum_page = st.Page(_render_curriculum, title="Curriculum", url_path="curriculum")
auth_page       = st.Page(_render_auth,       title="Account",    url_path="account")

# Belt detail pages — file-based so Streamlit derives URLs as curriculum/<belt_key>
# from the nested file path pages/curriculum/<belt_key>.py.
belt_order = get_belt_order()   # [(belt_key, belt_name), ...]
belt_pages = {
    key: st.Page(f"pages/curriculum/{key}.py", title=name)
    for key, name in belt_order
}

# Store page refs so curriculum_page.py can call st.switch_page without importing app.py
st.session_state["_curriculum_page"] = curriculum_page
st.session_state["_belt_pages"]       = belt_pages

all_pages = [settings_page, flashcards_page, curriculum_page, auth_page, *belt_pages.values()]
pg = st.navigation(all_pages, position="hidden")

# ── Sidebar ───────────────────────────────────────────────────────────────────

PAGE_LABELS  = ["⚙️  Settings", "🃏  Flashcards", "📋  Curriculum"]
PAGE_OBJECTS = [settings_page, flashcards_page, curriculum_page]

is_belt_page = pg in belt_pages.values()
current_idx  = 2 if is_belt_page else next(
    (i for i, p in enumerate(PAGE_OBJECTS) if p.title == pg.title), 0
)

with st.sidebar:
    st.markdown("## 🥋 REMA Flashcards")
    st.divider()
    selected_label = st.radio(
        "Navigate",
        PAGE_LABELS,
        index=current_idx,
        label_visibility="collapsed",
    )
    st.divider()
    if st.session_state.get("settings_saved"):
        selected = st.session_state.get("selected_belt_keys", [])
        st.caption(f"Belts selected: **{len(selected)}**")
        unlocked = st.session_state.get("unlocked_cycles", [])
        if unlocked:
            st.caption(f"Cycles unlocked: **{len(unlocked)}**")

    st.divider()
    user = st.session_state.get("current_user")
    if user:
        st.caption(f"👤 {user['first_name']} {user['last_name']}")
        if st.button("Log Out", use_container_width=True):
            from utils.auth import sign_out
            sign_out()
            st.rerun()
    else:
        if st.button("Log In / Sign Up", use_container_width=True):
            st.switch_page(auth_page)

selected_idx = PAGE_LABELS.index(selected_label)

if selected_idx != current_idx:
    st.switch_page(PAGE_OBJECTS[selected_idx])

pg.run()
