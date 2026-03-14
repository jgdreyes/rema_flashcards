import json
import streamlit as st
from utils.data import load_curriculum, get_belt, get_cycle, get_form, get_weapon

# Belt background / foreground colors
BELT_COLORS = {
    "white_belt":             ("#F5F5F5", "#222222"),
    "gold_belt":              ("#FFD700", "#2a1f00"),
    "high_gold_belt":         ("#DAA520", "#2a1f00"),
    "orange_belt":            ("#FF8C00", "#1a0800"),
    "high_orange_belt":       ("#E06000", "#1a0600"),
    "green_belt":             ("#2E8B57", "#FFFFFF"),
    "purple_belt":            ("#7B2D8B", "#FFFFFF"),
    "blue_belt":              ("#1E6FBF", "#FFFFFF"),
    "high_blue_belt":         ("#0A4A8F", "#FFFFFF"),
    "red_belt":               ("#C41E3A", "#FFFFFF"),
    "high_red_belt":          ("#8B0000", "#FFFFFF"),
    "low_brown_belt":         ("#B8732A", "#FFFFFF"),
    "brown_belt":             ("#8B4513", "#FFFFFF"),
    "high_brown_belt":        ("#5C2E0A", "#FFFFFF"),
    "conditional_black_belt": ("#1A1A1A", "#FFFFFF"),
}


def _belt_color_script():
    """Inject JS that styles belt-name buttons with their belt color."""
    curriculum = load_curriculum()
    color_map = {
        belt["belt_name"]: list(BELT_COLORS.get(belt["belt_key"], ("#888", "#FFF")))
        for belt in curriculum
    }
    color_map_json = json.dumps(color_map)
    return f"""
<script>
(function () {{
    const colors = {color_map_json};

    function styleButtons() {{
        document.querySelectorAll('button[data-testid="stBaseButton-secondary"]').forEach(function (btn) {{
            var text = btn.innerText.trim();
            if (colors[text]) {{
                btn.style.setProperty('background-color', colors[text][0], 'important');
                btn.style.setProperty('color',            colors[text][1], 'important');
                btn.style.setProperty('height',           '90px',         'important');
                btn.style.setProperty('font-size',        '13px',         'important');
                btn.style.setProperty('font-weight',      '700',          'important');
                btn.style.setProperty('border-radius',    '10px',         'important');
                btn.style.setProperty('white-space',      'normal',       'important');
                btn.style.setProperty('line-height',      '1.3',          'important');
                btn.style.setProperty('border',           '2px solid rgba(0,0,0,0.15)', 'important');
            }}
        }});
    }}

    var obs = new MutationObserver(styleButtons);
    obs.observe(document.body, {{ childList: true, subtree: true }});
    styleButtons();
    setTimeout(styleButtons, 200);
    setTimeout(styleButtons, 600);
}})();
</script>
"""


# ── Grid view ────────────────────────────────────────────────────────────────

def _show_grid():
    st.title("📋 Belt Curriculum")
    st.caption("Select a belt to view its full curriculum.")

    st.markdown(_belt_color_script(), unsafe_allow_html=True)

    curriculum = load_curriculum()
    COLS = 5
    rows = [curriculum[i : i + COLS] for i in range(0, len(curriculum), COLS)]

    for row in rows:
        cols = st.columns(COLS)
        for col, belt in zip(cols, row):
            with col:
                if st.button(
                    belt["belt_name"],
                    key=f"grid_{belt['belt_key']}",
                    use_container_width=True,
                ):
                    st.session_state.curriculum_selected_belt = belt["belt_key"]
                    st.rerun()


# ── Detail view ──────────────────────────────────────────────────────────────

def _section_header(text):
    st.markdown(f"### {text}")


