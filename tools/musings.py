#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown>=3.7", "pyyaml>=6.0"]
# ///
"""Obsidian → roofbeam.net/musings/ — the posting practice.

Jeremy writes in Obsidian and posts weekly-ish. This renders what he writes
into the static site, so publishing is `git push` and the archive outlives
whatever infrastructure happens to be running.

    tools/musings.py new "On tranquility"   # scaffold a note in the vault
    tools/musings.py list                   # what's in the vault, and its status
    tools/musings.py build                  # render everything marked live
    tools/musings.py build on-tranquility   # just one

Run it directly — the PEP 723 header makes `uv` fetch markdown and pyyaml
into a throwaway environment, so there is no venv to commit and nothing to
install into the system Python.

Source lives in the vault, NOT in this repo: ~/Documents/Obsidian Vault/
Atlas/Musings, beside Atlas/Essays. Override with ROOFBEAM_MUSINGS_DIR.
Drafts stay in the vault and never reach the repo, so an unfinished thought
cannot be published by a careless `git add`.

The rendered head comes from tools/share.py, the same one the toys use — so
a musing gets its OG card, canonical link and JSON-LD for free, and
`share.py verify` checks musings and toys with one pass.
"""

import argparse
import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import unicodedata

import markdown
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import share  # noqa: E402  — the single source for share metadata

REPO = pathlib.Path(__file__).resolve().parent.parent
VAULT = pathlib.Path(
    os.environ.get("ROOFBEAM_MUSINGS_DIR",
                   pathlib.Path.home() / "Documents/Obsidian Vault/Atlas/Musings")
)
OUT = REPO / "musings"

DEFAULT_PROMPT = "What did this make you notice?"

WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)[:60].strip("-")


# --------------------------------------------------------------- the source

def plain_text(md):
    """Markdown → readable prose, for strings that end up in metadata."""
    md = WIKILINK.sub(lambda m: (m.group(2) or m.group(1)).strip(), md)
    md = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", md)      # images → alt
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)       # links → text
    md = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", md)          # code
    md = re.sub(r"(\*\*|__)(.*?)\1", r"\2", md)             # bold
    md = re.sub(r"(\*|_)(.*?)\1", r"\2", md)                 # italic
    md = re.sub(r"^#{1,6}\s*", "", md)                      # heading marks
    md = md.replace("\\", "")
    return " ".join(md.split())


class Musing:
    def __init__(self, path):
        self.path = path
        raw = path.read_text()
        meta, body = {}, raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError as e:
                    fail(f"{path.name}: frontmatter is not valid YAML — {e}")
                body = parts[2]
        self.meta = meta
        self.body_md = body.strip()

        self.title = str(meta.get("title") or path.stem).strip()
        self.slug = str(meta.get("slug") or slugify(self.title))
        self.status = str(meta.get("status") or "draft").strip().lower()
        self.summary = plain_text(str(meta.get("summary") or "").strip())
        self.prompt = str(meta.get("prompt") or DEFAULT_PROMPT).strip()

        d = meta.get("date")
        if isinstance(d, dt.datetime):
            d = d.date()
        elif isinstance(d, str):
            try:
                d = dt.date.fromisoformat(d.strip()[:10])
            except ValueError:
                d = None
        self.date = d if isinstance(d, dt.date) else None

    @property
    def is_live(self):
        # Anything that is not explicitly live stays in the vault. "draft
        # compilation", the status already used in Atlas/Essays, correctly
        # reads as not-live.
        return self.status == "live"

    def first_paragraph(self):
        """The first real paragraph, reduced to PLAIN TEXT.

        This string leaves the page and becomes og:description, the OG card
        and the archive entry — none of which render markdown. A summary
        that still contains [[wikilinks]] or **asterisks** is precisely how
        vault writing looks broken in public, which is the thing the
        wikilink handling exists to prevent. So it is stripped here too.
        """
        for block in self.body_md.split("\n\n"):
            t = " ".join(block.split())
            if t and not t.startswith(("#", ">", "-", "*", "|", "!", "```")):
                return plain_text(t)
        return ""

    def problems(self):
        """Everything that would make a bad page, reported together rather
        than one exception at a time."""
        out = []
        if not self.title:
            out.append("no title")
        if not self.slug:
            out.append("title produces an empty slug — set `slug:` explicitly")
        if not self.body_md:
            out.append("no body")
        if self.date is None:
            out.append("no usable `date:` (expected YYYY-MM-DD)")
        if "![[" in self.body_md:
            out.append("contains an Obsidian embed `![[...]]` — not supported yet; "
                       "use a normal ![alt](url) with the file committed under /musings/<slug>/")
        return out


