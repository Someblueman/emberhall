"""Draw a Gallery excerpt from the shipped mixed-change review; stdout is SVG."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from textwrap import wrap

SAMPLE = Path(__file__).parent / "sample/milestone-2-mixed/review.html"


class Excerpt(HTMLParser):
    """Read the changed row and its comment in the sample's fourth file."""

    def __init__(self):
        super().__init__()
        self.inside = False
        self.changed = False
        self.capture = None
        self.parts = {"title": [], "old": [], "new": [], "comment": []}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.inside = attrs.get("id") == "file-4"
        if not self.inside:
            return
        classes = attrs.get("class", "").split()
        if tag == "tr":
            self.changed = "replace" in classes
        if tag == "h2":
            self.capture = "title"
        elif tag == "td" and self.changed and "code" in classes:
            self.capture = "old" if "old" in classes else "new"
        elif tag == "pre" and "comment-body" in classes:
            self.capture = "comment"

    def handle_endtag(self, tag):
        if tag in {"h2", "td", "pre"}:
            self.capture = None
        if tag == "section":
            self.inside = False

    def handle_data(self, data):
        if self.inside and self.capture:
            self.parts[self.capture].append(data)


def svg(source: str) -> str:
    excerpt = Excerpt()
    excerpt.feed(source)
    parts = {key: "".join(value) for key, value in excerpt.parts.items()}
    if not all(parts.values()):
        raise ValueError("The sample no longer contains the expected changed row and comment")
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-labelledby="title desc">',
        '<title id="title">Review Skein: a change with a question attached</title>',
        f'<desc id="desc">An invented sample, excerpted from the shipped review. Before: {escape(parts["old"])} After: {escape(parts["new"])} Comment: {escape(parts["comment"])}</desc>',
        '<rect width="1200" height="620" rx="22" fill="#f6f0e6"/>',
        '<g font-family="system-ui, sans-serif" fill="#282f32">',
        '<text x="46" y="58" font-size="20" letter-spacing="3">REVIEW SKEIN / INVENTED SAMPLE</text>',
        '<text x="46" y="112" font-size="34" font-weight="600">One line changes. A question stays with it.</text>',
        '<rect x="46" y="146" width="1108" height="294" rx="12" fill="#fffdf8" stroke="#cfc7b9"/>',
        f'<text x="70" y="185" font-size="22">{escape(parts["title"])}</text>',
        '<path d="M46 207H1154" stroke="#cfc7b9"/>',
    ]
    for x, side, color, mark, label in [(66, "old", "#fae0da", "−", "BEFORE · REMOVED"),
                                        (620, "new", "#e1edda", "+", "AFTER · ADDED")]:
        elements.append(f'<rect x="{x}" y="225" width="514" height="194" rx="8" fill="{color}"/>')
        elements.append(f'<text x="{x + 20}" y="261" font-size="18" font-weight="600">{label}</text>')
        for i, line in enumerate(wrap(parts[side], 28)):
            elements.append(f'<text x="{x + 20}" y="{310 + i * 36}" font-size="25" font-family="ui-monospace, monospace">{mark if i == 0 else " "} {escape(line)}</text>')
    elements.extend([
        '<rect x="46" y="460" width="1108" height="116" rx="12" fill="#e7e5f1"/>',
        '<text x="70" y="493" font-size="18" font-weight="600">OPEN QUESTION · ATTACHED TO THE CHANGED LINE</text>',
    ])
    for i, line in enumerate(wrap(parts["comment"], 78)):
        elements.append(f'<text x="70" y="{527 + i * 29}" font-size="23">{escape(line)}</text>')
    elements.extend(['<text x="46" y="604" font-size="17">Excerpt from the shipped mixed-change packet · open the sample to inspect every line</text>',
                     '</g></svg>'])
    return "\n".join(elements) + "\n"


if __name__ == "__main__":
    print(svg(SAMPLE.read_text()), end="")
