import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScoreOverview } from './ScoreOverview';

/**
 * BDD Scenarios:
 *
 * Feature: Partner Dashboard Score
 *
 *   Scenario: Score shows ✔️/❌ ratio instead of weighted score
 *     Given a brand with 3 ✔️ and 1 ❌ verdicts across categories
 *     When the partner views the Score Overview
 *     Then the score shows "75 /100" (ratio-based)
 *     And "✔️ 3" and "❌ 1" counts are displayed
 *
 *   Scenario: Neutral verdicts are excluded from count
 *     Given a metric with verdict "-"
 *     When counting ✔️/❌
 *     Then that metric is not counted in either total
 *
 *   Scenario: Verdict always shows "Performa dapat Ditingkatkan"
 *     Given any evaluation verdict
 *     When viewing the dashboard
 *     Then the badge shows "Performa dapat Ditingkatkan"
 */

const makeRow = (metric: string, verdict: string) => ({
    metric,
    value: 100,
    benchmark: '-',
    verdict,
    message: '',
    score: 10,
});

const scoreBreakdown = [
    {
        category: 'Operasional',
        score: 20,
        max_score: 30,
        rows: [
            makeRow('Tingkat Pesanan', '✔️'),
            makeRow('Tingkat Keterlambatan', '❌'),
            makeRow('Masa Pengemasan', '✔️'),
            makeRow('Persentase Chat', '✔️'),
            makeRow('Keseluruhan Penilaian', '-'), // neutral — excluded
        ],
    },
];

describe('ScoreOverview – Partner Score', () => {
    it('shows ✔️/❌ ratio score instead of weighted score', () => {
        // Arrange — 3 ✔️, 1 ❌, 1 neutral → ratio = 3/4 = 75
        render(
            <ScoreOverview
                score={20}
                verdict="✔️"
                template="fashion"
                scoreBreakdown={scoreBreakdown}
            />
        );

        // Assert — partner score (75) not weighted score (20)
        expect(screen.getAllByText('75').length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText('20')).not.toBeInTheDocument();
    });

    it('displays ✔️/❌ counts', () => {
        render(
            <ScoreOverview
                score={20}
                verdict="✔️"
                template="fashion"
                scoreBreakdown={scoreBreakdown}
            />
        );

        // Assert — shows check and x counts
        expect(screen.getByText('3')).toBeInTheDocument();
        expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('always shows "Performa dapat Ditingkatkan" as verdict', () => {
        render(
            <ScoreOverview
                score={20}
                verdict="✔️"
                template="fashion"
                scoreBreakdown={scoreBreakdown}
            />
        );

        // Assert — partner label, not "Approved"/"Rejected"
        expect(screen.getByText('Performa dapat Ditingkatkan')).toBeInTheDocument();
    });

    it('excludes neutral verdicts from count', () => {
        // Arrange — all neutral
        const allNeutral = [{
            category: 'Test',
            score: 0,
            max_score: 10,
            rows: [
                makeRow('Metric A', '-'),
                makeRow('Metric B', '-'),
            ],
        }];

        render(
            <ScoreOverview
                score={0}
                verdict="❌"
                template="fashion"
                scoreBreakdown={allNeutral}
            />
        );

        // Assert — score should be 0 when no ✔️ or ❌
        expect(screen.getAllByText('0').length).toBeGreaterThanOrEqual(1);
    });
});
