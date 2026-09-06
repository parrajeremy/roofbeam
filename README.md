# Roofbeam

The front door for [roofbeam.net](https://roofbeam.net) — Jeremy Parra's solo workshop: projects, writing, and a reading list.

## What this is

A **static front door** — deliberately cheap, fast, and near-impossible to break. It links out to projects; it does not run them. Interactive "toys" are deployed separately (Cloud Run on Roofbeam's GCP) and linked from here, so a half-finished experiment can never take down the homepage.

- **Stack:** plain static HTML/CSS (no build step). Edit `index.html` directly.
- **Host:** GitHub Pages, served on the custom domain `roofbeam.net`.
- **Deploy:** `git push` to `main`. That's the whole pipeline.

## Structure

- `index.html` — the whole site (home + Projects / Writing / Reading sections).
- `CNAME` — the custom domain GitHub Pages serves (`roofbeam.net`).
- `.nojekyll` — tells Pages to serve files as-is (no Jekyll processing).

## Editing content

Everything is placeholder until filled. In `index.html`:
- **Projects** — duplicate a `.card` block per project; set the tag, title, blurb, and wrap it in a link when it's live.
- **Writing** — add `<li>` rows under the Writing list (or graduate to markdown posts later).
- **Reading** — add `<li>` rows under the Reading list.

---
Roofbeam LLC (Oregon) — Jeremy's solo-entrepreneur vehicle.
