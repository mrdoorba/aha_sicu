import React, { useState } from 'react';
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
  operational: 'Operasional',
  business: 'Bisnis',
  content: 'Konten',
  visitors: 'Pengunjung',
  promo_tools: 'Alat Promo',
  products_status: 'Produk & Status',
  ads: 'Iklan',
  campaign: 'Kampanye',
  stock: 'Stok',
  discount: 'Diskon',
  marketing: 'Marketing',
};

const RULE_LABELS: Record<string, string> = {
  unfulfilled_order_rate: 'Tingkat Pesanan Tidak Terselesaikan',
  late_shipment_rate: 'Tingkat Keterlambatan Pengiriman',
  preparation_time: 'Masa Pengemasan',
  chat_response_rate: 'Persentase Chat Dibalas',
  overall_rating: 'Keseluruhan Penilaian',
  monthly_sales_trend: 'Tren Penjualan Bulanan',
  six_month_avg_threshold: 'Rata-rata 6 Bulan',
  conversion_rate: 'Tingkat Konversi',
  quality_ratio: 'Rasio Kualitas',
  returning_visitors_pct: 'Pengunjung Kembali %',
  followers: 'Pengikut',
  usage_pct_threshold: 'Penggunaan %',
  effectiveness_pct_threshold: 'Efektivitas %',
  product_count: 'Jumlah Produk',
  store_status_points: 'Status Toko',
  roi_threshold: 'ROI',
  gmv_ratio_threshold: 'Rasio GMV',
  cost_ratio_range: 'Rentang Rasio Biaya',
  participation_pct_threshold: 'Partisipasi %',
  high_threshold: 'Stok Tinggi',
  mid_threshold: 'Stok Sedang',
  low_penalty: 'Stok Rendah',
  fake_discount_flag: 'Diskon Palsu',
  floor: 'Batas Bawah',
  floor_fashion: 'Batas Bawah (Fashion)',
  base_subtraction: 'Pengurangan Dasar',
  upper_limit_base: 'Batas Atas Dasar',
  fashion_adjustment: 'Penyesuaian Fashion',
  minimum_threshold: 'Ambang Minimum',
  display_max: 'Tampilan Maks',
  display_min: 'Tampilan Min',
  individual_messages: 'Pesan Individual Promo',
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
  message_pass: 'Lulus',
  message_fail: 'Gagal',
  message_fail_severe: 'Gagal (parah)',
  message_no_ads: 'Tanpa iklan',
  message_too_minimal: 'Terlalu minimal',
  message_no_data: 'Tidak ada data',
  message_zero: 'Pendapatan nol',
  message_dependent: 'Terlalu bergantung',
  message_pass_afiliasi: 'Lulus (afiliasi)',
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

function formatThreshold(rule: RuleThreshold, key?: string): string {
  // Value-only fields (marketing category) — display as percentage
  if (rule.value !== undefined) {
    if (key && MARKETING_FRACTION_KEYS.has(key)) {
      return `${(rule.value * 100).toFixed(1)}%`;
    }
    return `${rule.value}`;
  }
  // Store status — display status type labels instead of "-"
  if (rule.mall !== undefined) {
    return 'Per tipe toko';
  }
  if (rule.min !== undefined && rule.max !== undefined && rule.min !== null && rule.max !== null) {
    return `${rule.min} - ${rule.max}`;
  }
  // Fake discount — no numeric threshold
  if (rule.points_no_flag !== undefined) {
    return 'Cek flag';
  }
  const comparison = rule.comparison ? COMPARISON_SYMBOLS[rule.comparison] || rule.comparison : '';
  const value = rule.threshold ?? rule.threshold_pct ?? '';
  if (value === '' && comparison === '') return '-';
  return `${comparison} ${value}`;
}

function formatPoints(rule: RuleThreshold): string {
  if (rule.info_only) return 'Info saja';
  // Value-only fields (marketing) — no points column
  if (rule.value !== undefined) return '-';
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
        Per tipe toko
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
    return <span>Cek flag</span>;
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
  if (rule.info_only) return <Badge variant="outline" className="text-muted-foreground">Info saja</Badge>;

  // Value-only fields (marketing) — no points to edit
  if (rule.value !== undefined) return <span>-</span>;

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

export const RulesCategoryCard = ({ category, rules, differingKeys, isEditing = false, onRuleChange, onMessageChange, validationErrors }: RulesCategoryCardProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set());
  const maxPoints = calculateMaxPoints(rules, category);
  const label = CATEGORY_LABELS[category] || category;

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
                <Badge variant="secondary">Max: {maxPoints} pts</Badge>
              ) : category === 'marketing' ? (
                <Badge variant="outline">Config</Badge>
              ) : null}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Metrik</TableHead>
                  <TableHead>Ambang Batas</TableHead>
                  <TableHead>Poin</TableHead>
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
                            {RULE_LABELS[key] || key}
                            {isDiffering && (
                              <Badge variant="outline" className="ml-1 text-xs text-blue-600 border-blue-300">
                                berbeda
                              </Badge>
                            )}
                            {hasMessages && (
                              <button
                                type="button"
                                onClick={() => toggleMessages(key)}
                                className="ml-1 text-xs text-muted-foreground hover:text-foreground"
                                aria-label={`Toggle messages for ${RULE_LABELS[key] || key}`}
                              >
                                {messagesExpanded ? '▼' : '▶'} {messageFields.length} msg
                              </button>
                            )}
                          </span>
                        </TableCell>
                        <TableCell>
                          {isEditing && onRuleChange ? (
                            renderEditableThreshold(rule, category, key, onRuleChange, validationErrors)
                          ) : (
                            <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                              {formatThreshold(rule, key)}
                            </code>
                          )}
                        </TableCell>
                        <TableCell>
                          {isEditing && onRuleChange ? (
                            renderEditablePoints(rule, category, key, onRuleChange, validationErrors)
                          ) : rule.info_only ? (
                            <Badge variant="outline" className="text-muted-foreground">Info saja</Badge>
                          ) : (
                            <span className="text-sm">{formatPoints(rule)}</span>
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
                                      {MESSAGE_FIELD_LABELS[field] || field}
                                    </span>
                                    {isEditing && onMessageChange ? (
                                      <div className="flex flex-col gap-0.5">
                                        <textarea
                                          value={value}
                                          onChange={(e) => onMessageChange(category, key, field, e.target.value)}
                                          className="w-full min-h-[2.5rem] rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none resize-y"
                                          aria-label={`${RULE_LABELS[key] || key} ${MESSAGE_FIELD_LABELS[field] || field}`}
                                          rows={1}
                                          maxLength={500}
                                        />
                                        {placeholders.length > 0 && (
                                          <span className="text-xs text-muted-foreground">
                                            Placeholder: {placeholders.map((p) => (
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
