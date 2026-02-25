## Context

The scoring system's G72/G73 cells implement the marketing budget recommendation. In the original Google Sheets formula:

- **G72** is a boolean: `capped_value > CEILING(G68_first_number / 100, 0.01)`
- **G73** branches on G72:
  - `TRUE` → display the capped value (hard-capped at 20% non-fashion, 25% fashion)
  - `FALSE` → display `CEILING(G68_first_number / 100, 0.01)` (can exceed 20%)

The Python `_compute_g72` currently returns a float (the capped value only), ignoring the boolean comparison and the fallback branch. `_compute_g73` receives this float and formats it. The FALSE branch — where the G68 competitor data drives the result — is never executed.

### G68 Format

`_compute_g68` produces strings like `"15.3% ~ 22.7%"`. The spreadsheet extracts values differently on each side of the G72 comparison:

| Side | Spreadsheet extraction | Result for "15.3% ~ 22.7%" |
|------|------------------------|---------------------------|
| LEFT (capped) | `VALUE(LEFT(G68, FIND("~",G68)-1))` | 0.153 |
| RIGHT (ceiling) | `CEILING(REGEXEXTRACT(G68, number)/100, 0.01)` | 0.16 |

The LEFT side uses the raw percentage (0.153) in its MIN chain. The RIGHT side uses `CEILING(..., 0.01)` which rounds up to nearest 1% (0.16).

## Goals / Non-Goals

**Goals:**
- Match the spreadsheet's G72 boolean comparison + G73 branching logic exactly
- Allow non-fashion stores to receive marketing recommendations above 20% when G68 data supports it
- Maintain the existing function signatures and call pattern (g72 returns float → g73 formats it)

**Non-Goals:**
- Changing the G68 computation itself
- Changing the capped formula's internal logic (MIN/MAX chain)
- Adding new configurable rules parameters
- Changing the display range clamp (10%-25%) in G73

## Decisions

### Keep `_compute_g72` returning a float (not a boolean)

**Rationale**: In the spreadsheet, G72 is boolean and G73 does branching. But in our code, `_compute_g72`'s result is only consumed by `_compute_g73`. Rather than splitting into boolean + two values, it's cleaner to have `_compute_g72` internally handle the comparison and return the correct marketing percentage directly. The call site (`g72 = _compute_g72(...)`, `g73 = _compute_g73(verdict, g72, ...)`) stays unchanged.

**Alternative considered**: Return a tuple `(bool, capped, ceiling_g68)` — rejected because it changes the call interface and leaks spreadsheet implementation details into the API.

### Two distinct G68 parsing methods inside `_compute_g72`

The function needs to extract the G68 first percentage twice, using different methods:

1. **For the MIN chain (LEFT side)**: Parse `VALUE(LEFT(g68, indexOf("~")-1))` → raw fraction (e.g., 0.153)
2. **For the ceiling fallback (RIGHT side)**: Parse first number, divide by 100, `CEILING` to 0.01 (e.g., 0.16)

Currently the code only has one extraction (`math.ceil(float(...))/100`), which corresponds to the RIGHT side. We need to add the LEFT side extraction.

## Risks / Trade-offs

- **Behavioral change for existing evaluations**: Non-fashion stores that previously showed 20% may now show higher percentages (up to 25%). This is the intended fix — the previous behavior was a bug.
- **G68 parsing edge cases**: If G68 text doesn't contain "~" (e.g., empty or malformed), the LEFT side parse falls back to 0.0, making the comparison `0 > ceiling_g68` always FALSE, which means the ceiling_g68 value is used. This matches the spreadsheet's IFERROR behavior.
