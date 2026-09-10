# ADR-0002 — The social layer: POSSE, two instruments, and a prediction log instead of KPIs

- **Status:** proposed — the shape is settled, three items marked ⛔ are Jeremy's to close before building
- **Proposed:** 2026-09-10
- **Extends:** [ADR-0001](0001-workshop-architecture.md) — same models, same governing rule. **Not a new system.**
- **Vault reasoning:** `Builder Vault/Efforts/Roofbeam/areas/Workshop Architecture.md` (§ *The social layer*, § *The 2026-09-09 22:52 memo*)

## Context — in his words

> "Go into the agora, Jeremy — **but make sure you're not wired up to the Agora the way that the Agora wants you to be wired up to it.** That's gonna be the mechanism of my art. **It's the Banksy of social media.**"

> "I come to the table to give my musing, to build my toys. They get posted on roofbeam.net, and interaction is tabulated in the back end and that drives some behavior."

> "**The goal will be not to grow an audience as the KPI.** … **It's not chasing likes, it's repurposing those platforms** — taking the questions that get asked and using those to decide what to repost… **and then you repost the question in some anonymized fashion.**"

**The governing rule of ADR-0001 already wrote most of this spec.** The social layer is the first surface where keeping that rule costs something.

## Decision

### 1. POSSE — publish here, syndicate out, pull responses home

Adopt the IndieWeb pattern rather than inventing it: the **canonical post lives on roofbeam.net**; platforms receive copies that point home. **Webmention** (W3C Rec) is the response protocol; **Bridgy** backfeeds silo responses.

Its founding motivation is Jeremy's stated thesis, published fifteen years earlier. Per the OSS-reuse principle: **adopt or fork, do not rebuild.**

**Honest limit:** Bridgy backfeed covers Mastodon, Bluesky, GitHub, Reddit, Flickr. Facebook, Instagram and Twitter support died when those APIs closed.

### 2. ⭐ Two instruments, and the fork lives in the schema

From the 2026-09-09 22:52 memo — **a prior objection to this plan, made twelve hours before the plan:**

> "You have to **know the person receiving the thing** to know how they're going to act for that to update anything reasonable. If not — **the other end of the pipe is completely noisy. So whatever comes down is not trustworthy except for that which you cherry pick.**" · "**You need friends.**"

And its resolution, in the same memo:

> "Can you learn from a bigger audience? You can gain response **about the world** from how they respond to your art. **It's a way of polling the survey. The survey you write.**"

| | **the circle** — known people | **the world** — strangers |
|---|---|---|
| what a response tells you | about **you and your claim** — the pipe has a known end | about the **shared meaning landscape** |
| valid operation | **falsifiable prediction**, checked | **aggregate distribution**, read as a poll |
| invalid operation | — | treating an individual response as feedback on you |

⚠️ **This is a schema requirement, not a disposition.** `Person` gains a **known-to-Jeremy** dimension and `Comment` handling **forks on it**. If both kinds land in one undifferentiated table the distinction survives only in Jeremy's head — and the memo's whole warning is that the head is where cherry-picking happens. **Put the fork in the model.**

Note the failure mode is not flattery: *"which, by the way, is not necessarily the good things. You might like feeling bad."*

### 3. ⭐ No engagement metrics. A prediction log.

> "**Making claim before you act.** … putting something falsifiable in front of yourself and then determining whether it indeed led to the outcome that you had, **and how far off you are.**"

Before a post goes out, the claim goes in — who responds, how, to what. Afterwards it is scored. **The measure is calibration, not engagement.**

Why this and not an "authenticity score": *an authenticity score is a vanity metric with better manners.* **A calibration score goes down when you flatter yourself**, which is the property the governing rule actually needs. It also cannot be gamed by posting more.

**JENI already has `record_prediction`.** No new mechanism. This is load-bearing determinism applied to the art: the pre-registered claim is the load-bearing artifact; verification is mechanical, not vibes.

### 4. The practice stays small, and is derived from belief

From the 2026-09-09 18:26 memo: *"Behaviors are all over the place, so Stoics would have **a simpler practice, coordinate behavior**, and belief is underneath the method."*

**Cadence is not tuned to response.** A few coordinated practices, each carrying a prediction. Frequency is a consequence of the practice, never a target.

