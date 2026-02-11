import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import type { CategoryScore } from '../../../hooks/useScoring';

interface ScoreBreakdownProps {
  categoryScores: CategoryScore[];
}

export const ScoreBreakdown = ({ categoryScores }: ScoreBreakdownProps) => {
  // Filter to categories that have actual scoring (non-zero max or negative possible)
  const scoredCategories = categoryScores.filter(
    (cat) => cat.max_score !== 0 || cat.score !== 0,
  );

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Category</TableHead>
          <TableHead className="text-right">Score</TableHead>
          <TableHead className="text-right">Max</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {scoredCategories.map((cat) => (
          <TableRow key={cat.category}>
            <TableCell className="font-medium">{cat.category}</TableCell>
            <TableCell
              className={`text-right tabular-nums ${
                cat.score < 0 ? 'text-destructive font-semibold' : ''
              }`}
            >
              {cat.score}
            </TableCell>
            <TableCell className="text-right tabular-nums text-muted-foreground">
              {cat.max_score}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
