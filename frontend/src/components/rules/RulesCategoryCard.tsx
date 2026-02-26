import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  onMessageChange?: (category: string, key: string, field: string, value: string) => void;
  validationErrors?: Record<string, string>;
}

const CATEGORY_LABELS: Record<string, string> = {
  operational: 'rules.category.operational',
  business: 'rules.category.business',
  visitors: 'rules.category.visitors',
  promo_tools: 'rules.category.promoTools',
  products_status: 'rules.category.productsStatus',
  ads: 'rules.category.ads',
  campaign: 'rules.category.campaign',
  stock: 'rules.category.stock',
  discount: 'rules.category.discount',
  marketing: 'rules.category.marketing',
};

const RULE_LABELS: Record<string, string> = {
  unfulfilled_order_rate: 'rules.label.unfulfilledOrderRate',
  late_shipment_rate: 'rules.label.lateShipmentRate',
  preparation_time: 'rules.label.preparationTime',
  chat_response_rate: 'rules.label.chatResponseRate',
  overall_rating: 'rules.label.overallRating',
  monthly_sales_trend: 'rules.label.monthlySalesTrend',
  six_month_avg_threshold: 'rules.label.sixMonthAvgThreshold',
  conversion_rate: 'rules.label.conversionRate',
  quality_ratio: 'rules.label.qualityRatio',
  returning_visitors_pct: 'rules.label.returningVisitorsPct',
  followers: 'rules.label.followers',
  usage_pct_threshold: 'rules.label.usagePctThreshold',
  effectiveness_pct_threshold: 'rules.label.effectivenessPctThreshold',
  product_count: 'rules.label.productCount',
  store_status_points: 'rules.label.storeStatusPoints',
  roi_threshold: 'rules.label.roiThreshold',
  gmv_ratio_threshold: 'rules.label.gmvRatioThreshold',
  cost_ratio_range: 'rules.label.costRatioRange',
  participation_pct_threshold: 'rules.label.participationPctThreshold',
  high_threshold: 'rules.label.highThreshold',
  mid_threshold: 'rules.label.midThreshold',
  low_penalty: 'rules.label.lowPenalty',
  fake_discount_flag: 'rules.label.fakeDiscountFlag',
  floor: 'rules.label.floor',
  floor_fashion: 'rules.label.floorFashion',
  base_subtraction: 'rules.label.baseSubtraction',
  upper_limit_base: 'rules.label.upperLimitBase',
  fashion_adjustment: 'rules.label.fashionAdjustment',
  minimum_threshold: 'rules.label.minimumThreshold',
  display_max: 'rules.label.displayMax',
  display_min: 'rules.label.displayMin',
  individual_messages: 'rules.label.individualMessages',
};

const COMPARISON_SYMBOLS: Record<string, string> = {
  gte: '\u2265',
  lte: '\u2264',
  gt: '>',
  lt: '<',
  eq: '=',
};

// Marketing value fields represent fractions (0.15 = 15%)
const MARKETING_FRACTION_KEYS = new Set([
  'floor', 'floor_fashion', 'base_subtraction', 'upper_limit_base', 'fashion_adjustment',
  'minimum_threshold', 'display_max', 'display_min',
]);

const MESSAGE_FIELD_LABELS: Record<string, string> = {
  message_pass: 'rules.message.pass',
  message_fail: 'rules.message.fail',
  message_fail_severe: 'rules.message.failSevere',
  message_no_ads: 'rules.message.noAds',
  message_too_minimal: 'rules.message.tooMinimal',
  message_no_data: 'rules.message.noData',
  message_zero: 'rules.message.zero',
  message_dependent: 'rules.message.dependent',
  message_pass_afiliasi: 'rules.message.passAfiliasi',
};

const MESSAGE_FIELDS = Object.keys(MESSAGE_FIELD_LABELS);

function getMessageFields(rule: RuleThreshold): [string, string][] {
  const fields: [string, string][] = [];
  for (const field of MESSAGE_FIELDS) {
    const val = rule[field as keyof RuleThreshold];
    if (typeof val === 'string') {
      fields.push([field, val]);
    }
  }
  return fields;
}

function extractPlaceholders(template: string): string[] {
  const matches = template.match(/\{(\w+)\}/g);
  if (!matches) return [];
  return [...new Set(matches)];
}

function formatThreshold(rule: RuleThreshold, key: string | undefined, t: (k: string) => string): string {
  // Value-only fields (marketing category) — display as percentage
  if (rule.value !== undefined) {
    if (key && MARKETING_FRACTION_KEYS.has(key)) {
      return `${(rule.value * 100).toFixed(1)}%`;
    }
    return `${rule.value}`;
  }
  // Store status — display status type labels instead of "-"
  if (rule.mall !== undefined) {
    return t('rules.perStoreType');
  }
  if (rule.min !== undefined && rule.max !== undefined && rule.min !== null && rule.max !== null) {
    return `${rule.min} - ${rule.max}`;
  }
  // Fake discount — no numeric threshold
  if (rule.points_no_flag !== undefined) {
    return t('rules.checkFlag');
  }
  const comparison = rule.comparison ? COMPARISON_SYMBOLS[rule.comparison] || rule.comparison : '';
  const value = rule.threshold ?? rule.threshold_pct ?? '';
  if (value === '' && comparison === '') return '-';
  return `${comparison} ${value}`;
}

