import { useTranslation } from 'react-i18next';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import type { CategoryScore } from '../../../hooks/useScoring';
import { CATEGORY_MAP } from '../../../lib/categoryMap';

interface ScoreBreakdownProps {
  categoryScores: CategoryScore[];
}

export const ScoreBreakdown = ({ categoryScores }: ScoreBreakdownProps) => {
  const { t } = useTranslation();
  // Filter to categories that have actual scoring (non-zero max or negative possible)
  const scoredCategories = categoryScores.filter(
    (cat) => cat.max_score !== 0 || cat.score !== 0,
  );

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{t('scoreBreakdown.header.category')}</TableHead>
          <TableHead className="text-right">{t('scoreBreakdown.header.score')}</TableHead>
          <TableHead className="text-right">{t('scoreBreakdown.header.max')}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {scoredCategories.map((cat) => {
          const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
          return (
          <TableRow key={cat.category}>
            <TableCell className="font-medium">{mapped ? t(mapped.labelKey) : cat.category}</TableCell>
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
          );
        })}
      </TableBody>
    </Table>
  );
};
