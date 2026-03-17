import { useCallback, useEffect, useRef, useState } from 'react';
import { useSaveEvaluationInputs, type CategoryType } from './useEvaluation';
import type { ManualData, CompetitionData } from '../components/evaluation/forms/formConfig';
import { buildManualData, mergeWithOverrides } from './manualDataUtils';
import { toRecord } from '../lib/typeGuards';

/** Type-safe keys of ManualData (excluding competition which has nested structure) */
type FlatCategory = Exclude<keyof ManualData, 'competition'>;

function isFlatCategory(key: string): key is FlatCategory {
  return ['operational', 'business', 'visitors', 'promoTools', 'products', 'ads', 'campaign'].includes(key);
}

/** Correlated update helper — preserves key-value relationship so TS doesn't widen to intersection */
function setFlatCategory<K extends FlatCategory>(
  target: Partial<ManualData>,
  category: K,
  value: ManualData[K],
): void {
  target[category] = value;
}

function isCompetitionProductKey(key: string): key is keyof CompetitionData {
  return key === 'product1' || key === 'product2' || key === 'product3';
}

function isCategoryType(value: string | null): value is CategoryType | null {
  return value === null || value === 'fashion' || value === 'non_fashion';
}

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveFormOptions {
  brandId: number;
  categoryType: string | null;
  initialData: Record<string, unknown> | null;
  marketplace?: string;
}

export function useAutoSaveForm({ brandId, categoryType, initialData, marketplace }: UseAutoSaveFormOptions) {
  const saveMutation = useSaveEvaluationInputs(brandId);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingDataRef = useRef<ManualData | null>(null);

  // Deep merge API data into defaults (M1 fix)
  const manualData = buildManualData(initialData);

  // Store latest values in refs so callbacks stay stable (M3 fix)
  const manualDataRef = useRef(manualData);
  useEffect(() => { manualDataRef.current = manualData; }, [manualData]);

  const [localOverrides, setLocalOverrides] = useState<Partial<ManualData>>({});

  const mergedData = mergeWithOverrides(manualData, localOverrides);

  // Clean up debounce timer on unmount (M4 fix)
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const doSave = useCallback(
    (dataToSave: ManualData) => {
      setSaveStatus('saving');
      saveMutation.mutate(
        {
          category_type: isCategoryType(categoryType) ? categoryType : null,
          manual_data: toRecord(dataToSave),
          marketplace,
        },
        {
          onSuccess: () => {
            setSaveStatus('saved');
            setLastSaved(new Date());
            setLocalOverrides({});
          },
          onError: () => {
            setSaveStatus('error');
          },
        },
      );
    },
    [saveMutation, categoryType, marketplace],
  );

  const scheduleSave = useCallback(
    (updatedData: ManualData) => {
      pendingDataRef.current = updatedData;
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        if (pendingDataRef.current) {
          doSave(pendingDataRef.current);
          pendingDataRef.current = null;
        }
      }, 500);
    },
    [doSave],
  );

  // Stable callback — uses refs instead of render-scoped values (M3 fix)
  const handleFieldChange = useCallback(
    (category: string, key: string, value: number | string | null) => {
      setLocalOverrides((prev) => {
        const base = manualDataRef.current;
        const updated = { ...prev };

        if (category === 'competition' && key.includes('.')) {
          const [productKey, fieldKey] = key.split('.');
          const currentComp: CompetitionData = {
            product1: { ...base.competition.product1, ...prev.competition?.product1 },
            product2: { ...base.competition.product2, ...prev.competition?.product2 },
            product3: { ...base.competition.product3, ...prev.competition?.product3 },
          };
          if (isCompetitionProductKey(productKey)) {
            currentComp[productKey] = { ...currentComp[productKey], [fieldKey]: value };
          }
          updated.competition = currentComp;
        } else if (isFlatCategory(category)) {
          const baseCategory = base[category];
          const prevCategory = prev[category];
          const currentCat = { ...baseCategory, ...prevCategory, [key]: value };
          setFlatCategory(updated, category, currentCat);
        }

        return updated;
      });
    },
    [], // Stable — reads from refs, not render-scoped values
  );

  // Use functional updater to read latest overrides without stale closure (L2 fix)
  const triggerSave = useCallback(() => {
    setLocalOverrides((currentOverrides) => {
      const base = manualDataRef.current;
      scheduleSave(mergeWithOverrides(base, currentOverrides));
      return currentOverrides;
    });
  }, [scheduleSave]);

  const retrySave = useCallback(() => {
    setLocalOverrides((currentOverrides) => {
      const base = manualDataRef.current;
      doSave(mergeWithOverrides(base, currentOverrides));
      return currentOverrides;
    });
  }, [doSave]);

  return {
    manualData: mergedData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
  };
}

// Re-exported for backward compatibility
export { buildManualData, mergeWithOverrides } from './manualDataUtils';
