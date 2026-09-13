# Tree of Human Thought — Authored Augmentation: Sources & Method

Generated 2026-09-13. Companion to `build/augment.json`.

## What this is
An authored, cited augmentation branch that fills the ancient / non-Western / religious
gaps in the Wikidata-P737 spine (`tree_spine.json`) and — most importantly — supplies the
**cross-tradition transmission edges** that P737 almost entirely lacks. It is meant to be
shown two-toned against the documented spine.

- **94 new nodes** (figures/traditions genuinely absent from the spine).
- **288 edges**, each individually sourced.
- Confidence mix: **116 documented · 147 consensus · 24 contested · 1 inferred-oral**.
- **232 of 288 edges touch a spine node**, and **143 run wholly between two existing spine
  nodes** — i.e. they are pure connective tissue re-uniting fragments the spine already had
  but left unlinked (e.g. Aquinas–Avicenna, Zhu Xi–Mencius, Schopenhauer–Buddhism).

## Method
1. **Read the spine first.** Discovered most world-historical figures were already present as
   nodes but were disconnected; the spine's poverty is in *edges*, not names. So the payload is
   edges, freely referencing real spine Q-ids so the data merges.
2. **Every Q-id resolved deterministically**, never from memory. Memorized Q-ids proved
   unreliable (e.g. Q9319 is Tintoretto, not Mozi; Q131018 is Rabelais, not Thoreau). Resolution
   used the Wikidata `wbsearchentities` API and, for disambiguation, Wikipedia `pageprops
   wikibase_item`. Emperor/philosopher-type collisions were checked explicitly (e.g. the
   Ethiopian philosopher **Zera Yacob = Q2896591**, NOT the emperor Zara Yaqob = Q147677).
3. **Load-bearing cross-tradition claims were fetched and verified**, not asserted. The
   Greek→Islamic→Latin chain, Schopenhauer↔India, Emerson↔Asia, Zhu Xi's lineage, Nagarjuna's
   sources, Maimonides, Shankara, Averroes, and Leibniz↔China were each read from the primary
   reference article before the edge was written; quoted phrases are reflected in edge `note`s.
4. **Confidence is honest.** `documented` only where a fetched source explicitly states the
   influence; `consensus` for textbook lineage facts cited to a standard reference entry;
   `contested` for real but debated links (flagged, not hidden); `inferred-oral` for the single
   pre-literate membership edge. Nothing was invented to hit a count.

## Primary sources fetched & verified (the load-bearing edges)
- **SEP, "Influence of Arabic and Islamic Philosophy on the Latin West"** — Avicenna→Aquinas
  ("God as the necessary being"), Avicenna→Albertus Magnus & Duns Scotus, Averroes→Aquinas,
  al-Farabi→Latin West via Gundissalinus, al-Ghazali's reworking of Avicenna, the Proclus→Liber
  de Causis transmission.
- **SEP, "Ibn Rushd [Averroes]"** — Averroes as "the Commentator" on Aristotle; critical
  engagement with al-Farabi & Avicenna; reply to al-Ghazali; adoption in Latin & Jewish thought.
- **SEP, "Maimonides"** — Aristotle / al-Farabi / Avicenna → Maimonides → Aquinas, Spinoza.
- **SEP, "Arthur Schopenhauer"** — Upanishads (read from 1814) and Buddhism → Schopenhauer;
  Schopenhauer → Nietzsche.
- **SEP, "Ralph Waldo Emerson"** — Emerson read "avidly in Indian, especially Hindu, philosophy,
  and in Confucianism"; Plato/Neoplatonism and Kant (via Coleridge) → Emerson → Thoreau.
- **SEP, "Zhu Xi"** — Confucius, Mencius, Zhou Dunyi, the Cheng brothers, Zhang Zai, Shao Yong →
  Zhu Xi; the Cheng-Zhu synthesis and its canonization in the examination system.
- **SEP, "Nagarjuna"** — the Buddha, the Abhidharma (as critical target), and the Prajnaparamita
  literature → Nagarjuna → Madhyamaka / Tibetan Prasangika.
- **SEP, "Sankara"** — Upanishads, Badarayana's Brahma Sutras, and Gaudapada (via Govinda) →
  Shankara; Ramanuja and Madhva as opponents.
- **E. S. Nelson, "Leibniz and China"** + Leibniz, *Discourse on the Natural Theology of the
  Chinese* (1716) — Leibniz's engagement with *Confucius Sinarum Philosophus* (1687) and Zhu Xi's
  li/qi, via the Jesuit conduit (Ricci/Longobardi). Marked consensus/contested per the debate.
- **Erman (1924); Lichtheim, *Ancient Egyptian Literature* II** — the Instruction of Amenemope
  and Proverbs 22:17–24:34: dependence widely held, its exact nature debated (so: consensus + note).