# ------------------------------------------------------------- the markdown

def resolve_wikilinks(md, known):
    """Obsidian wikilinks. If the target is another live musing, link it;
    otherwise keep the human-readable text and drop the brackets — a dangling
    [[...]] rendered literally is the most common way vault writing looks
    broken in public."""
    def sub(m):
        target, label = m.group(1).strip(), (m.group(2) or "").strip()
        text = label or target
        slug = known.get(target.lower()) or known.get(slugify(target))
        if slug:
            return f"[{text}](/musings/{slug}/)"
        return text
    return WIKILINK.sub(sub, md)


CALLOUT = re.compile(r"^>\s*\[!(\w+)\]\s*(.*)$", re.M)


def render(md_text, known):
    md_text = resolve_wikilinks(md_text, known)
    # Obsidian callouts degrade to plain blockquotes with the kind as a lead-in.
    md_text = CALLOUT.sub(lambda m: f"> **{m.group(1).title()}**" + (f" — {m.group(2)}" if m.group(2) else ""), md_text)
    return markdown.markdown(
        md_text,
        extensions=["extra", "smarty", "sane_lists", "admonition"],
        output_format="html5",
    )


# ----------------------------------------------------------------- the page

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<!-- share metadata — generated from musings/{slug}/musing.json by tools/share.py.
     Do not hand-edit: change the source note in the vault, re-run
     `tools/musings.py build`, and `tools/share.py verify` fails if these drift. -->
{share_head}
<style>
:root {{
  --bg:#f6f3ec; --panel:#fffdf8; --ink:#23201b; --muted:#6b6459;
  --line:#e2dccf; --accent:#b4531f; --accent-soft:#eadfce;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#17150f; --panel:#201d16; --ink:#ece7db; --muted:#a49b89;
    --line:#322d23; --accent:#e08a4e; --accent-soft:#2b2418;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#17150f; --panel:#201d16; --ink:#ece7db; --muted:#a49b89;
  --line:#322d23; --accent:#e08a4e; --accent-soft:#2b2418;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;
  line-height:1.75; -webkit-font-smoothing:antialiased;
}}
a {{ color:var(--accent); }}
a:hover {{ text-decoration:underline; }}
header.site {{ border-bottom:1px solid var(--line); }}
.nav {{ display:flex; align-items:baseline; justify-content:space-between;
  padding:16px 24px; max-width:760px; margin:0 auto; }}
.brand {{ font-family:Fraunces,Georgia,serif; font-weight:600; font-size:1.1rem;
  color:var(--ink); text-decoration:none; letter-spacing:-.01em; }}
.brand span {{ color:var(--accent); }}
.nav a.link {{ color:var(--muted); font-size:.9rem; margin-left:20px; text-decoration:none; }}
.nav a.link:hover {{ color:var(--ink); }}
main {{ max-width:760px; margin:0 auto; padding:0 24px 96px; }}
article {{ max-width:34em; }}
.kicker {{ font-size:.78rem; letter-spacing:.09em; text-transform:uppercase;
  color:var(--accent); margin:56px 0 14px; }}
h1 {{ font-family:Fraunces,Georgia,serif; font-weight:600; line-height:1.15;
  font-size:clamp(2rem,5vw,2.8rem); letter-spacing:-.02em; margin:0 0 14px; }}
.meta {{ color:var(--muted); font-size:.92rem; margin:0 0 40px;
  padding-bottom:22px; border-bottom:1px solid var(--line); }}
article h2, article h3 {{ font-family:Fraunces,Georgia,serif; font-weight:600;
  line-height:1.25; margin:2.2em 0 .6em; }}
article h2 {{ font-size:1.5rem; }}
article h3 {{ font-size:1.2rem; }}
article p {{ font-size:1.08rem; margin:0 0 1.3em; }}
article blockquote {{ margin:1.8em 0; padding:2px 0 2px 20px;
  border-left:3px solid var(--accent-soft); color:var(--muted); font-style:italic; }}
