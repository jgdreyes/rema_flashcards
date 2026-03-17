import random
import streamlit as st
from utils.deck_builder import build_deck
from utils.data import get_belt_order, get_belt, load_cycles


MODES = ["Comprehensive", "Individual (Info Split)", "Word of the Belt"]

MODE_DESCRIPTIONS = {
    "Comprehensive": "One card per belt — tests everything at once: word of belt, combos, forms, and more.",
    "Individual (Info Split)": "Most granular — one card per combo, one card per form, one card for word of belt.",
    "Word of the Belt": "One card per selected belt — word and meaning only. Ignores cycle selections.",
}


def _build_and_shuffle():
    cards = build_deck(
        st.session_state.session_belt_keys or st.session_state.selected_belt_keys,
        st.session_state.unlocked_cycles,
        st.session_state.flashcard_mode,
        include_word=st.session_state.info_split_include_word,
        include_forms=st.session_state.info_split_include_forms,
    )
    st.session_state.cards       = cards
    st.session_state.card_index  = 0
    st.session_state.show_answer = False


def _show_progress_tags():
    selected_keys = st.session_state.get("selected_belt_keys", [])
    session_keys  = set(st.session_state.get("session_belt_keys", []))
    unlocked      = st.session_state.get("unlocked_cycles", [])
    has_focus     = bool(session_keys) and session_keys != set(selected_keys)

    if not selected_keys:
        st.caption("No belts configured.")
        return

    pills_html = []
    for key in selected_keys:
        belt = get_belt(key)
        if not belt:
            continue
        name   = belt["belt_name"]
        color  = belt.get("belt_color", {})
        bg     = color.get("background_color", "#888888")
        stripe = color.get("stripe_color")
        if stripe:
            bg_css = f"linear-gradient(to bottom, {bg} 0%, {bg} 35%, {stripe} 35%, {stripe} 65%, {bg} 65%)"
        else:
            bg_css = bg
        dimmed = has_focus and key not in session_keys
        extra  = "opacity:0.2;filter:grayscale(60%);" if dimmed else ""
        pills_html.append(
            f'<span class="belt-tip" style="background:{bg_css};width:32px;height:18px;'
            f'border-radius:4px;margin:2px 3px;display:inline-block;cursor:default;'
            f'position:relative;vertical-align:middle;{extra}">'
            f'<span class="belt-tiptext">{name}</span>'
            f'</span>'
        )

    cycle_count = len(unlocked)
    cycle_label = f"{cycle_count} cycle{'s' if cycle_count != 1 else ''} unlocked"
    if unlocked:
        all_cycles = load_cycles()
        cycle_name_map = {c["cycle_key"]: c["cycle_name"] for c in all_cycles}
        cycle_names = [cycle_name_map.get(k, k) for k in unlocked]
        tooltip_content = "<br>".join(cycle_names)
        cycle_pill = (
            f'<span class="cycle-tip" style="background:#2c2c2c;color:#cccccc;padding:3px 10px;'
            f'border-radius:12px;font-size:0.8rem;font-weight:600;'
            f'margin:2px 3px;display:inline-block;cursor:default;position:relative;">'
            f'🔄 {cycle_label}'
            f'<span class="cycle-tiptext">{tooltip_content}</span>'
            f'</span>'
        )
    else:
        cycle_pill = (
            f'<span style="background:#2c2c2c;color:#cccccc;padding:3px 10px;'
            f'border-radius:12px;font-size:0.8rem;font-weight:600;'
            f'margin:2px 3px;display:inline-block;">🔄 {cycle_label}</span>'
        )
    pills_html.append(cycle_pill)

    tooltip_css = """
    <style>
    .belt-tip .belt-tiptext, .cycle-tip .cycle-tiptext {
        visibility: hidden;
        background: #333;
        color: #fff;
        font-size: 0.75rem;
        font-weight: 400;
        text-align: left;
        padding: 6px 10px;
        border-radius: 6px;
        position: absolute;
        bottom: 140%;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
        z-index: 999;
        line-height: 1.6;
    }
    .belt-tip:hover .belt-tiptext { visibility: visible; }
    .cycle-tip:hover .cycle-tiptext { visibility: visible; }
    </style>
    """
    st.markdown(tooltip_css + " ".join(pills_html), unsafe_allow_html=True)


