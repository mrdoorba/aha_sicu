# Onboarding wizard — the patterns, and why they exist

Written for AHAbot (and anyone else) building a partner onboarding flow. AHAbot's
flow is a different one; this is not a spec to copy, it is the set of decisions
that made SICU's flow work, each with the failure it prevents. Take the ones that
apply.

Live reference: `aha-coms-sicu-dev.web.app/preview`. Code: `frontend/src/pages/onboarding/`
and `frontend/src/components/onboarding/`.

---

## 1. One decision per screen

Six screens, each asking exactly one thing:

```
(logged out)  Claim voucher      → is this code real, and whose brand is it?
1  Biaya      Discount           → what does this cost me?
2  NDA        Sign               → am I protected?
3  Tutorial   Create sub-account → what do I have to go do?
4  Sub akun   Confirm            → did you do it, and with which credentials?
5  Proses     Waiting            → is anything happening?
6  Hasil      Result             → what did I get?
```

A screen that asks two things gets one of them answered badly. The test: name the
screen's question in one sentence. If you need "and", split it.

**Order matters more than content.** The cost screen is first because an unanswered
"what will this cost me?" sits in the partner's head through every later step. The
NDA is second because the tutorial asks them to hand over account access, and
nobody should be asked for access before they are told how it is protected.

## 2. Lock the CTA until the screen's question is actually answered

Every screen's primary button is disabled until that screen's one decision is made:

- voucher page — until the code resolves to a real, unclaimed, unexpired voucher
- sub-account — until one of the two radios is picked
- NDA paper route — until a signed scan is attached

```tsx
<Link
  aria-disabled={!canContinue}
  tabIndex={canContinue ? undefined : -1}
  className={cn('block h-13 rounded-full text-center …',
    canContinue
      ? 'bg-primary text-primary-foreground hover:bg-primary-dark'
      : 'pointer-events-none bg-muted text-muted-foreground')}
>
```

`pointer-events-none` **and** `tabIndex={-1}` **and** `aria-disabled` — the first
stops the click, the second stops tab-and-enter reaching it, the third tells a
screen reader. Only doing the first leaves the button fully usable by keyboard.

And always say *why* it is locked, next to the button. A greyed button with no
explanation is the single most common dead end in a wizard.

## 3. Never preselect the answer you want to hear

The sub-account screen asks: did you use the credentials we gave you, or your own?
It starts with **neither** selected.

An earlier version had "Sudah, saya pakai email yang diberikan" pre-ticked. That is
the answer most people leave untouched, so it would have collected a lot of yeses
from partners who had done no such thing — each one costing the team a failed login
and a day of back-and-forth. A default is only safe when being wrong is cheap.

The same screen uses **radios, not checkboxes**, because the two answers are
mutually exclusive. The old checkbox-plus-collapsible let someone tick "sudah" and
also fill in different credentials, which is a state nobody downstream can act on.
If two options cannot both be true, the control must make that impossible.

## 4. Every dead end needs an exit

A partner who cannot proceed will not email you. They will close the tab.

The voucher page has six states, and the five non-valid ones each say what to **do**,
not just what went wrong:

| state | what it says |
|---|---|
| empty | 12 characters, your BD team sends it on WhatsApp |
| typing | "8 characters to go" — never called invalid mid-type |
| unknown | check the spelling, or ask BD to resend |
| expired | expired on *date* — BD can issue a new one **at no cost** |
| already claimed | sign in instead; you don't need another voucher |
| valid | brand auto-fills, the account fields appear, button unlocks |

Plus a standing "Belum punya voucher?" panel with a WhatsApp link, because a brand
cannot issue itself a voucher — without that the page is a wall.

Two details worth stealing:

- **`typing` is a separate state from `unknown`.** Shouting "code not found" at
  someone four characters in is wrong. Nothing is judged until the input is complete.
- **The page starts empty.** Our first version prefilled a valid code, which meant
  the state most visitors actually meet was the one state we never looked at.

