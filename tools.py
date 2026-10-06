"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str
"""

import re
import config
from generate import generate
from utils.data_loader import load_listings


# ── Helper: Size Matching ─────────────────────────────────────────────────────

def _matches_size(item_size: str, target_size: str) -> bool:
    """
    Checks whether item_size matches target_size without false positives
    like 's' matching 'us 9' or 'l' matching 'xl'.
    """
    if not item_size or not target_size:
        return False

    item_str = str(item_size).strip().lower()
    target_str = str(target_size).strip().lower()

    # Exact string match
    if item_str == target_str:
        return True

    # Normalize common text words to standard letter sizes
    aliases = {
        "small": "s",
        "medium": "m",
        "large": "l",
        "extra large": "xl",
        "x-large": "xl",
    }
    target_str = aliases.get(target_str, target_str)

    # Tokenize size string by whitespace, slashes, hyphens, and parentheses
    tokens = [t for t in re.split(r"[/,\s\(\)\-]+", item_str) if t]

    # Direct token match (e.g., target 'm' matches inside 's/m')
    if target_str in tokens:
        return True

    # Waist size matching (e.g. target '30' matches 'w30' or vice versa)
    target_num = target_str.lstrip("w")
    for t in tokens:
        if t.lstrip("w") == target_num and target_num.isdigit():
            return True

    return False


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.
    """
    listings = load_listings()
    stop_words = {"a", "an", "the", "in", "on", "under", "for", "with", "size", "and", "or", "to", "of"}
    
    # Extract search keywords (words longer than 1 character)
    keywords = [
        word.lower()
        for word in re.findall(r"\b[a-zA-Z0-9]+\b", description)
        if len(word) > 1 and word.lower() not in stop_words
    ]

    scored = []

    for item in listings:
        # 1. Price ceiling check (inclusive)
        if max_price is not None and float(item.get("price", 0.0)) > float(max_price):
            continue

        # 2. Size filter
        if size is not None and not _matches_size(item.get("size", ""), size):
            continue

        # 3. Score remaining listings by keyword overlap
        title_text = item.get("title", "").lower()
        desc_text = item.get("description", "").lower()
        cat_text = item.get("category", "").lower()
        tags_text = " ".join(item.get("style_tags", [])).lower()

        score = 0
        if keywords:
            for kw in keywords:
                if kw in title_text:
                    score += 3
                if kw in tags_text:
                    score += 2
                if kw in cat_text:
                    score += 2
                if kw in desc_text:
                    score += 1
        else:
            score = 1

        # 4. Drop anything scoring zero
        if score > 0:
            scored.append((score, item))

    # 5. Sort by score descending, breaking ties with lower price
    scored.sort(key=lambda x: (-x[0], x[1].get("price", 0.0)))

    limit = getattr(config, "SEARCH_RESULT_LIMIT", 5)
    return [item for _, item in scored[:limit]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.
    """
    if not new_item:
        return "No thrifted item provided."

    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    # Handle empty wardrobe
    if not items:
        prompt = f"""
You are a thrift fashion stylist. A user found this item:
- Title: {new_item.get('title')}
- Category: {new_item.get('category')}
- Style Tags: {', '.join(new_item.get('style_tags', []))}
- Colors: {', '.join(new_item.get('colors', []))}

The user's wardrobe is currently empty. Give 2 to 3 sentences of styling advice on what general staple pieces, colors, and footwear they can pair with this item.
"""
        return generate(prompt).strip()

    # Format existing wardrobe pieces
    wardrobe_lines = [
        f"- {w.get('name')} (Category: {w.get('category')}, Colors: {', '.join(w.get('colors', []))}, Tags: {', '.join(w.get('style_tags', []))})"
        for w in items
    ]
    wardrobe_text = "\n".join(wardrobe_lines)

    prompt = f"""
You are a thrift fashion stylist. Suggest a cohesive outfit combining this thrifted item with 1-2 pieces from the user's wardrobe.

Thrifted Item:
- Title: {new_item.get('title')}
- Category: {new_item.get('category')}
- Style Tags: {', '.join(new_item.get('style_tags', []))}
- Colors: {', '.join(new_item.get('colors', []))}

User's Wardrobe:
{wardrobe_text}

Rules:
1. Specifically name 1 or 2 items from the wardrobe to pair with this piece.
2. In 2-3 sentences, explain why the colors, textures, and silhouettes work together.
"""
    return generate(prompt).strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.
    """
    if not outfit or not outfit.strip():
        return "No outfit details available to generate a fit card."

    prompt = f"""
Write a short, aesthetic social media caption (2 to 4 sentences) for someone sharing their thrift find.

Thrifted Item:
- Title: {new_item.get('title')}
- Price: ${new_item.get('price')}
- Platform: {new_item.get('platform')}
- Brand: {new_item.get('brand') or 'vintage'}

Styling Suggestion:
{outfit}

Requirements:
- Sound like an authentic personal post (not a product catalog or advertisement).
- Naturally mention the item title, its price (${new_item.get('price')}), and the platform ({new_item.get('platform')}) once each.
- Highlight the styling aesthetic.
- End with 2-4 aesthetic hashtags (e.g. #thriftfinds #vintage).
"""
    return generate(prompt).strip()