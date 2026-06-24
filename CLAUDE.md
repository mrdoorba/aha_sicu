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