## 5. Show the clock as a thing that shrinks

"7 days left" as text is read once and forgotten. A bar that visibly shrinks is read
every time the page loads.

`components/onboarding/DeadlineMeter.tsx` + the maths in `deadline.ts`:

- width = `remaining / total`, so the bar empties as the deadline approaches
- colour escalates **calm → soon → critical** at 3 days and 1 day left
- an expired deadline keeps a **3% sliver** — a 0%-wide bar reads as broken, not as
  out of time
- `clamped = max(0, min(remaining, total))` — a negative remaining is an expired
  voucher, not a negative-width bar

**Put the maths in a pure function, not the component.** An off-by-one in a width
calculation is invisible in a screenshot and wrong on day 7. Ours has 6 tests.

**Give yourself a way to see the other frames.** A fresh preview always sits at a
full 7/7 — exactly the frame that demonstrates nothing. `?sisa=N` overrides the
remaining count, so a reviewer can see the bar part-spent and the colour escalate
without waiting five days. One gotcha we hit: `?sisa=` with no value parses as
`Number('') === 0`, which silently rendered an expired voucher. Guard the empty string.

## 6. Working days are not days

`lib/workdays.ts`: Mon–Fri, public holidays deliberately **not** observed (confirmed
with Alfiano — adding a holiday calendar means maintaining a holiday calendar).

- `addWorkdays(from, n)` never counts `from` itself
- `workdaysBetween(from, to)` floors at 0, so `0` unambiguously means expired

Derive expiry from the stored timestamp **at read time**. Never store an `expired`
boolean — it is wrong the moment nobody updates it.

## 7. Offer the paper route

Some partners will not sign anything digitally. Until we added it, those partners had
no way through the NDA step at all.

The route is: print → sign over a meterai → scan → upload. Two things make it honest:

- on the paper route the rendered document leaves the signature line **blank**.
  Printing a typed signature the partner never made defeats the point of signing by hand.
- the copy names **who** verifies the upload (Partnership) and **how long** it takes
  (1 working day), and lets them continue to the next step while it is pending.
  "Uploaded ✓" with no human in the sentence implies they are done when they are not.

## 8. Say who the document protects

The NDA screen opens with: **"NDA ini melindungi Anda, bukan kami."** Then what it
binds AHA to, in plain language, above the legal text.

A partner handing over their sales data is making a trust decision, and legalese
alone reads as something to be defended against. The clause text is right there —
the plain-language line is what gets read.

The NDA fills in **live** as the form is typed, side by side. Nobody reads a document
they have to imagine.

## 9. Waiting is a screen, not a spinner

Step 5 is a timeline with four stages — done, running, not started — plus a named
completion estimate and a line saying an email will arrive. It explicitly says
*"tidak ada yang perlu Anda lakukan"*.

A bare spinner makes people refresh, then email, then assume it is broken. Name the
stages, say who is working, say how they will be told.

## 10. Build it with fake data first, and gate it

The whole flow shipped and was reviewed **before any backend existed**:
`mocks/onboarding.ts` holds fixtures shaped like the future API responses, so swapping
them for real calls is a change of source, not a change of screens. Three rounds of
UX feedback cost nothing because there was nothing to migrate.

Gate it properly. `lib/preview.ts`:

```ts
const PREVIEW_HOSTS = new Set([
  'localhost', '127.0.0.1', '[::1]',
  'aha-coms-sicu-dev.web.app', 'aha-coms-sicu-dev.firebaseapp.com',
]);
export function isPreviewEnabled(hostname = window.location.hostname) {
  return PREVIEW_HOSTS.has(hostname.toLowerCase());
}
```

**Exact whole hosts, in a Set.** Our first version tested the prefix
`/^aha-coms-sicu-dev\./`, which also accepts `aha-coms-sicu-dev.attacker.com` — a
domain anyone can register. The test that caught it asserted the lookalike domain
passes; the fix was to the implementation, not the test.

