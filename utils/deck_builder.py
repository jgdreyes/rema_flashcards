"""
Builds flashcard decks from belt/cycle data.

Each card is a dict:
  {
    "question": str,
    "answer":   str,
    "category": str,   # "Word of Belt", "Combo", "Form", etc.
    "belt":     str,   # belt_name
  }

Modes
─────
comprehensive      – one card per belt covering ALL info
individual_info    – one card for word, one for all combos, one for all forms
individual_split   – one card for word, one per combo, one per form
"""

from utils.data import get_belts_for_keys, load_curriculum, get_cycle


# ── helpers ─────────────────────────────────────────────────────────────────

def _fmt_combos(combos):
    lines = []
    for c in combos:
        lines.append(f"  {c['number']}. {c['text']}")
    return "\n".join(lines)


def _fmt_forms(forms):
    lines = []
    for f in forms:
        lines.append(f"  • {f['name']} — {f['meaning']}")
    return "\n".join(lines)


def _basics_text(basics):
    parts = []
    for section, items in basics.items():
        parts.append(f"**{section.title()}:** " + ", ".join(items))
    return "\n".join(parts)


def _cycle_label(cycle_key):
    if not cycle_key:
        return ""
    cyc = get_cycle(cycle_key)
    return f" *(introduced in {cyc['cycle_name']})*" if cyc else ""


# ── per-belt card factories ──────────────────────────────────────────────────

def _comprehensive_card(belt):
    curr = belt.get("curriculum", {})
    answer_parts = []

    # Word of belt
    answer_parts.append(
        f"**Word of the Belt:** {belt['word_of_the_belt']}\n"
        f"{belt.get('description') or ''}"
    )

    # Fitness
    answer_parts.append(f"**Fitness reps:** {belt['fitness_reps']}")

    # Basics (White / Gold)
    if curr.get("basics"):
        answer_parts.append("**Basics:**\n" + _basics_text(curr["basics"]))

    # Combos
    if curr.get("combos"):
        combo_lines = []
        for c in curr["combos"]:
            label = _cycle_label(c.get("cycle_key"))
            combo_lines.append(f"  {c['number']}. {c['text']}{label}")
        answer_parts.append("**Combos:**\n" + "\n".join(combo_lines))

    # Forms
    if curr.get("forms"):
        answer_parts.append("**Forms:**\n" + _fmt_forms(curr["forms"]))

    # Kicks / footwork (High Orange)
    if curr.get("kicks"):
        answer_parts.append("**Kicks:** " + ", ".join(curr["kicks"]))
    if curr.get("footwork_patterns"):
        answer_parts.append("**Footwork:** " + ", ".join(curr["footwork_patterns"]))

    return {
        "question": f"Tell me everything about **{belt['belt_name']}**.",
        "answer": "\n\n".join(answer_parts),
        "category": "Comprehensive",
        "belt": belt["belt_name"],
    }


def _info_cards(belt):
    """One card for word, one for all combos, one for all forms."""
    curr = belt.get("curriculum", {})
    cards = []

    # Word of belt
    cards.append({
        "question": f"What is the **Word of the Belt** for {belt['belt_name']}?",
        "answer": f"**{belt['word_of_the_belt']}**\n\n{belt.get('description') or ''}",
        "category": "Word of Belt",
        "belt": belt["belt_name"],
    })

    # Basics
    if curr.get("basics"):
        cards.append({
            "question": f"What are the **basics** taught at {belt['belt_name']}?",
            "answer": _basics_text(curr["basics"]),
            "category": "Basics",
            "belt": belt["belt_name"],
        })

    # Kicks / footwork (High Orange)
    if curr.get("kicks") or curr.get("footwork_patterns"):
        ans = []
        if curr.get("kicks"):
            ans.append("**Kicks:** " + ", ".join(curr["kicks"]))
        if curr.get("footwork_patterns"):
            ans.append("**Footwork patterns:** " + ", ".join(curr["footwork_patterns"]))
        cards.append({
            "question": f"What kicks and footwork are introduced at {belt['belt_name']}?",
            "answer": "\n\n".join(ans),
            "category": "Kicks & Footwork",
            "belt": belt["belt_name"],
        })

    # All combos together
    if curr.get("combos"):
        combo_lines = []
        for c in curr["combos"]:
            label = _cycle_label(c.get("cycle_key"))
            combo_lines.append(f"**{c['number']}.** {c['text']}{label}")
        cards.append({
            "question": f"What are all the **combos** for {belt['belt_name']}?",
            "answer": "\n\n".join(combo_lines),
            "category": "Combos",
            "belt": belt["belt_name"],
        })

    # All forms together
    if curr.get("forms"):
        cards.append({
            "question": f"What **forms** does a {belt['belt_name']} student know?",
            "answer": _fmt_forms(curr["forms"]),
            "category": "Forms",
            "belt": belt["belt_name"],
        })

    return cards


