import streamlit as st
from utils.data import get_belt_order, get_belt, load_cycles


def render():
    st.title("⚙️ Settings")
    st.markdown("Configure your current belt rank and which cycles you've unlocked.")
    st.divider()

    belt_order = get_belt_order()   # [(key, name), ...]
    belt_names = [name for _, name in belt_order]
    belt_keys  = [key  for key, _ in belt_order]

    # ── Current belt ─────────────────────────────────────────────────────────
    st.subheader("🥋 Current Belt")

    saved_key = st.session_state.get("current_belt_key") or belt_keys[0]

    def make_belt_handler(changed_key):
        def handler():
            if st.session_state[f"belt_cb_{changed_key}"]:
                for k in belt_keys:
                    if k != changed_key:
                        st.session_state[f"belt_cb_{k}"] = False
            else:
                if not any(st.session_state.get(f"belt_cb_{k}") for k in belt_keys):
                    st.session_state[f"belt_cb_{changed_key}"] = True
        return handler

    selected_key = None
    for key, name in belt_order:
        is_checked = st.checkbox(
            name,
            value=(key == saved_key),
            key=f"belt_cb_{key}",
            on_change=make_belt_handler(key),
        )
        if is_checked:
            selected_key = key

    if selected_key is None:
        selected_key = saved_key

    selected_name = belt_names[belt_keys.index(selected_key)]
    selected_belt = get_belt(selected_key)

    if selected_belt:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Fitness Reps", selected_belt["fitness_reps"])
        with col2:
            st.metric("Word of the Belt", selected_belt["word_of_the_belt"])

    # ── Cycles (only shown if belt has cycles) ───────────────────────────────
    all_cycles = load_cycles()
    selected_cycles = []

    # Gather all cycles relevant up to the selected belt
    # We need to find which cycles apply to any belt up to selected
    relevant_cycle_keys = set()
    for key, _ in belt_order:
        belt = get_belt(key)
        if belt and belt.get("cycles"):
            for ck in belt["cycles"]:
                relevant_cycle_keys.add(ck)
        if key == selected_key:
            break

    relevant_cycles = [c for c in all_cycles if c["cycle_key"] in relevant_cycle_keys]

    if relevant_cycles:
        st.divider()
        st.subheader("🔄 Unlocked Cycles")
        st.markdown(
            "Multi-cycle belts (Red Belt and above) are taught in rotating cycles. "
            "Select which cycles your class has completed."
        )

        saved_unlocked = st.session_state.get("unlocked_cycles", [])

        cols = st.columns(2)
        for i, cycle in enumerate(relevant_cycles):
            with cols[i % 2]:
                # Show what the cycle contains
                details = []
                if cycle.get("form"):
                    details.append(f"Form: *{cycle['form']['name']}*")
                if cycle.get("weapon"):
                    details.append(f"Weapon: *{cycle['weapon']['name']}*")
                applies = ", ".join(cycle["applies_to_belts"]).replace("_", " ").title()
                details.append(f"Belts: {applies}")

                checked = st.checkbox(
                    cycle["cycle_name"],
                    value=cycle["cycle_key"] in saved_unlocked,
                    key=f"cycle_{cycle['cycle_key']}",
                    help=" | ".join(details),
                )
                if checked:
                    selected_cycles.append(cycle["cycle_key"])

    # ── Save ─────────────────────────────────────────────────────────────────
    st.divider()
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.session_state.current_belt_key  = selected_key
        st.session_state.current_belt_name = selected_name
        st.session_state.unlocked_cycles   = selected_cycles
        st.session_state.settings_saved    = True
        # Reset any active deck so it gets rebuilt
        st.session_state.cards      = []
        st.session_state.card_index = 0
        st.session_state.show_answer = False
        st.success(f"✅ Settings saved! Belt: **{selected_name}** | Cycles unlocked: **{len(selected_cycles)}**")
        st.balloons()
