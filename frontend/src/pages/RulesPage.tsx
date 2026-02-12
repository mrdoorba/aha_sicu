import { useState } from 'react';
import { toast } from 'sonner';
import { Header } from '../components/layout/Header';
import { useRules, type ScoringRule } from '../hooks/useRules';
import { useUpdateRule } from '../hooks/useUpdateRule';
import { useCurrentUser } from '../hooks/useCurrentUser';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Input } from '../components/ui/input';
import { RulesCategoryCard } from '../components/rules/RulesCategoryCard';
import { PasswordConfirmDialog } from '../components/rules/PasswordConfirmDialog';

const CATEGORY_ORDER = [
  'operational',
  'business',
  'content',
  'visitors',
  'promo_tools',
  'products_status',
  'ads',
  'campaign',
  'stock',
  'discount',
  'marketing',
] as const;

const DIFFERING_KEYS = new Set([
  'business.conversion_rate',
  'ads.roi_threshold',
  'marketing.floor',
  'marketing.fashion_adjustment',
]);

export const RulesPage = () => {
  const { rules, isLoading, isError, refetch } = useRules();
  const { profile } = useCurrentUser();
  const updateRule = useUpdateRule();
  const [activeTemplate, setActiveTemplate] = useState('fashion');
  const [isEditing, setIsEditing] = useState(false);
  const [editedRules, setEditedRules] = useState<Record<string, Record<string, unknown>>>({});
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const canEdit = profile?.role === 'leader' || profile?.role === 'admin';

  const rulesByTemplate: Record<string, ScoringRule> = {};
  for (const rule of rules) {
    rulesByTemplate[rule.template] = rule;
  }

  const activeRule = rulesByTemplate[activeTemplate];

  const enterEditMode = () => {
    const cloned: Record<string, Record<string, unknown>> = {};
    for (const rule of rules) {
      cloned[rule.template] = JSON.parse(JSON.stringify(rule.rules));
    }
    setEditedRules(cloned);
    setValidationErrors({});
    setIsEditing(true);
  };

  const cancelEdit = () => {
    setEditedRules({});
    setValidationErrors({});
    setIsEditing(false);
  };

  const hasChanges = () => {
    for (const rule of rules) {
      if (JSON.stringify(rule.rules) !== JSON.stringify(editedRules[rule.template])) {
        return true;
      }
    }
    return false;
  };

  const handleRuleChange = (category: string, key: string, field: string, value: number | null) => {
    const errorKey = `${activeTemplate}.${category}.${key}.${field}`;
    if (value === null) {
      setValidationErrors((prev) => ({ ...prev, [errorKey]: 'Required' }));
    } else {
      setValidationErrors((prev) => {
        const { [errorKey]: _, ...rest } = prev;
        return rest;
      });
    }
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[activeTemplate]?.[category]?.[key]) {
        updated[activeTemplate][category][key][field] = value;
      }
      return updated;
    });
  };

  const hasValidationErrors = Object.keys(validationErrors).length > 0;

  const handleInterpretationChange = (tmpl: string, rangeIdx: number, field: 'min' | 'max', value: number | null) => {
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[tmpl]?.interpretation?.ranges?.[rangeIdx]) {
        updated[tmpl].interpretation.ranges[rangeIdx][field] = value;
      }
      return updated;
    });
  };

  const handleSaveConfirm = async () => {
    // Save all templates that changed
    for (const rule of rules) {
      const edited = editedRules[rule.template];
      if (JSON.stringify(rule.rules) !== JSON.stringify(edited)) {
        await updateRule.mutateAsync({
          template: rule.template as 'fashion' | 'non_fashion',
          rules: edited,
        });
      }
    }
    setShowPasswordDialog(false);
    setIsEditing(false);
    setEditedRules({});
    toast.success('Rules updated successfully');
  };

  if (isLoading) {
    return (
      <>
        <Header />
        <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-10 bg-muted rounded w-1/2" />
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-muted rounded" />
            ))}
          </div>
        </main>
      </>
    );
  }

  if (isError) {
    return (
      <>
        <Header />
        <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-destructive mb-4">Failed to load scoring rules.</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </main>
      </>
    );
  }

  const displayRules = isEditing ? editedRules : undefined;

  return (
    <>
      <Header />
      <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">Scoring Rules</h2>
          <div className="flex items-center gap-3">
            {activeRule && !isEditing && (
              <span className="text-sm text-muted-foreground">
                v{activeRule.version} &middot; Updated{' '}
                {new Date(activeRule.updated_at).toLocaleDateString()}
              </span>
            )}
            {canEdit && !isEditing && (
              <Button onClick={enterEditMode}>Edit Rules</Button>
            )}
            {isEditing && (
              <>
                <Button variant="outline" onClick={cancelEdit}>Cancel</Button>
                <Button
                  onClick={() => setShowPasswordDialog(true)}
                  disabled={!hasChanges() || hasValidationErrors}
                >
                  Save Changes
                </Button>
              </>
            )}
          </div>
        </div>

        <Tabs value={activeTemplate} onValueChange={setActiveTemplate} className="space-y-6">
          <TabsList>
            <TabsTrigger value="fashion">Fashion</TabsTrigger>
            <TabsTrigger value="non_fashion">Non-Fashion</TabsTrigger>
          </TabsList>

          {['fashion', 'non_fashion'].map((template) => {
            const rule = rulesByTemplate[template];
            if (!rule) return null;

            const rulesData = displayRules
              ? displayRules[template] as ScoringRule['rules']
              : rule.rules;

            // Filter validation errors for this template
            const templatePrefix = `${template}.`;
            const templateErrors: Record<string, string> = {};
            for (const [errKey, msg] of Object.entries(validationErrors)) {
              if (errKey.startsWith(templatePrefix)) {
                templateErrors[errKey.slice(templatePrefix.length)] = msg;
              }
            }

            return (
              <TabsContent key={template} value={template} className="space-y-4">
                {CATEGORY_ORDER.map((category) => {
                  const categoryRules = rulesData[category];
                  if (!categoryRules) return null;

                  return (
                    <RulesCategoryCard
                      key={category}
                      category={category}
                      rules={categoryRules as Record<string, import('../hooks/useRules').RuleThreshold>}
                      differingKeys={DIFFERING_KEYS}
                      isEditing={isEditing}
                      onRuleChange={handleRuleChange}
                      validationErrors={templateErrors}
                    />
                  );
                })}

                {/* Score Interpretation */}
                {rulesData.interpretation?.ranges && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Score Interpretation</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Score Range</TableHead>
                            <TableHead>Label</TableHead>
                            <TableHead>Verdict</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {rulesData.interpretation.ranges.map((range, idx) => (
                            <TableRow key={idx}>
                              <TableCell>
                                {isEditing ? (
                                  <span className="flex items-center gap-1">
                                    <Input
                                      type="number"
                                      value={range.min ?? ''}
                                      onChange={(e) => {
                                        const val = e.target.value === '' ? null : parseFloat(e.target.value);
                                        if (e.target.value !== '' && isNaN(val as number)) return;
                                        handleInterpretationChange(template, idx, 'min', val);
                                      }}
                                      className="w-16 h-7 text-sm"
                                      aria-label={`Range ${idx + 1} min`}
                                    />
                                    <span>-</span>
                                    <Input
                                      type="number"
                                      value={range.max ?? ''}
                                      onChange={(e) => {
                                        const val = e.target.value === '' ? null : parseFloat(e.target.value);
                                        if (e.target.value !== '' && isNaN(val as number)) return;
                                        handleInterpretationChange(template, idx, 'max', val);
                                      }}
                                      className="w-16 h-7 text-sm"
                                      aria-label={`Range ${idx + 1} max`}
                                    />
                                  </span>
                                ) : (
                                  <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                                    {range.min ?? 0} - {range.max ?? '100+'}
                                  </code>
                                )}
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant={
                                    range.label === 'Good Candidate'
                                      ? 'default'
                                      : range.label === 'Needs Review'
                                        ? 'secondary'
                                        : 'destructive'
                                  }
                                >
                                  {range.label}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-lg">{range.verdict}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            );
          })}
        </Tabs>
      </main>

      <PasswordConfirmDialog
        open={showPasswordDialog}
        onConfirm={handleSaveConfirm}
        onCancel={() => setShowPasswordDialog(false)}
        isLoading={updateRule.isPending}
      />
    </>
  );
};
