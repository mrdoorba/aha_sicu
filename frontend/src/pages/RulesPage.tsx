import { useState } from 'react';
import { toast } from 'sonner';
import { useRules, type ScoringRule } from '../hooks/useRules';
import { useUpdateRule } from '../hooks/useUpdateRule';
import { useCurrentUser } from '../hooks/useCurrentUser';
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

export const RulesPage = () => {
  const { rules, isLoading, isError, refetch } = useRules();
  const { profile } = useCurrentUser();
  const updateRule = useUpdateRule();
  const [isEditing, setIsEditing] = useState(false);
  const [editedRules, setEditedRules] = useState<Record<string, Record<string, unknown>>>({});
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const canEdit = profile?.role === 'leader' || profile?.role === 'admin';

  // Find the default rule (or fall back to first available)
  const activeRule = rules.find((r) => r.template === 'default') ?? rules[0] ?? null;
  const template = (activeRule?.template ?? 'default') as 'fashion' | 'non_fashion' | 'default';

  const enterEditMode = () => {
    if (!activeRule) return;
    const cloned: Record<string, Record<string, unknown>> = {
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
      setValidationErrors((prev) => ({ ...prev, [errorKey]: 'Required' }));
    } else {
      setValidationErrors((prev) => {
        const { [errorKey]: _removed, ...rest } = prev;
        void _removed;
        return rest;
      });
    }
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[template]?.[category]?.[key]) {
        updated[template][category][key][field] = value;
      }
      return updated;
    });
  };

  const handleMessageChange = (category: string, key: string, field: string, value: string) => {
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[template]?.[category]?.[key]) {
        updated[template][category][key][field] = value;
      }
      return updated;
    });
  };

  const handleClosingMessageChange = (_tmpl: string, verdictKey: string, value: string) => {
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[template]?.interpretation?.closing_messages) {
        updated[template].interpretation.closing_messages[verdictKey] = value;
      }
      return updated;
    });
  };

  const handleCompetitionMessageChange = (_tmpl: string, field: string, value: string) => {
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[template]?.competition) {
        updated[template].competition[field] = value;
      }
      return updated;
    });
  };

  const hasValidationErrors = Object.keys(validationErrors).length > 0;

  const handleInterpretationChange = (_tmpl: string, rangeIdx: number, field: 'min' | 'max', value: number | null) => {
    setEditedRules((prev) => {
      const updated = JSON.parse(JSON.stringify(prev));
      if (updated[template]?.interpretation?.ranges?.[rangeIdx]) {
        updated[template].interpretation.ranges[rangeIdx][field] = value;
      }
      return updated;
    });
  };

  const handleSaveConfirm = async () => {
    if (!activeRule) return;
    const edited = editedRules[template];
    if (JSON.stringify(activeRule.rules) !== JSON.stringify(edited)) {
      await updateRule.mutateAsync({
        template,
        rules: edited,
      });
    }
    setShowPasswordDialog(false);
    setIsEditing(false);
    setEditedRules({});
    toast.success('Aturan berhasil diperbarui');
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
          <p className="text-destructive mb-4">Gagal memuat aturan penilaian.</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  if (!activeRule) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <p className="text-muted-foreground text-center py-12">Tidak ada aturan penilaian ditemukan.</p>
      </div>
    );
  }

  const rulesData = isEditing
    ? editedRules[template] as unknown as ScoringRule['rules']
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
          <h2 className="text-2xl font-bold tracking-tight">Aturan Penilaian</h2>
          <div className="flex items-center gap-3">
            {!isEditing && (
              <span className="text-sm text-muted-foreground">
                Updated{' '}
                {new Date(activeRule.updated_at).toLocaleDateString()}
              </span>
            )}
            {canEdit && !isEditing && (
              <Button onClick={enterEditMode}>Edit Aturan</Button>
            )}
            {isEditing && (
              <>
                <Button variant="outline" onClick={cancelEdit}>Batal</Button>
                <Button
                  onClick={() => setShowPasswordDialog(true)}
                  disabled={!hasChanges() || hasValidationErrors}
                >
                  Simpan Perubahan
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="space-y-4">
          {CATEGORY_ORDER.map((category) => {
            const categoryRules = rulesData[category];
            if (!categoryRules) return null;

            return (
              <RulesCategoryCard
                key={category}
                category={category}
                rules={categoryRules as Record<string, import('../hooks/useRules').RuleThreshold>}
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
                <CardTitle className="text-base">Pesan Kompetisi</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(rulesData.competition).map(([field, value]) => (
                  <div key={field} className="flex flex-col gap-0.5">
                    <span className="text-xs font-medium text-muted-foreground">
                      {field === 'message_pass' ? 'Kompetitif' : field === 'message_fail' ? 'Tidak kompetitif' : field}
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

          {/* Score Interpretation */}
          {rulesData.interpretation?.ranges && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Interpretasi Skor</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Rentang Skor</TableHead>
                      <TableHead>Label</TableHead>
                      <TableHead>Keputusan</TableHead>
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

          {/* G75 Closing Messages */}
          {rulesData.interpretation?.closing_messages && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Pesan Penutup (G75)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(rulesData.interpretation.closing_messages).map(([verdict, message]) => (
                  <div key={verdict} className="flex flex-col gap-0.5">
                    <span className="text-xs font-medium text-muted-foreground">
                      Keputusan: {verdict || '(kosong / performa baik)'}
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
                      <span className="text-sm text-muted-foreground">{message || '(kosong)'}</span>
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
    </main>
  );
};
