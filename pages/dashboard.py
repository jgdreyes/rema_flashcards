import streamlit as st
from utils.auth import get_current_user
from utils.data import get_belt_order, get_belt, load_cycles
from utils.user_settings import load_settings


def render():
    user = get_current_user()
    if not user:
        st.switch_page(st.session_state["_curriculum_page"])
        return

    if not st.session_state.get("settings_loaded_from_db"):
        load_settings(user["id"])

    selected_keys  = st.session_state.get("selected_belt_keys", [])
    unlocked_keys  = st.session_state.get("unlocked_cycles", [])
    belt_order     = get_belt_order()   # [(key, name), ...]
    selected_set   = set(selected_keys)

    st.title(f"Hello, Future Black Belt! 🥋")
    st.markdown(f"Welcome back, **{user['first_name']}**. Look at your progress already!")
    st.divider()

    if not selected_keys:
        st.info("You haven't saved any belt selections yet. Head to **User Settings** to get started.")
        return

    # ── Belt progression ──────────────────────────────────────────────────────
    # Find index of last achieved belt in full order
    last_achieved_idx = -1
    for i, (key, _) in enumerate(belt_order):
        if key in selected_set:
            last_achieved_idx = i

    all_cycles    = load_cycles()
    cycle_map     = {c["cycle_key"]: c["cycle_name"] for c in all_cycles}

    rows_html = []
    for i, (key, name) in enumerate(belt_order):
        belt      = get_belt(key)
        color     = belt.get("belt_color", {}) if belt else {}
        bg        = color.get("background_color", "#888888")
        fg        = color.get("foreground_color", "#FFFFFF")
        stripe    = color.get("stripe_color")
        achieved  = key in selected_set

        if achieved:
            if stripe:
                dot_bg = f"linear-gradient(to bottom, {bg} 0%, {bg} 35%, {stripe} 35%, {stripe} 65%, {bg} 65%)"
            else:
                dot_bg = bg
            dot_style  = (
                f"width:36px;height:36px;border-radius:50%;background:{dot_bg};"
                f"flex-shrink:0;box-shadow:0 0 0 3px {bg}44;"
            )
            name_style = f"color:{fg if fg != '#FFFFFF' else 'inherit'};font-weight:700;font-size:1rem;"
            row_bg     = f"background:{bg}22;border-radius:8px;padding:6px 14px;"
        else:
            dot_style  = (
                "width:36px;height:36px;border-radius:50%;background:#3a3a3a;"
                "flex-shrink:0;border:2px solid #555;"
            )
            name_style = "color:#666;font-weight:400;font-size:1rem;"
            row_bg     = "padding:6px 14px;"

        # Cycle sub-labels for this belt
        belt_cycle_keys = belt.get("cycles", []) if belt else []
        earned_cycles   = [cycle_map[ck] for ck in belt_cycle_keys if ck in unlocked_keys and ck in cycle_map]
        cycle_html      = ""
        if earned_cycles and achieved:
            tags = "".join(
                f'<span style="background:#ffffff22;color:inherit;font-size:0.7rem;'
                f'padding:1px 7px;border-radius:10px;margin-left:6px;">{c}</span>'
                for c in earned_cycles
            )
            cycle_html = f'<span style="margin-left:8px;">{tags}</span>'

        rows_html.append(
            f'<div style="display:flex;align-items:center;gap:14px;{row_bg}margin:0;">'
            f'  <div style="{dot_style}"></div>'
            f'  <span style="{name_style}">{name}{cycle_html}</span>'
            f'</div>'
        )

        # Connector line between rows
        if i < len(belt_order) - 1:
            if i == last_achieved_idx:
                # Dashed line after last achieved belt
                rows_html.append(
                    '<div style="display:flex;align-items:center;gap:14px;padding:0 14px;">'
                    '  <div style="width:36px;display:flex;justify-content:center;">'
                    '    <div style="width:2px;height:28px;border-left:2px dashed #555;"></div>'
                    '  </div>'
                    '  <span style="color:#555;font-size:0.75rem;letter-spacing:0.05em;">your journey continues...</span>'
                    '</div>'
                )
            else:
                line_color = "#555" if not achieved else bg
                rows_html.append(
                    f'<div style="display:flex;gap:14px;padding:0 14px;">'
                    f'  <div style="width:36px;display:flex;justify-content:center;">'
                    f'    <div style="width:2px;height:16px;background:{line_color};opacity:0.5;"></div>'
                    f'  </div>'
                    f'</div>'
                )

    st.markdown(
        '<div style="max-width:480px;">' + "".join(rows_html) + '</div>',
        unsafe_allow_html=True,
    )

    # ── Cycles summary ────────────────────────────────────────────────────────
    if unlocked_keys:
        st.divider()
        st.markdown(f"**🔄 Cycles unlocked:** {len(unlocked_keys)}")
        for ck in unlocked_keys:
            st.markdown(f"- {cycle_map.get(ck, ck)}")