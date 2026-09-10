# ADR-0002 — The social layer: POSSE, two instruments, and a prediction log instead of KPIs

- **Status:** proposed. **#3 (sequence) closed 2026-09-10** — Facebook first, then narrowed by the platform correction below to *Facebook for distribution, roofbeam.net for response*. **#1 (consent posture) is now moot for Facebook** (nothing is importable) and applies only to genuinely importable sources; for **native** comments there is a moment of agreement, so it does not block them. **#2 (what JENI may optimise) is still open.**
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
| **Facebook** | ✅ **Page only** — personal profiles have no publishing API | ✅ comments on a Page — by **polling** in Development mode; **webhooks need Advanced Access** (see § Sequencing) | ❌ |
| **Threads** | ✅ | ✅ replies + insights | ❌ |
| **Instagram** | ✅ Business/Creator linked to a Page | ✅ comments + webhooks | ❌ |
| **LinkedIn** | ✅ personal (`w_member_social`) | ❌ partner-gated | ❌ no API at all |
| **X** | ✅ | 💰 paid tiers | ❌ |

**Browser automation is rejected** for LinkedIn / Facebook / Instagram: it breaches ToS and gets accounts restricted, and LinkedIn detects and litigates. Not worth Jeremy's real accounts.

> ### ⚠️ CORRECTION 2026-09-10 — the export path does NOT carry responses
>
> This ADR said the sanctioned path for closed platforms is **periodic export**, "complete, legitimate, not real-time, and adequate for a cadence measured in weeks." **The first half is right and the last clause is wrong**, and the error matters because the whole point of the exercise is bringing responses home.
>
> A Facebook DYI export contains **his posts and the comments *he* wrote**. It does **not** contain comments *other people* wrote on his posts. Meta's stated reason is that those comments *belong to the people who wrote them*.
>
> So for Jeremy's **private profile** there is **no legitimate response path at all**: personal-profile publishing died with `publish_actions` in 2018 and has not returned; the **Groups API was retired outright in April 2024** and removed from every Graph version, so a private group is not a way around it; and export omits exactly the half that matters. Browser automation is the only remaining mechanism and this ADR already rejects it — doubly so on a personal account.
>
> **Note what Facebook's reason actually is.** *"They belong to the people who wrote them"* is ⛔ #1's own argument, enforced at the platform level. Facebook is not being obstructive here; it is taking the position this ADR was asking Jeremy to consider. **That makes ⛔ #1 moot for Facebook** — there is nothing to decide a posture about, because there is nothing importable.
>
> **This is § The finding, in its sharpest form.** Not "Facebook is slower to wire up" — the earlier objection, which was wrong on the cost — but *Facebook structurally will not return the conversation from the one surface where his circle actually is*, and it will not do so on privacy grounds he would endorse.

### ⭐ The finding

**The platforms that will let him wire this up are exactly the ones that don't own the conversation.** Facebook and LinkedIn take the words and keep the responses; Mastodon and Bluesky give them back. *"Don't be wired up the way the Agora wants"* is not a posture to maintain against the infrastructure — **it is a description of which infrastructure will cooperate.**

## Sequencing

*Revised 2026-09-10 after ⛔ #3 closed Facebook-first and the review-cycle objection was found to be wrong.*

1. ✅ **OG / Twitter cards / canonical / JSON-LD on the toys.** Blocked everything else — ADR-0001's known gap. **Done 2026-09-10** (`7424542`): generated from a per-toy manifest by `tools/share.py`, with a `verify` mode that fails on drift.
2. ⭐ **Native comments on roofbeam.net — the circle instrument's real home.** *Revised 2026-09-10 (see the correction above): the circle cannot be instrumented on Facebook at all.* It can be instrumented here. On his own site the moment of agreement **exists**, so `Consent.text_shown` is satisfiable and ⛔ #1 does not block native comments; he owns the corpus (ADR-0001 §3); and `Person.relation = circle` can be set truthfully. No platform can withhold it.
3. **Facebook = distribution only, by hand.** He posts the link to his own profile himself. No API, no Page, no token, no ToS exposure — and the conversation is invited home by the link, which is what POSSE has always meant. The response half happens at (2), not on Facebook.
4. Three model additions + a post object with a canonical URL.
5. **Bluesky + Mastodon** — the only platforms that give the conversation back, so they remain the route to a *wired* loop and to the **world** instrument. A public Roofbeam Page (`tools/posse/facebook.py`, already built) is an option here too, on the same footing: a world surface, not a circle one.
6. Threads + Instagram — same Meta auth as (2).
7. LinkedIn — post-out only. X — only if there is a reason to pay.

