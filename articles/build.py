#!/usr/bin/env python3
"""Render the feature-desk markdown drafts into styled reading pages."""
import html
import re
from pathlib import Path

HERE = Path(__file__).parent

ARTICLES = [
    {
        "slug": "micro-retirement",
        "kicker": "Business &middot; The New Workplace",
        "byline": "Dana Whitfield",
        "summary": "A growing share of workers in their 30s, 40s and 50s are drawing down leisure in "
                   "three-month increments rather than saving it all for 67. The arithmetic is "
                   "brutal — roughly $137,000 for a six-month break at 35. They are doing it anyway.",
    },
    {
        "slug": "third-places",
        "kicker": "Culture &middot; American Life",
        "byline": "Owen Braddock",
        "summary": "Bowling alleys, corner taverns and parish halls have been thinning for forty "
                   "years, and what replaced them charges $189 a month. What a town loses when the "
                   "buildings where people ran into each other stop existing.",
    },
    {
        "slug": "sleep-industrial-complex",
        "kicker": "Health &middot; Well",
        "byline": "Miriam Solberg",
        "summary": "Rings and bands turned rest into a nightly performance review, and clinicians "
                   "now have a name for what happens next. What the evidence actually supports, and "
                   "when to stop optimizing and call a doctor.",
    },
]

CSS = """
  :root { --ink:#121212; --muted:#5a5a5a; --rule:#e2e2e2; --accent:#a81817; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:Georgia,'Times New Roman',serif; color:var(--ink);
         background:#fff; line-height:1.6; padding:26px 20px 90px; }
  .wrap { max-width:1120px; margin:0 auto; }
  .masthead { text-align:center; border-bottom:1px solid var(--ink); padding-bottom:12px; }
  .masthead a { color:inherit; text-decoration:none; }
  .masthead h1 { font-size:clamp(30px,6vw,54px); font-weight:900; letter-spacing:-1px; }
  .dateline { display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
    font-family:Helvetica,Arial,sans-serif; font-size:10.5px; letter-spacing:.09em;
    text-transform:uppercase; color:var(--muted); padding:8px 0;
    border-bottom:3px double var(--ink); margin-bottom:34px; }
  .kicker { font-family:Helvetica,Arial,sans-serif; font-size:10.5px; font-weight:700;
    letter-spacing:.11em; text-transform:uppercase; color:var(--accent); margin-bottom:12px; }
  .byline { font-family:Helvetica,Arial,sans-serif; font-size:11px; text-transform:uppercase;
    letter-spacing:.07em; color:var(--muted); }
  .read { font-family:Helvetica,Arial,sans-serif; font-size:10.5px; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase; color:#326891; text-decoration:none; }
  .read:hover { text-decoration:underline; }
  figure { margin:26px 0; }
  figure img { width:100%; display:block; }
  figcaption { font-family:Helvetica,Arial,sans-serif; font-size:12px; line-height:1.45;
    color:var(--muted); padding-top:8px; border-bottom:1px solid var(--rule); padding-bottom:10px; }
  footer { margin-top:52px; padding-top:14px; border-top:1px solid var(--rule);
    font-family:Helvetica,Arial,sans-serif; font-size:11.5px; color:var(--muted); text-align:center; }
"""

ARTICLE_CSS = """
  .story { max-width:680px; margin:0 auto; }
  .story h1 { font-size:clamp(30px,5.2vw,46px); line-height:1.12; letter-spacing:-.7px; }
  .story h2.standfirst { font-size:20px; font-weight:400; color:#444; line-height:1.4;
    margin-top:14px; font-style:italic; }
  .meta { margin:20px 0 4px; padding-top:14px; border-top:1px solid var(--rule); }
  .meta .date { font-family:Helvetica,Arial,sans-serif; font-size:11px; color:var(--muted);
    letter-spacing:.05em; text-transform:uppercase; margin-top:4px; }
  .story p { font-size:18.5px; margin:0 0 20px; }
  .story p.dropcap-holder:first-letter { font-size:58px; float:left; line-height:.82;
    padding:4px 8px 0 0; font-weight:700; }
  .story h3 { font-size:23px; margin:36px 0 14px; letter-spacing:-.3px; }
  .story hr { border:none; border-top:1px solid var(--rule); margin:34px 0; }
  .story em.note { }
  .story .endnote { font-size:14px; color:var(--muted); font-style:italic; line-height:1.55; }
  .back { display:inline-block; margin-top:8px; }
"""


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = text.replace("&amp;mdash;", "&mdash;")
    return text


