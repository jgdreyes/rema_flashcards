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

    saved_key = st.session_state.get("current_belt_key")
    default_idx = belt_keys.index(saved_key) if saved_key in belt_keys else 0

    selected_name = st.selectbox(
        "Select your current belt",
        belt_names,
        index=default_idx,
    )
    selected_key = belt_keys[belt_names.index(selected_name)]
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