function formatPoints(rule: RuleThreshold, t: (k: string) => string): string {
  if (rule.info_only) return t('rules.infoOnly');
  // Value-only fields (marketing) — no points column
  if (rule.value !== undefined) return '-';
  if (rule.points !== undefined) return `${rule.points} ${t('rules.points.pts')}`;
  if (rule.opportunity_points !== undefined) return `${rule.opportunity_points} ${t('rules.points.oppPts')}`;
  if (rule.points_no_flag !== undefined) return `${rule.points_no_flag} / ${rule.points_flag} ${t('rules.points.pts')}`;
  // store_status_points
  if (rule.mall !== undefined) {
    return `${t('rules.storeType.mall')}: ${rule.mall}, ${t('rules.storeType.starPlus')}: ${rule.star_plus}, ${t('rules.storeType.star')}: ${rule.star}, ${t('rules.storeType.regular')}: ${rule.regular}`;
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
  validationErrors: Record<string, string> | undefined,
  t: (k: string) => string,
) {
  // Value-only fields (marketing category) — fractions 0-1
  if (rule.value !== undefined) {
    const isFraction = MARKETING_FRACTION_KEYS.has(key);
    return (
      <span className="flex items-center gap-1">
        <EditableNumber
          value={rule.value}
          onChange={(v) => {
            if (isFraction && v !== null && (v < 0 || v > 1)) return;
            onRuleChange(category, key, 'value', v);
          }}
          label={`${key} value`}
          error={validationErrors?.[`${category}.${key}.value`]}
        />
        {isFraction && <span className="text-xs text-muted-foreground">({((rule.value ?? 0) * 100).toFixed(0)}%)</span>}
      </span>
    );
  }

  const comparison = rule.comparison ? COMPARISON_SYMBOLS[rule.comparison] || rule.comparison : '';

  // Store status — editable per store type
  if (rule.mall !== undefined) {
    return (
      <span className="flex items-center gap-1 flex-wrap">
        {t('rules.perStoreType')}
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
    return <span>{t('rules.checkFlag')}</span>;
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
  validationErrors: Record<string, string> | undefined,
  t: (k: string) => string,
) {
  if (rule.info_only) return <Badge variant="outline" className="text-muted-foreground">{t('rules.infoOnly')}</Badge>;

  // Value-only fields (marketing) — no points to edit
  if (rule.value !== undefined) return <span>-</span>;

  if (rule.points !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.points} onChange={(v) => onRuleChange(category, key, 'points', v)} label={`${key} points`} error={validationErrors?.[`${category}.${key}.points`]} />
        <span className="text-sm">{t('rules.points.pts')}</span>
      </span>
    );
  }

  if (rule.opportunity_points !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.opportunity_points} onChange={(v) => onRuleChange(category, key, 'opportunity_points', v)} label={`${key} opportunity points`} error={validationErrors?.[`${category}.${key}.opportunity_points`]} />
        <span className="text-sm">{t('rules.points.oppPts')}</span>
      </span>
    );
  }

  if (rule.points_no_flag !== undefined) {
    return (
      <span className="flex items-center gap-1">
        <EditableNumber value={rule.points_no_flag} onChange={(v) => onRuleChange(category, key, 'points_no_flag', v)} label={`${key} points no flag`} error={validationErrors?.[`${category}.${key}.points_no_flag`]} />
        <span className="text-sm">/</span>
        <EditableNumber value={rule.points_flag} onChange={(v) => onRuleChange(category, key, 'points_flag', v)} label={`${key} points flag`} error={validationErrors?.[`${category}.${key}.points_flag`]} />
        <span className="text-sm">{t('rules.points.pts')}</span>
      </span>
    );
  }

  // Store status points
  if (rule.mall !== undefined) {
    return (
      <span className="flex items-center gap-1 flex-wrap text-sm">
        <span>{t('rules.storeType.mall')}:</span>
        <EditableNumber value={rule.mall} onChange={(v) => onRuleChange(category, key, 'mall', v)} label={`${key} mall`} error={validationErrors?.[`${category}.${key}.mall`]} />
        <span>{t('rules.storeType.starPlus')}:</span>
        <EditableNumber value={rule.star_plus} onChange={(v) => onRuleChange(category, key, 'star_plus', v)} label={`${key} star plus`} error={validationErrors?.[`${category}.${key}.star_plus`]} />
        <span>{t('rules.storeType.star')}:</span>
        <EditableNumber value={rule.star} onChange={(v) => onRuleChange(category, key, 'star', v)} label={`${key} star`} error={validationErrors?.[`${category}.${key}.star`]} />
        <span>{t('rules.storeType.reg')}:</span>
        <EditableNumber value={rule.regular} onChange={(v) => onRuleChange(category, key, 'regular', v)} label={`${key} regular`} error={validationErrors?.[`${category}.${key}.regular`]} />
      </span>
    );
  }

  return <span>-</span>;
}