article blockquote p {{ margin:0 0 .7em; }}
article img {{ max-width:100%; height:auto; border-radius:10px; }}
article hr {{ border:0; border-top:1px solid var(--line); margin:2.6em 0; }}
article code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em;
  background:var(--accent-soft); padding:1px 5px; border-radius:4px; }}
article pre {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:14px 16px; overflow-x:auto; }}
article pre code {{ background:none; padding:0; }}
article table {{ border-collapse:collapse; width:100%; font-size:.95rem; }}
article th, article td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; }}
.response {{ max-width:34em; margin-top:72px; padding-top:28px; border-top:1px solid var(--line); }}
.response h2 {{ font-family:Fraunces,Georgia,serif; font-size:1.3rem; font-weight:600; margin:0 0 10px; }}
.response .prompt {{ color:var(--ink); font-size:1.05rem; margin:0 0 18px; }}
.response .state {{ color:var(--muted); font-size:.94rem; }}
footer.site {{ border-top:1px solid var(--line); margin-top:64px; }}
.foot {{ max-width:760px; margin:0 auto; padding:22px 24px 40px;
  color:var(--muted); font-size:.88rem; display:flex; gap:14px; flex-wrap:wrap; }}
</style>
</head>
<body>
<header class="site"><nav class="nav">
  <a class="brand" href="/">Roof<span>beam</span></a>
  <span><a class="link" href="/musings/">Musings</a><a class="link" href="/#projects">Projects</a><a class="link" href="/">Home</a></span>
</nav></header>

<main>
  <p class="kicker">A musing</p>
  <article>
    <h1>{title}</h1>
    <p class="meta">{date_human}</p>
    {body}
  </article>

  <section class="response" id="response">
    <h2>Respond</h2>
    <p class="prompt">{prompt}</p>
    <div class="state" id="response-state">Loading the conversation&hellip;</div>
  </section>
</main>

<footer class="site"><div class="foot">
  <span>Jeremy Parra</span>
  <span>&middot;</span>
  <a href="/">roofbeam.net</a>
  <span>&middot;</span>
  <span>{licence}</span>
</div></footer>