def parse(md_path: Path):
    """Return (title, standfirst, section, byline, date, body_html)."""
    lines = md_path.read_text().split("\n")
    title = standfirst = section = byline = date = ""
    body, i, n = [], 0, len(lines)

    while i < n:
        line = lines[i].rstrip()

        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("### ") and not standfirst and not body:
            standfirst = line[4:].strip()
        elif line.startswith("**") and "|" in line and not section:
            section = line.strip("*").strip()
        elif line.startswith("*By "):
            byline = line.strip("*").strip()[3:]
        elif re.match(r"^\*\w+ \d+, \d{4}\*$", line):
            date = line.strip("*").strip()
        elif line.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", line)
            cap = ""
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and lines[j].startswith("*") and lines[j].rstrip().endswith("*"):
                cap = lines[j].strip().strip("*").strip()
                i = j
            body.append(
                f'<figure><img src="{m.group(2)}" alt="{html.escape(m.group(1), quote=True)}">'
                + (f"<figcaption>{inline(cap)}</figcaption>" if cap else "")
                + "</figure>"
            )
        elif line.startswith("## "):
            body.append(f"<h3>{inline(line[3:].strip())}</h3>")
        elif line.strip() == "---":
            body.append("<hr>")
        elif line.strip():
            para, buf = line, []
            buf.append(para)
            while i + 1 < n and lines[i + 1].strip() and not lines[i + 1].startswith(
                ("#", "!", "---")
            ):
                i += 1
                buf.append(lines[i].rstrip())
            joined = " ".join(buf).strip()
            if joined.startswith("*") and joined.endswith("*") and joined.count("*") == 2:
                body.append(f'<p class="endnote">{inline(joined)}</p>')
            else:
                body.append(f"<p>{inline(joined)}</p>")
        i += 1

    # drop-cap the first real paragraph after the lead art
    for k, blk in enumerate(body):
        if blk.startswith("<p>") and "&mdash;" not in blk[:120]:
            continue
    for k, blk in enumerate(body):
        if blk.startswith("<p>"):
            body[k] = blk.replace("<p>", '<p class="dropcap-holder">', 1)
            break

    return title, standfirst, section, byline, date, "\n".join(body)


def shell(title, css_extra, inner):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title, quote=True)}</title>
<style>{CSS}{css_extra}</style>
</head>
<body>
<div class="wrap">
  <div class="masthead"><h1><a href="index.html">The Feature Desk</a></h1></div>
  <div class="dateline">
    <span>Monday, July 27, 2026</span>
    <span>Original Long-Form Drafts</span>
    <span>Business &middot; Culture &middot; Health</span>
  </div>
{inner}
  <footer>Original feature drafts written for this repository. Individuals, institutions and
  quotations are illustrative; photographs were generated for illustration.</footer>
</div>
</body>
</html>
"""


def main():
    cards = []
    for art in ARTICLES:
        md = HERE / f"{art['slug']}.md"
        title, standfirst, section, byline, date, body = parse(md)

        inner = f"""  <div class="story">
    <div class="kicker">{art['kicker']}</div>
    <h1>{inline(title)}</h1>
    {f'<h2 class="standfirst">{inline(standfirst)}</h2>' if standfirst else ''}
    <div class="meta"><span class="byline">By {html.escape(byline or art['byline'])}</span>
      <div class="date">{html.escape(date)}</div></div>
{body}
    <a class="read back" href="index.html">&larr; Back to the front page</a>
  </div>"""
        (HERE / f"{art['slug']}.html").write_text(shell(title, ARTICLE_CSS, inner))

        # first image + first substantive paragraph for the front page card
        img = re.search(r'<img src="(.*?)"', body).group(1)
        summary = art["summary"]

        cards.append(f"""    <article>
      <a href="{art['slug']}.html"><img src="{img}" alt=""></a>
      <div class="kicker">{art['kicker']}</div>
      <h2><a href="{art['slug']}.html">{inline(title)}</a></h2>
      {f'<p class="deck">{inline(standfirst)}</p>' if standfirst else ''}
      <div class="byline">By {html.escape(byline or art['byline'])}</div>
      <p class="summary">{summary}</p>
      <a class="read" href="{art['slug']}.html">Read the article &rarr;</a>
    </article>""")

    index_css = """
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:0; }
  article { padding:0 26px; border-left:1px solid var(--rule); }
  article:first-child { border-left:none; padding-left:0; }
  article:last-child { padding-right:0; }
  article img { width:100%; display:block; margin-bottom:14px; }
  article h2 { font-size:25px; line-height:1.16; letter-spacing:-.4px; margin-bottom:10px; }
  article h2 a { color:inherit; text-decoration:none; }
  article h2 a:hover { text-decoration:underline; }
  .deck { font-size:16px; font-style:italic; color:#444; margin-bottom:10px; line-height:1.4; }
  .summary { font-size:16px; color:#333; margin:10px 0 14px; }
  @media (max-width:900px){
    article { border-left:none; padding:26px 0; border-top:1px solid var(--rule); }
    article:first-child { border-top:none; padding-top:0; }
  }
"""
    body = '  <div class="grid">\n' + "\n".join(cards) + "\n  </div>"
    (HERE / "index.html").write_text(
        shell("The Feature Desk — Three Original Articles", index_css, body)
    )
    print("built:", ", ".join(a["slug"] + ".html" for a in ARTICLES), "+ index.html")


if __name__ == "__main__":
    main()