The preview routes also render **outside** the auth provider, so a logged-out
reviewer can walk the flow.

---

## Design rules this flow follows

From aha-coms `DESIGN.md` — ask AHAbot's own repo for the current copy.

- **Two registers.** The authed app is strictly **flat** — no gradients. Logged-out
  surfaces (our claim page) use the AHA Blue Gradient as the page field. Don't mix:
  a gradient inside the authed wizard looks like a different product.
- **Tokens, never raw palette.** `bg-primary`, `text-muted-foreground`, `bg-card`,
  `border-border`. We shipped the step rail on raw `slate`/`blue`/`green`/`orange`
  and had to go back and fix it.
- **Gold is reserved** — primary CTA, success, win. Always with dark ink
  (`text-deep-navy`), never white on gold.
- **Buttons and filter chips are pills** (`rounded-full`, org-wide as of 14 Oct).
  Inputs, cards, callouts and tables keep their normal radius. A full-width row is
  not a button — rounding its ends makes it read as one.
- **Focus the first filter on desktop only** — `useAutoFocusFirstFilter`, never bare
  `autoFocus`. See `CLAUDE.md`.

## Structure

- `OnboardingLayout` owns the step rail + deadline bar and takes `current` (1–6) and
  `showDeadline`. Every step page is just content inside it. Hide the deadline on
  Proses and Hasil — once the work is AHA's, the clock is not the partner's.
- Pure logic lives next to the component but in its own module (`deadline.ts`,
  `workdays.ts`, `lookupVoucher` in `mocks/onboarding.ts`) so the behaviour is
  testable without rendering anything.
- `VoucherStatus` takes the lookup result and renders the message. One component,
  one switch, every state visible in one place — much easier to review than six
  conditionals scattered through the page.

## i18n

`i18next`, flat dotted keys, one file per language: `locales/{id,en,th}.json`, ~985
keys each, all three maintained. If we align with AHAbot, align on **key names** —
the file shape doesn't need to match.

The picker is its own component, not the authed `LanguageToggle`: that one persists
through an authenticated API call, and a brand on the public sign-up page has no
account yet. The choice goes to `localStorage` and is restored on **every** step, not
just the first — someone who picks English on step 1 and reloads on step 4 has
already told us once.

**Reuse the keys the email already has.** The results page prints the SICU email, and
the backend renders that email from these same locale files. So the page stores a key
and its numbers (`scoring.adsROI.pass`, `{ value: '16.3' }`), never a finished
sentence. The brand reads the result in the language the email reached them in, and
nobody keeps two wordings of "Kurang Baik" in step by hand.

Three things stay untranslated, deliberately, each with a visible line saying why:

- **NDA clause text.** Translating a legal document changes what people sign. UI
  chrome in all three languages; the document body stays Indonesian as the binding
  version until Legal supplies reviewed translations.
- **Third-party UI labels.** The Shopee permission names are the strings the brand has
  to find on Shopee's own screen. A translated list sends them hunting for wording
  Shopee never shows.
- **Currency in its own convention.** `Rp 3.000.000` stays Indonesian-formatted in
  every language, because that is how the number is written.

Two cheap tests are worth more than they look: one asserting the three files carry
identical keys and placeholders (a missing key does not throw — i18next prints the key
itself on the brand's screen), and one rendering every key the results page asks for in
all three languages.

## What NOT to copy

- The **6 steps** are SICU's shape, not a template. Yours will differ. The one-question-
  per-screen rule survives; the step list does not.
- The **voucher** exists because BD must control who gets in. If your partners
  self-serve, you don't need it — and don't add a gate just to have one.
- The **sub-account tutorial** is a Shopee Seller Centre constraint.
- `caberawit123!` is a shared password for a temporary sub-account that gets deleted
  after evaluation. It is deliberate here and almost certainly wrong for you.
