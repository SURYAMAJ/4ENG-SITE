#!/usr/bin/env python3
"""Build the 4ENG single-page site.

    python3 build.py            -> public/index.html  (deployed as Cloudflare Workers static assets)
                                   preview/index.html (fragment used for the Claude artifact preview)

Edit SITE and EMAIL below before deploying.
"""
import html, json, math, re
from pathlib import Path

SITE = "https://4eng.tech"          # canonical domain (no trailing slash)
EMAIL = "m.venkatesh@tasind.com"    # public contact address
APP = "https://4eng.app"            # sign-up destination (the SaaS app)

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "index.src.html"

FAQ = [
    ("What is 4ENG?",
     "4ENG is an AI execution platform for engineering firms. It connects a shared engineering model, tested production skills and governed human review, so approved requirements become reviewed deliverables such as loop drawings, panel general arrangements, control packages, proposals and handover evidence."),
    ("Does 4ENG replace our CAD, electrical or plant engineering tools?",
     "No. 4ENG orchestrates the engineering engines you already trust through documented APIs and open formats such as DXF, IFC, STEP and DEXPI. Geometry, simulation and native authoring stay in specialist tools. 4ENG owns the workflow, the shared object model and the review trail."),
    ("Will 4ENG produce certified or construction-ready designs on its own?",
     "No. 4ENG generates checked candidates. A qualified engineer approves every output before it is issued, and protection settings, safety decisions and certification stay with the responsible discipline lead."),
    ("Which deliverables come first?",
     "Repeatable 2D outputs with approved typicals and complete source data: loop drawings and termination schedules, panel general arrangements with BOMs, and proposal or review packs. Mechanical, P&ID and civil workflows follow as they pass acceptance testing."),
    ("Who is 4ENG for?",
     "Automation and systems integration firms, engineering service teams and equipment builders, typically with 50 to 500 people, repeatable deliverables and accessible source data."),
    ("How does the design-partner programme work?",
     "Over 90 days we prove up to three bounded workflows on your own data and templates. Together we measure net effort saved, first-pass acceptance, defects found and total execution cost. The programme is paid, and onboarding your engineering methods as skills is scoped as a service."),
    ("What happens to our engineering data?",
     "Your templates, typicals and project data are used to run your workflows. Tenancy, hosting region, access permissions, retention and IP boundaries are agreed in writing before a pilot starts."),
    ("How is 4ENG priced?",
     "Pricing combines a platform fee per firm, seats, optional industry packs and metered execution for AI, CAD and compute. Design partners agree pricing as part of the programme."),
]

LOGO = ('<span class="brand-lockup" aria-hidden="true">'
        '<img class="logo-accent" src="/assets/logo/4eng-shared-stem-lockup-accent.svg" width="248" height="100" alt="">'
        '<img class="logo-white" src="/assets/logo/4eng-shared-stem-lockup-white.svg" width="248" height="100" alt="">'
        '</span>')
TICK = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7.5L5.5 11L12 3.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
CROSS = '<svg viewBox="0 0 13 13" aria-hidden="true"><path d="M2 2L11 11M11 2L2 11" style="stroke:var(--redline)" stroke-width="2"/></svg>'


def cloud(x, y, w, h, r=6.0):
    """Revision-cloud path around a rectangle (clockwise, arcs bulge outward)."""
    def side(length):
        n = max(1, round(length / (1.6 * r)))
        return n, length / n
    d = [f"M{x:.1f} {y:.1f}"]
    for dx, dy, length in ((1, 0, w), (0, 1, h), (-1, 0, w), (0, -1, h)):
        n, c = side(length)
        for _ in range(n):
            d.append(f"a{r:.1f} {r:.1f} 0 0 1 {dx*c:.1f} {dy*c:.1f}")
    return "".join(d) + "Z"


def doc(x, title, docno, rows, bad):
    x = int(x)
    out = [f'<g><rect x="{x}" y="10" width="170" height="190" class="pp"/>',
           f'<text x="{x+10}" y="28" class="tb">{html.escape(title)}</text>',
           f'<text x="{x+10}" y="42" class="t2">{html.escape(docno)}</text>',
           f'<line x1="{x}" y1="50" x2="{x+170}" y2="50" class="ln"/>']
    for i, row in enumerate(rows):
        label, value = row.split("|")
        ty = 50 + i * 37 + 23
        if i:
            out.append(f'<line x1="{x+8}" y1="{50+i*37}" x2="{x+162}" y2="{50+i*37}" class="lt"/>')
        out.append(f'<text x="{x+10}" y="{ty}" class="t2">{html.escape(label.upper())}</text>')
        hot = (i == 1)
        style = ' style="font-size:11px;font-weight:700"' if hot else ' style="font-size:10.5px"'
        cls = "red-t" if (hot and bad) else "t"
        out.append(f'<text x="{x+160}" y="{ty}" text-anchor="end" class="{cls}"{style}>{html.escape(value)}</text>')
        if hot and bad:
            out.append(f'<path class="red" d="{cloud(x+90, ty-15, 74, 21, 4.2)}"/>')
            out.append(f'<path d="M{x+72} {ty-12}L{x+80} {ty+2}H{x+64}Z" class="red"/>'
                       f'<text x="{x+72}" y="{ty}" text-anchor="middle" class="red-t" style="font-size:7.5px">1</text>')
    out.append("</g>")
    return "".join(out)


def build():
    s = SRC.read_text()
    s = s.replace("{{LOGO}}", LOGO).replace("{{TICK}}", TICK).replace("{{CROSS}}", CROSS)
    s = re.sub(r"\{\{CLOUD:([\d.,]+)\}\}",
               lambda m: cloud(*[float(v) for v in m.group(1).split(",")]), s)

    def docm(m):
        parts = m.group(1).split(",")
        return doc(parts[0], parts[1], parts[2], parts[3:7], parts[7] == "1")
    s = re.sub(r"\{\{DOC:(.*?)\}\}", docm, s)
    s = s.replace("{{TERMS}}", "".join(
        f'<rect x="{x}" y="166" width="8" height="40" class="pp"/>' for x in range(200, 462, 10)))

    faq_html = "\n".join(
        f'      <details{" open" if i == 0 else ""}><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>'
        for i, (q, a) in enumerate(FAQ))
    faq_ld = ",".join(json.dumps({"@type": "Question", "name": q,
                                  "acceptedAnswer": {"@type": "Answer", "text": a}}, ensure_ascii=False)
                      for q, a in FAQ)
    s = s.replace("{{FAQ_HTML}}", faq_html).replace("{{FAQ_JSONLD}}", faq_ld)
    s = s.replace("{{SITE}}", SITE).replace("{{EMAIL}}", EMAIL).replace("{{APP}}", APP)
    assert "{{" not in s, re.findall(r"\{\{[^}]*\}\}", s)[:5]

    fonts_self = (
        '<link rel="preload" href="/assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>\n'
        '<style>@font-face{font-family:"Archivo";src:url(/assets/fonts/archivo-var.woff2) format("woff2");'
        'font-weight:100 900;font-stretch:62% 125%;font-display:swap}'
        '@font-face{font-family:"B612";src:url(/assets/fonts/b612-400.woff2) format("woff2");font-weight:400;font-display:swap}'
        '@font-face{font-family:"B612";src:url(/assets/fonts/b612-700.woff2) format("woff2");font-weight:700;font-display:swap}</style>')
    fonts_google = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=B612:wght@400;700&display=swap">')

    public = s.replace("<!--@FONTS-->", fonts_self).replace("<!--@SEO-START-->\n", "").replace("<!--@SEO-END-->\n", "")
    (ROOT / "public" / "index.html").write_text(public)

    # Artifact preview fragment: no doctype/html/head/body, no SEO head, Google-hosted fonts.
    head = s.split("<head>", 1)[1].split("</head>", 1)[0]
    head = re.sub(r"<!--@SEO-START-->.*?<!--@SEO-END-->\n", "", head, flags=re.S)
    head = re.sub(r"<meta[^>]*>\n", "", head).replace("<!--@FONTS-->", fonts_google)
    body = s.split("<body>", 1)[1].split("</body>", 1)[0]
    title = re.search(r"<title>.*?</title>", head).group(0)
    head = head.replace(title, "")
    (ROOT / "preview").mkdir(exist_ok=True)
    (ROOT / "preview" / "index.html").write_text("<title>4ENG Website</title>\n" + head.strip() + "\n" + body)
    for name in ("robots.txt", "sitemap.xml", "llms.txt"):
        f = ROOT / "public" / name
        f.write_text(re.sub(r"https://[a-z0-9.-]+(?=/)", SITE, f.read_text()))
    print("built", len(public) // 1024, "KB")


if __name__ == "__main__":
    build()
