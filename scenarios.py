"""
The runs your test needs. ← UNIT 4, MILESTONE 3
"""

SCENARIOS = [
    {
        # Criterion 1: Happy path — full 3-tool execution
        "name": "matching query completes all 3 tools",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # Criterion 2: Empty search branch — halts before tool 2
        "name": "impossible query stops early with actionable guidance",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3: Session state handoff — selected item ID matches downstream tool input
        "name": "item state handoff across tool calls",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4: Fit card content — includes price, title, and aesthetic hashtags
        "name": "fit card includes required price and hashtags",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5: Price ceiling fidelity — strictly <= max_price
        "name": "price ceiling strictly enforced",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Diagnostic run: empty wardrobe fallback (criterion: None)
        "name": "empty wardrobe fallback handling",
        "query": "corduroy wide-leg pants under $40",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems