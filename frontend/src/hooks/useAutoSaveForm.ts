import { useCallback, useEffect, useRef, useState } from 'react';
import { useSaveEvaluationInputs } from './useEvaluation';
import type { ManualData } from '../components/evaluation/forms/formConfig';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveFormOptions {
  brandId: number;
  categoryType: string | null;
  initialData: Record<string, unknown> | null;
}

/** Deep merge initialData into EMPTY_MANUAL_DATA to preserve null defaults for missing fields */
function buildManualData(initialData: Record<string, unknown> | null): ManualData {
  const raw = (initialData ?? {}) as Partial<ManualData>;
  return {
    operational: { ...EMPTY_MANUAL_DATA.operational, ...raw.operational },
    business: { ...EMPTY_MANUAL_DATA.business, ...raw.business },
    visitors: { ...EMPTY_MANUAL_DATA.visitors, ...raw.visitors },
    promoTools: { ...EMPTY_MANUAL_DATA.promoTools, ...raw.promoTools },
    products: { ...EMPTY_MANUAL_DATA.products, ...raw.products },
    ads: { ...EMPTY_MANUAL_DATA.ads, ...raw.ads },
    campaign: { ...EMPTY_MANUAL_DATA.campaign, ...raw.campaign },
    competition: {
      product1: { ...EMPTY_MANUAL_DATA.competition.product1, ...raw.competition?.product1 },
      product2: { ...EMPTY_MANUAL_DATA.competition.product2, ...raw.competition?.product2 },
      product3: { ...EMPTY_MANUAL_DATA.competition.product3, ...raw.competition?.product3 },
    },
  };
}

/** Merge local overrides into base server data */
function mergeWithOverrides(base: ManualData, overrides: Partial<ManualData>): ManualData {
  return {
    operational: { ...base.operational, ...overrides.operational },
    business: { ...base.business, ...overrides.business },
    visitors: { ...base.visitors, ...overrides.visitors },
    promoTools: { ...base.promoTools, ...overrides.promoTools },
    products: { ...base.products, ...overrides.products },
    ads: { ...base.ads, ...overrides.ads },
    campaign: { ...base.campaign, ...overrides.campaign },
    competition: {
      product1: { ...base.competition.product1, ...overrides.competition?.product1 },
      product2: { ...base.competition.product2, ...overrides.competition?.product2 },
      product3: { ...base.competition.product3, ...overrides.competition?.product3 },
    },
  };
}

export function useAutoSaveForm({ brandId, categoryType, initialData }: UseAutoSaveFormOptions) {
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
          category_type: categoryType as 'fashion' | 'non_fashion' | null,
          manual_data: dataToSave as unknown as Record<string, unknown>,
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
    [saveMutation, categoryType],
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
          const currentComp = {
            product1: { ...base.competition.product1, ...prev.competition?.product1 },
            product2: { ...base.competition.product2, ...prev.competition?.product2 },
            product3: { ...base.competition.product3, ...prev.competition?.product3 },
          };
          (currentComp as Record<string, Record<string, unknown>>)[productKey][fieldKey] = value;
          updated.competition = currentComp;
        } else {
          const currentCat = {
            ...(base as unknown as Record<string, Record<string, unknown>>)[category],
            ...(prev as unknown as Record<string, Record<string, unknown>>)[category],
          };
          currentCat[key] = value;
          (updated as Record<string, unknown>)[category] = currentCat;
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

// Exported for testing
export { buildManualData, mergeWithOverrides };
