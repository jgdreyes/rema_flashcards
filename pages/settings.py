import streamlit as st
from utils.data import get_belt_order, get_belt, load_cycles


def render():
    st.title("⚙️ Settings")
    st.markdown("Configure which belts and cycles you want to study.")
    st.divider()

    belt_order = get_belt_order()   # [(key, name), ...]

    # ── Belt selection ────────────────────────────────────────────────────────
    st.subheader("🥋 Belts")
    st.markdown("Select which belts to include in your flashcard deck.")

    saved_keys = set(st.session_state.get("selected_belt_keys", []))

    selected_belt_keys = []
    for key, name in belt_order:
        checked = st.checkbox(name, value=(key in saved_keys), key=f"belt_cb_{key}")
        if checked:
            selected_belt_keys.append(key)

    # ── Cycles (shown for any selected belt that has cycles) ─────────────────
    all_cycles = load_cycles()
    selected_cycles = []

    relevant_cycle_keys = set()
    for key in selected_belt_keys:
        belt = get_belt(key)
        if belt and belt.get("cycles"):
            for ck in belt["cycles"]:
                relevant_cycle_keys.add(ck)

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
                details = []
                for fk in cycle.get("form_keys", []):
                    details.append(f"Form: *{fk.replace('_', ' ').title()}*")
                if cycle.get("weapon_key"):
                    details.append(f"Weapon: *{cycle['weapon_key'].replace('_', ' ').title()}*")
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
        st.session_state.selected_belt_keys = selected_belt_keys
        st.session_state.unlocked_cycles    = selected_cycles
        st.session_state.settings_saved     = True

        # Reset any active deck so it gets rebuilt
        st.session_state.cards       = []
        st.session_state.card_index  = 0
        st.session_state.show_answer = False
        st.success(f"✅ Settings saved! Belts: **{len(selected_belt_keys)}** | Cycles unlocked: **{len(selected_cycles)}**")
        st.balloons()