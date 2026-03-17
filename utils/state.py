import streamlit as st


def init_state():
    defaults = {
        "settings_saved": False,
        "selected_belt_keys": [],    # list of belt_keys to include in deck
        "unlocked_cycles": [],       # list of cycle_keys
        "flashcard_mode": "Comprehensive",
        "cards": [],                 # generated deck
        "card_index": 0,
        "show_answer": False,
        "info_split_include_word":  True,  # include Word of Belt cards in Info Split
        "info_split_include_forms": True,  # include Form cards in Info Split
        "current_user":             None,   # logged-in user dict, or None for guests
        "settings_loaded_from_db":  False,  # True once DB settings have been pulled
        "session_belt_keys":        [],     # active session focus (subset of selected_belt_keys)
        "focus_gen":                0,      # incremented to reset focus checkboxes
        "fullscreen_mode":          False,  # phone / full-screen card view
        "fs_nav_gen":               0,      # incremented to reset fullscreen nav control
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
