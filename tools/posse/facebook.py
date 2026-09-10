#!/usr/bin/env python3
"""POSSE to a Facebook Page — publish here, syndicate out, pull responses home.

ADR-0002 step 3, Facebook edition. The canonical post lives on roofbeam.net;
Facebook gets a copy that points home.

    tools/posse/facebook.py check                 # who am I, which Page, what can I do
    tools/posse/facebook.py publish <slug>        # syndicate a toy to the Page
    tools/posse/facebook.py publish <slug> --dry-run
    tools/posse/facebook.py posts                 # what has been syndicated
    tools/posse/facebook.py pull                  # bring responses home  (GATED, see below)

WHY POLLING AND NOT WEBHOOKS. Real-time Page webhooks need Advanced Access,
which needs App Review, which needs Business Verification — and Roofbeam has no
EIN yet. Polling `GET /{post-id}/comments` works in Development mode against a
Page you administer, with no review of any kind. ADR-0002 sets a cadence
measured in weeks, so polling is not a compromise here; it is the right tool.

⛔ `pull` IS DELIBERATELY GATED AND WILL REFUSE TO RUN.
Importing someone's Facebook comment is a privacy act, not a data sync — they
addressed Facebook's audience, not Jeremy's, so ADR-0001's `Consent.text_shown`
cannot be satisfied: there was no moment of agreement. ADR-0002 marks the
posture ⛔ undecided. So `pull` refuses until POSSE_IMPORT_POSTURE is set
explicitly. There is no default, on purpose — a default is how an undecided
privacy question gets decided by whoever wrote the code.

⚠️ NOTHING FETCHED HERE MAY ENTER THIS REPO. ~/core/roofbeam is a public
GitHub Pages source: every file in it is served to the world. Third-party
comments therefore live OUTSIDE the repo, under ~/.roofbeam/posse/, so that
even `git add -f` cannot publish someone else's words.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
GRAPH = "https://graph.facebook.com/v25.0"

# Outside the repo, deliberately. See the module docstring.
STATE = pathlib.Path(os.environ.get("POSSE_STATE", pathlib.Path.home() / ".roofbeam/posse"))

# The postures ADR-0002 ⛔ #1 is choosing between. No default — see docstring.
POSTURES = {
    "private-anonymized": (
        "Jeremy-readable only; never republished with attribution; "
        "anonymization mandatory. The ADR-0002 candidate."
    ),
    "private-attributed": (
        "Jeremy-readable only; author handle retained for the circle/world "
        "fork; still never republished."
    ),
}


def fail(msg, code=2):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------ config

def load_env():
    """Read .env.local from the repo root. Never committed — see .gitignore."""
    env = {}
    f = REPO / ".env.local"
    if f.exists():
        if f.stat().st_mode & 0o077:
            print(f"warning: {f} is group/world readable; chmod 600 it", file=sys.stderr)
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("'\"")
    env.update({k: v for k, v in os.environ.items() if k.startswith("POSSE_") or k.startswith("FB_")})
    return env


def token(env):
    t = env.get("FB_PAGE_TOKEN")
    if not t:
        fail("FB_PAGE_TOKEN is not set.\n"
             "  Put it in .env.local (gitignored) as  FB_PAGE_TOKEN=...\n"
             "  The /stash-secret skill can store it without pasting it into chat.\n"
             "  See the Facebook section of the Roofbeam errand sheet for how to mint one.")
    return t


# ------------------------------------------------------------------- graph

def graph(path, env, params=None, post=None):
    params = dict(params or {})
    params["access_token"] = token(env)
    url = f"{GRAPH}/{path.lstrip('/')}"
    if post is None:
        url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
    else:
        body = urllib.parse.urlencode({**params, **post}).encode()
        req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            err = json.loads(detail).get("error", {})
            detail = f"{err.get('type')}: {err.get('message')} (code {err.get('code')})"
        except Exception:
            pass
        fail(f"Graph API {e.code} on {path}\n  {detail}")
    except urllib.error.URLError as e:
        fail(f"could not reach the Graph API: {e.reason}")


# ---------------------------------------------------------------- manifest

def manifest(slug):
    f = REPO / "toys" / slug / "toy.json"
    if not f.exists():
        have = sorted(p.parent.name for p in REPO.glob("toys/*/toy.json"))
        fail(f"no manifest at {f.relative_to(REPO)}. Toys with manifests: {', '.join(have)}")
    return json.loads(f.read_text())


def compose(toy):
    """The syndicated copy. The QUESTION travels, the link points home, and
    Facebook renders the OG card that tools/share.py generated."""
    url = f"https://roofbeam.net/toys/{toy['slug']}/"
    return f"{toy['title']}\n\n{toy['card_question']}\n\n{url}", url


# ------------------------------------------------------------------- state

def state_file(name):
    STATE.mkdir(parents=True, exist_ok=True)
    STATE.chmod(0o700)
    return STATE / name


def load_state(name, default):
    f = state_file(name)
    return json.loads(f.read_text()) if f.exists() else default


def save_state(name, data):
    f = state_file(name)
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    f.chmod(0o600)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- commands

def cmd_check(args, env):
    page_id = env.get("FB_PAGE_ID")
    print(f"Graph API   {GRAPH.rsplit('/', 1)[1]}")
    print(f"state dir   {STATE}  (outside the repo, by design)")
    print(f"token       {'set' if env.get('FB_PAGE_TOKEN') else 'NOT SET'}")
    print(f"page id     {page_id or 'NOT SET'}")
    posture = env.get("POSSE_IMPORT_POSTURE")
    print(f"posture     {posture or 'UNSET — `pull` will refuse (ADR-0002 blocking decision 1)'}")
    if not env.get("FB_PAGE_TOKEN"):
        print("\nNot configured yet. See the errand sheet; nothing here can be done for you —\n"
              "creating the Page, creating the Meta app and granting OAuth are all yours.")
        return
    me = graph("me", env, {"fields": "id,name"})
    print(f"\nauthenticated as  {me.get('name')}  ({me.get('id')})")
    if page_id:
        # fields are named explicitly and fan_count is NOT among them. The Graph
        # API will hand over follower counts for free; the governing rule says
        # no vanity metrics anywhere, so the cheapest place to obey it is to
        # never ask for the number in the first place.
        p = graph(page_id, env, {"fields": "id,name,link"})
        print(f"page              {p.get('name')}  {p.get('link')}")
    perms = graph("me/permissions", env).get("data", [])
    granted = {p["permission"] for p in perms if p.get("status") == "granted"}
    need = {"pages_show_list", "pages_read_engagement", "pages_manage_posts"}
    print(f"\npermissions granted: {', '.join(sorted(granted)) or '(none)'}")
    missing = need - granted
    print("missing for publish : " + (", ".join(sorted(missing)) if missing else "none — ready"))


def cmd_publish(args, env):
    toy = manifest(args.slug)
    if not toy.get("published", False):
        fail(f"'{args.slug}' is not published (toy.json says published=false).\n"
             "  Syndicating a link to a parked toy sends people to a page you have "
             "unpublished, and robots.txt may stop the card rendering at all.")

    message, url = compose(toy)
    page_id = env.get("FB_PAGE_ID")

    print("── the syndicated copy " + "─" * 46)
    print(message)
    print("─" * 68)
    print(f"canonical  {url}")
    print(f"og card    https://roofbeam.net/toys/{toy['slug']}/og.png")

    if args.dry_run:
        print("\n[dry run] nothing sent.")
        return
    if not page_id:
        fail("FB_PAGE_ID is not set in .env.local")

    resp = graph(f"{page_id}/feed", env, post={"message": message, "link": url})
    remote_id = resp.get("id", "")
    record = {
        "slug": toy["slug"],
        "target": "facebook",
        "remote_id": remote_id,
        "url": f"https://www.facebook.com/{remote_id.replace('_', '/posts/')}" if "_" in remote_id else "",
        "canonical": url,
        "message": message,
        "syndicated_at": now(),
    }
    posts = load_state("syndicated.json", [])
    posts.append(record)
    save_state("syndicated.json", posts)
    print(f"\npublished. remote_id={remote_id}")
    print(f"recorded  {state_file('syndicated.json')}")


def cmd_posts(args, env):
    posts = load_state("syndicated.json", [])
    if not posts:
        print("nothing syndicated yet.")
        return
    for p in posts:
        print(f"{p['syndicated_at']}  {p['target']:<10} {p['slug']:<28} {p['remote_id']}")
    print(f"\n{len(posts)} syndicated post(s) — {state_file('syndicated.json')}")


def cmd_pull(args, env):
    posture = env.get("POSSE_IMPORT_POSTURE")
    if posture not in POSTURES:
        print("⛔ REFUSING TO IMPORT — the consent posture is undecided.\n", file=sys.stderr)
        print("Importing someone's Facebook comment is a privacy act, not a data sync.", file=sys.stderr)
        print("They addressed Facebook's audience, not Jeremy's, so ADR-0001's", file=sys.stderr)
        print("Consent.text_shown cannot be satisfied — there was no moment of agreement.", file=sys.stderr)
        print("ADR-0002 marks this ⛔ and it is Jeremy's to close, not this script's.\n", file=sys.stderr)
        print("Set POSSE_IMPORT_POSTURE in .env.local to one of:", file=sys.stderr)
        for k, v in POSTURES.items():
            print(f"  {k:<20} {v}", file=sys.stderr)
        print("\nThere is no default, deliberately.", file=sys.stderr)
        sys.exit(3)

    posts = load_state("syndicated.json", [])
    if not posts:
        print("nothing syndicated yet — nothing to pull.")
        return

    store = load_state("comments.json", [])
    seen = {c["remote_id"] for c in store}
    added = 0
    for p in posts:
        if p["target"] != "facebook":
            continue
        data = graph(f"{p['remote_id']}/comments", env,
                     {"fields": "id,message,created_time,from", "limit": 100}).get("data", [])
        for c in data:
            if c["id"] in seen:
                continue
            author = (c.get("from") or {})
            store.append({
                "remote_id": c["id"],
                "source": "facebook",
                "syndicated_post": p["remote_id"],
                "canonical": p["canonical"],
                "slug": p["slug"],
                "message": c.get("message", ""),
                "created_time": c.get("created_time"),
                # The circle/world fork (ADR-0002 §2) lives HERE, in the record,
                # not in Jeremy's head. Unclassified until he says which it is —
                # an unclassified comment is not eligible for any aggregate.
                "person_relation": None,
                "author_handle": author.get("name") if posture == "private-attributed" else None,
                "author_remote_id": author.get("id") if posture == "private-attributed" else None,
                "import_posture": posture,
                "imported_at": now(),
            })
            added += 1

    save_state("comments.json", store)
    unclassified = sum(1 for c in store if c["person_relation"] is None)
    print(f"imported {added} new comment(s) under posture '{posture}'")
    print(f"stored   {state_file('comments.json')}  (outside the repo — never published)")
    if unclassified:
        print(f"\n⚠️  {unclassified} comment(s) await circle/world classification.")
        print("    Until classified they are eligible for NO aggregate — the fork lives")
        print("    in the record, not in your head (ADR-0002 §2).")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="show configuration and granted permissions")
    pub = sub.add_parser("publish", help="syndicate a toy to the Page")
    pub.add_argument("slug")
    pub.add_argument("--dry-run", action="store_true", help="compose and show, send nothing")
    sub.add_parser("posts", help="list what has been syndicated")
    sub.add_parser("pull", help="bring responses home (gated on the consent posture)")
    args = ap.parse_args()
    env = load_env()
    {"check": cmd_check, "publish": cmd_publish, "posts": cmd_posts, "pull": cmd_pull}[args.cmd](args, env)


if __name__ == "__main__":
    main()
