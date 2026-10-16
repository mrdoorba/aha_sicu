# Which brands are eligible for a voucher

A free-SICU voucher is issued when a brand has had its **1st meeting but not yet
its 2nd**. This is how to determine that. Source: the AHA BD session reading
`ahacommerce/aha-bd` at commit `c5aacc3`, 15 Oct 2026. That session was studying
the code, not speaking for the BD product owner — treat it as an accurate reading
of the source, not a contract. Confirm anything load-bearing with BD before Phase A
ships.

## The short version

There is **no field on the brand** that records meeting stage. `bdStage` is
`not_approached | active | rejected | registered` — the lock lifecycle, not meetings.

Meeting stage lives on each document in the `meetings` collection as
`meetingType: 'first' | 'second'` (`src/lib/types.ts:313`).

In the exported sheet **`meetingType` is not a column — it is the tab**. `1st Meeting`
and `2nd Meeting` are two tabs sharing an identical 14-column header
(`functions/src/sheets.js:41-42`). So:

- has a 1st meeting → a row in `1st Meeting` for that brand
- has a 2nd meeting → a row in `2nd Meeting` for that brand
- **"not yet 2nd" = the absence of a row.** No blank, no date, no enum. Absence is
  the only signal.
- join on **Brand ID, column M (index 12)** — not the brand name.

**Consequence for us:** `meeting_raw_data` from the 1st Meeting sheet alone cannot
answer this. We must sync the 2nd Meeting tab too.

## The better condition

The 2nd-meeting option in the BD UI is gated on
`canSecond = !!brand.sicuPassed || isAdminRole(user.role)` (`src/pages/MeetingForm.tsx:117`).

So "between meeting 1 and 2" is very nearly **"1st meeting done AND NOT sicuPassed"** —
and SICU owns the second half already. The brand doc carries `sicuScore`,
`sicuPassed`, `sicuPeriod`, `sicuCheckedAt`, and the `Brands Data` tab exports
`sicuScore` and `sicuPassed` as columns J and K (indices 9 and 10).

That is likely cleaner than re-deriving from two meeting tabs, and it is the
recommended route. It does not remove the need to handle the exception below.

## Three traps

**1. Mis-typed meetings happen, and the dangerous direction is the one that is silent.**

An admin can book a 2nd with no 1st on file (`meetingType` is a plain dropdown and the
`canSecond` gate is bypassed for admins). Whether that has actually occurred is
unknown — answering it needs a query against live Firestore, which nobody has run.

What *has* occurred is the mirror image, and it is recorded in the repo as the reason
`src/lib/firstMeeting.ts` exists: the **1 Oct 2026 Cassion** meeting was booked as
'1st' and again as '2nd', and the **15 Sep KindKain** one as '1st' then '2nd' two
minutes later. Both counted as an extra 1st meeting until someone removed them by
hand. The automatic twin-cleanup never caught them because it only folds duplicates of
the *same* `meetingType` (`functions/src/meetings.js:105`), so a booking duplicated
across types is invisible to it.

For us that means a brand who really only had a 1st meeting can carry a spurious
`second` row — and "1st AND NOT 2nd" would then **silently deny a voucher to a brand
who deserves one**. A false negative: nobody complains, nobody notices. So write the
orphan/mismatch case as a real branch rather than an assertion, and **log every
exclusion** so we can see who we are turning away.

**2. Don't count raw rows.** Two exclusions apply, and only one of them is visible in
the sheet:

- `verified === false` — the Meet attendance check saw under 30 minutes. Excluded from
  every BD KPI. In the sheet this is the **Verified column K (index 10)**, written
  Yes/No/blank. **Blank means not yet checked, which is not the same as No.**

  **Never filter on `verified === true`.** The field is *undefined* for every
  in-person meeting — only `locationType === 'Online'` is ever checked against Meet
  attendance — so a positive filter silently discards every HQ and brand-office
  meeting we have. Exclude `false`, keep everything else.
- `dedupedInto` — a booking twin folded into another record (same brand booked twice).
  Also excluded, and **this field is not exported to the sheet at all**.

