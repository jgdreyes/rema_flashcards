import json
import streamlit as st
import streamlit.components.v1 as components
from utils.data import load_curriculum, get_belt, get_cycle, get_form, get_weapon

_DEFAULT_BG    = "#888888"
_DEFAULT_FG    = "#FFFFFF"
_DEFAULT_STRIPE = None


def _belt_colors(belt):
    """Return (background_color, foreground_color, stripe_color) from belt data."""
    c = belt.get("belt_color", {})
    return (
        c.get("background_color", _DEFAULT_BG),
        c.get("foreground_color", _DEFAULT_FG),
        c.get("stripe_color", _DEFAULT_STRIPE),
    )


def _inject_belt_colors():
    """Use a components iframe to run JS that styles belt buttons in the parent page."""
    curriculum = load_curriculum()
    color_map = {
        belt["belt_name"]: list(_belt_colors(belt))
        for belt in curriculum
    }
    color_map_json = json.dumps(color_map)
    components.html(f"""
<script>
(function () {{
    var colors = {color_map_json};

    function styleButtons() {{
        var doc = window.parent.document;
        doc.querySelectorAll('button').forEach(function (btn) {{
            var text = btn.innerText.trim();
            if (colors[text]) {{
                var bg     = colors[text][0];
                var fg     = colors[text][1];
                var stripe = colors[text][2];
                var bgValue = stripe
                    ? 'linear-gradient(to bottom,' + bg + ' 0%,' + bg + ' 34%,' + stripe + ' 34%,' + stripe + ' 66%,' + bg + ' 66%,' + bg + ' 100%)'
                    : bg;
                var textColor = stripe
                    ? (stripe === '#000000' ? '#FFFFFF' : '#000000')
                    : fg;
                btn.style.setProperty('background',    bgValue,                       'important');
                btn.style.setProperty('color',         textColor,                     'important');
                btn.style.setProperty('height',        '90px',                        'important');
                btn.style.setProperty('font-size',     '13px',                        'important');
                btn.style.setProperty('font-weight',   '700',                         'important');
                btn.style.setProperty('border-radius', '10px',                        'important');
                btn.style.setProperty('white-space',   'normal',                      'important');
                btn.style.setProperty('line-height',   '1.3',                         'important');
                btn.style.setProperty('border',        '2px solid rgba(0,0,0,0.15)', 'important');
            }}
        }});
    }}

    var obs = new MutationObserver(styleButtons);
    obs.observe(window.parent.document.body, {{ childList: true, subtree: true }});
    styleButtons();
    setTimeout(styleButtons, 300);
    setTimeout(styleButtons, 800);
}})();
</script>
""", height=0)


# ── Grid view ────────────────────────────────────────────────────────────────

def _show_grid():
    st.title("📋 Belt Curriculum")
    st.caption("Select a belt to view its full curriculum.")

    _inject_belt_colors()

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
                    st.switch_page(st.session_state["_belt_pages"][belt["belt_key"]])


# ── Detail view ──────────────────────────────────────────────────────────────

def _section_header(text):
    st.markdown(f"### {text}")


def _video_previews(video_urls):
    if not video_urls:
        return
    cols = st.columns(min(len(video_urls), 3))
    for i, url in enumerate(video_urls):
        with cols[i % len(cols)]:
            label = f"Part {i + 1}" if len(video_urls) > 1 else None
            if label:
                st.caption(label)
            st.video(url)


def _show_detail(belt_key):
    belt = get_belt(belt_key)
    if not belt:
        st.error("Belt not found.")
        return

    bg, fg, _stripe = _belt_colors(belt)
    curr = belt.get("curriculum", {})

    # ── Back button ───────────────────────────────────────────────────────────
    if st.button("← Back to Curriculum"):
        st.switch_page(st.session_state["_curriculum_page"])

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
        if belt.get("word_of_the_belt_description"):
            st.markdown(belt["word_of_the_belt_description"])

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
        multiple = len(curr["forms"]) > 1
        for f in curr["forms"]:
            form = get_form(f["form_key"])
            if not form:
                continue
            if multiple:
                with st.expander(f"{form['form_name']} — *{form['meaning']}*"):
                    _video_previews(form.get("video_urls", []))
            else:
                st.markdown(f"**{form['form_name']}** — *{form['meaning']}*")
                _video_previews(form.get("video_urls", []))
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
                            _video_previews(form.get("video_urls", []))
                    if cycle.get("weapon_key"):
                        weapon = get_weapon(cycle["weapon_key"])
                        if weapon:
                            st.markdown(f"**Weapon:** {weapon['weapon_name']}")
                            if weapon.get("description"):
                                st.caption(weapon["description"])
                            _video_previews(weapon.get("video_urls", []))
                            if weapon.get("techniques"):
                                st.markdown("**Techniques:**")
                                for tech in weapon["techniques"]:
                                    st.markdown(f"• {tech}")


# ── Entry point ───────────────────────────────────────────────────────────────

def render():
    _show_grid()
