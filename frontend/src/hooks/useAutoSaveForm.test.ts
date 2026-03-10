import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildManualData, mergeWithOverrides } from './manualDataUtils';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';
import type { ManualData } from '../components/evaluation/forms/formConfig';

// ── Unit tests for pure utility functions ─────────────────────────────────

describe('buildManualData', () => {
  it('returns EMPTY_MANUAL_DATA when initialData is null', () => {
    const result = buildManualData(null);
    expect(result).toEqual(EMPTY_MANUAL_DATA);
  });

  it('deep merges partial category data preserving null defaults', () => {
    const partial = {
      operational: { unfulfilledOrderRate: 0.5 },
    } as Record<string, unknown>;

    const result = buildManualData(partial);

    // The provided field should be set
    expect(result.operational.unfulfilledOrderRate).toBe(0.5);
    // Other fields in the same category should still be null (not undefined)
    expect(result.operational.lateShipmentRate).toBeNull();
    expect(result.operational.preparationTime).toBeNull();
    expect(result.operational.chatResponseRate).toBeNull();
    expect(result.operational.overallRating).toBeNull();
  });

  it('deep merges competition nested data', () => {
    const partial = {
      competition: {
        product1: { keyword: 'sepatu' },
        // product2 and product3 missing entirely
      },
    } as Record<string, unknown>;

    const result = buildManualData(partial);

    expect(result.competition.product1.keyword).toBe('sepatu');
    expect(result.competition.product1.marketPrice).toBeNull();
    expect(result.competition.product2.keyword).toBeNull();
    expect(result.competition.product3.marketPrice).toBeNull();
  });

  it('preserves all provided values across categories', () => {
    const full = {
      operational: {
        unfulfilledOrderRate: 0.5,
        lateShipmentRate: 0.3,
        preparationTime: 0.8,
        chatResponseRate: 97,
        overallRating: 4.8,
      },
      business: {
        salesMonth0: 500000000,
        salesMonth1: null,
        salesMonth2: null,
        salesMonth3: null,
        salesMonth4: null,
        salesMonth5: null,
        conversionRate: 3.5,
      },
    } as Record<string, unknown>;

    const result = buildManualData(full);
    expect(result.operational.unfulfilledOrderRate).toBe(0.5);
    expect(result.operational.overallRating).toBe(4.8);
    expect(result.business.salesMonth0).toBe(500000000);
    expect(result.business.conversionRate).toBe(3.5);
    // Other categories default to null
    expect(result.ads.adSales).toBeNull();
  });
});

describe('mergeWithOverrides', () => {
  it('returns base data when overrides are empty', () => {
    const result = mergeWithOverrides(EMPTY_MANUAL_DATA, {});
    expect(result).toEqual(EMPTY_MANUAL_DATA);
  });

  it('overrides specific fields while preserving others', () => {
    const overrides: Partial<ManualData> = {
      operational: { ...EMPTY_MANUAL_DATA.operational, chatResponseRate: 95 },
    };

    const result = mergeWithOverrides(EMPTY_MANUAL_DATA, overrides);
    expect(result.operational.chatResponseRate).toBe(95);
    expect(result.operational.unfulfilledOrderRate).toBeNull();
    expect(result.business.salesMonth0).toBeNull();
  });

  it('deep merges competition overrides', () => {
    const base: ManualData = {
      ...EMPTY_MANUAL_DATA,
      competition: {
        product1: { keyword: 'original', marketPrice: 100 },
        product2: { keyword: null, marketPrice: null },
        product3: { keyword: null, marketPrice: null },
      },
    };

    const overrides: Partial<ManualData> = {
      competition: {
        product1: { keyword: 'updated', marketPrice: 100 },
        product2: { keyword: null, marketPrice: null },
        product3: { keyword: null, marketPrice: null },
      },
    };

    const result = mergeWithOverrides(base, overrides);
    expect(result.competition.product1.keyword).toBe('updated');
    expect(result.competition.product1.marketPrice).toBe(100);
  });
});

// ── Integration tests for the hook ────────────────────────────────────────

const mockMutate = vi.fn();