export const RulesCategoryCard = ({ category, rules, differingKeys, isEditing = false, onRuleChange, onMessageChange, validationErrors }: RulesCategoryCardProps) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(true);
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set());
  const maxPoints = calculateMaxPoints(rules, category);
  const label = t(CATEGORY_LABELS[category] || category);

  const toggleMessages = (key: string) => {
    setExpandedMessages((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

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
              {maxPoints > 0 ? (
                <Badge variant="secondary">{t('rules.badge.max', { points: maxPoints })}</Badge>
              ) : category === 'marketing' ? (
                <Badge variant="outline">{t('rules.badge.config')}</Badge>
              ) : null}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('rules.table.metric')}</TableHead>
                  <TableHead>{t('rules.table.threshold')}</TableHead>
                  <TableHead>{t('rules.table.points')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(rules).map(([key, rule]) => {
                  const isDiffering = differingKeys?.has(`${category}.${key}`);
                  const messageFields = getMessageFields(rule);
                  const hasMessages = messageFields.length > 0;
                  const messagesExpanded = expandedMessages.has(key);

                  return (
                    <React.Fragment key={key}>
                      <TableRow className={isDiffering ? 'bg-blue-50 dark:bg-blue-950/30' : ''}>
                        <TableCell className="font-medium">
                          <span className="flex items-center gap-1">
                            {t(RULE_LABELS[key] || key)}
                            {isDiffering && (
                              <Badge variant="outline" className="ml-1 text-xs text-blue-600 border-blue-300">
                                {t('rules.badge.different')}
                              </Badge>
                            )}
                            {hasMessages && (
                              <button
                                type="button"
                                onClick={() => toggleMessages(key)}
                                className="ml-1 text-xs text-muted-foreground hover:text-foreground"
                                aria-label={`Toggle messages for ${t(RULE_LABELS[key] || key)}`}
                              >
                                {messagesExpanded ? '▼' : '▶'} {messageFields.length} msg
                              </button>
                            )}
                          </span>
                        </TableCell>
                        <TableCell>
                          {isEditing && onRuleChange ? (
                            renderEditableThreshold(rule, category, key, onRuleChange, validationErrors, t)
                          ) : (
                            <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                              {formatThreshold(rule, key, t)}
                            </code>
                          )}
                        </TableCell>
                        <TableCell>
                          {isEditing && onRuleChange ? (
                            renderEditablePoints(rule, category, key, onRuleChange, validationErrors, t)
                          ) : rule.info_only ? (
                            <Badge variant="outline" className="text-muted-foreground">{t('rules.infoOnly')}</Badge>
                          ) : (
                            <span className="text-sm">{formatPoints(rule, t)}</span>
                          )}
                        </TableCell>
                      </TableRow>
                      {hasMessages && messagesExpanded && (
                        <TableRow className="hover:bg-transparent">
                          <TableCell colSpan={3} className="pt-0 pb-3 pl-8">
                            <div className="space-y-2">
                              {messageFields.map(([field, value]) => {
                                const placeholders = extractPlaceholders(value);
                                return (
                                  <div key={field} className="flex flex-col gap-0.5">
                                    <span className="text-xs font-medium text-muted-foreground">
                                      {t(MESSAGE_FIELD_LABELS[field] || field)}
                                    </span>
                                    {isEditing && onMessageChange ? (
                                      <div className="flex flex-col gap-0.5">
                                        <textarea
                                          value={value}
                                          onChange={(e) => onMessageChange(category, key, field, e.target.value)}
                                          className="w-full min-h-[2.5rem] rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none resize-y"
                                          aria-label={`${t(RULE_LABELS[key] || key)} ${t(MESSAGE_FIELD_LABELS[field] || field)}`}
                                          rows={1}
                                          maxLength={500}
                                        />
                                        {placeholders.length > 0 && (
                                          <span className="text-xs text-muted-foreground">
                                            {t('rules.placeholder')} {placeholders.map((p) => (
                                              <code key={p} className="mx-0.5 px-1 py-0.5 bg-muted rounded text-xs">{p}</code>
                                            ))}
                                          </span>
                                        )}
                                      </div>
                                    ) : (
                                      <span className="text-sm text-muted-foreground break-all">{value}</span>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
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
