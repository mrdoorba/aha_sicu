# aha_sicu — agent notes

## Promoting to production

Promotion is **fast-forward only**. Run:

```
bash scripts/promote-production.sh
```

It fast-forwards `production` to the verified `origin/develop` tip and pushes;
the push triggers `deploy.yml` on `production` (backend reuses the already-built
develop image digest via `promote-backend.yml` — it does not rebuild).

**Do NOT promote via a GitHub develop→production PR / "Merge pull request" button.**
That creates a merge commit that lives only on `production`, which (a) breaks the
script's `--ff-only` forever after and (b) can never satisfy a strict
up-to-date rule without merging production back into develop. We hit exactly
this on 2026-06-23 (merge commits from #33/#35/#39/#44) and had to force-realign
`production` to develop's linear tip to escape it.

Branch protection on `production` is deliberately `strict: false` (up-to-date
NOT required) so the ff-push isn't blocked; required status checks
(Backend Tests & Lint, Frontend CI) are still enforced on the promoted commit.
**Do not re-enable the strict / "require branches up to date" rule** — it
reintroduces the contradiction.

## Code architecture

**Changing one thing must not mean touching 2+ files unless it genuinely has to.**
Optimise for the next edit, not just this one.

That is **locality**, and it comes from **deep modules**: a lot of behaviour behind a
small interface, at a clean seam. Use these words as written — module, interface,
depth, seam, adapter, locality — not "component", "service", or "boundary".

- **Module** — anything with an interface and an implementation: a function, a file, a
  package, a slice spanning app + API + db.
- **Interface** — everything a caller must know to use it correctly. Types, but also
  invariants, ordering, error modes, required config, cost.
- **Deep** = small interface, lots of behaviour. **Shallow** = interface nearly as
  complex as the implementation. Fix shallow by hiding more inside, never by adding
  methods.

Four tests, before adding a module, a parameter, or an abstraction:

- **Deletion test** — delete it mentally. Complexity vanishes → it was a pass-through.
  Complexity reappears across N callers → it earns its keep.
- **The interface is the test surface** — wanting to test *past* it means the module is
  the wrong shape.
- **One adapter = hypothetical seam; two = real.** No seam until something varies across
  it. Production + test counts as two; a hypothetical future backend does not.
- **Depth is a property of the interface, not the implementation.** A deep module can be
  built from small internal pieces — they just don't surface at the seam.

In practice:

- Look before you add: a helper that already exists two files over beats a new one.
- Accept dependencies rather than construct them; return results rather than mutate.
- Used by 2+ apps → it belongs in `packages/*`. Used by one → keep it there until a
  second caller actually shows up.
- Deepening a module replaces its tests, it doesn't layer on them. Once tests exist at
  the new interface, the old shallow-module tests are dead weight — delete them.

This is a tiebreaker for where code goes, not a licence to refactor on sight. A one-line
fix stays a one-line fix.
