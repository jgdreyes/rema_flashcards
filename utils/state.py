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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
