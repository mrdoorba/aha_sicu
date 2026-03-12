import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import { useRules, type ScoringRules, type RuleThreshold } from '../hooks/useRules';
import type { UpdateRuleParams } from '../hooks/useUpdateRule';
import { useUpdateRule } from '../hooks/useUpdateRule';
import { useCurrentUser } from '../hooks/useCurrentUser';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { RulesCategoryCard } from '../components/rules/RulesCategoryCard';
import { PasswordConfirmDialog } from '../components/rules/PasswordConfirmDialog';

type RuleTemplate = UpdateRuleParams['template'];

function isRuleTemplate(value: string): value is RuleTemplate {
  return value === 'fashion' || value === 'non_fashion' || value === 'default';
}

const CATEGORY_ORDER = [
  'operational',
  'business',
  'visitors',
  'promo_tools',
  'products_status',
  'ads',
  'campaign',
  'stock',
  'discount',
  'marketing',
] as const;

type RuleCategory = typeof CATEGORY_ORDER[number];

/**
 * Type-safe accessor for ScoringRules category data.
 * Every key in CATEGORY_ORDER maps to Record<string, RuleThreshold> in ScoringRules.
 */
function getCategoryRules(rules: ScoringRules, category: RuleCategory): Record<string, RuleThreshold> {
  return rules[category];
}

function isRuleCategory(value: string): value is RuleCategory {
  return (CATEGORY_ORDER as readonly string[]).includes(value);
}