def _show_detail(belt_key):
    belt = get_belt(belt_key)
    if not belt:
        st.error("Belt not found.")
        return

    bg, fg = BELT_COLORS.get(belt_key, ("#888888", "#FFFFFF"))
    curr = belt.get("curriculum", {})

    # ── Back button ───────────────────────────────────────────────────────────
    if st.button("← Back to Curriculum"):
        st.session_state.curriculum_selected_belt = None
        st.rerun()

    # ── Colored header banner ─────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background:{bg};
            color:{fg};
            padding:28px 36px;
            border-radius:14px;
            margin:12px 0 24px;
        ">
            <h1 style="margin:0;color:{fg};font-size:2rem;">{belt['belt_name']}</h1>
            <p style="margin:10px 0 0;font-size:1.1em;opacity:0.9;font-style:italic;">
                {belt.get('word_of_the_belt', '')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Overview row ──────────────────────────────────────────────────────────
    info_col, rep_col, pdf_col = st.columns([3, 1, 1])

    with info_col:
        if belt.get("description"):
            st.markdown(belt["description"])

    with rep_col:
        st.metric("Fitness Reps", belt.get("fitness_reps", "—"))

    with pdf_col:
        pdf_url = curr.get("curriculum_pdf")
        if pdf_url:
            st.link_button("📄 PDF", pdf_url, use_container_width=True)

    st.divider()

    # ── Basics ────────────────────────────────────────────────────────────────
    if curr.get("basics"):
        _section_header("Basics")
        basics = curr["basics"]
        section_cols = st.columns(len(basics))
        for col, (section_name, items) in zip(section_cols, basics.items()):
            with col:
                st.markdown(f"**{section_name.title()}**")
                for item in items:
                    st.markdown(f"• {item}")
        st.divider()

    # ── Kicks ─────────────────────────────────────────────────────────────────
    if curr.get("kicks"):
        _section_header("Kicks")
        kick_cols = st.columns(min(len(curr["kicks"]), 4))
        for i, kick in enumerate(curr["kicks"]):
            kick_cols[i % len(kick_cols)].markdown(f"• {kick}")
        st.divider()

    # ── Footwork ──────────────────────────────────────────────────────────────
    if curr.get("footwork_patterns"):
        _section_header("Footwork Patterns")
        fp_cols = st.columns(min(len(curr["footwork_patterns"]), 4))
        for i, fp in enumerate(curr["footwork_patterns"]):
            fp_cols[i % len(fp_cols)].markdown(f"• {fp}")
        st.divider()

    # ── Combos ────────────────────────────────────────────────────────────────
    if curr.get("combos"):
        _section_header("Combos")
        if curr.get("note"):
            st.caption(curr["note"])
        for combo in curr["combos"]:
            st.markdown(f"**{combo['number']}.** {combo['text']}")
        st.divider()

    # ── Forms ─────────────────────────────────────────────────────────────────
    if curr.get("forms"):
        _section_header("Forms")
        for f in curr["forms"]:
            form = get_form(f["form_key"])
            if form:
                st.markdown(f"**{form['form_name']}** — *{form['meaning']}*")
        st.divider()

    # ── Cycles (multi-cycle belts) ────────────────────────────────────────────
    if belt.get("cycles"):
        _section_header("Cycles")
        st.caption("This belt trains across multiple cycles. Each cycle introduces new content.")
        for cycle_key in belt["cycles"]:
            cycle = get_cycle(cycle_key)
            if not cycle:
                continue
            with st.expander(cycle["cycle_name"]):
                c1, c2 = st.columns([3, 1])
                with c2:
                    if cycle.get("curriculum_pdf"):
                        st.link_button("📄 Cycle PDF", cycle["curriculum_pdf"], use_container_width=True)
                with c1:
                    for fk in cycle.get("form_keys", []):
                        form = get_form(fk)
                        if form:
                            st.markdown(f"**Form:** {form['form_name']} — *{form['meaning']}*")
                    if cycle.get("weapon_key"):
                        weapon = get_weapon(cycle["weapon_key"])
                        if weapon:
                            st.markdown(f"**Weapon:** {weapon['weapon_name']}")
                            if weapon.get("description"):
                                st.caption(weapon["description"])
                            if weapon.get("techniques"):
                                st.markdown("**Techniques:**")
                                for tech in weapon["techniques"]:
                                    st.markdown(f"• {tech}")


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    selected = st.session_state.get("curriculum_selected_belt")
    if selected:
        _show_detail(selected)
    else:
        _show_grid()