vi.mock('./useEvaluation', () => ({
  useSaveEvaluationInputs: () => ({
    mutate: mockMutate,
  }),
}));

// Must import after mocks
const { useAutoSaveForm } = await import('./useAutoSaveForm');

describe('useAutoSaveForm', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockMutate.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const defaultOptions = {
    brandId: 1,
    categoryType: 'non_fashion' as string | null,
    initialData: null as Record<string, unknown> | null,
  };

  it('returns empty manual data when initialData is null', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));
    expect(result.current.manualData).toEqual(EMPTY_MANUAL_DATA);
  });

  it('returns pre-filled data when initialData provided', () => {
    const { result } = renderHook(() =>
      useAutoSaveForm({
        ...defaultOptions,
        initialData: {
          operational: { unfulfilledOrderRate: 0.5 },
        },
      }),
    );

    expect(result.current.manualData.operational.unfulfilledOrderRate).toBe(0.5);
    expect(result.current.manualData.operational.lateShipmentRate).toBeNull();
  });

  it('starts with idle save status', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));
    expect(result.current.saveStatus).toBe('idle');
    expect(result.current.lastSaved).toBeNull();
  });

  it('updates local overrides on handleFieldChange', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.handleFieldChange('operational', 'chatResponseRate', 95);
    });

    expect(result.current.manualData.operational.chatResponseRate).toBe(95);
  });

  it('handles competition nested field changes', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.handleFieldChange('competition', 'product1.keyword', 'sepatu');
    });

    expect(result.current.manualData.competition.product1.keyword).toBe('sepatu');
    expect(result.current.manualData.competition.product1.marketPrice).toBeNull();
  });

  it('debounces save by 500ms on triggerSave', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.handleFieldChange('operational', 'overallRating', 4.8);
    });

    act(() => {
      result.current.triggerSave();
    });

    // Before debounce fires
    expect(mockMutate).not.toHaveBeenCalled();

    // After 500ms
    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(mockMutate).toHaveBeenCalledTimes(1);
    const callArgs = mockMutate.mock.calls[0][0];
    expect(callArgs.category_type).toBe('non_fashion');
    expect(callArgs.manual_data.operational.overallRating).toBe(4.8);
  });

  it('coalesces multiple triggerSave calls within debounce window', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.handleFieldChange('operational', 'overallRating', 4.8);
      result.current.triggerSave();
    });

    // Second change before debounce fires
    act(() => {
      vi.advanceTimersByTime(200);
      result.current.handleFieldChange('operational', 'chatResponseRate', 95);
      result.current.triggerSave();
    });

    // First debounce should have been canceled
    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(mockMutate).toHaveBeenCalledTimes(1);
    const callArgs = mockMutate.mock.calls[0][0];
    expect(callArgs.manual_data.operational.overallRating).toBe(4.8);
    expect(callArgs.manual_data.operational.chatResponseRate).toBe(95);
  });

  it('transitions to saving status when mutation fires', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.triggerSave();
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current.saveStatus).toBe('saving');
  });

  it('transitions to saved status on mutation success', () => {
    mockMutate.mockImplementation((_data: unknown, options: { onSuccess: () => void }) => {
      options.onSuccess();
    });

    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.triggerSave();
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current.saveStatus).toBe('saved');
    expect(result.current.lastSaved).toBeInstanceOf(Date);
  });

  it('transitions to error status on mutation failure', () => {
    mockMutate.mockImplementation((_data: unknown, options: { onError: () => void }) => {
      options.onError();
    });

    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.triggerSave();
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current.saveStatus).toBe('error');
  });

  it('retrySave calls mutation immediately without debounce', () => {
    const { result } = renderHook(() => useAutoSaveForm(defaultOptions));

    act(() => {
      result.current.handleFieldChange('ads', 'adSales', 1000000);
    });

    act(() => {
      result.current.retrySave();
    });

    // Should call immediately, no debounce needed
    expect(mockMutate).toHaveBeenCalledTimes(1);
    expect(mockMutate.mock.calls[0][0].manual_data.ads.adSales).toBe(1000000);
  });
});
