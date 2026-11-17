from pathlib import Path

from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Seedcast_Poster_22x36.pdf"
PAGE = portrait((22 * inch, 36 * inch))

GREEN = colors.HexColor("#176B4D")
DARK = colors.HexColor("#14231D")
MINT = colors.HexColor("#EAF5EF")
CREAM = colors.HexColor("#F7F4EC")
GOLD = colors.HexColor("#D8A93D")
RED = colors.HexColor("#A84B42")
GRAY = colors.HexColor("#5D6A64")
LIGHT = colors.HexColor("#D8E2DC")
WHITE = colors.white


def register_fonts():
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("PosterSans", str(regular)))
        pdfmetrics.registerFont(TTFont("PosterSans-Bold", str(bold)))
        return "PosterSans", "PosterSans-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


def paragraph(c, text, x, y_top, width, size=14, leading=None, color=DARK, bold=False):
    style = ParagraphStyle(
        "poster",
        fontName=FONT_BOLD if bold else FONT,
        fontSize=size,
        leading=leading or size * 1.28,
        textColor=color,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    p = Paragraph(text, style)
    _, height = p.wrap(width, 20 * inch)
    p.drawOn(c, x, y_top - height)
    return y_top - height


def section_title(c, title, x, y_top, width):
    c.setFillColor(GREEN)
    c.roundRect(x, y_top - 0.46 * inch, width, 0.46 * inch, 0.10 * inch, fill=1, stroke=0)
    paragraph(c, title, x + 0.16 * inch, y_top - 0.08 * inch, width - 0.32 * inch, 22, 24, WHITE, True)
    return y_top - 0.62 * inch


def bullets(c, items, x, y_top, width, size=14):
    y = y_top
    for item in items:
        y = paragraph(c, f"<font color='#176B4D'><b>•</b></font> {item}", x, y, width, size, size * 1.32)
        y -= 0.11 * inch
    return y


def flow_box(c, text, x, y, width, height, fill=MINT):
    c.setFillColor(fill)
    c.setStrokeColor(LIGHT)
    c.setLineWidth(1.5)
    c.roundRect(x, y, width, height, 0.13 * inch, fill=1, stroke=1)
    p = Paragraph(
        text,
        ParagraphStyle(
            "flow", fontName=FONT_BOLD, fontSize=14, leading=17, textColor=DARK, alignment=1
        ),
    )
    _, ph = p.wrap(width - 0.2 * inch, height)
    p.drawOn(c, x + 0.1 * inch, y + (height - ph) / 2)


def down_arrow(c, x, y_top, length=0.26 * inch):
    c.setStrokeColor(GREEN)
    c.setFillColor(GREEN)
    c.setLineWidth(2.5)
    c.line(x, y_top, x, y_top - length)
    c.line(x, y_top - length, x - 0.07 * inch, y_top - length + 0.08 * inch)
    c.line(x, y_top - length, x + 0.07 * inch, y_top - length + 0.08 * inch)


def bar_chart(c, x, y, width, height, title, labels, values, max_value, suffix=""):
    paragraph(c, title, x, y + height, width, 16, 19, DARK, True)
    plot_y = y + 0.35 * inch
    plot_h = height - 0.62 * inch
    bar_w = 0.72 * inch
    gap = 0.48 * inch
    start_x = x + (width - (2 * bar_w + gap)) / 2
    for index, (label, value, color) in enumerate(zip(labels, values, (GOLD, GREEN))):
        bx = start_x + index * (bar_w + gap)
        bh = plot_h * value / max_value
        c.setFillColor(color)
        c.roundRect(bx, plot_y, bar_w, bh, 0.06 * inch, fill=1, stroke=0)
        paragraph(c, f"{value:.2f}{suffix}", bx - 0.18 * inch, plot_y + bh + 0.22 * inch, bar_w + 0.36 * inch, 13, 15, DARK, True)
        paragraph(c, label, bx - 0.25 * inch, plot_y - 0.08 * inch, bar_w + 0.5 * inch, 12, 14, GRAY, True)


def results_table(c, x, y_top, width):
    rows = [
        ("Metric", "Baseline", "Model"),
        ("MAE", "0.054991", "0.056230"),
        ("RMSE", "0.065537", "0.069410"),
        ("Directional accuracy", "27.27%", "40.91%"),
        ("R-squared", "n/a", "-0.662852"),
    ]
    heights = [0.4 * inch] + [0.38 * inch] * 4
    col_widths = [width * 0.48, width * 0.26, width * 0.26]
    y = y_top
    for r, row in enumerate(rows):
        h = heights[r]
        y -= h
        c.setFillColor(GREEN if r == 0 else (WHITE if r % 2 else CREAM))
        c.rect(x, y, width, h, fill=1, stroke=0)
        cx = x
        for i, value in enumerate(row):
            paragraph(
                c,
                value,
                cx + 0.09 * inch,
                y + h - 0.09 * inch,
                col_widths[i] - 0.18 * inch,
                12.5,
                15,
                WHITE if r == 0 else DARK,
                r == 0 or i == 0,
            )
            cx += col_widths[i]
    c.setStrokeColor(LIGHT)
    c.rect(x, y, width, sum(heights), fill=0, stroke=1)
    return y


def draw_qr(c, url, x, y, size):
    widget = qr.QrCodeWidget(url)
    bounds = widget.getBounds()
    drawing = Drawing(size, size, transform=[size / (bounds[2] - bounds[0]), 0, 0, size / (bounds[3] - bounds[1]), 0, 0])
    drawing.add(widget)
    drawing.drawOn(c, x, y)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=PAGE)
    c.setTitle("Seedcast - AI-powered financial planning poster")
    width, height = PAGE
    margin = 0.62 * inch
    gutter = 0.30 * inch
    col_w = (width - 2 * margin - 2 * gutter) / 3
    cols = [margin, margin + col_w + gutter, margin + 2 * (col_w + gutter)]

    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.rect(0, height - 3.25 * inch, width, 3.25 * inch, fill=1, stroke=0)
    paragraph(c, "SEEDCAST", margin, height - 0.52 * inch, 12 * inch, 56, 58, WHITE, True)
    paragraph(c, "Money-first planning with transparent market forecasts", margin, height - 1.42 * inch, 13.5 * inch, 25, 30, colors.HexColor("#DDF1E6"), True)
    paragraph(c, "Dhruv Thakkar  •  Parul Mudaliar  •  Suriyavardhan Gopal", margin, height - 2.18 * inch, 14.5 * inch, 17, 21, WHITE)
    paragraph(c, "dthaker3@illinois.edu  •  parulm2@illinois.edu  •  gopal8@illinois.edu", margin, height - 2.61 * inch, 14.5 * inch, 14, 18, colors.HexColor("#DDF1E6"))
    c.setFillColor(GOLD)
    c.roundRect(width - 5.2 * inch, height - 2.6 * inch, 4.5 * inch, 1.35 * inch, 0.18 * inch, fill=1, stroke=0)
    paragraph(c, "Educational paper-money simulation<br/>No personalized investment advice", width - 4.95 * inch, height - 1.52 * inch, 4 * inch, 18, 22, DARK, True)

    top = height - 3.62 * inch
    bottom = 1.75 * inch

    # Column 1
    y = section_title(c, "1  Problem and motivation", cols[0], top, col_w)
    y = bullets(c, [
        "Beginning investors may have a small monthly surplus but no clear next step.",
        "Budgeting tools and market screeners separate financial readiness from market information.",
        "Seedcast calculates a surplus, explains an initial allocation, and displays saved forecasts with uncertainty and freshness.",
    ], cols[0] + 0.06 * inch, y, col_w - 0.12 * inch, 14.5)
    y -= 0.12 * inch
    y = section_title(c, "Product workflow", cols[0], y, col_w)
    screenshot = ROOT / "docs" / "screenshots" / "04-dashboard-seed-split.png"
    if screenshot.exists():
        img_h = 3.75 * inch
        c.drawImage(str(screenshot), cols[0], y - img_h, width=col_w, height=img_h, preserveAspectRatio=True, anchor="c", mask="auto")
        y -= img_h + 0.14 * inch
        y = paragraph(c, "Money Snapshot output: saved monthly surplus and an explained Seed Split", cols[0], y, col_w, 12.5, 15, GRAY)
    y -= 0.20 * inch
    y = section_title(c, "Implemented features", cols[0], y, col_w)
    y = bullets(c, [
        "Authenticated profile and monthly budget workflow with user isolation.",
        "Three-bucket Seed Split for emergency savings, extra debt payoff, and paper-money practice.",
        "Cast Explorer search, filters, asset details, cached prices, and internal JSON endpoints.",
        "Offline gradient-boosting command that saves a real Django Forecast record.",
    ], cols[0] + 0.06 * inch, y, col_w - 0.12 * inch, 14)

    # Column 2
    y = section_title(c, "2  System architecture", cols[1], top, col_w)
    y -= 0.04 * inch
    paragraph(c, "Money path", cols[1], y, col_w, 16, 19, GREEN, True)
    y -= 0.46 * inch
    box_h = 0.67 * inch
    for label in ["User profile and monthly snapshot", "Django forms and validation", "FinancialProfile and MonthlyBudget", "Seed Split dashboard"]:
        flow_box(c, label, cols[1] + 0.45 * inch, y - box_h, col_w - 0.9 * inch, box_h)
        y -= box_h
        if label != "Seed Split dashboard":
            down_arrow(c, cols[1] + col_w / 2, y - 0.05 * inch)
            y -= 0.35 * inch
    y -= 0.30 * inch
    paragraph(c, "AI and market path", cols[1], y, col_w, 16, 19, GREEN, True)
    y -= 0.46 * inch
    for label in ["Frozen AAPL OHLCV data", "pandas feature pipeline", "scikit-learn point and quantile models", "Validated Django Forecast record", "Cast Explorer, detail page, and JSON API"]:
        flow_box(c, label, cols[1] + 0.45 * inch, y - box_h, col_w - 0.9 * inch, box_h, WHITE if "Django" in label else MINT)
        y -= box_h
        if label != "Cast Explorer, detail page, and JSON API":
            down_arrow(c, cols[1] + col_w / 2, y - 0.05 * inch)
            y -= 0.35 * inch
    y -= 0.22 * inch
    c.setFillColor(colors.HexColor("#FFF4D6"))
    c.setStrokeColor(GOLD)
    c.roundRect(cols[1], y - 1.22 * inch, col_w, 1.22 * inch, 0.14 * inch, fill=1, stroke=1)
    paragraph(c, "Request-time safety", cols[1] + 0.16 * inch, y - 0.16 * inch, col_w - 0.32 * inch, 16, 19, DARK, True)
    paragraph(c, "Model training runs offline. Web requests read saved predictions. Missing values remain unavailable, and old data receives a stale label.", cols[1] + 0.16 * inch, y - 0.53 * inch, col_w - 0.32 * inch, 13.5, 17, DARK)

    # Column 3
    y = section_title(c, "3  Evaluation and analytics", cols[2], top, col_w)
    y = paragraph(c, "Time-ordered holdout with 21 overlapping labels purged before training", cols[2], y, col_w, 14.5, 18, DARK, True) - 0.15 * inch
    bar_chart(c, cols[2], y - 2.35 * inch, col_w, 2.35 * inch, "Forecast error (lower is better)", ["Baseline", "Model"], [5.50, 5.62], 6.2, "%")
    y -= 2.70 * inch
    bar_chart(c, cols[2], y - 2.35 * inch, col_w, 2.35 * inch, "Directional accuracy", ["Baseline", "Model"], [27.27, 40.91], 50, "%")
    y -= 2.72 * inch
    y = results_table(c, cols[2], y, col_w) - 0.32 * inch
    y = section_title(c, "4  Key results", cols[2], y, col_w)
    y = bullets(c, [
        "506 frozen AAPL rows produced 436 usable observations.",
        "The integrated command saves 506 cached prices and one real model forecast.",
        "Directional accuracy increased 13.64 percentage points, while MAE and RMSE worsened.",
        "The merged money, markets, and AI implementation passes 53 automated tests.",
    ], cols[2] + 0.06 * inch, y, col_w - 0.12 * inch, 13.5)
    y -= 0.10 * inch
    y = section_title(c, "5  Limitations and future work", cols[2], y, col_w)
    bullets(c, [
        "One old ticker cannot represent current market regimes.",
        "Probability-positive uses empirical training residuals and is not calibrated.",
        "Next: licensed current data, more assets, walk-forward validation, calibrated intervals, and monitoring.",
    ], cols[2] + 0.06 * inch, y, col_w - 0.12 * inch, 13.5)

    # Footer
    c.setFillColor(DARK)
    c.rect(0, 0, width, 1.45 * inch, fill=1, stroke=0)
    qr_size = 1.02 * inch
    draw_qr(c, "https://github.com/dthaker7/seedcast", margin, 0.20 * inch, qr_size)
    paragraph(c, "GitHub repository", margin + 1.25 * inch, 1.10 * inch, 3.3 * inch, 16, 19, WHITE, True)
    paragraph(c, "github.com/dthaker7/seedcast", margin + 1.25 * inch, 0.73 * inch, 4.3 * inch, 13, 16, colors.HexColor("#DDF1E6"))
    paragraph(c, "Dataset: Plotly datasets (MIT License), frozen educational sample. The repository does not identify the upstream market-data vendor.", 6.2 * inch, 1.04 * inch, 14.9 * inch, 12.5, 16, colors.HexColor("#DDF1E6"))

    c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
