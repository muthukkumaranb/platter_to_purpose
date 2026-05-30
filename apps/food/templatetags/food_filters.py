from django import template

register = template.Library()


@register.filter
def to_stars(value):
    try:
        rating = float(value)
    except (ValueError, TypeError):
        return ""

    # Allow full stars only for cleaner look, or handle halves
    # User requested "star format", standard is often just full stars or halves
    # Let's do rounded to nearest half logic visually

    # Logic:
    # 0-0.24 -> 0
    # 0.25-0.74 -> 0.5 (half star)
    # 0.75-1.0 -> 1 (full star)

    # For simplicity and standard text rendering:
    # We will round to nearest integer for solid stars to avoid complex half-star unicode issues on some devices/fonts,
    # unless we use specific characters.
    # Unicode: ★ (2605) and ☆ (2606). No half star in standard set universally reliable without font support.
    # We will stick to full stars for robustness.

    stars = int(round(rating))
    stars = max(0, min(5, stars))  # Clamp between 0 and 5

    return "★" * stars + "☆" * (5 - stars)