<script>
// ADR-0001's designed failure mode: the writing is static and always
// readable; only the conversation depends on the backend. If the API is
// absent or down this degrades to a line of text and nothing else breaks.
// Never the reverse.
(function () {{
  var state = document.getElementById('response-state');
  var base = window.ROOFBEAM_API || 'https://api.roofbeam.net';
  var url = base + '/api/responses/?entry=' + encodeURIComponent({slug_json});
  var done = false;
  function settle(msg) {{ if (!done) {{ done = true; state.textContent = msg; }} }}
  setTimeout(function () {{ settle('The conversation isn\\u2019t wired up yet.'); }}, 4000);
  fetch(url, {{ headers: {{ 'Accept': 'application/json' }} }})
    .then(function (r) {{ return r.ok ? r.json() : Promise.reject(r.status); }})
    .then(function (data) {{
      done = true;
      var items = (data && data.results) || [];
      if (!items.length) {{ state.textContent = 'No responses here yet.'; return; }}
      state.textContent = '';
      items.forEach(function (c) {{
        var d = document.createElement('div');
        d.style.cssText = 'margin:0 0 18px;padding-bottom:18px;border-bottom:1px solid var(--line)';
        var who = document.createElement('div');
        who.style.cssText = 'font-weight:500;color:var(--ink);font-size:.92rem;margin-bottom:4px';
        who.textContent = c.display_name || 'Anonymous';
        var body = document.createElement('p');
        body.style.cssText = 'margin:0;color:var(--muted)';
        body.textContent = c.body || '';
        d.appendChild(who); d.appendChild(body); state.appendChild(d);
      }});
    }})
    .catch(function () {{ settle('The conversation isn\\u2019t wired up yet.'); }});
}})();
</script>
</body>
</html>
"""


def build_one(m, known):
    d = OUT / m.slug
    d.mkdir(parents=True, exist_ok=True)

    summary = m.summary or m.first_paragraph()[:280]
    manifest = {
        "slug": m.slug,
        "kind": "musing",
        "path": f"/musings/{m.slug}/",
        "title": m.title,
        "page_title": m.title,
        "tagline": summary,
        "card_question": m.prompt,
        "source": f"A musing · {m.date.strftime('%-d %B %Y')}" if m.date else "A musing",
        "published": True,
        "created": m.date.isoformat() if m.date else None,
        "discussion_prompt": m.prompt,
    }
    (d / "musing.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    page = PAGE.format(
        page_title=html.escape(m.title),
        title=html.escape(m.title),
        desc=html.escape(summary),
        slug=m.slug,
        slug_json=json.dumps(m.slug),
        share_head=share.head_block(manifest),
        date_human=m.date.strftime("%-d %B %Y") if m.date else "",
        body=render(m.body_md, known),
        prompt=html.escape(m.prompt),
        licence="CC BY 4.0",
    )
    (d / "index.html").write_text(page)
    return manifest


ARCHIVE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Musings — Roofbeam</title>
<meta name="description" content="Notes I'm thinking through, published as I go.">
<link rel="canonical" href="https://roofbeam.net/musings/">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#f6f3ec; --ink:#23201b; --muted:#6b6459; --line:#e2dccf; --accent:#b4531f; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#17150f; --ink:#ece7db; --muted:#a49b89; --line:#322d23; --accent:#e08a4e; }} }}
:root[data-theme="dark"] {{ --bg:#17150f; --ink:#ece7db; --muted:#a49b89; --line:#322d23; --accent:#e08a4e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); line-height:1.65;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif; }}
a {{ color:var(--accent); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
header {{ border-bottom:1px solid var(--line); }}
.nav {{ display:flex; justify-content:space-between; align-items:baseline;
  padding:16px 24px; max-width:760px; margin:0 auto; }}
.brand {{ font-family:Fraunces,Georgia,serif; font-weight:600; font-size:1.1rem; color:var(--ink); }}
.brand span {{ color:var(--accent); }}
.nav a.link {{ color:var(--muted); font-size:.9rem; margin-left:20px; }}
main {{ max-width:760px; margin:0 auto; padding:56px 24px 96px; }}
h1 {{ font-family:Fraunces,Georgia,serif; font-weight:600; font-size:clamp(2rem,5vw,2.6rem);
  letter-spacing:-.02em; margin:0 0 10px; }}
.lede {{ color:var(--muted); max-width:48ch; margin:0 0 44px; }}
ul {{ list-style:none; padding:0; margin:0; max-width:46em; }}
li {{ border-bottom:1px solid var(--line); padding:20px 0; }}
li a.t {{ font-family:Fraunces,Georgia,serif; font-size:1.25rem; font-weight:600; color:var(--ink); }}
li a.t:hover {{ color:var(--accent); text-decoration:none; }}
li .d {{ color:var(--muted); font-size:.86rem; margin-top:4px; }}
li .s {{ color:var(--muted); font-size:.98rem; margin-top:8px; }}
.empty {{ color:var(--muted); }}
</style>
</head>
<body>
<header><nav class="nav">
  <a class="brand" href="/">Roof<span>beam</span></a>
  <span><a class="link" href="/#projects">Projects</a><a class="link" href="/">Home</a></span>
</nav></header>
<main>
  <h1>Musings</h1>
  <p class="lede">Notes I&rsquo;m thinking through, published as I go. Not finished positions &mdash; working thoughts.</p>
  <ul>
{items}
  </ul>
</main>
</body>
</html>
"""


def build_archive(manifests):
    if manifests:
        items = "\n".join(
            f'    <li><a class="t" href="{m["path"]}">{html.escape(m["title"])}</a>'
            f'<div class="d">{m["source"]}</div>'
            f'<div class="s">{html.escape(m["tagline"][:200])}</div></li>'
            for m in manifests
        )
    else:
        items = '    <li class="empty">Nothing published yet.</li>'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(ARCHIVE.format(items=items))


HOME_START = "<!-- musings:start -->"
HOME_END = "<!-- musings:end -->"


