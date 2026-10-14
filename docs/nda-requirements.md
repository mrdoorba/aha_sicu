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

Note that signing and verifying are deliberately different people: Pak Andre signs
as Pihak Pertama, Marwah verifies manually uploaded scans. Don't collapse them.

## 3. Required fields must block signing — DONE

Every company field is marked `*` and an empty one blocks the CTA on **both** the
digital and the paper route. A printed NDA with a blank party is no better than a
digital one.

Fields: bentuk badan usaha, nama perusahaan/brand, nama penanggung jawab, jabatan
PIC, alamat perusahaan.

## 4. AHA logo or letterhead — OPEN

> "Make sure untuk NDA ada logo AHA juga ya. Atau setidaknya kop surat AHA, supaya
> resmi."

The rendered document has no mark at all. The real logo asset
(`apps/coms/public/aha-logo.png` in aha-coms) is not in this repo, and `DESIGN.md`
bans redrawing it as an SVG approximation — so this needs the asset copied over,
not a lookalike.

Letterhead is the minimum; the logo is the ask.

## 5. Creation date and document metadata — OPEN

> "Di dalam NDA juga perlu cek tanggal pembuatan dan lain2nya."

The document currently shows no date. At minimum it needs the date it was created
or signed. "Dan lain-lainnya" is unspecified — worth asking Marwah what else the
Ragam Jasa Indah template carries (document number? place of signing? meterai
position?) rather than guessing, since this is exactly the detail the approved
format in item 1 will settle.

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

> Needed: the email, or a sample of the format.
