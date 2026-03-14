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
comprehensive    – one card per belt covering ALL info (all cycles)
individual_split – one card per combo, one card per form (unlocked cycles only)
"""

from utils.data import get_belts_for_keys, load_curriculum, get_cycle, get_form


# ── helpers ─────────────────────────────────────────────────────────────────

def _fmt_combos(combos):
    lines = []
    for c in combos:
        lines.append(f"  {c['number']}. {c['text']}")
    return "\n".join(lines)


def _fmt_forms(forms):
    lines = []
    for f in forms:
        form = get_form(f["form_key"])
        if form:
            lines.append(f"  • {form['form_name']} — {form['meaning']}")
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
        f"{belt.get('word_of_the_belt_description') or ''}"
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



def _info_split_cards(belt, include_word=True, include_forms=True):
    """One card per combo, one card per form, one card for word."""
    curr = belt.get("curriculum", {})
    cards = []

    # Word of belt
    if include_word:
        cards.append({
            "question": f"What is the **Word of the Belt** for {belt['belt_name']}?",
            "answer": f"**{belt['word_of_the_belt']}**\n\n{belt.get('word_of_the_belt_description') or ''}",
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
    if include_forms and curr.get("forms"):
        for f in curr["forms"]:
            form = get_form(f["form_key"])
            if not form:
                continue
            cyc_label = _cycle_label(f.get("cycle_key"))
            cards.append({
                "question": f"What does the form **{form['form_name']}** mean? (learned at {belt['belt_name']}{cyc_label})",
                "answer": f"**{form['form_name']}** — {form['meaning']}",
                "category": "Form",
                "belt": belt["belt_name"],
            })

    return cards


def _word_card(belt):
    answer = f"**{belt['word_of_the_belt']}**"
    if belt.get("word_of_the_belt_description"):
        answer += f"\n\n{belt['word_of_the_belt_description']}"
    return {
        "question": f"What is the **Word of the Belt** for {belt['belt_name']}?",
        "answer": answer,
        "category": "Word of Belt",
        "belt": belt["belt_name"],
    }


# ── public API ───────────────────────────────────────────────────────────────

def build_deck(selected_belt_keys, unlocked_cycles, mode,
               include_word=True, include_forms=True):
    """
    Build and return a list of flashcard dicts.

    selected_belt_keys: list of belt_keys to include in the deck.
    unlocked_cycles: list of cycle_keys the student has reached.

    Comprehensive: one card per belt with ALL info (combos/forms from the full
    sibling belt family, ignoring cycle locks).
    Individual (Info Split): one card per combo/form, aggregated from the sibling
    belt family filtered to the unlocked cycles.
    """
    import copy
    all_curriculum = load_curriculum()
    belts = get_belts_for_keys(selected_belt_keys)
    cards = []

    for belt in belts:
        if mode == "Word of the Belt":
            if belt.get("word_of_the_belt"):
                cards.append(_word_card(belt))
            continue

        belt = copy.deepcopy(belt)
        curr = belt.get("curriculum", {})
        is_multi_cycle = bool(belt.get("cycles"))

        if is_multi_cycle and mode != "Comprehensive":
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
                        cycle_ok = not f.get("cycle_key") or f.get("cycle_key") in unlocked_cycles
                        if cycle_ok and f["name"] not in seen_forms:
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
        else:
            cards.extend(_info_split_cards(belt, include_word=include_word, include_forms=include_forms))

    return cards
