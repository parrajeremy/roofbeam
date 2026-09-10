# Roofbeam — docs

Decision records for the workshop. **The reasoning lives in the Builder Vault** (`Efforts/Roofbeam/`); this folder holds the decisions that constrain the code, so they travel with the repo.

## The governing rule — read before designing anything here

> **The creations are not to be prized — not by Jeremy, not by anybody else. Their value is in how they align with his own meditations.**

It is not a mood. It forbids specific things, and those prohibitions are architectural: **no vanity metrics anywhere** · comments are input to meditation, not applause · shareability serves the idea travelling, never reach · never build for a launch. A design that needs one of those relaxed is out of scope for this repo, whatever else it has going for it.

Full derivation: `Efforts/Roofbeam/START HERE.md` and `areas/Workshop Architecture.md`.

## ADRs

| # | Decision | Status |
|---|---|---|
| [0001](adr/0001-workshop-architecture.md) | **Workshop architecture** — static surface (GitHub Pages), dynamic spine (Django at `api.roofbeam.net`), toy-as-object, own the comment corpus, six models | accepted 2026-09-07 |
| [0002](adr/0002-social-layer-posse-and-the-two-instruments.md) | **The social layer** — POSSE + Webmention, the circle/world fork in the schema, a prediction log instead of engagement metrics | proposed 2026-09-10, 3 blocking items |

## Where things live

| | |
|---|---|
| Front door + toys | this repo → GitHub Pages → roofbeam.net (**deploy = `git push`**) |
| Backend spine (planned) | Django, `api.roofbeam.net` — does **not** serve the public site |
| Reasoning, open questions, Ledger | Builder Vault `Efforts/Roofbeam/` |
| Project registry / cross-session memory | JENI, slug `roofbeam` |

## The two things blocking work right now

1. ⚠️ **No toy has Open Graph, Twitter Card, canonical link or JSON-LD.** Verified 2026-09-07, still true 2026-09-10. A shared link renders as a naked URL — no title, no image, no attribution. **Free to fix, and it blocks the whole social layer:** syndicating naked links is pointless.
2. ⛔ **Three decisions are Jeremy's** before anything ingests third-party comments — see ADR-0002, *Blocking*.