def _info_split_cards(belt):
    """One card per combo, one card per form, one card for word."""
    curr = belt.get("curriculum", {})
    cards = []

    # Word of belt
    cards.append({
        "question": f"What is the **Word of the Belt** for {belt['belt_name']}?",
        "answer": f"**{belt['word_of_the_belt']}**\n\n{belt.get('description') or ''}",
        "category": "Word of Belt",
        "belt": belt["belt_name"],
    })

    # Basics
    if curr.get("basics"):
        for section, items in curr["basics"].items():
            cards.append({
                "question": f"Name the **{section}** basics for {belt['belt_name']}.",
                "answer": "\n".join(f"• {i}" for i in items),
                "category": "Basics",
                "belt": belt["belt_name"],
            })

    # Kicks / footwork (High Orange) — split
    if curr.get("kicks"):
        cards.append({
            "question": f"What are the kicks learned at {belt['belt_name']}?",
            "answer": "\n".join(f"• {k}" for k in curr["kicks"]),
            "category": "Kicks",
            "belt": belt["belt_name"],
        })

    # Each combo individually
    if curr.get("combos"):
        for c in curr["combos"]:
            label = _cycle_label(c.get("cycle_key"))
            belt_label = c.get("_source_belt", belt["belt_name"])
            cards.append({
                "question": f"**{belt_label} — Combo {c['number']}**: What are the techniques?",
                "answer": f"{c['text']}{label}",
                "category": f"Combo {c['number']}",
                "belt": belt_label,
            })

    # Each form individually
    if curr.get("forms"):
        for f in curr["forms"]:
            cyc_label = _cycle_label(f.get("cycle_key"))
            cards.append({
                "question": f"What does the form **{f['name']}** mean? (learned at {belt['belt_name']}{cyc_label})",
                "answer": f"**{f['name']}** — {f['meaning']}",
                "category": "Form",
                "belt": belt["belt_name"],
            })

    return cards


# ── public API ───────────────────────────────────────────────────────────────

def build_deck(selected_belt_keys, unlocked_cycles, mode):
    """
    Build and return a list of flashcard dicts.

    selected_belt_keys: list of belt_keys to include in the deck.
    unlocked_cycles: list of cycle_keys the student has reached.

    Comprehensive / Individual (Info): belt-level info only (no cycle-specific
    combos or forms for multi-cycle belts).
    Individual (Info Split): aggregates combos/forms from the full sibling belt
    family (e.g. red/high_red/low_brown) filtered to the unlocked cycles.
    """
    import copy
    all_curriculum = load_curriculum()
    belts = get_belts_for_keys(selected_belt_keys)
    cards = []

    for belt in belts:
        belt = copy.deepcopy(belt)
        curr = belt.get("curriculum", {})
        is_multi_cycle = bool(belt.get("cycles"))

        if mode == "Comprehensive":
            if is_multi_cycle:
                # Comprehensive: belt-level info only — no cycle-specific combos/forms
                curr["combos"] = []
                curr["forms"] = []

        elif mode in ("Individual (Info)", "Individual (Info Split)"):
            if is_multi_cycle:
                # Aggregate combos/forms from the entire sibling belt family
                # (all belts that share the same cycles) for the unlocked cycles
                belt_cycle_set = set(belt["cycles"])
                agg_combos = []
                agg_forms = []
                seen_forms = set()

                for b in all_curriculum:
                    if b.get("cycles") and set(b["cycles"]) == belt_cycle_set:
                        b_curr = b.get("curriculum", {})
                        for c in b_curr.get("combos", []):
                            if c.get("cycle_key") in unlocked_cycles:
                                agg_combos.append({**c, "_source_belt": b["belt_name"]})
                        for f in b_curr.get("forms", []):
                            if (not f.get("cycle_key") or f.get("cycle_key") in unlocked_cycles) \
                                    and f["name"] not in seen_forms:
                                agg_forms.append(f)
                                seen_forms.add(f["name"])

                curr["combos"] = agg_combos
                curr["forms"] = agg_forms

        # Skip belt entirely if nothing to show
        has_content = (
            curr.get("combos") or curr.get("forms") or
            curr.get("basics") or curr.get("kicks")
        )
        if not has_content and not belt.get("word_of_the_belt"):
            continue

        if mode == "Comprehensive":
            cards.append(_comprehensive_card(belt))
        elif mode == "Individual (Info)":
            cards.extend(_info_cards(belt))
        elif mode == "Individual (Info Split)":
            cards.extend(_info_split_cards(belt))

    return cards