### ⛔ #3 — DECIDED 2026-09-10: **Facebook first.** Jeremy's call, and the objection to it was partly wrong.

The recommendation above said Facebook needs *"an app review cycle"* and that *"the loop cannot be proven there."* **Verified against Meta's live docs 2026-09-10: that is incorrect**, and the correction removes most of the cost that made Bluesky-first look obvious.

| claim as written | verified 2026-09-10 |
|---|---|
| needs an app review cycle | ❌ **No.** *"If your app will only be used by app users who have a role on the app itself, App Review is not required."* An app in **Development mode**, used only by Jeremy, needs none. |
| (implied) needs Business Verification | ❌ **No.** Business Verification is triggered *by* App Review / Advanced Access. No review → no verification → **no EIN.** Facebook POSSE does not touch the entity gate chain. |
| the loop cannot be proven there | ❌ **It can.** Publishing to a Page you administer and polling `GET /{post-id}/comments` both work in Development mode. The full round trip is provable. |
| needs a Page; the personal profile cannot be wired | ✅ **Correct, and unavoidable.** This is the one real cost and it remains. |
| real-time webhooks | ✅ **Correct** — those *do* need Advanced Access → App Review → Business Verification. **So we skip them and poll.** This ADR sets a cadence measured in weeks; polling is the right instrument at that cadence, not a compromise. |

**What survives of the original recommendation:** Bluesky is still cheaper per unit of first light, and Mastodon/Bluesky still give the conversation back in a way Facebook's terms do not. Those remain reasons to add them. They are no longer reasons to *sequence them first*, because the gap is now a Page and an app rather than a review cycle — and *"that's where the people I know actually are"* is decisive once the cost argument collapses. **The circle is the falsifiable-prediction instrument (§2), and the circle is on Facebook.**

Graph API **v25.0**. Implementation: `tools/posse/facebook.py`. Setup steps that need Jeremy's hands: Builder Vault `Efforts/Roofbeam/Jeremy Errand Sheet.md` § 6.

## ⛔ Blocking — Jeremy's to close before anything ingests

1. **Consent posture for imported comments.** Pulling someone's Facebook comment into a private corpus is a **privacy act, not a data sync** — they addressed that platform's audience. `Consent.text_shown` cannot be satisfied; there was no moment of agreement. *Candidate, and it is what he already asked for: imported comments are Jeremy-readable only, never republished with attribution, anonymization mandatory rather than optional.*
2. **What JENI is allowed to optimise.** "When to post" is scheduling; "what to post next" is editorial, and the second is where the governing rule can quietly lose.
3. ~~**Sequence** — Bluesky-first (recommended) or Facebook-first (his stated preference).~~ **CLOSED 2026-09-10: Facebook first.** See § Sequencing — the review-cycle objection was factually wrong and has been corrected there.

## Consequences

- Response stops being a signal to chase and becomes two separate instruments with different valid operations.
- Nothing in the system can report a number that goes up when more people react.
- **This is also the Leisure toy model** (`Builder Vault/Efforts/Leisure/Touchstone.md`, open since 2026-09-02): "comments aggregated into a response question" is a response primitive that is neither a like nor an essay — the middle of the feedback scale, running on real traffic. **Do not build it twice.**
- The Agora cast maps directly: Jeremy is the hero, responders are foils who are never placed on a stage, JENI is the mediator. It is an Agora instance in everything but registration.
