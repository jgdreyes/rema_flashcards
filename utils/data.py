import json
import os
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@st.cache_data
def load_curriculum():
    with open(os.path.join(DATA_DIR, "ripple_effect_curriculum.json")) as f:
        return json.load(f)


@st.cache_data
def load_cycles():
    with open(os.path.join(DATA_DIR, "ripple_effect_cycles.json")) as f:
        return json.load(f)


def get_belt_order():
    """Return list of (belt_key, belt_name) in rank order."""
    curriculum = load_curriculum()
    return [(b["belt_key"], b["belt_name"]) for b in curriculum]


def get_belt(belt_key):
    curriculum = load_curriculum()
    return next((b for b in curriculum if b["belt_key"] == belt_key), None)


def get_cycle(cycle_key):
    cycles = load_cycles()
    return next((c for c in cycles if c["cycle_key"] == cycle_key), None)


def get_belts_for_keys(belt_keys):
    """Return belt objects for the given keys, in curriculum order."""
    curriculum = load_curriculum()
    key_set = set(belt_keys)
    return [b for b in curriculum if b["belt_key"] in key_set]


def belts_up_to(belt_key):
    """Return all belt objects from White Belt up to and including belt_key."""
    curriculum = load_curriculum()
    result = []
    for b in curriculum:
        result.append(b)
        if b["belt_key"] == belt_key:
            break
    return result
