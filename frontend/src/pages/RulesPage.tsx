import { useState } from 'react';
import { Header } from '../components/layout/Header';
import { useRules, type ScoringRule } from '../hooks/useRules';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { RulesCategoryCard } from '../components/rules/RulesCategoryCard';

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
] as const;

const DIFFERING_KEYS = new Set([
  'business.conversion_rate',
  'ads.roi_threshold',
]);

export const RulesPage = () => {
  const { rules, isLoading, isError, refetch } = useRules();
  const [activeTemplate, setActiveTemplate] = useState('fashion');

  const rulesByTemplate: Record<string, ScoringRule> = {};
  for (const rule of rules) {
    rulesByTemplate[rule.template] = rule;
  }

  const activeRule = rulesByTemplate[activeTemplate];

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

  return (
    <>
      <Header />
      <main id="main-content" className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">Scoring Rules</h2>
          {activeRule && (
            <span className="text-sm text-muted-foreground">
              v{activeRule.version} &middot; Updated{' '}
              {new Date(activeRule.updated_at).toLocaleDateString()}
            </span>
          )}
        </div>

        <Tabs value={activeTemplate} onValueChange={setActiveTemplate} className="space-y-6">
          <TabsList>
            <TabsTrigger value="fashion">Fashion</TabsTrigger>
            <TabsTrigger value="non_fashion">Non-Fashion</TabsTrigger>
          </TabsList>

          {['fashion', 'non_fashion'].map((template) => {
            const rule = rulesByTemplate[template];
            if (!rule) return null;

            return (
              <TabsContent key={template} value={template} className="space-y-4">
                {CATEGORY_ORDER.map((category) => {
                  const categoryRules = rule.rules[category];
                  if (!categoryRules) return null;

                  return (
                    <RulesCategoryCard
                      key={category}
                      category={category}
                      rules={categoryRules as Record<string, import('../hooks/useRules').RuleThreshold>}
                      differingKeys={DIFFERING_KEYS}
                    />
                  );
                })}

                {/* Score Interpretation */}
                {rule.rules.interpretation?.ranges && (
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
                          {rule.rules.interpretation.ranges.map((range, idx) => (
                            <TableRow key={idx}>
                              <TableCell>
                                <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
                                  {range.min ?? 0} - {range.max ?? '100+'}
                                </code>
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
    </>
  );
};