## Standing reference works cited at `consensus`
Stanford Encyclopedia of Philosophy (plato.stanford.edu), the Internet Encyclopedia of
Philosophy (iep.utm.edu), and Encyclopædia Britannica per-figure articles — used for
textbook-consensus internal lineages (Milesian succession, Stoic scholarchs, the Neoplatonic
diadoche, Confucius→Mencius→Xunzi, the Chan/Zen and Kagyu transmissions, the Vishishtadvaita
lineage, etc.). These are named per-edge in the `source` field.

## Cross-tradition edges I am most confident in (the crown jewels)
1. **Aristotle → al-Farabi → Avicenna → Averroes → Aquinas / Albertus / Duns Scotus** — the
   Greek→Islamic→Latin arc, every link `documented` from the SEP transmission article.
2. **Aristotle / al-Farabi / Avicenna → Maimonides → Aquinas & Spinoza** — the Jewish bridge,
   `documented`.
3. **Upanishads + Buddhism → Schopenhauer → Nietzsche**, and **Schopenhauer → Deussen (who
   translated the Upanishads)** — `documented`.
4. **Upanishads/Vedanta + Confucianism → Emerson → Thoreau / Whitman** (American
   Transcendentalism) — `documented`/`consensus`.
5. **Confucius & Zhu Xi → (Jesuit conduit: Ricci) → Leibniz → Christian Wolff → Anton Wilhelm
   Amo** — an East-Asia-to-Enlightenment-to-Africa chain.
6. **Nagarjuna → (Aryadeva, Chandrakirti) → Atisa → Tsongkhapa** and **Zhiyi → Saicho**,
   **Bodhidharma → Huineng**, **Shandao → Honen → Shinran** — the Buddhist inter-regional web.
7. **Instruction of Amenemope → Book of Proverbs** — Egyptian wisdom into the Hebrew canon.

## Coverage: well-covered vs thin
**Well-covered:** Greek/Hellenistic internal succession; the full Greek→Islamic→Latin→Jewish
scholastic web; Chinese Confucian and Neo-Confucian lineage (incl. Cheng-Zhu and Lu-Wang);
Indian Buddhist Madhyamaka/Yogacara/pramana and its East-Asian and Tibetan transmission; Hindu
Vedanta (Advaita/Vishishtadvaita/Dvaita) and the six darshanas' founders; Sufi and kalam
lineages; the India→German/American reception; Kyoto School.

**Thin / deliberately light:**
- **Ibn Khaldun → modern sociology.** Popularly asserted, but there is *no documented
  reading-transmission* to Comte/Durkheim/Weber (they did not read him); I therefore represent
  Ibn Khaldun's own ancestry (Aristotle, Averroes) and refused to fabricate a forward edge. This
  is the single biggest "expected but unsourceable" gap.
- **Zoroaster → Second Temple Judaism.** Real scholarly hypothesis (apocalyptic, dualism,
  eschatology) but genuinely contested and lacking a person-to-person transmission node; I
  encoded only the solid **Mani → Zoroaster** syncretism instead.
- **Akhenaten → biblical monotheism.** Freud's thesis; fringe/contested — left as an
  unconnected node, no edge.
- **Hebrew prophetic internal lineage.** Text-dependence among the prophets is largely
  inferred; I included only the better-attested scholarly links (Jeremiah←Hosea, etc.) at
  `consensus` and rooted the cluster in Elijah, rather than manufacturing a chain.

## Pre-literate / oral traditions (the penumbra)
Per instruction, genuinely oral cosmologies are represented as **isolated tradition-root nodes
with NO fabricated influenced-by edges**:
- `aug:andean-cosmology` (Inca/Quechua), `aug:native-na-cosmology`, `aug:aboriginal-dreaming`.
The one oral edge is `Nezahualcoyotl → aug:tlamatinime` (`inferred-oral`): a documented Nahua
poet-philosopher placed within the sage tradition he belonged to (verses survive via
post-conquest transcription; cf. León-Portilla, *Aztec Thought and Culture*).

## Honest caveats
- Birth years for legendary/undated figures (Kapila, Vyasa-adjacent, the Duke of Zhou, prophets,
  the aug: text-roots) are approximate placement markers, flagged in node `note`s.
- `aug:` text/tradition nodes (Vedas, Upanishads, Proverbs, Sramana movement, Charvaka) are not
  persons; they anchor lineages whose true origin is a corpus, not an individual.
- A directed pair appears at most once (edges deduped, strongest occurrence kept). Where a spine
  node stores its own Q-id as its label (a spine quirk, e.g. Nietzsche Q9358, Kant Q9312), the
  Q-id was independently verified correct via Wikipedia `wikibase_item`.