@st.dialog("Configure Progress")
def _configure_progress_dialog():
    belt_order = get_belt_order()
    saved_keys = set(st.session_state.get("selected_belt_keys", []))

    st.subheader("🥋 Belts")
    selected_belt_keys = []
    for key, name in belt_order:
        if st.checkbox(name, value=(key in saved_keys), key=f"dlg_belt_{key}"):
            selected_belt_keys.append(key)

    # Cycles for selected belts
    all_cycles = load_cycles()
    relevant_cycle_keys = set()
    for key in selected_belt_keys:
        belt = get_belt(key)
        if belt and belt.get("cycles"):
            for ck in belt["cycles"]:
                relevant_cycle_keys.add(ck)

    relevant_cycles = [c for c in all_cycles if c["cycle_key"] in relevant_cycle_keys]
    selected_cycles = []

    if relevant_cycles:
        st.divider()
        st.subheader("🔄 Unlocked Cycles")
        saved_unlocked = st.session_state.get("unlocked_cycles", [])
        cols = st.columns(2)
        for i, cycle in enumerate(relevant_cycles):
            with cols[i % 2]:
                details = []
                for fk in cycle.get("form_keys", []):
                    details.append(f"Form: *{fk.replace('_', ' ').title()}*")
                if cycle.get("weapon_key"):
                    details.append(f"Weapon: *{cycle['weapon_key'].replace('_', ' ').title()}*")
                applies = ", ".join(cycle["applies_to_belts"]).replace("_", " ").title()
                details.append(f"Belts: {applies}")
                if st.checkbox(
                    cycle["cycle_name"],
                    value=cycle["cycle_key"] in saved_unlocked,
                    key=f"dlg_cycle_{cycle['cycle_key']}",
                    help=" | ".join(details),
                ):
                    selected_cycles.append(cycle["cycle_key"])

    st.divider()
    if st.button("💾 Save", type="primary", use_container_width=True):
        st.session_state.selected_belt_keys = selected_belt_keys
        st.session_state.unlocked_cycles    = selected_cycles
        st.session_state.settings_saved     = True
        st.session_state.cards              = []
        st.session_state.card_index         = 0
        st.session_state.show_answer        = False
        # Reset session focus to match new progress
        st.session_state.session_belt_keys  = list(selected_belt_keys)
        st.session_state.focus_gen         += 1
        st.rerun()


def render():
    from utils.auth import get_current_user
    user = get_current_user()

    st.title("🃏 Flashcards")

    if not st.session_state.get("settings_saved"):
        # ── Progress tags (always visible) ──────────────────────────────────
        tag_col, btn_col = st.columns([5, 1])
        with tag_col:
            _show_progress_tags()
        with btn_col:
            if st.button("⚙️ Configure", use_container_width=True):
                _configure_progress_dialog()
        if user:
            st.warning("👆 Hit Configure or visit **User Settings** to set up your belts and cycles.")
        else:
            st.info("👆 Hit Configure to select your belts and get started.")
        return

    # ── Sync session focus from checkbox widget states (runs before tags render)
    sel_set = set(st.session_state.selected_belt_keys)
    gen = st.session_state.focus_gen
    prev_focus = st.session_state.session_belt_keys
    # If checkbox keys exist in session_state, use them (they're updated before rerun)
    if any(f"sf_{k}_{gen}" in st.session_state for k in sel_set):
        synced = [k for k in st.session_state.selected_belt_keys
                  if st.session_state.get(f"sf_{k}_{gen}", True)]
        st.session_state.session_belt_keys = synced or list(st.session_state.selected_belt_keys)
    else:
        # First render — initialize to full set if empty
        valid = [k for k in st.session_state.session_belt_keys if k in sel_set]
        st.session_state.session_belt_keys = valid or list(st.session_state.selected_belt_keys)
    if set(st.session_state.session_belt_keys) != set(prev_focus):
        st.session_state.cards = []

    # ── Progress tags (always visible) ────────────────────────────────────────
    tag_col, btn_col = st.columns([5, 1])
    with tag_col:
        _show_progress_tags()
    with btn_col:
        if st.button("⚙️ Configure", use_container_width=True):
            _configure_progress_dialog()

    # ── Deck controls ─────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
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
        show_all = st.checkbox("Practice Mode", value=False, key="practice_show_all")

    with col3:
        # Belt focus dropdown
        configured = [(k, n) for k, n in get_belt_order() if k in sel_set]
        n_total = len(configured)
        n_focus = len(st.session_state.session_belt_keys)
        label = f"🎯 Focus ({n_focus}/{n_total})"
        with st.popover(label, use_container_width=True):
            new_keys = []
            for key, name in configured:
                checked = st.checkbox(
                    name,
                    value=key in st.session_state.session_belt_keys,
                    key=f"sf_{key}_{gen}",
                )
                if checked:
                    new_keys.append(key)
            if new_keys != st.session_state.session_belt_keys:
                st.session_state.session_belt_keys = new_keys or list(st.session_state.selected_belt_keys)
                st.session_state.cards = []
            st.divider()
            if st.button("↩️ Reset to All", use_container_width=True):
                st.session_state.session_belt_keys = list(st.session_state.selected_belt_keys)
                st.session_state.focus_gen        += 1
                st.session_state.cards             = []
                st.rerun()

    with col4:
        st.write("")
        if st.button("🔀 Shuffle", use_container_width=True):
            random.shuffle(st.session_state.cards)
            st.session_state.card_index  = 0
            st.session_state.show_answer = False
            st.rerun()

    with col5:
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

    if show_all:
        st.info("📖 **Practice Mode** — answers are always visible.")

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

        if st.session_state.show_answer or show_all:
            st.divider()
            st.markdown(card["answer"])
        else:
            st.markdown(" ")
            st.markdown(" ")

    # ── Flip / nav buttons ────────────────────────────────────────────────────
    if show_all:
        btn1, btn3, btn4 = st.columns([1, 1, 1])
    else:
        btn1, btn2, btn3, btn4 = st.columns([1, 1, 1, 1])

    with btn1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
            st.session_state.card_index  = idx - 1
            st.session_state.show_answer = False
            st.rerun()

    if not show_all:
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