## ADDED Requirements

### Requirement: Card clips overflow content
The `Card` component SHALL clip content that exceeds its boundaries, so that child elements with horizontal scroll containers (e.g., `overflow-x-auto`) display a scrollbar instead of visually overflowing.

#### Scenario: Wide table inside Card scrolls horizontally
- **WHEN** a `Table` with `whitespace-nowrap` cells is rendered inside a `Card` and the table content is wider than the card
- **THEN** the table container displays a horizontal scrollbar and the content does not overflow past the card boundary

#### Scenario: Card with normal content renders unchanged
- **WHEN** a `Card` contains content that fits within its width
- **THEN** the card renders normally with no visible scrollbar or clipping effect