export const RulesPage = () => {
  const { t } = useTranslation();
  const { rules, isLoading, isError, refetch } = useRules();
  const { profile } = useCurrentUser();
  const updateRule = useUpdateRule();
  const [isEditing, setIsEditing] = useState(false);
  const [editedRules, setEditedRules] = useState<Record<string, ScoringRules>>({});
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const canEdit = profile?.role === 'leader' || profile?.role === 'admin';

  // Find the default rule (or fall back to first available)
  const activeRule = rules.find((r) => r.template === 'default') ?? rules[0] ?? null;
  const rawTemplate = activeRule?.template ?? 'default';
  const template: RuleTemplate = isRuleTemplate(rawTemplate) ? rawTemplate : 'default';

  const enterEditMode = () => {
    if (!activeRule) return;
    const cloned: Record<string, ScoringRules> = {
      [template]: JSON.parse(JSON.stringify(activeRule.rules)),
    };
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
    if (!activeRule) return false;
    return JSON.stringify(activeRule.rules) !== JSON.stringify(editedRules[template]);
  };

  const handleRuleChange = (category: string, key: string, field: string, value: number | null) => {
    const errorKey = `${template}.${category}.${key}.${field}`;
    if (value === null) {
      setValidationErrors((prev) => ({ ...prev, [errorKey]: t('rules.validation.required') }));
    } else {
      setValidationErrors((prev) => {
        const { [errorKey]: _removed, ...rest } = prev;
        void _removed;
        return rest;
      });
    }
    setEditedRules((prev) => {
      const updated: Record<string, ScoringRules> = JSON.parse(JSON.stringify(prev));
      const rules = updated[template];
      if (rules && isRuleCategory(category)) {
        const cat = getCategoryRules(rules, category);
        if (cat[key]) {
          cat[key] = { ...cat[key], [field]: value };
        }
      }
      return updated;
    });
  };

  const handleMessageChange = (category: string, key: string, field: string, value: string) => {
    setEditedRules((prev) => {
      const updated: Record<string, ScoringRules> = JSON.parse(JSON.stringify(prev));
      const rules = updated[template];
      if (rules && isRuleCategory(category)) {
        const cat = getCategoryRules(rules, category);
        if (cat[key]) {
          cat[key] = { ...cat[key], [field]: value };
        }
      }
      return updated;
    });
  };

  const handleClosingMessageChange = (_tmpl: string, verdictKey: string, value: string) => {
    setEditedRules((prev) => {
      const updated: Record<string, ScoringRules> = JSON.parse(JSON.stringify(prev));
      const closingMessages = updated[template]?.interpretation?.closing_messages;
      if (closingMessages) {
        closingMessages[verdictKey] = value;
      }
      return updated;
    });
  };

  const handleCompetitionMessageChange = (_tmpl: string, field: string, value: string) => {
    setEditedRules((prev) => {
      const updated: Record<string, ScoringRules> = JSON.parse(JSON.stringify(prev));
      const competition = updated[template]?.competition;
      if (competition && (field === 'message_pass' || field === 'message_fail')) {
        competition[field] = value;
      }
      return updated;
    });
  };

  const hasValidationErrors = Object.keys(validationErrors).length > 0;

  const handleSaveConfirm = async () => {
    if (!activeRule) return;
    const edited = editedRules[template];
    if (!edited) return;
    if (JSON.stringify(activeRule.rules) !== JSON.stringify(edited)) {
      await updateRule.mutateAsync({
        template,
        rules: { ...edited },
      });
    }
    setShowPasswordDialog(false);
    setIsEditing(false);
    setEditedRules({});
    toast.success(t('rules.page.saveSuccess'));
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3" />
          <div className="h-10 bg-muted rounded w-1/2" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-muted rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <p className="text-destructive mb-4">{t('rules.page.errorLoading')}</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            {t('rules.page.retry')}
          </button>
        </div>
      </div>
    );
  }

  if (!activeRule) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <p className="text-muted-foreground text-center py-12">{t('rules.page.noRules')}</p>
      </div>
    );
  }

  const rulesData: ScoringRules = isEditing
    ? (editedRules[template] ?? activeRule.rules)
    : activeRule.rules;

  // Filter validation errors for this template
  const templatePrefix = `${template}.`;
  const templateErrors: Record<string, string> = {};
  for (const [errKey, msg] of Object.entries(validationErrors)) {
    if (errKey.startsWith(templatePrefix)) {
      templateErrors[errKey.slice(templatePrefix.length)] = msg;
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">{t('rules.page.title')}</h2>
          <div className="flex items-center gap-3">
            {!isEditing && (
              <span className="text-sm text-muted-foreground">
                {t('rules.page.updated')}{' '}
                {new Date(activeRule.updated_at).toLocaleDateString()}
              </span>
            )}
            {canEdit && !isEditing && (
              <Button onClick={enterEditMode}>{t('rules.page.editRules')}</Button>
            )}
            {isEditing && (
              <>
                <Button variant="outline" onClick={cancelEdit}>{t('rules.page.cancel')}</Button>
                <Button
                  onClick={() => setShowPasswordDialog(true)}
                  disabled={!hasChanges() || hasValidationErrors}
                >
                  {t('rules.page.saveChanges')}
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="space-y-4">
          {CATEGORY_ORDER.map((category) => {
            const categoryRules = getCategoryRules(rulesData, category);
            if (!categoryRules) return null;

            return (
              <RulesCategoryCard
                key={category}
                category={category}
                rules={categoryRules}
                isEditing={isEditing}
                onRuleChange={handleRuleChange}
                onMessageChange={handleMessageChange}
                validationErrors={templateErrors}
              />
            );
          })}

          {/* Competition Messages */}
          {rulesData.competition && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('rules.page.competitionMessages')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(rulesData.competition).map(([field, value]) => (
                  <div key={field} className="flex flex-col gap-0.5">
                    <span className="text-xs font-medium text-muted-foreground">
                      {field === 'message_pass' ? t('rules.page.competitive') : field === 'message_fail' ? t('rules.page.notCompetitive') : field}
                    </span>
                    {isEditing ? (
                      <textarea
                        value={value ?? ''}
                        onChange={(e) => handleCompetitionMessageChange(template, field, e.target.value)}
                        className="w-full min-h-[2.5rem] rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none resize-y"
                        aria-label={`Competition ${field}`}
                        rows={1}
                        maxLength={500}
                      />
                    ) : (
                      <span className="text-sm text-muted-foreground">{value}</span>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* G75 Closing Messages */}
          {rulesData.interpretation?.closing_messages && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('rules.page.closingMessages')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(rulesData.interpretation.closing_messages).map(([verdict, message]) => (
                  <div key={verdict} className="flex flex-col gap-0.5">
                    <span className="text-xs font-medium text-muted-foreground">
                      {t('rules.page.verdictPrefix')} {verdict || t('rules.page.emptyGoodPerformance')}
                    </span>
                    {isEditing ? (
                      <textarea
                        value={message ?? ''}
                        onChange={(e) => handleClosingMessageChange(template, verdict, e.target.value)}
                        className="w-full min-h-[2.5rem] rounded-md border border-input bg-transparent px-3 py-1.5 text-sm shadow-xs focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none resize-y"
                        aria-label={`Closing message for ${verdict || 'good performance'}`}
                        rows={2}
                        maxLength={500}
                      />
                    ) : (
                      <span className="text-sm text-muted-foreground">{message || t('rules.page.empty')}</span>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

      <PasswordConfirmDialog
        open={showPasswordDialog}
        onConfirm={handleSaveConfirm}
        onCancel={() => setShowPasswordDialog(false)}
        isLoading={updateRule.isPending}
      />
    </div>
  );
};
