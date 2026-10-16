# NDA — requirements

**Superseded on 15 Oct 2026.** Alfiano decided the NDA is generated **outside this
app**: the page shows the template and collects company details, and when the brand
agrees a button emails the internal team, who send the DocuSign NDA out of band.

Nothing is signed in the app. The in-app signature, the print/sign/scan/upload paper
route and the internal counter-signature queue were all removed with that decision —
they only existed to sign here.

What survives from Marwah's 14 Oct list:

- **Required fields block the request.** Every company field is marked `*` and an empty
  one keeps the button disabled. Those fields are what the team generates the NDA from,
  so a blank is a document that names nobody.
- **AHA letterhead and creation date** on the displayed template. Done. The mark is the
  real 1080×1080 asset from aha-coms; there is **no vector of it anywhere** in that
  repo, so a full-width printed A4 letterhead would need brand/creative. Not needed
  while the document is DocuSign's to render.

What was dropped, and should not be picked back up without a new decision:

- **The Ragam Jasa Indah template.** We no longer render clause text that anyone signs,
  so matching the approved format is DocuSign's problem, not the app's. Stop chasing
  the doc; the sibling Amalurra doc that aha-coms offered is likewise not needed.
- **Pak Andre's full legal name and title.** Nothing we render carries a signature
  block. Don't chase Marwah for it.
- **PowerForms mechanics** (account owner, envelope volume, per-NDA templates). Still
  real questions, but they belong to whoever owns DocuSign, not to this app.

Still open, and still ours:

- **Where the signed NDA lives.** Phase D. The executed document comes back from
  DocuSign; we need to decide whether SICU stores a copy, links to it, or merely
  records that it exists. Nothing is built.
- **Who the "email the internal team" button actually notifies**, and what that email
  contains. Right now the preview only changes state on screen.

## Adjacent, same thread

**Analysis output format — CLOSED.** Marwah asked that the SICU result follow the
format of "the @Handers email". Alfiano sent the actual SICU evaluation email on
15 Oct and the results page was rebuilt from it directly, so the question is answered
whether or not that was the email she meant. Worth one confirmation from her; not
blocking.
