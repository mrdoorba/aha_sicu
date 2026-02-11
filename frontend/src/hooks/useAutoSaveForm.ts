import { useCallback, useRef, useState } from 'react';
import { useSaveEvaluationInputs } from './useEvaluation';
import type { ManualData } from '../components/evaluation/forms/formConfig';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutoSaveFormOptions {
  brandId: number;
  categoryType: string | null;
  initialData: Record<string, unknown> | null;
}

export function useAutoSaveForm({ brandId, categoryType, initialData }: UseAutoSaveFormOptions) {
  const saveMutation = useSaveEvaluationInputs(brandId);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingDataRef = useRef<ManualData | null>(null);

  // Merge raw API data (Record<string, unknown>) into typed ManualData
  const manualData: ManualData = {
    ...EMPTY_MANUAL_DATA,
    ...(initialData as Partial<ManualData> | null),
  };

  // We track local edits on top of the server data
  const [localOverrides, setLocalOverrides] = useState<Partial<ManualData>>({});

  const mergedData: ManualData = {
    ...manualData,
    ...localOverrides,
    // Deep merge each category that has local overrides
    operational: { ...manualData.operational, ...localOverrides.operational },
    business: { ...manualData.business, ...localOverrides.business },
    content: { ...manualData.content, ...localOverrides.content },
    visitors: { ...manualData.visitors, ...localOverrides.visitors },
    promoTools: { ...manualData.promoTools, ...localOverrides.promoTools },
    products: { ...manualData.products, ...localOverrides.products },
    ads: { ...manualData.ads, ...localOverrides.ads },
    campaign: { ...manualData.campaign, ...localOverrides.campaign },
    competition: {
      product1: { ...manualData.competition.product1, ...localOverrides.competition?.product1 },
      product2: { ...manualData.competition.product2, ...localOverrides.competition?.product2 },
      product3: { ...manualData.competition.product3, ...localOverrides.competition?.product3 },
    },
  };

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

  const handleFieldChange = useCallback(
    (category: string, key: string, value: number | string | null) => {
      setLocalOverrides((prev) => {
        const updated = { ...prev };

        if (category === 'competition' && key.includes('.')) {
          // Handle nested competition fields: "product1.keyword", "product1.marketPrice"
          const [productKey, fieldKey] = key.split('.');
          const currentComp = {
            product1: { ...mergedData.competition.product1, ...prev.competition?.product1 },
            product2: { ...mergedData.competition.product2, ...prev.competition?.product2 },
            product3: { ...mergedData.competition.product3, ...prev.competition?.product3 },
          };
          (currentComp as Record<string, Record<string, unknown>>)[productKey][fieldKey] = value;
          updated.competition = currentComp;
        } else {
          // Handle flat category fields
          const currentCat = {
            ...(mergedData as Record<string, Record<string, unknown>>)[category],
            ...(prev as Record<string, Record<string, unknown>>)[category],
          };
          currentCat[key] = value;
          (updated as Record<string, unknown>)[category] = currentCat;
        }

        return updated;
      });
    },
    [mergedData],
  );

  const triggerSave = useCallback(() => {
    // Recompute merged data with latest overrides
    setLocalOverrides((prev) => {
      const latestMerged: ManualData = {
        ...manualData,
        ...prev,
        operational: { ...manualData.operational, ...prev.operational },
        business: { ...manualData.business, ...prev.business },
        content: { ...manualData.content, ...prev.content },
        visitors: { ...manualData.visitors, ...prev.visitors },
        promoTools: { ...manualData.promoTools, ...prev.promoTools },
        products: { ...manualData.products, ...prev.products },
        ads: { ...manualData.ads, ...prev.ads },
        campaign: { ...manualData.campaign, ...prev.campaign },
        competition: {
          product1: { ...manualData.competition.product1, ...prev.competition?.product1 },
          product2: { ...manualData.competition.product2, ...prev.competition?.product2 },
          product3: { ...manualData.competition.product3, ...prev.competition?.product3 },
        },
      };
      scheduleSave(latestMerged);
      return prev;
    });
  }, [manualData, scheduleSave]);

  const retrySave = useCallback(() => {
    const latestMerged: ManualData = {
      ...mergedData,
    };
    doSave(latestMerged);
  }, [mergedData, doSave]);

  return {
    manualData: mergedData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
  };
}
