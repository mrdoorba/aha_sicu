import type { PreviewAxis } from '../../mocks/onboarding';

const CENTRE = 180;
const RADIUS = 110;
const LABEL_RADIUS = 136;
const RINGS = [0.25, 0.5, 0.75, 1];

/** Axis i sits at -90° + i·(360/n), so axis 0 points up. */
function pointAt(index: number, count: number, distance: number): [number, number] {
  const angle = ((-90 + (360 / count) * index) * Math.PI) / 180;
  return [CENTRE + distance * Math.cos(angle), CENTRE + distance * Math.sin(angle)];
}

function polygon(count: number, distanceFor: (i: number) => number): string {
  return Array.from({ length: count }, (_, i) => pointAt(i, count, distanceFor(i)).join(','))
    .join(' ');
}

interface HealthRadarProps {
  axes: PreviewAxis[];
}

/**
 * Store-health radar: every axis is "higher is better".
 *
 * Deliberately NOT the 100-point SICU score — 30 of those points are awarded
 * when a brand FAILS, so plotting them would shrink the polygon as the store
 * improves. Values here are health, read the same way on every axis.
 */
export const HealthRadar = ({ axes }: HealthRadarProps) => {
  const n = axes.length;
  const description = axes.map((a) => `${a.label} ${a.value}`).join(', ');

  return (
    <svg
      viewBox="-40 -20 440 400"
      className="h-auto w-full"
      role="img"
      aria-label={`Radar kesehatan toko: ${description}, dari 100`}
    >
      {RINGS.map((ratio) => (
        <polygon
          key={ratio}
          points={polygon(n, () => RADIUS * ratio)}
          fill="none"
          stroke="var(--border)"
          strokeWidth={ratio === 1 ? 1.5 : 1}
        />
      ))}

      <g stroke="var(--border)" strokeWidth="1">
        {axes.map((axis, i) => {
          const [x, y] = pointAt(i, n, RADIUS);
          return <line key={axis.label} x1={CENTRE} y1={CENTRE} x2={x} y2={y} />;
        })}
      </g>

      <polygon
        points={polygon(n, (i) => RADIUS * (axes[i].value / 100))}
        fill="var(--primary)"
        fillOpacity="0.16"
        stroke="var(--primary)"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />

      <g fontSize="14" fontWeight="700" fill="var(--foreground)">
        {axes.map((axis, i) => {
          const [x, y] = pointAt(i, n, LABEL_RADIUS);
          // Nudge labels off the spoke so they never sit on the ring.
          const anchor = x > CENTRE + 4 ? 'start' : x < CENTRE - 4 ? 'end' : 'middle';
          return (
            <text key={axis.label} x={x} y={y + 5} textAnchor={anchor}>
              {axis.label}
            </text>
          );
        })}
      </g>
    </svg>
  );
};
