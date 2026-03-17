# M001: THB Marketplace Expansion

**Vision:** Multi-marketplace currency support for the AHA SICU evaluation system.

## Success Criteria


## Slices

- [x] **S01: Data Model Foundation** `risk:medium` `depends:[]`
  > After this: Create the marketplace constants module and the Alembic migration that adds the marketplace column to scoring_rules, evaluation_inputs, and evaluations tables, seeds THB rules, and updates constraints.
- [ ] **S02: Scoring Engine Marketplace Awareness** `risk:medium` `depends:[S01]`
  > After this: unit tests prove Scoring Engine Marketplace Awareness works
- [ ] **S03: CSV THB Parsing** `risk:medium` `depends:[S01]`
  > After this: unit tests prove CSV THB Parsing works
- [ ] **S04: Frontend Currency and Marketplace UI** `risk:medium` `depends:[S02]`
  > After this: unit tests prove Frontend Currency and Marketplace UI works
