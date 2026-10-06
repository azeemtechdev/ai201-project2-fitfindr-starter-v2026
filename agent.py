"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.
"""

import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── helper: query parser ──────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    """
    Extracts description keywords, size, and max_price from natural language input.
    """
    text = query.strip()
    max_price = None
    size = None

    # 1. Extract max_price (e.g., "under $30", "under 30", "< $30", "$30", "below $30")
    price_match = re.search(
        r"(?:under|below|max|budget(?:\s*of)?|<|\$)\s*\$?(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if price_match:
        try:
            max_price = float(price_match.group(1))
            text = text[:price_match.start()] + " " + text[price_match.end():]
        except ValueError:
            pass

    # 2. Extract size (e.g., "size M", "size: M", "size 8", "in size XXS")
    size_match = re.search(
        r"\b(?:size|in\s+size)[:\s]+([a-zA-Z0-9/]+)\b",
        text,
        re.IGNORECASE,
    )
    if size_match:
        size = size_match.group(1).strip()
        text = text[:size_match.start()] + " " + text[size_match.end():]
    else:
        # Check standalone size keywords (e.g., "W30 L30", "XXS", "XS", "XL", "XXL")
        standalone_size = re.search(
            r"\b(xxs|xs|s/m|m/l|xxl|xl|w\d+\s*l\d+)\b",
            text,
            re.IGNORECASE,
        )
        if standalone_size:
            size = standalone_size.group(1).strip()
            text = text[:standalone_size.start()] + " " + text[standalone_size.end():]

    # Clean description by collapsing whitespace
    clean_desc = " ".join(text.split())

    return {
        "description": clean_desc if clean_desc else query,
        "size": size,
        "max_price": max_price,
    }


def _format_no_match_message(parsed: dict) -> str:
    """
    Constructs an actionable message telling the user specifically what to change.
    """
    desc = parsed.get("description", "your query")
    size = parsed.get("size")
    max_price = parsed.get("max_price")

    suggestions = []
    if max_price is not None:
        suggestions.append(f"raising your price ceiling above ${max_price:.2f}")
    if size:
        suggestions.append(f"trying alternative sizes or removing the size filter ('{size}')")
    suggestions.append("using broader style keywords (e.g., 'vintage', 'casual', 'jacket')")

    if len(suggestions) > 1:
        tips = ", ".join(suggestions[:-1]) + f", or {suggestions[-1]}"
    else:
        tips = suggestions[0]

    return f"No thrift listings found matching '{desc}'. Try {tips}."


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price pulled out
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the chosen item — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.
    """
    session = new_session(query, wardrobe)
    iteration = 0

    try:
        # Step 1: Increment iteration and check bounds
        iteration += 1
        trace.check_iterations(iteration)

        # Step 2: Parse query into session state
        session["parsed"] = parse_query(session["query"])

        # Step 3: Run search_listings using parsed parameters from session
        parsed_params = session["parsed"]
        session["search_results"] = search_listings(
            description=parsed_params.get("description", ""),
            size=parsed_params.get("size"),
            max_price=parsed_params.get("max_price"),
        )

        # Step 4: THE BRANCH — Stop if search returned nothing
        if not session["search_results"]:
            session["error"] = _format_no_match_message(session["parsed"])
            return session

        # Step 5: Select item into session state
        session["selected_item"] = session["search_results"][0]

        # Step 6: Generate outfit suggestion using session state
        iteration += 1
        trace.check_iterations(iteration)
        session["outfit_suggestion"] = suggest_outfit(
            new_item=session["selected_item"],
            wardrobe=session["wardrobe"],
        )

        # Step 7: Generate fit card using session state
        iteration += 1
        trace.check_iterations(iteration)
        session["fit_card"] = create_fit_card(
            outfit=session["outfit_suggestion"],
            new_item=session["selected_item"],
        )

    except ModelUnavailable as e:
        session["error"] = f"Model service temporarily unavailable: {e}"
        return session

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )