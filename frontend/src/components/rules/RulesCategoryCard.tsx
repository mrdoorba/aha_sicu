import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { Badge } from '../ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { RuleThreshold } from '../../hooks/useRules';

interface RulesCategoryCardProps {
  category: string;
  rules: Record<string, RuleThreshold>;
  differingKeys?: Set<string>;
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

export const RulesCategoryCard = ({ category, rules, differingKeys }: RulesCategoryCardProps) => {
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
                        <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                          {formatThreshold(rule)}
                        </code>
                      </TableCell>
                      <TableCell>
                        {rule.info_only ? (
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
