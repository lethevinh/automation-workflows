#!/usr/bin/env python3
"""Extract the diagram SVG from an archify output HTML into a standalone .svg.

Embeds the page's <style> blocks inside the SVG so it renders correctly as a
plain image (e.g. GitHub README embeds). Usage:

    python3 scripts/extract-archify-svg.py <input.html> <output.svg>
"""
import re
import sys

# "Paper" brand theme — docs/visual-style.md. Overrides archify's CSS
# custom properties; appended last so it wins over the embedded theme.
BRAND = """
/* brand: paper — see docs/visual-style.md */
:root{
  --bg:#ffffff; --grid:#EEF2F7; --canvas-dot:rgba(100,116,139,.18);
  --text:#0F172A; --text-muted:#64748B; --text-dim:#94A3B8; --text-faint:#94A3B8;
  --panel:rgba(255,255,255,.9); --panel-border:#D8E0EA;
  --lane-fill:rgba(15,23,42,.035); --lane-stroke:#D8E0EA;
  --arrow:#94A3B8; --arrow-emphasis:#10B981; --mask:#ffffff;
  --frontend-fill:#EFF6FF; --frontend-stroke:#3B82F6;
  --backend-fill:#ECFDF5; --backend-stroke:#10B981;
  --database-fill:#F5F3FF; --database-stroke:#8B5CF6;
  --cloud-fill:#FFFBEB; --cloud-stroke:#F59E0B;
  --security-fill:#FEF2F2; --security-stroke:#EF4444;
  --messagebus-fill:#FDF2F8; --messagebus-stroke:#EC4899;
  --external-fill:#F8FAFC; --external-stroke:#64748B;
}
"""

html = open(sys.argv[1], encoding="utf8").read()

m = re.search(r'<svg[^>]*role="img"[^>]*>.*?</svg>', html, re.S)
if not m:
    sys.exit("no diagram <svg role=img> found")

svg = m.group(0)
styles = "".join(
    f"<style><![CDATA[{body}]]></style>"
    for body in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
)
if not styles:
    sys.exit("no <style> blocks found — SVG would render unstyled")

svg = re.sub(r"(<svg[^>]*>)", r"\1\n" + styles
             + f"<style><![CDATA[{BRAND}]]></style>", svg, count=1)
if 'xmlns=' not in svg.split(">", 1)[0]:
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)

open(sys.argv[2], "w", encoding="utf8").write(svg)
print(f"{sys.argv[2]}  ({len(svg)} bytes)")
