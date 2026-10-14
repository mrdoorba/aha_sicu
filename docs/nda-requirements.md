# NDA — requirements not yet built

Source: Marwah K. and Alfiano, team thread, 14 Oct 2026. Recorded now because the
signing work is parked until DocuSign PowerForms lands (see below); this is the
list to work from when it does.

Status key: **OPEN** = not built · **DONE** = shipped · **BLOCKED** = needs someone else first.

---

## 1. Follow the approved NDA format — OPEN

The document must follow *"Non Disclose Agreement - PT. Ragam Jasa Indah"*
(Google Doc, owned by Marwah Khairunnisa).

The clause text currently rendered in the wizard is a stand-in written to have
something on screen. It has **not** been checked against that document and should
not be treated as approved copy. Before anything is signed for real, the clauses
need to be replaced with the approved wording.

> Needed: a copy of that doc, or export access to it.

## 2. First-party signatory is Pak Andre — PARTLY DONE

`AHA_SIGNER` in `frontend/src/mocks/nda.ts` now names Pak Andre rather than
Partnership.

> Needed: his **full legal name and title** as they should appear on the document.
> "Pak Andre" is how he was referred to in chat, not a signature block.

Asked around on 14 Oct and came back **unconfirmed**. The aha-coms session found an
"Andre Arlis Chouwanto" (andre.chouwanto@ahacommerce.net) in COMS staff data, and
noted Partnership's onboarding checklist adds an "ANDRE" as admin to every partner
WA group — but explicitly could not confirm either is the NDA signatory, and said
not to take it from them. The MP App session has no record of him at all.

**Deliberately not written into the code.** `AHA_SIGNER` still reads "Pak Andre"
with a placeholder title. Get the name and jabatan from Marwah or Alfiano directly;
a guessed name on a signed legal document is worse than an obvious placeholder.

Note that signing and verifying are deliberately different people: Pak Andre signs
as Pihak Pertama, Marwah verifies manually uploaded scans. Don't collapse them.

## 3. Required fields must block signing — DONE

Every company field is marked `*` and an empty one blocks the CTA on **both** the
digital and the paper route. A printed NDA with a blank party is no better than a
digital one.

Fields: bentuk badan usaha, nama perusahaan/brand, nama penanggung jawab, jabatan
PIC, alamat perusahaan.

## 4. AHA logo or letterhead — DONE (with a caveat)

> "Make sure untuk NDA ada logo AHA juga ya. Atau setidaknya kop surat AHA, supaya
> resmi."

The document now opens with a kop surat: the real colour mark, the company name,
and the creation date. The asset is `frontend/public/aha-logo.png`, copied from
aha-coms `apps/coms/public/aha-logo.png` (1080×1080). At the ~3–4 cm it occupies on
a printed page that is roughly 700–900 dpi, so it prints cleanly.

**Caveat, from the aha-coms session (14 Oct): there is no vector of the AHA mark
anywhere in that repo.** No SVG, AI or PDF. Two consequences:

- a full-width A4 letterhead strip is not possible at print quality from what we
  have. `apps/hrd/assets/brand/aha-letterhead.png` exists but is only 600×121.
- `apps/nest/public/aha-logo-vertical-white.png` is 4500×4500 but is the WHITE
  lockup — usable on a dark band, not on white paper.

> Needed, if the NDA ever wants a full-width printed letterhead: the vector from
> brand/creative. The current mark is sufficient for the signature-page use.

## 5. Creation date and document metadata — PARTLY DONE

> "Di dalam NDA juga perlu cek tanggal pembuatan dan lain2nya."

The creation date now sits in the letterhead. It is computed at render time in the
preview; the real flow must **stamp it when the NDA is generated** and store it,
not recompute it — a date that moves every time the document is opened is worse
than no date.

"Dan lain-lainnya" is still unspecified. Don't guess: document number, place of
signing and meterai position are all plausible, and item 1's approved template will
settle them. Ask Marwah alongside the template.

## 6. Signing mechanism: DocuSign PowerForms — BLOCKED (deliberate)

Alfiano, 14 Oct: DocuSign **PowerForms**, link-based — no emailed envelope and no
per-recipient send step. The team or the partner opens a URL and lands on the
signing page.

Explicitly deferred ("will come later"). Until then the wizard keeps its generated
signature plus the print/sign/scan/upload paper route.

Partnership decided on 2 Oct to drop e-sign providers for the PKS. The NDA is a
**deliberate exception** and Alfiano is aware — this is not a conflict to re-raise.

Open before it can be built:
- does AHA already hold a DocuSign account/plan, and who owns it?
- expected envelope volume per month (PowerForms is priced per envelope, and a
  template is needed per NDA version)

## 7. Where the signed document lives — OPEN

Not built, and a Phase D decision. Current plan, not yet agreed with Partnership:

- the signed artefact (PowerForm result **or** uploaded scan) lands in GCS under
  the brand's own prefix
- a Postgres row carries `pending_review → approved | rejected`, who approved it,
  and when
- manual uploads are verified by **Partnership**, not BD — BD issued the voucher,
  so having them also approve the NDA removes the only second pair of eyes

---

## Adjacent, same thread

**Analysis output format — OPEN.** Marwah: the SICU result should follow the format
used in the email from @Handers. The result page is currently built from our own
shape, not that email's.

Handers is an AHA staff member — likely `handers.the@ahacommerce.net`, named by the
aha-coms session as COMS's owner/bootstrap admin, and by the MP App session as the
person who signed off MP's COMS integration in June. Neither session knows which
email Marwah means or what format it carries, and neither ties Handers to SICU.

> Needed: ask Marwah to forward the actual email, or a sample of the format. Do not
> reshape the result page on a guess about which email this is.
