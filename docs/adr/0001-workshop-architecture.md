# ADR-0001 — Workshop architecture: static surface, dynamic spine

- **Status:** accepted
- **Decided:** 2026-09-07 (recorded here 2026-09-10 — the ADR was owed and unwritten)
- **Scope:** roofbeam.net, the toys, and the conversation around them
- **Vault source of truth for the reasoning:** `Builder Vault/Efforts/Roofbeam/areas/Workshop Architecture.md`

## The governing rule — this ADR exists to record it, not just the stack

> **The creations are not to be prized — not by Jeremy, not by anybody else. Their value is in how they align with his own meditations.**

Stated 2026-09-07; the spine restated. *"Young Man's Primer really is directed at me"* (2026-08-08) · *"Not to influence others, although that may be part of it, but it is to make myself"* (2026-08-23).

YMP, the toys, the books, Onderdak and Roofbeam are **one practice with different surfaces**. The artifacts are byproducts of the meditation, not products of a career. Roofbeam is the roof they shelter under while they grow — **not a shopfront**.

**What the rule forbids, concretely — these are architectural constraints, not preferences:**

- no vanity metrics anywhere (views, likes, popularity, trending)
- comments are **input to meditation, not applause**
- provenance is an address, not a signature
- retiring a toy needs no ceremony
- never build for a launch
- shareability serves **the idea travelling**, never reach

Any later decision that requires violating one of these is out of scope for this repo, whatever its other merits.

## Context

Three asks — **embedding**, **commentary**, **contact capture** — are one system. The "Say hello" form is its smallest instance; solving it separately means building it twice.

The central tension: **embeddability and centralised commentary pull against each other.** The more decoupled a toy is, the more the natural place to react is wherever it was embedded. Centralising the conversation requires the embed to **carry its home with it**.

## Decision

### 1. The public site stays static; only the spine is dynamic

| Layer | Where | Why |
|---|---|---|
| Front door, toys, embeds | **GitHub Pages** (`git push`) | free, instant, effectively unkillable |
| Comments, capture, consent, moderation, corpus | **Django at `api.roofbeam.net`** | relational, ownable, ingestible |

**Django does not serve the public site.** Toys fetch comments client-side. **Designed failure mode: when the backend is down the toy still works** and the conversation degrades to "couldn't load discussion." Never the reverse.

### 2. A toy is a first-class object

Stable slug + manifest; everything else generates from that one record so metadata cannot drift:

- `/toys/<slug>/` — canonical page (toy + provenance + conversation)
- `/toys/<slug>/embed/` — chrome-free, built for iframing
- OG / Twitter cards + preview image; JSON-LD `CreativeWork`; **oEmbed JSON as a static file**
- **The embed carries a persistent provenance bar** — title · `roofbeam.net` · "Discuss this on Roofbeam →" with a ref param. That link is what pulls conversation home from every embed in the wild.

**Honest limit:** anyone can strip the footer and rehost; self-containment is exactly what makes toys embeddable. Design for the honest majority — **a stated licence does more work here than any technical measure.**

### 3. Own the comment corpus

Rejected: **Giscus/Utterances** (requires a GitHub account — gates out the intended audience) and **Disqus** (ads, third-party tracking, you don't own the corpus). Neither survives the stated purpose.

**`Toy.discussion_prompt` is the corpus-quality lever.** "Leave a comment" harvests hot takes; **"What did this make you notice?"** harvests reflection. Per-toy, authored, not generic.

### 4. Six models in a Django app `workshop`

`Toy` · `ToyVersion` (provenance survives revision) · `Person` · `Consent` · `Comment` · `EmbedOrigin` · `Message`

Two load-bearing separations:

- ⚠️ **`Person` is deliberately separate from `Comment`.** An anonymous comment can be **retroactively linked** to a Person if they later give an email. Collapse the two and that is lost forever.
- ⚠️ **`Consent.text_shown` is load-bearing** — the exact copy shown at the time. *Storing a boolean is not consent, it is a rumour of consent.*

**Pre-moderation is the default** (`status=pending`). At this volume it costs nothing and it is what makes "tractable" true.

⚠️ **Re-check the spam traps server-side.** The honeypot and time-trap in `index.html` today are client-side and advisory only — trivially bypassed by anything that POSTs directly.

## Consequences

- The site cannot 500 because Postgres hiccuped.
- The comment corpus is Jeremy's, ingestible, and answerable to which *version* of a toy a person saw.
- Later evolution (not now): Django becomes source-of-truth and **generates** the static site. A natural extension of this design, not a rewrite.

## Known gap at time of writing

⚠️ **Verified 2026-09-07 and still true 2026-09-10: no live toy has any Open Graph, Twitter Card, canonical link, or JSON-LD.** A shared link renders as a naked URL — no title, no image, no attribution. **This is the single biggest shareability gap and it is free to fix.** It blocks ADR-0002 in practice: syndicating to platforms is pointless while the links are naked.

## Still Jeremy's

Licence (CC BY 4.0?) · comment identity (lean: anonymous to post, optional email with explicit consent) · public inline vs. curated correspondence · whose Hetzner account · Patreon shape · whether `/costs` goes public.
