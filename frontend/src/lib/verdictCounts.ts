/**
 * Compute ✔️/❌ counts from score breakdown rows.
 * Neutral verdicts ("-") are excluded.
 */

interface RowWithVerdict {
    verdict: string;
}

interface CategoryWithRows {
    category: string;
    rows?: RowWithVerdict[];
}

export interface VerdictCounts {
    checks: number;
    xs: number;
    total: number;
    score: number; // ratio 0-100
}

export function computeVerdictCounts(categories: CategoryWithRows[]): VerdictCounts {
    let checks = 0;
    let xs = 0;

    for (const cat of categories) {
        if (!cat.rows) continue;
        for (const row of cat.rows) {
            if (row.verdict === '✔️') checks++;
            else if (row.verdict === '❌') xs++;
            // "-" and other verdicts are excluded
        }
    }

    const total = checks + xs;
    const score = total > 0 ? Math.round((checks / total) * 100) : 0;

    return { checks, xs, total, score };
}