So the sheet can over-count 1st meetings and carries no column that lets us correct
it. The canonical rule is `countedFirstMeeting()` in `src/lib/firstMeeting.ts`: skip
any meeting where `meetingType !== 'first'`, `verified === false`, or `dedupedInto` is
set.

**If a duplicate voucher is expensive, read Firestore rather than the sheet.** It is:
a voucher is a free SICU evaluation, and issuing two to the same brand is both a cost
and an embarrassment. Phase A should plan on Firestore, with the sheet as a fallback
we knowingly accept is lossy.

**3. `startAt` is mutable.** It gets rewritten when a brand reschedules the calendar
event; `startAtBooked` keeps the original. Don't treat the meeting date as immutable,
and don't key anything off it.

## The query

Admin SDK, Node. Supplied by the BD session, 15 Oct.

**First: the BD app runs two Firestore databases.** `(default)` is Indonesia, `'thai'`
is Thailand (`functions/src/core.js:9`). A brand exists in exactly one — pick the right
database or find nothing.

```js
// 1. Candidate 1st meetings. No `verified == true` filter — see the trap above.
const firsts = await db.collection('meetings').where('meetingType', '==', 'first').get();

// 2. countedFirstMeeting()'s exclusions, latest per brand.
const now = Date.now();
const byBrand = new Map();
for (const doc of firsts.docs) {
  const m = doc.data();
  if (m.verified === false) continue;   // no-show, or a folded twin
  if (m.dedupedInto) continue;          // folded twin, belt and braces
  const ms = m.startAt?.toMillis?.() ?? 0;
  if (!ms) continue;
  if (ms > now) continue;               // booked, not held — see note
  const prev = byBrand.get(m.brandId);
  if (!prev || ms > prev.ms) byBrand.set(m.brandId, { ms, meetingId: doc.id });
}

// 3. Anyone with ANY 2nd meeting is out.
const seconds = await db.collection('meetings')
  .where('meetingType', '==', 'second').select('brandId').get();
const hasSecond = new Set(seconds.docs.map((d) => d.data().brandId));

// 4. The SICU gate, by document ref — an `in` query caps at 30.
const ids = [...byBrand.keys()].filter((id) => !hasSecond.has(id));
const refs = ids.map((id) => db.collection('brands').doc(id));
const brands = refs.length ? await db.getAll(...refs) : [];

const eligible = brands.filter((snap) => {
  if (!snap.exists) return false;                // meeting points at a deleted brand
  const b = snap.data();
  if (b.sicuPassed === true) return false;       // already past the stage
  if (b.bdStage === 'registered') return false;  // already converted
  return true;
});
```

Decisions this query makes that we should make deliberately, not inherit:

- **`startAt > now` is not in the repo's own helper.** `countedFirstMeeting()` counts a
  meeting that is merely *booked*, because it exists to stop a BD double-booking. A
  voucher almost certainly wants "actually happened", so the future is filtered out
  here. Keep it, but keep it knowingly.
- **`source: 'migration'`** meetings (`meetings.js:819`) are imported history, never
  booked through the app. Decide whether those earn a voucher before going automatic.
- `verified === false` and `dedupedInto` overlap — the dedup writer sets both in one
  update. Checking both is free and matches the canonical helper exactly.

## There is no API

No callable answers "between meeting 1 and 2". The closest is client-side only: the
BD Brands page builds a per-brand `{first, second}` map and renders the 1st ✓ / 2nd ✓
badges (`src/pages/BrandsList.tsx:107`). Same derivation we would write ourselves.

## The `sicuPassed` coupling — read this before changing SICU's verdict

**Dated note, 15 Oct 2026.** Voucher eligibility reads `sicuPassed`, a field SICU
itself writes. If SICU ever changes what `sicuPassed` *means* — the threshold, the
rule, which evaluations set it — then who receives free evaluations moves with it,
with no code change on either side and no error anywhere.

That is not a reason to avoid the coupling; it is the cleanest available condition.
It is a reason to treat a change to `sicuPassed` semantics as a change to voucher
policy, and to say so in the same breath.

## Open with BD

- confirm the `sicuPassed` route is the one they'd want us to use
- has the orphan-2nd case (a 2nd with no 1st) ever actually occurred? Needs a query
  against live Firestore — the BD session has a read-only repo clone and no
  credentials, so this one needs someone with console access.
