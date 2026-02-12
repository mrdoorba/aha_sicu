import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Badge } from '../ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Input } from '../ui/input';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { RuleThreshold } from '../../hooks/useRules';

interface RulesCategoryCardProps {
  category: string;
  rules: Record<string, RuleThreshold>;
  differingKeys?: Set<string>;
  isEditing?: boolean;
  onRuleChange?: (category: string, key: string, field: string, value: number | null) => void;
  validationErrors?: Record<string, string>;
}

const CATEGORY_LABELS: Record<string, string> = {
  operational: 'Operational',
  business: 'Business',
  content: 'Content',
  visitors: 'Visitors',
  promo_tools: 'Promo Tools',
  products_status: 'Products & Status',
  ads: 'Ads',
  campaign: 'Campaign',
  stock: 'Stock',
  discount: 'Discount',
};

const RULE_LABELS: Record<string, string> = {
  unfulfilled_order_rate: 'Unfulfilled Order Rate',
  late_shipment_rate: 'Late Shipment Rate',
  preparation_time: 'Preparation Time',
  chat_response_rate: 'Chat Response Rate',
  overall_rating: 'Overall Rating',
  monthly_sales_trend: 'Monthly Sales Trend',
  six_month_avg_threshold: '6-Month Average',
  conversion_rate: 'Conversion Rate',
  quality_ratio: 'Quality Ratio',
  returning_visitors_pct: 'Returning Visitors %',
  followers: 'Followers',
  usage_pct_threshold: 'Usage %',
  effectiveness_pct_threshold: 'Effectiveness %',
  product_count: 'Product Count',
  store_status_points: 'Store Status',
  roi_threshold: 'ROI',
  gmv_ratio_threshold: 'GMV Ratio',
  cost_ratio_range: 'Cost Ratio Range',
  participation_pct_threshold: 'Participation %',
  high_threshold: 'High Stock',
  mid_threshold: 'Mid Stock',
  low_penalty: 'Low Stock',
  fake_discount_flag: 'Fake Discount',
};

const COMPARISON_SYMBOLS: Record<string, string> = {
  gte: '\u2265',
  lte: '\u2264',
  gt: '>',
  lt: '<',
  eq: '=',
};

// Fields that are editable numeric values
const EDITABLE_FIELDS = new Set([
  'threshold',
  'threshold_pct',
  'points',
  'opportunity_points',
  'min',
  'max',
  'points_no_flag',
  'points_flag',
  'mall',
  'star_plus',
  'star',
  'regular',
]);

function formatThreshold(rule: RuleThreshold): string {
  // Store status — display status type labels instead of "-"
  if (rule.mall !== undefined) {
    return 'By store type';
  }
  if (rule.min !== undefined && rule.max !== undefined && rule.min !== null && rule.max !== null) {
    return `${rule.min} - ${rule.max}`;
  }
  // Fake discount — no numeric threshold
  if (rule.points_no_flag !== undefined) {
    return 'Flag check';
  }
  const comparison = rule.comparison ? COMPARISON_SYMBOLS[rule.comparison] || rule.comparison : '';
  const value = rule.threshold ?? rule.threshold_pct ?? '';
  if (value === '' && comparison === '') return '-';
  return `${comparison} ${value}`;
}

function formatPoints(rule: RuleThreshold): string {
  if (rule.info_only) return 'Info only';
  if (rule.points !== undefined) return `${rule.points} pts`;
  if (rule.opportunity_points !== undefined) return `${rule.opportunity_points} opp pts`;
  if (rule.points_no_flag !== undefined) return `${rule.points_no_flag} / ${rule.points_flag} pts`;
  // store_status_points
  if (rule.mall !== undefined) {
    return `Mall: ${rule.mall}, Star+: ${rule.star_plus}, Star: ${rule.star}, Regular: ${rule.regular}`;
  }
  return '-';
}

// Categories where point tiers are mutually exclusive (only the highest applies)
const TIERED_CATEGORIES = new Set(['stock']);

function calculateMaxPoints(rules: Record<string, RuleThreshold>, category: string): number {
  if (TIERED_CATEGORIES.has(category)) {
    // Mutually exclusive tiers — max is the highest single tier value
    let best = 0;
    for (const rule of Object.values(rules)) {
      if (rule.points !== undefined && rule.points > best) best = rule.points;
    }
    return best;
  }

  let max = 0;
  for (const rule of Object.values(rules)) {
    if (rule.points && rule.points > 0) max += rule.points;
    if (rule.opportunity_points) max += rule.opportunity_points;
    if (rule.points_no_flag) max += rule.points_no_flag;
    if (rule.mall !== undefined) max += rule.mall;
  }
  return max;
}

function EditableNumber({
  value,
  onChange,
  label,
  error,
}: {
  value: number | null | undefined;
  onChange: (v: number | null) => void;
  label: string;
  error?: string;
}) {
  if (value === undefined) return null;
  return (
    <div className="inline-flex flex-col">
      <Input
        type="number"
        value={value ?? ''}
        onChange={(e) => {
          if (e.target.value === '') {
            onChange(null);
            return;
          }
          const parsed = parseFloat(e.target.value);
          if (!isNaN(parsed)) onChange(parsed);
        }}
        className={`w-20 h-7 text-sm${error ? ' border-destructive' : ''}`}
        aria-label={label}
      />
      {error && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}

function renderEditableThreshold(
  rule: RuleThreshold,
  category: string,
  key: string,
  onRuleChange: (category: string, key: string, field: string, value: number | null) => void,
  validationErrors?: Record<string, string>,
) {
  const comparison = rule.comparison ? COMPARISON_SYMBOLS[rule.comparison] || rule.comparison : '';

  // Store status — editable per store type
  if (rule.mall !== undefined) {
    return (
      <span className="flex items-center gap-1 flex-wrap">
        By store type
      </span>
    );
  }

  // Range (min - max)
  if (rule.min !== undefined && rule.max !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.min} onChange={(v) => onRuleChange(category, key, 'min', v)} label={`${key} min`} error={validationErrors?.[`${category}.${key}.min`]} />
        <span>-</span>
        <EditableNumber value={rule.max} onChange={(v) => onRuleChange(category, key, 'max', v)} label={`${key} max`} error={validationErrors?.[`${category}.${key}.max`]} />
      </span>
    );
  }

  // Fake discount — no threshold to edit
  if (rule.points_no_flag !== undefined) {
    return <span>Flag check</span>;
  }

  // Standard threshold or threshold_pct
  const thresholdField = rule.threshold !== undefined ? 'threshold' : rule.threshold_pct !== undefined ? 'threshold_pct' : null;
  const thresholdValue = rule.threshold !== undefined ? rule.threshold : rule.threshold_pct;

  if (thresholdField && thresholdValue !== undefined) {
    return (
      <span className="flex items-center gap-1">
        {comparison && <span>{comparison}</span>}
        <EditableNumber
          value={thresholdValue}
          onChange={(v) => onRuleChange(category, key, thresholdField, v)}
          label={`${key} threshold`}
          error={validationErrors?.[`${category}.${key}.${thresholdField}`]}
        />
      </span>
    );
  }

  return <span>-</span>;
}

function renderEditablePoints(
  rule: RuleThreshold,
  category: string,
  key: string,
  onRuleChange: (category: string, key: string, field: string, value: number | null) => void,
  validationErrors?: Record<string, string>,
) {
  if (rule.info_only) return <Badge variant="outline" className="text-muted-foreground">Info only</Badge>;

  if (rule.points !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.points} onChange={(v) => onRuleChange(category, key, 'points', v)} label={`${key} points`} error={validationErrors?.[`${category}.${key}.points`]} />
        <span className="text-sm">pts</span>
      </span>
    );
  }

  if (rule.opportunity_points !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.opportunity_points} onChange={(v) => onRuleChange(category, key, 'opportunity_points', v)} label={`${key} opportunity points`} error={validationErrors?.[`${category}.${key}.opportunity_points`]} />
        <span className="text-sm">opp pts</span>
      </span>
    );
  }

  if (rule.points_no_flag !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.points_no_flag} onChange={(v) => onRuleChange(category, key, 'points_no_flag', v)} label={`${key} points no flag`} error={validationErrors?.[`${category}.${key}.points_no_flag`]} />
        <span className="text-sm">/</span>
        <EditableNumber value={rule.points_flag} onChange={(v) => onRuleChange(category, key, 'points_flag', v)} label={`${key} points flag`} error={validationErrors?.[`${category}.${key}.points_flag`]} />
        <span className="text-sm">pts</span>
      </span>
    );
  }

  // Store status points
  if (rule.mall !== undefined) {
    return (
      <span className="flex items-center gap-1 flex-wrap text-sm">
        <span>Mall:</span>
        <EditableNumber value={rule.mall} onChange={(v) => onRuleChange(category, key, 'mall', v)} label={`${key} mall`} error={validationErrors?.[`${category}.${key}.mall`]} />
        <span>Star+:</span>
        <EditableNumber value={rule.star_plus} onChange={(v) => onRuleChange(category, key, 'star_plus', v)} label={`${key} star plus`} error={validationErrors?.[`${category}.${key}.star_plus`]} />
        <span>Star:</span>
        <EditableNumber value={rule.star} onChange={(v) => onRuleChange(category, key, 'star', v)} label={`${key} star`} error={validationErrors?.[`${category}.${key}.star`]} />
        <span>Reg:</span>
        <EditableNumber value={rule.regular} onChange={(v) => onRuleChange(category, key, 'regular', v)} label={`${key} regular`} error={validationErrors?.[`${category}.${key}.regular`]} />
      </span>
    );
  }

  return <span>-</span>;
}

export const RulesCategoryCard = ({ category, rules, differingKeys, isEditing = false, onRuleChange, validationErrors }: RulesCategoryCardProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const maxPoints = calculateMaxPoints(rules, category);
  const label = CATEGORY_LABELS[category] || category;

  return (
    <Card>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer select-none hover:bg-muted/50 transition-colors">
            <CardTitle className="flex items-center justify-between text-base">
              <span className="flex items-center gap-2">
                {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                {label}
              </span>
              {maxPoints > 0 && (
                <Badge variant="secondary">Max: {maxPoints} pts</Badge>
              )}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Metric</TableHead>
                  <TableHead>Threshold</TableHead>
                  <TableHead>Points</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(rules).map(([key, rule]) => {
                  const isDiffering = differingKeys?.has(`${category}.${key}`);
                  return (
                    <TableRow key={key} className={isDiffering ? 'bg-blue-50 dark:bg-blue-950/30' : ''}>
                      <TableCell className="font-medium">
                        {RULE_LABELS[key] || key}
                        {isDiffering && (
                          <Badge variant="outline" className="ml-2 text-xs text-blue-600 border-blue-300">
                            differs
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {isEditing && onRuleChange ? (
                          renderEditableThreshold(rule, category, key, onRuleChange, validationErrors)
                        ) : (
                          <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                            {formatThreshold(rule)}
                          </code>
                        )}
                      </TableCell>
                      <TableCell>
                        {isEditing && onRuleChange ? (
                          renderEditablePoints(rule, category, key, onRuleChange, validationErrors)
                        ) : rule.info_only ? (
                          <Badge variant="outline" className="text-muted-foreground">Info only</Badge>
                        ) : (
                          <span className="text-sm">{formatPoints(rule)}</span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};