### 5. Model additions — three, on the existing spine

```
SyndicationTarget   platform, handle, auth_ref, capabilities
SyndicatedPost      post FK, target FK, remote_id, url, syndicated_at
Comment            + source (native|mastodon|bluesky|facebook|…)
                   + remote_id, + SyndicatedPost FK
Person             + relation (circle|world)        # ← the fork from §2
```

`EmbedOrigin` generalises: a syndication target is *"where in the world is this, and where is the conversation I can invite home?"* with a known answer.

## What the platforms actually permit

⚠️ *Verify before building — platform terms move faster than any document. Shape as of mid-2026.*

| | post out | **responses back** | contacts |
|---|---|---|---|
| **Bluesky** (AT Proto) | ✅ free, open | ✅ full, incl. firehose | ✅ |
| **Mastodon** (ActivityPub) | ✅ free, open | ✅ full | ✅ |
| **Facebook** | ✅ **Page only** — personal profiles have no publishing API | ✅ comments + webhooks, on a Page | ❌ |
| **Threads** | ✅ | ✅ replies + insights | ❌ |
| **Instagram** | ✅ Business/Creator linked to a Page | ✅ comments + webhooks | ❌ |
| **LinkedIn** | ✅ personal (`w_member_social`) | ❌ partner-gated | ❌ no API at all |
| **X** | ✅ | 💰 paid tiers | ❌ |

**Browser automation is rejected** for LinkedIn / Facebook / Instagram: it breaches ToS and gets accounts restricted, and LinkedIn detects and litigates. Not worth Jeremy's real accounts. The sanctioned path for his own data on closed platforms is **periodic export** (LinkedIn archive, Facebook DYI, Instagram export) — complete, legitimate, not real-time, and adequate for a cadence measured in weeks.

### ⭐ The finding

**The platforms that will let him wire this up are exactly the ones that don't own the conversation.** Facebook and LinkedIn take the words and keep the responses; Mastodon and Bluesky give them back. *"Don't be wired up the way the Agora wants"* is not a posture to maintain against the infrastructure — **it is a description of which infrastructure will cooperate.**

## Sequencing

1. **OG / Twitter cards / canonical / JSON-LD on the toys.** Blocking everything else — see ADR-0001's known gap. One afternoon.
2. Three model additions + a post object with a canonical URL to syndicate.
3. **Bluesky + Mastodon** — free, open, full round trip. **Prove the loop where nothing is gated.**
4. Facebook Page + Threads + Instagram — one Meta auth, app review.
5. LinkedIn — post-out only.
6. X — only if there is a reason to pay.

⚠️ **Jeremy said "starting with Facebook."** Recorded as a live disagreement about **sequence, not destination**: Facebook needs a Page (his personal profile cannot be wired at all), an app, and a review cycle — slowest path to first light, and the loop cannot be proven there. Bluesky is an afternoon. *"That's where the people I know actually are" is a real reason and the call is his.*

## ⛔ Blocking — Jeremy's to close before anything ingests

1. **Consent posture for imported comments.** Pulling someone's Facebook comment into a private corpus is a **privacy act, not a data sync** — they addressed that platform's audience. `Consent.text_shown` cannot be satisfied; there was no moment of agreement. *Candidate, and it is what he already asked for: imported comments are Jeremy-readable only, never republished with attribution, anonymization mandatory rather than optional.*
2. **What JENI is allowed to optimise.** "When to post" is scheduling; "what to post next" is editorial, and the second is where the governing rule can quietly lose.
3. **Sequence** — Bluesky-first (recommended) or Facebook-first (his stated preference).

## Consequences

- Response stops being a signal to chase and becomes two separate instruments with different valid operations.
- Nothing in the system can report a number that goes up when more people react.
- **This is also the Leisure toy model** (`Builder Vault/Efforts/Leisure/Touchstone.md`, open since 2026-09-02): "comments aggregated into a response question" is a response primitive that is neither a like nor an essay — the middle of the feedback scale, running on real traffic. **Do not build it twice.**
- The Agora cast maps directly: Jeremy is the hero, responders are foils who are never placed on a stage, JENI is the mediator. It is an Agora instance in everything but registration.
