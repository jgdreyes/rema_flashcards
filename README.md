# 🥋 REMA Flashcards

A Streamlit flashcard app for Ripple Effect Martial Arts curriculum study.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

```
rema_flashcards/
├── app.py                        # Entry point + sidebar nav
├── requirements.txt
├── data/
│   ├── ripple_effect_curriculum.json
│   └── ripple_effect_cycles.json
├── pages/
│   ├── settings.py               # Belt + cycle configuration
│   └── flashcards.py             # Flashcard player
└── utils/
    ├── data.py                   # JSON loaders
    ├── state.py                  # Session state init
    └── deck_builder.py           # Card generation logic
```

## Flashcard Modes

| Mode | Description |
|------|-------------|
| **Comprehensive** | One card per belt covering all info at once |
| **Individual (Info)** | Separate cards for word of belt, all combos, all forms |
| **Individual (Info Split)** | One card per combo, one per form, one for word of belt |

## Settings

- **Current Belt** — select your rank; only content up to that belt is included
- **Unlocked Cycles** — for Red Belt and above, check which cycles your class has completed; only unlocked cycle content appears in the deck
- **Shuffle** — randomise card order each time you build the deck
