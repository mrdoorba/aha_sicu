import { lazy } from 'react';
import { Navigate, Route } from 'react-router-dom';
import { isPreviewEnabled } from '../../lib/preview';

const PreviewIndexPage = lazy(() =>
  import('./PreviewIndexPage').then((m) => ({ default: m.PreviewIndexPage })),
);
const ClaimVoucherPage = lazy(() =>
  import('../onboarding/ClaimVoucherPage').then((m) => ({ default: m.ClaimVoucherPage })),
);
const DiscountPage = lazy(() =>
  import('../onboarding/DiscountPage').then((m) => ({ default: m.DiscountPage })),
);
const NdaPage = lazy(() => import('../onboarding/NdaPage').then((m) => ({ default: m.NdaPage })));
const TutorialPage = lazy(() =>
  import('../onboarding/TutorialPage').then((m) => ({ default: m.TutorialPage })),
);
const SubAccountPage = lazy(() =>
  import('../onboarding/SubAccountPage').then((m) => ({ default: m.SubAccountPage })),
);
const WaitingPage = lazy(() =>
  import('../onboarding/WaitingPage').then((m) => ({ default: m.WaitingPage })),
);
const ResultPage = lazy(() =>
  import('../onboarding/ResultPage').then((m) => ({ default: m.ResultPage })),
);
const InternalNdaPage = lazy(() =>
  import('./InternalNdaPage').then((m) => ({ default: m.InternalNdaPage })),
);

/**
 * Routes for the fake-data onboarding preview.
 *
 * Returned as a fragment of <Route> elements so they sit OUTSIDE ProtectedRoute
 * — the brand-facing screens are public by nature, and requiring a SICU login
 * to look at them would defeat the point.
 *
 * On any host that isn't localhost or the Firebase dev target, every path here
 * redirects to /login rather than rendering. Fails closed: an unrecognised host
 * gets nothing.
 */
export function previewRoutes() {
  if (!isPreviewEnabled()) {
    return <Route path="/preview/*" element={<Navigate to="/login" replace />} />;
  }

  return (
    <Route path="/preview">
      <Route index element={<PreviewIndexPage />} />
      <Route path="daftar" element={<ClaimVoucherPage />} />
      <Route path="onboarding">
        <Route path="biaya" element={<DiscountPage />} />
        <Route path="nda" element={<NdaPage />} />
        <Route path="tutorial" element={<TutorialPage />} />
        <Route path="sub-akun" element={<SubAccountPage />} />
        <Route path="proses" element={<WaitingPage />} />
        <Route path="hasil" element={<ResultPage />} />
      </Route>
      <Route path="internal">
        <Route path="nda" element={<InternalNdaPage />} />
      </Route>
    </Route>
  );
}