def update_homepage(manifests):
    """Keep the homepage Writing list in step, between markers. If the markers
    are absent, say so and change nothing rather than guessing where to cut."""
    p = REPO / "index.html"
    s = p.read_text()
    if HOME_START not in s or HOME_END not in s:
        return False
    if manifests:
        rows = "\n".join(
            f'          <li><a class="t" href="{m["path"]}" style="color:inherit">{html.escape(m["title"])}</a>'
            f'<span class="d">{m["created"] or ""}</span></li>'
            for m in manifests[:6]
        )
    else:
        rows = '          <li><span class="t">Nothing published yet</span><span class="d"></span></li>'
    a, b = s.index(HOME_START) + len(HOME_START), s.index(HOME_END)
    p.write_text(s[:a] + "\n" + rows + "\n        " + s[b:])
    return True


# ---------------------------------------------------------------- commands

def load_all():
    if not VAULT.exists():
        fail(f"no musings directory at {VAULT}\n"
             f"  create it, or point ROOFBEAM_MUSINGS_DIR somewhere else.\n"
             f"  `tools/musings.py new \"A title\"` will create it for you.")
    return sorted((Musing(p) for p in VAULT.glob("*.md")),
                  key=lambda m: (m.date or dt.date.min), reverse=True)


def cmd_list(args):
    all_m = load_all()
    if not all_m:
        print(f"No musings in {VAULT}")
        return
    print(f"{VAULT}\n")
    for m in all_m:
        mark = "live " if m.is_live else "draft"
        date = m.date.isoformat() if m.date else "no date  "
        probs = m.problems()
        flag = "  ⚠️ " + "; ".join(probs) if probs else ""
        print(f"  [{mark}] {date}  {m.slug:<34} {m.title}{flag}")
    live = sum(1 for m in all_m if m.is_live)
    print(f"\n{live} live, {len(all_m) - live} draft. Only live ones are rendered into the repo.")


def cmd_build(args):
    all_m = load_all()
    live = [m for m in all_m if m.is_live]
    if args.slug:
        live = [m for m in live if m.slug == args.slug]
        if not live:
            fail(f"no LIVE musing with slug '{args.slug}'. `tools/musings.py list` shows what there is.")

    blocked = [(m, m.problems()) for m in live if m.problems()]
    if blocked:
        print("Not building — fix these first:\n", file=sys.stderr)
        for m, probs in blocked:
            print(f"  {m.path.name}", file=sys.stderr)
            for p in probs:
                print(f"    · {p}", file=sys.stderr)
        sys.exit(2)

    seen = {}
    for m in live:
        if m.slug in seen:
            fail(f"two musings share the slug '{m.slug}': {seen[m.slug]} and {m.path.name}")
        seen[m.slug] = m.path.name

    known = {}
    for m in live:
        known[m.title.lower()] = m.slug
        known[m.slug] = m.slug

    built = [build_one(m, known) for m in live]
    build_archive(built)
    touched_home = update_homepage(built)

    for man in built:
        print(f"  musings/{man['slug']}/index.html")
    print(f"\n{len(built)} musing(s) rendered · musings/index.html")
    print("homepage Writing list updated" if touched_home
          else "homepage NOT updated — no <!-- musings:start --> markers in index.html")
    print("\nnext:  tools/share.py cards && tools/share.py verify")


TEMPLATE = """---
title: "{title}"
slug: {slug}
date: {date}
status: draft
summary: ""
prompt: "{prompt}"
---

"""


def cmd_new(args):
    title = args.title.strip()
    if not title:
        fail("give it a title")
    VAULT.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    path = VAULT / f"{title.replace('/', '-')}.md"
    if path.exists():
        fail(f"{path} already exists")
    path.write_text(TEMPLATE.format(
        title=title.replace('"', "'"), slug=slug,
        date=dt.date.today().isoformat(), prompt=DEFAULT_PROMPT,
    ))
    print(f"created {path}")
    print(f"  slug: {slug}")
    print("\nWrite it in Obsidian. It stays a draft — and stays out of the repo —")
    print("until you change `status: draft` to `status: live`.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="what is in the vault, and its status")
    b = sub.add_parser("build", help="render live musings into the repo")
    b.add_argument("slug", nargs="?", help="just this one")
    n = sub.add_parser("new", help="scaffold a new musing in the vault")
    n.add_argument("title")
    args = ap.parse_args()
    {"list": cmd_list, "build": cmd_build, "new": cmd_new}[args.cmd](args)


if __name__ == "__main__":
    main()
