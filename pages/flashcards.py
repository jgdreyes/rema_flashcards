import random
import streamlit as st
from utils.deck_builder import build_deck


MODES = ["Comprehensive", "Individual (Info Split)", "Word of the Belt"]

MODE_DESCRIPTIONS = {
    "Comprehensive": "One card per belt — tests everything at once: word of belt, combos, forms, and more.",
    "Individual (Info Split)": "Most granular — one card per combo, one card per form, one card for word of belt.",
    "Word of the Belt": "One card per selected belt — word and meaning only. Ignores cycle selections.",
}


def _build_and_shuffle():
    cards = build_deck(
        st.session_state.selected_belt_keys,
        st.session_state.unlocked_cycles,
        st.session_state.flashcard_mode,
        include_word=st.session_state.info_split_include_word,
        include_forms=st.session_state.info_split_include_forms,
    )
    st.session_state.cards       = cards
    st.session_state.card_index  = 0
    st.session_state.show_answer = False


def render():
    if not st.session_state.get("settings_saved"):
        st.warning("👈 Please configure your belt and cycles in **Settings** first.")
        return

    st.title("🃏 Flashcards")

    # ── Deck controls ─────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        saved_mode = st.session_state.flashcard_mode
        mode_index = MODES.index(saved_mode) if saved_mode in MODES else 0
        mode = st.selectbox(
            "Mode",
            MODES,
            index=mode_index,
            help="\n\n".join(f"**{m}**: {d}" for m, d in MODE_DESCRIPTIONS.items()),
        )
        if mode != st.session_state.flashcard_mode:
            st.session_state.flashcard_mode = mode
            st.session_state.cards = []

    with col2:
        st.write("")
        if st.button("🔀 Shuffle", use_container_width=True):
            random.shuffle(st.session_state.cards)
            st.session_state.card_index  = 0
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        st.write("")
        if st.button("🃏 Build Deck", type="primary", use_container_width=True):
            _build_and_shuffle()

    # ── Info Split filters ────────────────────────────────────────────────────
    if mode == "Individual (Info Split)":
        fc1, fc2 = st.columns(2)
        with fc1:
            include_word = st.checkbox(
                "Include Word of Belt",
                value=st.session_state.info_split_include_word,
                key="cb_include_word",
            )
        with fc2:
            include_forms = st.checkbox(
                "Include Forms",
                value=st.session_state.info_split_include_forms,
                key="cb_include_forms",
            )
        if (include_word  != st.session_state.info_split_include_word or
                include_forms != st.session_state.info_split_include_forms):
            st.session_state.info_split_include_word  = include_word
            st.session_state.info_split_include_forms = include_forms
            st.session_state.cards = []

    # Auto-build if no deck yet
    if not st.session_state.cards:
        _build_and_shuffle()

    cards = st.session_state.cards
    if not cards:
        st.error("No flashcards generated. Try unlocking more cycles in Settings.")
        return

    idx   = st.session_state.card_index
    card  = cards[idx]
    total = len(cards)

    st.divider()

    # ── Progress ──────────────────────────────────────────────────────────────
    st.progress((idx) / total, text=f"Card {idx + 1} of {total}")

    # ── Belt + category badge ─────────────────────────────────────────────────
    badge_col, spacer = st.columns([3, 1])
    with badge_col:
        st.markdown(
            f"`{card['belt']}` &nbsp;·&nbsp; `{card['category']}`",
            unsafe_allow_html=True,
        )

    # ── Card ──────────────────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"### {card['question']}")

        if st.session_state.show_answer:
            st.divider()
            st.markdown(card["answer"])
        else:
            st.markdown(" ")
            st.markdown(" ")

    # ── Flip / nav buttons ────────────────────────────────────────────────────
    btn1, btn2, btn3, btn4 = st.columns([1, 1, 1, 1])

    with btn1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
            st.session_state.card_index  = idx - 1
            st.session_state.show_answer = False
            st.rerun()

    with btn2:
        flip_label = "🙈 Hide Answer" if st.session_state.show_answer else "👁️ Show Answer"
        if st.button(flip_label, use_container_width=True, type="primary"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()

    with btn3:
        if st.button("➡️ Next", use_container_width=True, disabled=(idx == total - 1)):
            st.session_state.card_index  = idx + 1
            st.session_state.show_answer = False
            st.rerun()

    with btn4:
        if st.button("🔁 Restart", use_container_width=True):
            st.session_state.card_index  = 0
            st.session_state.show_answer = False
            st.rerun()

    # ── Completion banner ─────────────────────────────────────────────────────
    if idx == total - 1 and st.session_state.show_answer:
        st.success("🎉 You've completed the deck! Hit Restart to go again.")

    # ── Deck overview ─────────────────────────────────────────────────────────
    with st.expander("📋 Full Deck Overview"):
        for i, c in enumerate(cards):
            marker = "👉" if i == idx else "  "
            st.markdown(f"{marker} **{i+1}.** `{c['belt']}` — {c['category']} — *{c['question'][:60]}...*")
