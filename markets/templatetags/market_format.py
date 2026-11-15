from decimal import ROUND_HALF_UP, Decimal

from django import template

register = template.Library()


@register.filter
def pct(value, places=1):
    """Format a decimal return (0.0125) as a percent string ("1.3%").

    None means the model has not produced a value, so it renders as
    "Not computed" rather than 0%.
    """
    if value is None:
        return "Not computed"
    places = int(places)
    step = Decimal(1).scaleb(-places)
    rounded = (Decimal(value) * 100).quantize(step, rounding=ROUND_HALF_UP)
    return f"{rounded}%"
